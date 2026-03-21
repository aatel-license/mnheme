"""
mnheme/brain.py
===============
Il Cervello cognitivo di MNHEME.

Il database è la memoria a lungo termine.
L'LLM è il cervello che percepisce, associa, ragiona e riflette.

Dipendenze
----------
  - mnheme.py      : MemoryDB, Feeling, Memory
  - llm_provider.py: LLMProvider agnostico da .env

Utilizzo rapido
---------------
    from mnheme        import MemoryDB
    from llm_provider  import LLMProvider
    from brain         import Brain

    db    = MemoryDB("mente.mnheme")
    llm   = LLMProvider.from_env(".env")           # legge il .env
    brain = Brain(db, llm)

    # Percepisci un input grezzo
    r = brain.perceive("Ho aperto una busta dalla banca. Le mani tremavano.")
    print(r.extracted_concept)   # "Debito"
    print(r.extracted_feeling)   # "paura"

    # RAG su memoria personale
    ans = brain.ask("Come mi sento rispetto al denaro?")
    print(ans.answer)

    # Analisi emotiva di un concetto nel tempo
    ref = brain.reflect("Debito")
    print(ref.arc)

    # Connessioni oniriche tra ricordi distanti
    dream = brain.dream()
    print(dream.connections)

    # Ritratto psicologico completo
    intro = brain.introspect()
    print(intro.portrait)
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from typing import Optional

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from mnheme       import MemoryDB, Memory, Feeling
from llm_provider import LLMProvider, LLMError


# ─────────────────────────────────────────────
# RISULTATI COGNITIVI
# ─────────────────────────────────────────────

@dataclass
class PerceptionResult:
    """Risultato di perceive()."""
    memory            : Memory
    extracted_concept : str
    extracted_feeling : str
    extracted_tags    : list[str]
    enriched_content  : str
    raw_input         : str


@dataclass
class AskResult:
    """Risultato di ask()."""
    question        : str
    answer          : str
    memories_used   : list[Memory]
    provider_used   : str
    confidence_note : str


@dataclass
class ReflectionResult:
    """Risultato di reflect()."""
    concept    : str
    reflection : str
    memories   : list[Memory]
    arc        : str


@dataclass
class DreamResult:
    """Risultato di dream()."""
    connections : str
    memories    : list[Memory]
    provider_used: str


@dataclass
class IntrospectionResult:
    """Risultato di introspect()."""
    portrait          : str
    dominant_concepts : list[str]
    emotional_map     : dict[str, int]
    total_memories    : int
    provider_used     : str


# ─────────────────────────────────────────────
# BRAIN
# ─────────────────────────────────────────────

class Brain:
    """
    Il cervello cognitivo di MNHEME.

    Parametri
    ---------
    db       : istanza di MemoryDB
    provider : LLMProvider (creato con LLMProvider.from_env(".env"))
    language : lingua per le risposte (default: "italiano")
    """

    _SYSTEM_BASE = (
        "Sei il cervello cognitivo di MNHEME, un sistema di memoria umana digitale.\n"
        "Elabora ricordi, emozioni e pattern cognitivi con profondità e sensibilità.\n"
        "Rispondi sempre in {language}.\n"
        "Sii diretto, profondo, mai banale. Niente disclaimer né frasi introduttive generiche."
    )

    def __init__(
        self,
        db       : MemoryDB,
        provider : LLMProvider,
        *,
        language : str = "italiano",
    ) -> None:
        self._db       = db
        self._llm      = provider
        self._language = language
        self._system   = self._SYSTEM_BASE.format(language=language)

    # ── PERCEIVE ─────────────────────────────

    def perceive(
        self,
        raw_input  : str,
        *,
        concept    : Optional[str]       = None,
        feeling    : Optional[str]       = None,
        tags       : Optional[list[str]] = None,
        note       : str                 = "",
        media_type : str                 = "text",
        media_data : Optional[str]       = None,
        media_mime : Optional[str]       = None,
    ) -> PerceptionResult:
        """
        Il cervello percepisce un input grezzo e lo trasforma in un ricordo strutturato.

        L'LLM estrae: concept, feeling, tags, e arricchisce il testo.
        Tutti i campi sono sovrascrivibili manualmente.

        Per input multimediali (image/audio/video/doc), usa complete_vision()
        se il provider lo supporta, e include il media come content block
        invece di serializzare il base64 nel prompt testuale.

        Parametri
        ---------
        raw_input  : testo descrittivo o titolo del ricordo
        concept    : sovrascrive il concept estratto dall'LLM
        feeling    : sovrascrive il feeling estratto dall'LLM
        tags       : sovrascrive i tag estratti dall'LLM
        note       : nota manuale allegata al ricordo
        media_type : "text" | "image" | "video" | "audio" | "doc"
        media_data : base64 puro del file (senza prefisso data:...)
                     oppure data URL completo (data:mime;base64,...)
        media_mime : MIME type es. "image/jpeg" (obbligatorio se media_data presente)

        Esempio
        -------
        >>> r = brain.perceive("Ho aperto una busta dalla banca. Le mani tremavano.")
        >>> r = brain.perceive(
        ...     "Foto del contratto firmato",
        ...     media_type = "image",
        ...     media_data = "<base64>",
        ...     media_mime = "image/jpeg",
        ... )
        """
        valid_feelings     = [f.value for f in Feeling]
        valid_feelings_str = ", ".join(valid_feelings)

        prompt = (
            f"Analizza questo input e restituisci SOLO un JSON con questi campi:\n\n"
            f"{{\n"
            f'  "concept": "concetto chiave astratto (1-3 parole, es: Debito, Famiglia, Lavoro)",\n'
            f'  "feeling": "uno ESATTO tra: {valid_feelings_str}",\n'
            f'  "tags": ["tag1", "tag2", "tag3"],\n'
            f'  "enriched": "il ricordo riscritto in prima persona con profondità psicologica (2-3 frasi)"\n'
            f"}}\n\n"
            f"Input: {raw_input}\n\n"
            f"Rispondi SOLO con il JSON, nessun altro testo."
        )

        # Determina se usare vision o testo puro
        is_media = media_type != "text" and media_data

        if is_media:
            # Estrai base64 puro se arriva come data URL
            b64 = media_data
            mime = media_mime or "application/octet-stream"
            if isinstance(b64, str) and b64.startswith("data:"):
                # formato: data:<mime>;base64,<b64>
                try:
                    header, b64 = b64.split(",", 1)
                    if not mime or mime == "application/octet-stream":
                        mime = header.split(":")[1].split(";")[0]
                except ValueError:
                    pass

            size_kb = round(len(b64) * 3 / 4 / 1024)  # stima dimensione file reale

            media_items = [{
                "type":       media_type,
                "data":       b64,
                "media_type": mime,
                "size_kb":    size_kb,
            }]

            # Arricchisci il prompt con contesto sul tipo di media
            vision_prompt = (
                f"Hai ricevuto un file {media_type.upper()} allegato.\n"
                f"Descrivi brevemente cosa vedi/senti, poi rispondi con il JSON richiesto.\n\n"
                + prompt
            )

            raw_json = self._llm.complete_vision(
                self._system,
                vision_prompt,
                media_items,
            )
        else:
            raw_json = self._llm.complete(self._system, prompt)

        parsed = _parse_json(raw_json)

        ext_concept = concept or parsed.get("concept", "Generale")
        ext_feeling = feeling or parsed.get("feeling", "nostalgia")
        ext_tags    = tags    or parsed.get("tags", [])
        enriched    = parsed.get("enriched", raw_input)

        if ext_feeling not in valid_feelings:
            ext_feeling = _closest_feeling(ext_feeling, valid_feelings)

        # Il campo content nel DB salva:
        # - per text: il testo arricchito
        # - per media: il data URL completo (per poter recuperare il file)
        if is_media and media_data:
            # Ricostruisci data URL se era solo base64
            mime = media_mime or "application/octet-stream"
            if media_data.startswith("data:"):
                db_content = media_data
            else:
                db_content = f"data:{mime};base64,{media_data}"
        else:
            db_content = enriched

        memory = self._db.remember(
            concept    = ext_concept,
            feeling    = ext_feeling,
            content    = db_content,
            media_type = media_type,
            note       = note or f"Input originale: {raw_input[:200]}",
            tags       = ext_tags,
        )

        return PerceptionResult(
            memory            = memory,
            extracted_concept = ext_concept,
            extracted_feeling = ext_feeling,
            extracted_tags    = ext_tags,
            enriched_content  = enriched,
            raw_input         = raw_input,
        )

    # ── ASK ──────────────────────────────────

    def ask(
        self,
        question     : str,
        *,
        max_memories : int = 15,
        concepts     : Optional[list[str]] = None,
    ) -> AskResult:
        """
        RAG su memoria personale: risponde usando solo i ricordi reali.

        1. Estrae keyword dalla domanda
        2. Recupera ricordi rilevanti dal DB
        3. Risponde basandosi esclusivamente su quei ricordi

        Esempio
        -------
        >>> ans = brain.ask("Come mi sento rispetto al denaro?")
        >>> ans = brain.ask("C'è qualcosa di irrisolto con la mia famiglia?")
        """
        # Step 1: keyword extraction
        kw_prompt = (
            f"Dalla domanda seguente estrai keyword e concetti per cercare in un DB di ricordi.\n"
            f'Rispondi SOLO con JSON: {{"keywords": ["kw1","kw2"], "concepts": ["Concetto1"]}}\n\n'
            f"Domanda: {question}"
        )
        kw_parsed    = _parse_json(self._llm.complete(self._system, kw_prompt))
        keywords     = kw_parsed.get("keywords", [])
        llm_concepts = concepts or kw_parsed.get("concepts", [])

        # Step 2: recupero memorie
        memories: list[Memory] = []
        seen: set[str] = set()

        def _add(mems: list[Memory]) -> None:
            for m in mems:
                if m.memory_id not in seen:
                    memories.append(m)
                    seen.add(m.memory_id)

        for c in llm_concepts:
            _add(self._db.recall(c, limit=5))
        for kw in keywords:
            _add(self._db.search(kw, limit=5))
        if not memories:
            _add(self._db.recall_all(limit=max_memories))

        memories = memories[:max_memories]
        context  = _memories_to_context(memories)

        # Step 3: risposta
        answer_prompt = (
            f"Hai accesso a questi ricordi personali:\n\n{context}\n\n"
            f"---\nDomanda: {question}\n\n"
            f"Rispondi basandoti ESCLUSIVAMENTE sui ricordi forniti.\n"
            f"Se le informazioni non bastano, dillo chiaramente.\n"
            f'Ultima riga: "Certezza: [alta/media/bassa] — [motivazione breve]"'
        )
        raw = self._llm.complete(self._system, answer_prompt)

        confidence, answer_text = _extract_trailing_line(raw, "Certezza:")

        return AskResult(
            question        = question,
            answer          = answer_text,
            memories_used   = memories,
            provider_used   = self._llm.active_profile.name,
            confidence_note = confidence,
        )

    # ── REFLECT ──────────────────────────────

    def reflect(self, concept: str) -> ReflectionResult:
        """
        Analizza l'evoluzione emotiva di un concetto nel tempo.

        Esempio
        -------
        >>> ref = brain.reflect("Debito")
        >>> ref.arc          # "da terrore silenzioso a serenità conquistata"
        >>> ref.reflection   # testo approfondito
        """
        memories = self._db.recall(concept, oldest_first=True)
        if not memories:
            raise ValueError(f"Nessun ricordo per '{concept}'")

        timeline     = self._db.concept_timeline(concept)
        feelings_seq = " → ".join(t["feeling"] for t in timeline)
        context      = _memories_to_context(memories)

        prompt = (
            f'Questi sono tutti i ricordi relativi al concetto "{concept}", '
            f"in ordine cronologico:\n\n{context}\n\n"
            f"Sequenza emotiva: {feelings_seq}\n\n"
            f"Produci una riflessione profonda su:\n"
            f'1. Come è cambiato il rapporto emotivo con "{concept}" nel tempo\n'
            f"2. Pattern ricorrenti\n"
            f"3. Cosa resta irrisolto\n"
            f"4. Il significato psicologico del percorso\n\n"
            f'Ultima riga: "Arco: [sintesi brevissima dell\'evoluzione]"'
        )

        raw       = self._llm.complete(self._system, prompt)
        arc, text = _extract_trailing_line(raw, "Arco:")

        return ReflectionResult(
            concept    = concept,
            reflection = text,
            memories   = memories,
            arc        = arc,
        )

    # ── DREAM ────────────────────────────────

    def dream(self, n_memories: int = 8) -> DreamResult:
        """
        Associazione libera: trova connessioni inattese tra ricordi distanti.
        Simula il processo onirico di consolidamento della memoria.

        Esempio
        -------
        >>> d = brain.dream()
        >>> print(d.connections)
        """
        all_mems = self._db.recall_all()
        if len(all_mems) < 2:
            raise ValueError("Servono almeno 2 ricordi per sognare.")

        # Campiona da sentimenti diversi
        by_feeling: dict[str, list[Memory]] = {}
        for m in all_mems:
            by_feeling.setdefault(m.feeling, []).append(m)

        sampled: list[Memory] = []
        feelings = list(by_feeling.keys())
        random.shuffle(feelings)
        per_f = max(1, n_memories // len(feelings))
        for f in feelings:
            sampled.extend(random.sample(by_feeling[f], min(per_f, len(by_feeling[f]))))
        random.shuffle(sampled)
        sampled = sampled[:n_memories]

        context = _memories_to_context(sampled)
        prompt  = (
            f"Questi ricordi sembrano non correlati. Trovane il filo nascosto.\n\n"
            f"{context}\n\n"
            f"Trova:\n"
            f"1. La connessione più inattesa e profonda\n"
            f"2. Il tema latente che li attraversa tutti\n"
            f"3. Cosa rivelano insieme che nessuno rivela da solo\n"
            f"4. Una metafora o immagine che li contenga tutti\n\n"
            f"Scrivi come un'analisi onirica — suggestiva, non banale."
        )

        return DreamResult(
            connections  = self._llm.complete(self._system, prompt),
            memories     = sampled,
            provider_used= self._llm.active_profile.name,
        )

    # ── INTROSPECT ───────────────────────────

    def introspect(self) -> IntrospectionResult:
        """
        Ritratto psicologico completo basato su tutti i ricordi.

        Analizza: distribuzione emotiva, pattern, tensioni irrisolte, risorse.

        Esempio
        -------
        >>> intro = brain.introspect()
        >>> print(intro.portrait)
        """
        total = self._db.count()
        if total == 0:
            raise ValueError("Database vuoto.")

        concepts = self._db.list_concepts()
        feelings = self._db.feeling_distribution()
        top_c    = sorted(concepts, key=lambda c: c["total"], reverse=True)[:8]
        top_mems = self._db.recall_all(limit=20)

        stats  = f"Totale ricordi: {total}\n\nConcetti principali:\n"
        for c in top_c:
            fs = ", ".join(f"{f}({n})" for f, n in c["feelings"].items())
            stats += f"  {c['concept']}: {c['total']} ricordi [{fs}]\n"
        stats += "\nDistribuzione emotiva:\n"
        for f, n in sorted(feelings.items(), key=lambda x: x[1], reverse=True):
            stats += f"  {f}: {n} ({n/total*100:.1f}%)\n"

        context = _memories_to_context(top_mems)
        prompt  = (
            f"Analizza questo database di ricordi e produci un ritratto psicologico.\n\n"
            f"STATISTICHE:\n{stats}\n"
            f"CAMPIONE RICORDI (più recenti):\n{context}\n\n"
            f"Produci:\n"
            f"1. Ritratto della persona — chi è, come elabora il mondo emotivo\n"
            f"2. Pattern cognitivi ricorrenti\n"
            f"3. Tensioni irrisolte più evidenti\n"
            f"4. Risorse emotive e punti di forza\n"
            f"5. Una frase che cattura l'essenza di questa mente\n\n"
            f"Sii specifico, non generalizzare."
        )

        return IntrospectionResult(
            portrait          = self._llm.complete(self._system, prompt),
            dominant_concepts = [c["concept"] for c in top_c],
            emotional_map     = feelings,
            total_memories    = total,
            provider_used     = self._llm.active_profile.name,
        )

    # ── SUMMARIZE ────────────────────────────

    def summarize(
        self,
        memories : list[Memory],
        *,
        style    : str = "narrativo",
    ) -> str:
        """
        Riassume un insieme di ricordi.

        Parametri
        ---------
        style : "narrativo" | "analitico" | "poetico"
        """
        if not memories:
            return "Nessun ricordo da riassumere."

        styles = {
            "narrativo":  "Prima persona, fluido, continuo.",
            "analitico":  "Analizza pattern, cause, temi. Tono oggettivo.",
            "poetico":    "Prosa poetica. Immagini, ritmo, emozione.",
        }
        instr = styles.get(style, styles["narrativo"])
        context = _memories_to_context(memories)

        return self._llm.complete(
            self._system,
            f"Riassumi questi ricordi personali.\n\n{context}\n\n"
            f"{instr}\nMantieni la complessità emotiva. Non semplificare."
        )

    def __repr__(self) -> str:
        return (
            f"Brain(\n"
            f"  db={self._db!r}\n"
            f"  llm={self._llm!r}\n"
            f"  language='{self._language}'\n"
            f")"
        )


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _memories_to_context(memories: list[Memory]) -> str:
    lines = []
    for i, m in enumerate(memories, 1):
        ts = m.timestamp[:10]

        # Per media non-testuali, NON includiamo il contenuto base64 raw
        # nel contesto LLM — esploderebbe il context window.
        # Includiamo invece una descrizione compatta del media.
        media_type = getattr(m, "media_type", "text") or "text"
        if media_type != "text":
            content_display = f"[{media_type.upper()} — {len(m.content)} bytes b64]"
        else:
            # Testo: tronchiamo a 500 chars per non sprecare token
            content_display = m.content[:500] + ("…" if len(m.content) > 500 else "")

        lines.append(
            f"[{i}] {ts} | Concetto: {m.concept} | Sentimento: {m.feeling}\n"
            f"    Contenuto: {content_display}\n"
            f"    Note: {m.note or '—'}  |  Tag: {', '.join(m.tags) or '—'}"
        )
    return "\n\n".join(lines)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(
            l for l in text.split("\n") if not l.strip().startswith("```")
        ).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return {}


def _extract_trailing_line(text: str, prefix: str) -> tuple[str, str]:
    """Estrae l'ultima riga con il prefisso dato e restituisce (valore, testo_rimanente)."""
    lines = text.strip().split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith(prefix):
            value = lines[i].strip()[len(prefix):].strip()
            body  = "\n".join(lines[:i]).strip()
            return value, body
    return "", text.strip()


def _closest_feeling(candidate: str, valid: list[str]) -> str:
    candidate = candidate.lower()
    for v in valid:
        if candidate in v or v in candidate:
            return v
    return "nostalgia"
