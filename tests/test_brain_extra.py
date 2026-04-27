"""
test_brain_extra.py — Copertura delle funzionalità di brain.py non ancora coperte.

Copre: summarize(), _parse_json(), _extract_trailing_line(), _closest_feeling(),
       _memories_to_context(), PersonaResult.__post_init__, WillResult, ChoiceResult,
       brain.ask(), brain.reflect(), brain.dream(), brain.introspect()
"""
import json
import os
import tempfile
import pytest

from mnheme import MemoryDB, Feeling, Memory
from llm_provider import LLMProvider, ProviderProfile
from brain import (
    Brain, PersonaResult, WillResult, ChoiceResult,
    PerceptionResult, AskResult, ReflectionResult, DreamResult, IntrospectionResult,
    _parse_json, _extract_trailing_line, _closest_feeling, _memories_to_context,
)


# ── MockLLM ───────────────────────────────────────────────────────────────────

class FlexMockLLM(LLMProvider):
    """Mock LLM configurabile per risposta."""

    def __init__(self, response: str = "{}"):
        p = ProviderProfile(name="mock", url="http://mock", model="mock-model", api_key="", rpm=9999)
        super().__init__({"mock": p}, active="mock")
        self._response = response

    def complete(self, system, user, **kw):
        return self._response

    def complete_vision(self, system, user, media_items):
        return self._response


def _make_db(tmp_path=None):
    if tmp_path is None:
        tmp_path = tempfile.mkdtemp()
    else:
        tmp_path = str(tmp_path)
    db = MemoryDB(os.path.join(tmp_path, "brain_test.mnheme"))
    db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.")
    db.remember("Famiglia", Feeling.AMORE, "Sorriso di mia figlia.")
    db.remember("Viaggio", Feeling.NOSTALGIA, "Lisbona sotto la pioggia.")
    db.remember("Lavoro", Feeling.RABBIA, "Il capo mi ha ignorato.")
    db.remember("Salute", Feeling.PAURA, "Risultati degli esami.")
    return db


# ── _parse_json ───────────────────────────────────────────────────────────────

def test_parse_json_plain():
    assert _parse_json('{"a": 1}') == {"a": 1}


def test_parse_json_with_fences():
    text = '```json\n{"a": 1}\n```'
    result = _parse_json(text)
    assert result.get("a") == 1


def test_parse_json_embedded():
    text = 'Testo prima {"x": 42} testo dopo'
    result = _parse_json(text)
    assert result.get("x") == 42


def test_parse_json_fallback_braces():
    text = 'prefix { "k": "v" } suffix extra'
    result = _parse_json(text)
    assert result.get("k") == "v"


def test_parse_json_empty():
    assert _parse_json("") == {}


def test_parse_json_no_json():
    assert _parse_json("nessun json qui") == {}


def test_parse_json_nested():
    text = '{"outer": {"inner": 1}}'
    result = _parse_json(text)
    assert result["outer"]["inner"] == 1


# ── _extract_trailing_line ────────────────────────────────────────────────────

def test_extract_trailing_line_found():
    text = "Prima riga\nSeconda riga\nArco: da paura a speranza"
    value, body = _extract_trailing_line(text, "Arco:")
    assert value == "da paura a speranza"
    assert "Prima riga" in body


def test_extract_trailing_line_not_found():
    text = "Prima riga\nSeconda riga"
    value, body = _extract_trailing_line(text, "Arco:")
    assert value == ""
    assert body == text.strip()


def test_extract_trailing_line_middle():
    text = "Prima\nArco: sintesi\nUltima riga"
    value, body = _extract_trailing_line(text, "Arco:")
    # Cerca dall'ultimo — qui è a metà, ma deve trovare comunque
    assert "Ultima riga" not in value


# ── _closest_feeling ──────────────────────────────────────────────────────────

def test_closest_feeling_exact_substring():
    valid = ["ansia", "paura", "gioia"]
    assert _closest_feeling("ansia forte", valid) == "ansia"


def test_closest_feeling_no_match():
    valid = ["ansia", "paura", "gioia"]
    result = _closest_feeling("xyzxyz", valid)
    assert result == "neutralità"


def test_closest_feeling_valid_in_candidate():
    valid = ["nostalgia", "amore", "malinconia"]
    assert _closest_feeling("malinconia_profonda", valid) == "malinconia"


# ── _memories_to_context ──────────────────────────────────────────────────────

def test_memories_to_context_text(tmp_path):
    db = _make_db(tmp_path)
    mems = db.recall_all(limit=2)
    ctx = _memories_to_context(mems)
    assert "Concetto:" in ctx
    assert "Sentimento:" in ctx


def test_memories_to_context_media(tmp_path):
    db = _make_db(tmp_path)
    # Aggiungi un ricordo multimediale
    db.remember("Foto", Feeling.GIOIA, "data:image/jpeg;base64,abc", media_type="image")
    mems = db.recall("Foto")
    ctx = _memories_to_context(mems)
    assert "[IMAGE" in ctx


def test_memories_to_context_long_content(tmp_path):
    db = _make_db(tmp_path)
    long_text = "X" * 600
    db.remember("Lungo", Feeling.NOIA, long_text)
    mems = db.recall("Lungo")
    ctx = _memories_to_context(mems)
    assert "…" in ctx


def test_memories_to_context_empty():
    ctx = _memories_to_context([])
    assert ctx == ""


# ── PersonaResult __post_init__ ───────────────────────────────────────────────

def test_persona_result_post_init():
    p = PersonaResult(
        core_traits=[1, None, "testardo"],
        values=[2, "lealtà"],
        fears=[3],
        desires=[4],
        voice="diretto",
        worldview="Il mondo...",
        persona_summary="Sono...",
        provider_used="mock",
    )
    # Tutti i valori devono essere str
    assert all(isinstance(t, str) for t in p.core_traits)
    assert all(isinstance(v, str) for v in p.values)


# ── Brain.ask() ───────────────────────────────────────────────────────────────

def test_ask(tmp_path):
    db = _make_db(tmp_path)
    ask_response = (
        'Hai accesso a questi ricordi.\n'
        'La risposta è che ho paura del debito.\n'
        'Certezza: alta — molti ricordi su questo tema'
    )
    mock = FlexMockLLM(
        json.dumps({"keywords": ["debito"], "concepts": ["Debito"]})
    )

    class DualMock(FlexMockLLM):
        def __init__(self):
            super().__init__()
            self._calls = 0

        def complete(self, system, user, **kw):
            self._calls += 1
            if self._calls == 1:
                return json.dumps({"keywords": ["debito"], "concepts": ["Debito"]})
            return ask_response

    brain = Brain(db, DualMock())
    result = brain.ask("Come mi sento riguardo al debito?")
    assert isinstance(result, AskResult)
    assert result.question == "Come mi sento riguardo al debito?"


def test_ask_no_memories_fallback(tmp_path):
    """ask() con DB quasi vuoto ricade su recall_all."""
    path = os.path.join(str(tmp_path), "ask_empty.mnheme")
    db = MemoryDB(path)
    db.remember("Solo", Feeling.GIOIA, "un ricordo")

    class DualMock(FlexMockLLM):
        def __init__(self):
            super().__init__()
            self._calls = 0

        def complete(self, system, user, **kw):
            self._calls += 1
            if self._calls == 1:
                return "{}"  # nessuna keyword/concept
            return "Risposta generica.\nCertezza: bassa — poche info"

    brain = Brain(db, DualMock())
    result = brain.ask("Qual è il tuo umore?")
    assert isinstance(result, AskResult)


# ── Brain.reflect() ───────────────────────────────────────────────────────────

def test_reflect(tmp_path):
    db = _make_db(tmp_path)
    mock = FlexMockLLM("Riflessione profonda.\nArco: da ansia a sollievo")
    brain = Brain(db, mock)
    result = brain.reflect("Debito")
    assert isinstance(result, ReflectionResult)
    assert result.concept == "Debito"
    assert result.arc == "da ansia a sollievo"


def test_reflect_no_memories(tmp_path):
    path = os.path.join(str(tmp_path), "ref.mnheme")
    db = MemoryDB(path)
    brain = Brain(db, FlexMockLLM())
    with pytest.raises(ValueError, match="Nessun ricordo"):
        brain.reflect("Concetto_Inesistente")


# ── Brain.dream() ────────────────────────────────────────────────────────────

def test_dream(tmp_path):
    db = _make_db(tmp_path)
    brain = Brain(db, FlexMockLLM("Connessioni oniriche tra i ricordi..."))
    result = brain.dream()
    assert isinstance(result, DreamResult)
    assert len(result.memories) > 0
    assert result.provider_used == "mock"


def test_dream_too_few_memories(tmp_path):
    path = os.path.join(str(tmp_path), "dream.mnheme")
    db = MemoryDB(path)
    db.remember("Solo", Feeling.GIOIA, "un ricordo")
    brain = Brain(db, FlexMockLLM())
    with pytest.raises(ValueError, match="almeno 2"):
        brain.dream()


def test_dream_custom_n(tmp_path):
    db = _make_db(tmp_path)
    brain = Brain(db, FlexMockLLM("sogno..."))
    result = brain.dream(n_memories=3)
    assert len(result.memories) <= 3


# ── Brain.introspect() ───────────────────────────────────────────────────────

def test_introspect(tmp_path):
    db = _make_db(tmp_path)
    brain = Brain(db, FlexMockLLM("Ritratto psicologico."))
    result = brain.introspect()
    assert isinstance(result, IntrospectionResult)
    assert result.total_memories == 5


def test_introspect_empty_db(tmp_path):
    path = os.path.join(str(tmp_path), "intr.mnheme")
    db = MemoryDB(path)
    brain = Brain(db, FlexMockLLM())
    with pytest.raises(ValueError, match="vuoto"):
        brain.introspect()


# ── Brain.summarize() ────────────────────────────────────────────────────────

def test_summarize(tmp_path):
    db = _make_db(tmp_path)
    mems = db.recall_all(limit=3)
    brain = Brain(db, FlexMockLLM("Riassunto narrativo."))
    result = brain.summarize(mems)
    assert isinstance(result, str)
    assert "Riassunto" in result


def test_summarize_empty(tmp_path):
    db = _make_db(tmp_path)
    brain = Brain(db, FlexMockLLM())
    result = brain.summarize([])
    assert "Nessun" in result


def test_summarize_styles(tmp_path):
    db = _make_db(tmp_path)
    mems = db.recall_all(limit=2)
    for style in ["narrativo", "analitico", "poetico", "unknown_style"]:
        brain = Brain(db, FlexMockLLM(f"Risposta stile {style}"))
        result = brain.summarize(mems, style=style)
        assert isinstance(result, str)


# ── Brain.__repr__ ───────────────────────────────────────────────────────────

def test_brain_repr(tmp_path):
    db = _make_db(tmp_path)
    brain = Brain(db, FlexMockLLM())
    r = repr(brain)
    assert "Brain" in r
    assert "language" in r


# ── Brain language parameter ─────────────────────────────────────────────────

def test_brain_language(tmp_path):
    db = _make_db(tmp_path)
    brain = Brain(db, FlexMockLLM(), language="english")
    assert brain._language == "english"
    assert "english" in brain._system


# ── Brain.persona() edge cases ───────────────────────────────────────────────

def test_persona_empty_db(tmp_path):
    path = os.path.join(str(tmp_path), "persona.mnheme")
    db = MemoryDB(path)
    brain = Brain(db, FlexMockLLM())
    with pytest.raises(ValueError, match="vuoto"):
        brain.persona()


def test_persona_partial_json(tmp_path):
    """persona() con JSON parziale deve produrre PersonaResult senza crash."""
    db = _make_db(tmp_path)
    # JSON con solo alcuni campi
    partial = json.dumps({"core_traits": ["a", "b"]})
    brain = Brain(db, FlexMockLLM(partial))
    p = brain.persona()
    assert isinstance(p, PersonaResult)
    assert p.core_traits == ["a", "b"]
    assert p.values == []


# ── Brain.will() edge cases ──────────────────────────────────────────────────

def test_will_with_persona(tmp_path):
    db = _make_db(tmp_path)
    persona = PersonaResult(
        core_traits=["testardo"],
        values=["libertà"],
        fears=["abbandono"],
        desires=["capire"],
        voice="diretto",
        worldview="Il mondo delude",
        persona_summary="Sono...",
        provider_used="mock",
    )
    will_resp = json.dumps({
        "impulse": "Voglio partire",
        "impulse_type": "desiderio",
        "action": "Prenotare un volo",
        "why": "Perché resto troppo fermo.",
    })
    brain = Brain(db, FlexMockLLM(will_resp))
    w = brain.will(persona=persona)
    assert isinstance(w, WillResult)
    assert w.impulse_type == "desiderio"


def test_will_invalid_impulse_type(tmp_path):
    db = _make_db(tmp_path)
    will_resp = json.dumps({
        "impulse": "Voglio qualcosa",
        "impulse_type": "tipo_invalido",
        "action": "Qualcosa",
        "why": "Perché sì.",
    })
    brain = Brain(db, FlexMockLLM(will_resp))
    w = brain.will()
    # Fallback a "desiderio"
    assert w.impulse_type == "desiderio"


def test_will_with_seed_feeling_no_match(tmp_path):
    """seed_feeling che non corrisponde a nessun ricordo → usa tutti i ricordi."""
    db = _make_db(tmp_path)
    will_resp = json.dumps({
        "impulse": "Voglio qualcosa",
        "impulse_type": "curiosità",
        "action": "Esploro",
        "why": "Perché posso.",
    })
    brain = Brain(db, FlexMockLLM(will_resp))
    w = brain.will(seed_feeling="sentimento_inesistente_xyz")
    assert isinstance(w, WillResult)


# ── Brain.choose() edge cases ────────────────────────────────────────────────

def test_choose_less_than_two_options(tmp_path):
    db = _make_db(tmp_path)
    brain = Brain(db, FlexMockLLM())
    with pytest.raises(ValueError, match="2 opzioni"):
        brain.choose(["sola_opzione"])


def test_choose_with_context(tmp_path):
    db = _make_db(tmp_path)
    choice_resp = json.dumps({
        "chosen_index": 0,
        "reasoning": "Per via dell'ansia.",
        "emotional_driver": "ansia",
        "certainty": "sicuro",
        "rejected": {"B": "troppo rischioso"},
    })
    brain = Brain(db, FlexMockLLM(choice_resp))
    c = brain.choose(["restare", "partire"], context="situazione familiare")
    assert isinstance(c, ChoiceResult)
    assert c.chosen in ["restare", "partire"]


def test_choose_chosen_by_name(tmp_path):
    """chosen viene estratto per nome ('chosen') invece di chosen_index."""
    db = _make_db(tmp_path)
    choice_resp = json.dumps({
        "chosen": "partire",
        "reasoning": "Ragione.",
        "emotional_driver": "nostalgia",
        "certainty": "riluttante",
        "rejected": [],
    })
    brain = Brain(db, FlexMockLLM(choice_resp))
    c = brain.choose(["restare", "partire"])
    assert c.chosen == "partire"


def test_choose_out_of_bounds_index(tmp_path):
    """chosen_index fuori range → fallback a options[0]."""
    db = _make_db(tmp_path)
    choice_resp = json.dumps({
        "chosen_index": 999,
        "reasoning": "Ragione.",
        "emotional_driver": "gioia",
        "certainty": "sicuro",
        "rejected": {},
    })
    brain = Brain(db, FlexMockLLM(choice_resp))
    c = brain.choose(["a", "b"])
    assert c.chosen == "a"


def test_choose_reasoning_as_list(tmp_path):
    """reasoning come lista di stringhe deve essere convertito in stringa."""
    db = _make_db(tmp_path)
    choice_resp = json.dumps({
        "chosen_index": 1,
        "reasoning": ["Prima ragione", "Seconda ragione"],
        "emotional_driver": "ansia",
        "certainty": "incerto molto",
        "rejected": {},
    })
    brain = Brain(db, FlexMockLLM(choice_resp))
    c = brain.choose(["a", "b"])
    assert isinstance(c.reasoning, str)
    assert "Prima" in c.reasoning
    # certainty deve essere solo la prima parola
    assert c.certainty == "incerto"


def test_choose_rejected_list_fallback(tmp_path):
    """rejected come lista invece di dict."""
    db = _make_db(tmp_path)
    choice_resp = json.dumps({
        "chosen_index": 0,
        "reasoning": "Motivazione.",
        "emotional_driver": "gioia",
        "certainty": "sicuro",
        "rejected": ["b non va bene"],
    })
    brain = Brain(db, FlexMockLLM(choice_resp))
    c = brain.choose(["a", "b"])
    assert isinstance(c.rejected, list)


def test_choose_emotional_driver_fallback(tmp_path):
    """Se emotional_driver è vuoto, viene calcolato dai ricordi."""
    db = _make_db(tmp_path)
    choice_resp = json.dumps({
        "chosen_index": 0,
        "reasoning": "Motivazione.",
        "certainty": "sicuro",
        "rejected": {},
    })
    brain = Brain(db, FlexMockLLM(choice_resp))
    c = brain.choose(["a", "b"])
    # Non deve crashare, emotional_driver può essere stringa o vuoto
    assert isinstance(c.emotional_driver, str)


def test_choose_chosen_fuzzy_match(tmp_path):
    """chosen by name con match parziale (es. 'partire lontano' → 'partire')."""
    db = _make_db(tmp_path)
    choice_resp = json.dumps({
        "chosen": "partire lontano",  # non esatto ma contiene 'partire'
        "reasoning": "Ragione.",
        "emotional_driver": "nostalgia",
        "certainty": "riluttante",
        "rejected": {},
    })
    brain = Brain(db, FlexMockLLM(choice_resp))
    c = brain.choose(["restare", "partire"])
    assert c.chosen == "partire"


# ── ChoiceResult con DB vuoto ─────────────────────────────────────────────────

def test_choose_empty_db(tmp_path):
    path = os.path.join(str(tmp_path), "empty.mnheme")
    db = MemoryDB(path)
    brain = Brain(db, FlexMockLLM())
    c = brain.choose(["a", "b"])
    assert c.chosen == "a"
    assert c.certainty == "incerto"
