"""
test_personality.py — Test Brain persona(), will(), choose() con mock LLM
"""
import tempfile
from mnheme import MemoryDB, Feeling
from llm_provider import LLMProvider, ProviderProfile
from brain import Brain, PersonaResult, WillResult, ChoiceResult


class MockLLM(LLMProvider):
    """Mock provider per test deterministici."""
    def __init__(self):
        p = ProviderProfile(name="mock", url="http://mock", model="mock", api_key="", rpm=9999)
        super().__init__({"mock": p}, active="mock")

    def complete(self, system, user, **kw):
        import json as _j
        if '"core_traits"' in user:
            return _j.dumps({
                "core_traits": ["testardo", "ipersensibile", "ironico"],
                "values": ["lealtà", "autonomia"],
                "fears": ["abbandono", "stagnazione"],
                "desires": ["essere capito", "creare qualcosa di vero"],
                "voice": "diretto, tagliente, ironico",
                "worldview": "Il mondo delude, ma vale la pena amarlo lo stesso",
                "persona_summary": "Sono una persona che ha sofferto molto ma non si è arresa."
            })
        if '"impulse"' in user:
            return _j.dumps({
                "impulse": "Voglio smettere di giustificarmi con chiunque",
                "impulse_type": "ribellione",
                "action": "Scrivere una lettera che non spedirò mai",
                "why": "Perché ho passato troppo tempo a spiegare le mie scelte."
            })
        if '"chosen_index"' in user:
            return _j.dumps({
                "chosen_index": 1,
                "reasoning": "Partire è l'unica via per non stagnare.",
                "emotional_driver": "paura di stagnare",
                "certainty": "riluttante",
                "rejected": {"A": "restare: troppo comodo"}
            })
        return "{}"


def make_brain(tmp_path=None):
    import os
    if tmp_path is None:
        tmp_path = tempfile.mkdtemp()
    else:
        tmp_path = str(tmp_path)
    db = MemoryDB(os.path.join(tmp_path, "test.mnheme"))
    mock = MockLLM()
    # Carica ricordi di base
    db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.")
    db.remember("Famiglia", Feeling.AMORE, "Sorriso di mia figlia.")
    db.remember("Viaggio", Feeling.NOSTALGIA, "Lisbona con la pioggia.")
    return Brain(db, mock), db


def make_empty_brain(tmp_path=None):
    """Crea un Brain con DB vuoto (path temporaneo)."""
    import os
    if tmp_path is None:
        tmp_path = tempfile.mkdtemp()
    else:
        tmp_path = str(tmp_path)
    db = MemoryDB(os.path.join(tmp_path, "empty.mnheme"))
    mock = MockLLM()
    return Brain(db, mock)


def test_persona():
    brain, _ = make_brain()
    p = brain.persona()
    assert isinstance(p, PersonaResult)
    assert len(p.core_traits) >= 3
    assert len(p.values) >= 2
    assert len(p.fears) >= 1
    assert "stagnazione" in p.worldview.lower() or "delude" in p.worldview.lower()


def test_persona_empty_db(tmp_path):
    brain = make_empty_brain(tmp_path)
    # persona() richiede almeno un ricordo
    try:
        brain.persona()
        assert False, "Doveva sollevare ValueError"
    except ValueError as e:
        assert "vuoto" in str(e).lower() or "Nessuna identità" in str(e)


def test_will():
    brain, _ = make_brain()
    w = brain.will()
    assert isinstance(w, WillResult)
    assert len(w.impulse) > 0
    assert w.impulse_type == "ribellione"
    assert len(w.action) > 0
    assert len(w.why) > 0


def test_will_seed_feeling():
    brain, _ = make_brain()
    w = brain.will(seed_feeling="ansia")
    assert isinstance(w, WillResult)
    assert len(w.impulse) > 0


def test_will_empty_db(tmp_path):
    brain = make_empty_brain(tmp_path)
    # will() richiede almeno 2 ricordi
    try:
        brain.will()
        assert False, "Doveva sollevare ValueError"
    except ValueError as e:
        assert "2 ricordi" in str(e) or "almeno" in str(e).lower()


def test_choose():
    brain, _ = make_brain()
    c = brain.choose(
        ["restare", "partire", "aspettare"],
        context="abbandonare la propria città",
    )
    assert isinstance(c, ChoiceResult)
    assert c.chosen in ["restare", "partire", "aspettare"]


def test_choose_with_persona():
    brain, _ = make_brain()
    p = brain.persona()
    c = brain.choose(
        ["restare", "partire"],
        context="lasciare casa",
        persona=p,
    )
    assert isinstance(c, ChoiceResult)


def test_choose_empty_db(tmp_path):
    brain = make_empty_brain(tmp_path)
    # choose() con DB vuoto ritorna la prima opzione come fallback
    c = brain.choose(["opz_a", "opz_b"])
    assert isinstance(c, ChoiceResult)


def test_choose_single_option(tmp_path):
    brain = make_empty_brain(tmp_path)
    try:
        brain.choose(["solo"])
        assert False, "Doveva sollevare ValueError"
    except ValueError as e:
        assert "2 opzioni" in str(e)


def test_provider_used_in_persona():
    brain, _ = make_brain()
    p = brain.persona()
    assert p.provider_used == "mock"


def test_provider_used_in_will():
    brain, _ = make_brain()
    w = brain.will()
    assert w.provider_used == "mock"


def test_provider_used_in_choose():
    brain, _ = make_brain()
    c = brain.choose(["a", "b"])
    assert c.provider_used == "mock"
