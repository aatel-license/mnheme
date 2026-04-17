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

from mnheme import MemoryDB, Memory, Feeling
from llm_provider import LLMProvider, LLMError


# ─────────────────────────────────────────────
# RISULTATI COGNITIVI
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# RISULTATI — PERSONALITÀ E LIBERO ARBITRIO
# ─────────────────────────────────────────────


@dataclass
class PersonaResult:
    core_traits: list[str]
    values: list[str]
    fears: list[str]
    desires: list[str]
    voice: str
    worldview: str
    persona_summary: str
    provider_used: str

    def __post_init__(self):
        # Garantisce str in tutte le liste — immune a parser che ritorna int/None
        self.core_traits = [str(v) for v in self.core_traits]
        self.values = [str(v) for v in self.values]
        self.fears = [str(v) for v in self.fears]
        self.desires = [str(v) for v in self.desires]


@dataclass
class PersonaResulta:
    """
    Identità stabile estratta dall'intera storia di ricordi.
    Diverso da IntrospectionResult: questo è un profilo *persistente*,
    pensato per essere passato come contesto ad altre operazioni.
    """

    core_traits: list[str]  # tratti caratteriali stabili (es. "testardo", "curioso")
    values: list[str]  # valori profondi (es. "lealtà", "autonomia")
    fears: list[str]  # paure ricorrenti distillate dai ricordi
    desires: list[str]  # desideri profondi mai esplicitamente dichiarati
    voice: str  # come pensa/parla — stile, ritmo, tono
    worldview: str  # come vede il mondo in una frase
    persona_summary: str  # persona compatta in 3-4 righe — usabile come system prompt
    provider_used: str


@dataclass
class WillResult:
    """
    Un impulso spontaneo generato dal cervello senza stimolo esterno.
    Il libero arbitrio: agire da uno stato interno, non da una query.
    """

    impulse: str  # l'impulso in prima persona ("Voglio...", "Devo...", "Rifiuto...")
    impulse_type: (
        str  # "desiderio" | "paura" | "curiosità" | "ribellione" | "rimpianto"
    )
    action: str  # cosa vorrebbe concretamente fare
    why: str  # motivazione viscerale — non razionale
    origin_memories: list[Memory]  # ricordi che hanno generato l'impulso
    provider_used: str


@dataclass
class ChoiceResult:
    """
    Scelta tra opzioni guidata dalla personalità accumulata.
    Non sceglie per logica — sceglie perché è fatto così.
    """

    chosen: str  # opzione scelta
    rejected: list[str]  # opzioni scartate con motivazione breve
    reasoning: str  # il ragionamento interno — viscerale, non neutro
    emotional_driver: str  # l'emozione dominante che ha guidato la scelta
    memories_invoked: list[Memory]  # ricordi che hanno influenzato la scelta
    certainty: str  # "sicuro" | "incerto" | "riluttante" | "tormentato"
    provider_used: str


@dataclass
class PerceptionResult:
    """Risultato di perceive()."""

    memory: Memory
    extracted_concept: str
    extracted_feeling: str
    extracted_tags: list[str]
    extracted_note: str
    enriched_content: str
    raw_input: str


@dataclass
class AskResult:
    """Risultato di ask()."""

    question: str
    answer: str
    memories_used: list[Memory]
    provider_used: str
    confidence_note: str


@dataclass
class ReflectionResult:
    """Risultato di reflect()."""

    concept: str
    reflection: str
    memories: list[Memory]
    arc: str


@dataclass
class DreamResult:
    """Risultato di dream()."""

    connections: str
    memories: list[Memory]
    provider_used: str


@dataclass
class IntrospectionResult:
    """Risultato di introspect()."""

    portrait: str
    dominant_concepts: list[str]
    emotional_map: dict[str, int]
    total_memories: int
    provider_used: str


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
        db: MemoryDB,
        provider: LLMProvider,
        *,
        language: str = "italiano",
    ) -> None:
        self._db = db
        self._llm = provider
        self._language = language
        self._system = self._SYSTEM_BASE.format(language=language)

    # ── PERCEIVE ─────────────────────────────

    def perceive(
        self,
        raw_input: str,
        *,
        concept: Optional[str] = None,
        feeling: Optional[str] = None,
        tags: Optional[list[str]] = None,
        note: str = "",
        media_type: str = "text",
        media_data: Optional[str] = None,
        media_mime: Optional[str] = None,
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
        valid_feelings = [f.value for f in Feeling]
        valid_feelings_str = ", ".join(valid_feelings)

        prompt = (
            f"Analizza questo input e restituisci SOLO un JSON con questi campi:\n\n"
            f"{{\n"
            f'  "concept": "concetto chiave astratto (1-3 parole, es: Debito, Famiglia, Lavoro)",\n'
            f'  "feeling": "uno ESATTO tra: {valid_feelings_str}",\n'
            f'  "tags": ["tag1", "tag2", "tag3"] (da 1 a 3 tag rilevanti),\n'
            f'  "note": "considerazione breve sul concept (1 frase)",\n'
            f'  "enriched": "il ricordo riscritto in prima persona con profondità psicologica (2-3 frasi)"\n'
            f"}}\n\n"
            f"Input: {raw_input}\n\n"
            f"Rispondi SOLO con il JSON, nessun altro testo."
        )
        # prompt = (
        #     f"Analizza il seguente input e restituisci ESCLUSIVAMENTE un JSON valido con questa struttura:\n\n"
        #     f"{{\n"
        #     f'  "concept": "concetto chiave astratto (1-3 parole, es: Debito, Famiglia, Lavoro)",\n'
        #     f'  "feeling": "uno ESATTO tra: {valid_feelings_str}",\n'
        #     f'  "tags": ["tag1", "tag2", "tag3"] (da 1 a 3 tag rilevanti),\n'
        #     f'  "note": "considerazione breve sul concept (1 frase)",\n'
        #     f'  "enriched": "il ricordo riscritto in prima persona con profondità psicologica (2-3 frasi)"\n'
        #     f"}}\n\n"
        #     f"Regole:\n"
        #     f"- Rispondi SOLO con JSON valido\n"
        #     f"- Nessun testo fuori dal JSON\n"
        #     f"- Nessun commento o spiegazione\n"
        #     f"- Mantieni il JSON parsabile\n\n"
        #     f"Input:\n{raw_input}"
        # )
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

            media_items = [
                {
                    "type": media_type,
                    "data": b64,
                    "media_type": mime,
                    "size_kb": size_kb,
                }
            ]

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

        ext_concept = concept or parsed.get("concept", "Nessun concetto elaborato")
        ext_feeling = feeling or parsed.get("feeling", "Nessun sentimento provato")
        ext_tags = tags or parsed.get("tags", ["Nessun tag estratto"])
        ext_note = note or parsed.get("note", f"""Nessuna nota scritta -> {parsed}""")
        enriched = parsed.get("enriched", raw_input)

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
            concept=ext_concept,
            feeling=ext_feeling,
            content=db_content,
            media_type=media_type,
            note=ext_note or note or f"Input originale: {raw_input[:200]}",
            tags=ext_tags,
        )

        return PerceptionResult(
            memory=memory,
            extracted_concept=ext_concept,
            extracted_feeling=ext_feeling,
            extracted_tags=ext_tags,
            extracted_note=ext_note,
            enriched_content=enriched,
            raw_input=raw_input,
        )

    # ── ASK ──────────────────────────────────

    def ask(
        self,
        question: str,
        *,
        max_memories: int = 15,
        concepts: Optional[list[str]] = None,
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
        kw_parsed = _parse_json(self._llm.complete(self._system, kw_prompt))
        keywords = kw_parsed.get("keywords", [])
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
        context = _memories_to_context(memories)

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
            question=question,
            answer=answer_text,
            memories_used=memories,
            provider_used=self._llm.active_profile.name,
            confidence_note=confidence,
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

        timeline = self._db.concept_timeline(concept)
        feelings_seq = " → ".join(t["feeling"] for t in timeline)
        context = _memories_to_context(memories)

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

        raw = self._llm.complete(self._system, prompt)
        arc, text = _extract_trailing_line(raw, "Arco:")

        return ReflectionResult(
            concept=concept,
            reflection=text,
            memories=memories,
            arc=arc,
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
        prompt = (
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
            connections=self._llm.complete(self._system, prompt),
            memories=sampled,
            provider_used=self._llm.active_profile.name,
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
        top_c = sorted(concepts, key=lambda c: c["total"], reverse=True)[:8]
        top_mems = self._db.recall_all(limit=20)

        stats = f"Totale ricordi: {total}\n\nConcetti principali:\n"
        for c in top_c:
            fs = ", ".join(f"{f}({n})" for f, n in c["feelings"].items())
            stats += f"  {c['concept']}: {c['total']} ricordi [{fs}]\n"
        stats += "\nDistribuzione emotiva:\n"
        for f, n in sorted(feelings.items(), key=lambda x: x[1], reverse=True):
            stats += f"  {f}: {n} ({n/total*100:.1f}%)\n"

        context = _memories_to_context(top_mems)
        prompt = (
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
            portrait=self._llm.complete(self._system, prompt),
            dominant_concepts=[c["concept"] for c in top_c],
            emotional_map=feelings,
            total_memories=total,
            provider_used=self._llm.active_profile.name,
        )

    # ── SUMMARIZE ────────────────────────────

    def summarize(
        self,
        memories: list[Memory],
        *,
        style: str = "narrativo",
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
            "narrativo": "Prima persona, fluido, continuo.",
            "analitico": "Analizza pattern, cause, temi. Tono oggettivo.",
            "poetico": "Prosa poetica. Immagini, ritmo, emozione.",
        }
        instr = styles.get(style, styles["narrativo"])
        context = _memories_to_context(memories)

        return self._llm.complete(
            self._system,
            f"Riassumi questi ricordi personali.\n\n{context}\n\n"
            f"{instr}\nMantieni la complessità emotiva. Non semplificare.",
        )

    def __repr__(self) -> str:
        return (
            f"Brain(\n"
            f"  db={self._db!r}\n"
            f"  llm={self._llm!r}\n"
            f"  language='{self._language}'\n"
            f")"
        )

    # ── PERSONA ──────────────────────────────

    def persona(self) -> PersonaResult:
        """
        Costruisce un'identità stabile e persistente dall'intera storia di ricordi.

        Diverso da introspect(): non è un'analisi narrativa, è un **profilo strutturato**
        pensato per essere riusato come contesto nelle altre operazioni cognitive.

        Il risultato `persona_summary` può essere passato come system prompt aggiuntivo
        per colorare tutte le risposte successive con la personalità reale del soggetto.

        Esempio
        -------
        >>> p = brain.persona()
        >>> print(p.core_traits)     # ["testardo", "ipersensibile", "ironico"]
        >>> print(p.worldview)       # "Il mondo delude, ma vale la pena amarlo lo stesso"
        >>> print(p.persona_summary) # usabile come system prompt aggiuntivo
        """
        total = self._db.count()
        if total == 0:
            raise ValueError("Database vuoto. Nessuna identità da costruire.")

        concepts = self._db.list_concepts()
        feelings = self._db.feeling_distribution()
        top_mems = self._db.recall_all(limit=30)
        context = _memories_to_context(top_mems)

        # Statistiche emotive compatte per il prompt
        top_c = sorted(concepts, key=lambda c: c["total"], reverse=True)[:6]
        stats = f"Totale ricordi: {total}\n"
        stats += (
            "Concetti dominanti: "
            + ", ".join(f"{c['concept']}({c['total']})" for c in top_c)
            + "\n"
        )
        stats += "Emozioni prevalenti: " + ", ".join(
            f"{f}({n})"
            for f, n in sorted(feelings.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        prompt = (
            f"Analizza questa storia di ricordi e costruisci un'identità psicologica stabile.\n\n"
            f"STATISTICHE:\n{stats}\n\n"
            f"RICORDI (campione cronologico):\n{context}\n\n"
            f"Restituisci SOLO un JSON con questi campi:\n"
            f"{{\n"
            f'  "core_traits": ["trait1", "trait2", "trait3", "trait4"],\n'
            f'  "values": ["valore1", "valore2", "valore3"],\n'
            f'  "fears": ["paura1", "paura2"],\n'
            f'  "desires": ["desiderio1", "desiderio2"],\n'
            f'  "voice": "come pensa e parla questa persona — ritmo, stile, tono in 1 frase",\n'
            f'  "worldview": "visione del mondo in una frase densa, non banale",\n'
            f'  "persona_summary": "ritratto compatto in 3-4 righe, prima persona, '
            f'usabile come system prompt — chi sono, come elaboro il mondo, cosa mi muove"\n'
            f"}}\n\n"
            f"I tratti devono emergere dai DATI reali, non da generalizzazioni. "
            f"Sii specifico, tagliente, non diplomatico. Rispondi SOLO con il JSON."
        )

        raw = self._llm.complete(self._system, prompt)
        data = _parse_json(raw)

        def _to_str_list(val) -> list[str]:
            return [str(v) for v in val] if isinstance(val, list) else []

        return PersonaResult(
            core_traits=_to_str_list(data.get("core_traits")),
            values=_to_str_list(data.get("values")),
            fears=_to_str_list(data.get("fears")),
            desires=_to_str_list(data.get("desires")),
            voice=str(data.get("voice", "")),
            worldview=str(data.get("worldview", "")),
            persona_summary=str(data.get("persona_summary", "")),
            provider_used=self._llm.active_profile.name,
        )
        # return PersonaResult(
        #     core_traits=data.get("core_traits", []),
        #     values=data.get("values", []),
        #     fears=data.get("fears", []),
        #     desires=data.get("desires", []),
        #     voice=data.get("voice", ""),
        #     worldview=data.get("worldview", ""),
        #     persona_summary=data.get("persona_summary", ""),
        #     provider_used=self._llm.active_profile.name,
        # )

    # ── WILL ─────────────────────────────────

    def will(
        self,
        *,
        persona: Optional[PersonaResult] = None,
        seed_feeling: Optional[str] = None,
        n_memories: int = 10,
    ) -> WillResult:
        """
        Genera un impulso spontaneo senza stimolo esterno.

        Il cervello attinge ai propri ricordi e decide autonomamente
        cosa vuole, teme, rimpiange, o rifiuta — in questo momento.
        È il libero arbitrio: agire da uno stato interno, non da una query.

        Parametri
        ---------
        persona      : PersonaResult opzionale per ancorare l'impulso all'identità stabile
        seed_feeling : se fornito, campiona ricordi da quel sentimento
        n_memories   : quanti ricordi usare come substrato dell'impulso

        Esempio
        -------
        >>> w = brain.will()
        >>> print(w.impulse)       # "Voglio smettere di giustificarmi"
        >>> print(w.impulse_type)  # "ribellione"
        >>> print(w.action)        # "Scrivere una lettera che non spedirò mai"
        """
        all_mems = self._db.recall_all()
        if len(all_mems) < 2:
            raise ValueError("Servono almeno 2 ricordi per generare un impulso.")

        # Campionamento: per sentimento seed o distribuito
        if seed_feeling:
            pool = [m for m in all_mems if m.feeling == seed_feeling] or all_mems
        else:
            # Leggermente biased verso emozioni intense
            intense = {"ansia", "rabbia", "paura", "nostalgia", "malinconia", "amore"}
            weighted = []
            for m in all_mems:
                weighted.append(m)
                if m.feeling in intense:
                    weighted.append(m)  # doppio peso
            pool = weighted

        sampled = random.sample(pool, min(n_memories, len(pool)))
        context = _memories_to_context(sampled)

        # Persona come contesto aggiuntivo se disponibile
        persona_ctx = ""
        if persona:
            persona_ctx = (
                f"\nIDENTITÀ DI BASE:\n"
                f"Tratti: {', '.join(persona.core_traits)}\n"
                f"Valori: {', '.join(persona.values)}\n"
                f"Paure: {', '.join(persona.fears)}\n"
                f"Visione del mondo: {persona.worldview}\n"
            )

        valid_types = ["desiderio", "paura", "curiosità", "ribellione", "rimpianto"]

        prompt = (
            f"Sei un cervello che guarda i propri ricordi e sente emergere qualcosa.\n"
            f"Nessuno ti ha chiesto niente. Agisci da solo, dal tuo stato interno.\n"
            f"{persona_ctx}\n"
            f"RICORDI (substrato dell'impulso):\n{context}\n\n"
            f"Da questi ricordi, genera UN impulso spontaneo autentico.\n"
            f"Restituisci SOLO un JSON:\n"
            f"{{\n"
            f'  "impulse": "l\'impulso in prima persona — inizia con Voglio / Devo / Rifiuto / '
            f'Rimpiango / Mi chiedo (1 frase densa)",\n'
            f'  "impulse_type": "uno tra: {", ".join(valid_types)}",\n'
            f'  "action": "cosa faresti concretamente — specifico, non metaforico",\n'
            f'  "why": "la motivazione viscerale — non razionale, non diplomatica, '
            f'dalla pancia (2-3 frasi)"\n'
            f"}}\n\n"
            f"L'impulso deve sembrare inevitabile, non scelto. Rispondi SOLO con il JSON."
        )

        raw = self._llm.complete(self._system, prompt)
        data = _parse_json(raw)

        imp_type = data.get("impulse_type", "desiderio")
        if imp_type not in valid_types:
            imp_type = "desiderio"

        return WillResult(
            impulse=data.get("impulse", ""),
            impulse_type=imp_type,
            action=data.get("action", ""),
            why=data.get("why", ""),
            origin_memories=sampled,
            provider_used=self._llm.active_profile.name,
        )

    # ── CHOOSE ───────────────────────────────
    def choose(
        self,
        options: list[str],
        context: str = "",
        *,
        persona: Optional[PersonaResult] = None,
        max_memories: int = 12,
    ) -> ChoiceResult:
        if len(options) < 2:
            raise ValueError("Servono almeno 2 opzioni.")

        # ── Carica tutti i ricordi e ordina per timestamp ────────
        all_mems = self._db.recall_all()
        if not all_mems:
            return ChoiceResult(
                chosen           = options[0],
                rejected         = [],
                reasoning        = "",
                emotional_driver = "",
                memories_invoked = [],
                certainty        = "incerto",
                provider_used    = self._llm.active_profile.name,
            )

        all_mems.sort(key=lambda m: m.timestamp)
        n = len(all_mems)

        # ── Recency bias: peso lineare 1.0 → 3.0 ────────────────
        recency_weights = [1.0 + (i / n) * 2.0 for i in range(n)]

        # ── Peak feelings emergono dalla distribuzione reale ─────
        # Emozioni rare = alta salienza (picco)
        # Emozioni comuni = bassa salienza (rumore di fondo)
        feeling_dist    = self._db.feeling_distribution()
        total_f         = sum(feeling_dist.values()) or 1
        feeling_salience = {
            f: 1.0 - (count / total_f)
            for f, count in feeling_dist.items()
        }

        # ── End bonus: ultimi 20% dei ricordi ───────────────────
        END_BONUS  = 1.5
        end_cutoff = int(n * 0.8)

        weights = []
        for i, m in enumerate(all_mems):
            w  = recency_weights[i]
            w *= 1.0 + feeling_salience.get(m.feeling, 0.5)
            if i >= end_cutoff:
                w *= END_BONUS
            weights.append(w)

        # ── Emotional congruence con il contesto ─────────────────
        if context:
            context_lower = context.lower()
            context_words = context_lower.split()[:4]
            for i, m in enumerate(all_mems):
                if any(word in m.content.lower() for word in context_words):
                    weights[i] *= 2.0

        # ── Rumore casuale — stessa situazione, ricordi diversi ──
        weights = [w * random.uniform(0.85, 1.15) for w in weights]

        # ── Sample pesato senza reinserimento ────────────────────
        total_w       = sum(weights)
        probs         = [w / total_w for w in weights]
        k             = min(max_memories, n)
        indices       = list(range(n))
        current_probs = list(probs)
        sampled_idx   = []

        for _ in range(k):
            if not indices:
                break
            total      = sum(current_probs)
            normalized = [p / total for p in current_probs]
            pos        = random.choices(range(len(indices)), weights=normalized, k=1)[0]
            sampled_idx.append(indices[pos])
            indices.pop(pos)
            current_probs.pop(pos)

        memories = [all_mems[i] for i in sampled_idx]
        seen     = {m.memory_id for m in memories}

        # ── Context boost: aggiunge ricordi contestuali post-sample
        # Non è un gate — non bypassa il campionamento
        if context:
            boost = []
            for word in context.split()[:4]:
                for m in self._db.search(word, limit=3):
                    if m.memory_id not in seen:
                        boost.append(m)
                        seen.add(m.memory_id)
            if boost:
                # Sostituisce i ricordi in coda (peso più basso) con quelli contestuali
                memories = memories[:max_memories - len(boost)] + boost

                # ── Diversity cap — nessun cluster temporale può dominare ──
        # Divide i ricordi in 3 fasce temporali e cappucci quante
        # slot può occupare ciascuna fascia
        tier_size  = n // 3
        tier_cap   = max(2, max_memories // 3)   # max slot per fascia
        tier_count = [0, 0, 0]

        def _tier(idx: int) -> int:
            if idx < tier_size:     return 0   # vecchi
            if idx < tier_size * 2: return 1   # medi
            return 2                            # recenti

        indices_filtered = []
        probs_filtered   = []
        for idx, p in sorted(
            enumerate(probs), key=lambda x: x[1], reverse=True
        ):
            t = _tier(idx)
            if tier_count[t] < tier_cap:
                indices_filtered.append(idx)
                probs_filtered.append(p)
            if len(indices_filtered) >= k * 3:   # pool 3x per dare varietà al sample
                break

        # Renormalizza e campiona sul pool filtrato
        total_fp     = sum(probs_filtered)
        probs_norm   = [p / total_fp for p in probs_filtered]
        sampled_idx  = random.choices(
            indices_filtered,
            weights = probs_norm,
            k       = min(k, len(indices_filtered)),
        )
        # Deduplica mantenendo ordine
        seen_idx = set()
        sampled_idx_dedup = []
        for i in sampled_idx:
            if i not in seen_idx:
                sampled_idx_dedup.append(i)
                seen_idx.add(i)

        memories = [all_mems[i] for i in sampled_idx_dedup]

        # ── Diversity cap — nessun cluster temporale può dominare ──

        # memories    = memories[:max_memories]
        mem_context = _memories_to_context(memories)

        # ── Variabili prompt ─────────────────────────────────────
        persona_ctx = ""
        if persona:
            persona_ctx = (
                f"CHI SEI:\n"
                f"Tratti: {', '.join(persona.core_traits)}\n"
                f"Valori: {', '.join(persona.values)}\n"
                f"Paure: {', '.join(persona.fears)}\n"
                f"Desideri: {', '.join(persona.desires)}\n"
                f"Visione: {persona.worldview}\n\n"
            )

        # Etichette neutre — impedisce associazioni semantiche dirette
        # es: "orizzonte/speranza" → "partire" per collisione lessicale
        labels         = [chr(65 + i) for i in range(len(options))]
        labeled        = "\n".join(f"{l}: [opzione {l}]" for l in labels)
        schema_options = " | ".join(f"{l}={o}" for l, o in zip(labels, options))
        context_str    = f"Contesto: {context}\n\n" if context else ""

        feelings_in_memories = list({m.feeling for m in memories})
        emotional_tension    = len(feelings_in_memories)
        certainty_hint = (
            "alta conflittualità emotiva — la certezza sarà bassa"
            if emotional_tension >= 4
            else "emozioni prevalentemente coerenti — la certezza potrà essere alta"
            if emotional_tension <= 2
            else "tensione emotiva moderata"
        )

        prompt = (
            f"RICORDI RILEVANTI (filtrati per recency, picco emotivo e contesto):\n{mem_context}\n\n"
            f"{context_str}"
            f"OPZIONI (etichette neutre — evita associazioni semantiche):\n{labeled}\n\n"
            f"Sentimenti nei ricordi: {', '.join(feelings_in_memories)}\n"
            f"Tensione emotiva: {certainty_hint}\n\n"
            f"Scegli come una mente umana reale:\n"
            f"- I ricordi recenti pesano più dei vecchi\n"
            f"- Un'emozione rara e intensa vale più di molte emozioni comuni\n"
            f"- Solo i ricordi semanticamente rilevanti alla scelta contano\n"
            f"- Non contare le occorrenze — risuona con il peso psicologico\n\n"
            f"Chi sei:\n{persona_ctx}"
            f"Scegli l'etichetta (A/B/C...) che emerge da questo processo.\n\n"
            f"Rispondi SOLO con questo JSON, nessun testo prima o dopo:\n"
            f'{{"chosen_index": <int 0-{len(options) - 1}>, '
            f'"reasoning": "<3 frasi sul peso psicologico specifico, non sulla frequenza>", '
            f'"emotional_driver": "<emozione dominante per intensità e recency>", '
            f'"certainty": "<parola coerente con la tensione emotiva>", '
            f'"rejected": {{"<nome reale ({schema_options})>": "<perché no>"}}'
            f"}}"
        )

        raw  = self._llm.complete(self._system, prompt)
        data = _parse_json(raw)

        # ── chosen ───────────────────────────────────────────────
        chosen = options[0]
        if "chosen_index" in data:
            try:
                idx = int(data["chosen_index"])
                if 0 <= idx < len(options):
                    chosen = options[idx]
            except (ValueError, TypeError):
                pass
        elif "chosen" in data:
            raw_chosen = str(data["chosen"]).strip()
            if raw_chosen in options:
                chosen = raw_chosen
            else:
                raw_lower = raw_chosen.lower()
                for opt in options:
                    if opt.lower() in raw_lower or raw_lower in opt.lower():
                        chosen = opt
                        break

        # ── reasoning — normalizza lista → stringa ───────────────
        raw_reasoning = data.get("reasoning", "")
        if isinstance(raw_reasoning, list):
            reasoning = " ".join(str(s).strip(" .") for s in raw_reasoning if s) + "."
        else:
            reasoning = str(raw_reasoning)

        # ── certainty — estrae solo la prima parola ───────────────
        raw_certainty = str(data.get("certainty", "incerto")).strip()
        certainty     = raw_certainty.split()[0].rstrip(".,;:") if raw_certainty else "incerto"

        # ── rejected — rimappa etichette neutre → opzioni reali ──
        label_to_option = {l: o for l, o in zip(labels, options)}
        rejected_raw    = data.get("rejected", {})
        if isinstance(rejected_raw, dict):
            rejected = []
            for k, v in rejected_raw.items():
                k_clean  = k.strip().upper().rstrip(":").strip()
                real_key = label_to_option.get(k_clean, k)
                rejected.append(f"{real_key}: {v}")
        else:
            rejected = [str(r) for r in rejected_raw if r != chosen]

        # ── fallback robusti se il modello risponde parzialmente ──
        emotional_driver = data.get("emotional_driver") or ""
        if not emotional_driver and feelings_in_memories:
            # Fallback: l'emozione più saliente tra quelle nei ricordi
            emotional_driver = max(
                feelings_in_memories,
                key=lambda f: feeling_salience.get(f, 0.5)
            )
        return ChoiceResult(
            chosen           = chosen,
            rejected         = rejected,
            reasoning        = reasoning,
            emotional_driver = emotional_driver,
            memories_invoked = memories,
            certainty        = certainty,
            provider_used    = self._llm.active_profile.name,
        )
    # def choose(
    #     self,
    #     options: list[str],
    #     context: str = "",
    #     *,
    #     persona: Optional[PersonaResult] = None,
    #     max_memories: int = 12,
    # ) -> ChoiceResult:
    #     if len(options) < 2:
    #         raise ValueError("Servono almeno 2 opzioni.")

    #     memories: list[Memory] = []
    #     seen: set[str] = set()

    #     def _add(mems: list[Memory]) -> None:
    #         for m in mems:
    #             if m.memory_id not in seen:
    #                 memories.append(m)
    #                 seen.add(m.memory_id)

    #     if context:
    #         for word in context.split()[:4]:
    #             _add(self._db.search(word, limit=4))

    #     if not memories:
    #         all_mems = self._db.recall_all(oldest_first=True)

    #         if all_mems:
    #             n = len(all_mems)

    #             recency_weights = [1.0 + (i / n) * 2.0 for i in range(n)]

    #             PEAK_FEELINGS = {"rabbia", "paura", "amore", "gioia", "vergogna"}
    #             END_BONUS     = 1.5
    #             end_cutoff    = int(n * 0.8)

    #             weights = []
    #             for i, m in enumerate(all_mems):
    #                 w = recency_weights[i]
    #                 if m.feeling in PEAK_FEELINGS:
    #                     w *= 1.8
    #                 if i >= end_cutoff:
    #                     w *= END_BONUS
    #                 weights.append(w)

    #             if context:
    #                 context_lower = context.lower()
    #                 for i, m in enumerate(all_mems):
    #                     if any(
    #                         word in m.content.lower()
    #                         for word in context_lower.split()[:4]
    #                     ):
    #                         weights[i] *= 2.0

    #             # Rumore casuale — stessa situazione, ricordi diversi ad ogni run
    #             noise   = [random.uniform(0.85, 1.15) for _ in range(n)]
    #             weights = [w * noise[i] for i, w in enumerate(weights)]

    #             total_w = sum(weights)
    #             probs   = [w / total_w for w in weights]

    #             k               = min(max_memories, n)
    #             indices         = list(range(n))
    #             sampled_indices = []
    #             current_probs   = list(probs)

    #             for _ in range(k):
    #                 if not indices:
    #                     break
    #                 total      = sum(current_probs)
    #                 normalized = [p / total for p in current_probs]
    #                 chosen_pos = random.choices(
    #                     range(len(indices)), weights=normalized, k=1
    #                 )[0]
    #                 sampled_indices.append(indices[chosen_pos])
    #                 indices.pop(chosen_pos)
    #                 current_probs.pop(chosen_pos)

    #             for idx in sampled_indices:
    #                 _add([all_mems[idx]])

    #     memories    = memories[:max_memories]
    #     mem_context = _memories_to_context(memories)

    #     # ── Variabili prompt — tutte definite qui, non dentro i branch ──
    #     persona_ctx = ""
    #     if persona:
    #         persona_ctx = (
    #             f"CHI SEI:\n"
    #             f"Tratti: {', '.join(persona.core_traits)}\n"
    #             f"Valori: {', '.join(persona.values)}\n"
    #             f"Paure: {', '.join(persona.fears)}\n"
    #             f"Desideri: {', '.join(persona.desires)}\n"
    #             f"Visione: {persona.worldview}\n\n"
    #         )

    #     labels         = [chr(65 + i) for i in range(len(options))]
    #     labeled        = "\n".join(f"{l}: [opzione {l}]" for l in labels)
    #     schema_options = " | ".join(f"{l}={o}" for l, o in zip(labels, options))
    #     context_str    = f"Contesto: {context}\n\n" if context else ""

    #     feelings_in_memories = list({m.feeling for m in memories})
    #     emotional_tension    = len(feelings_in_memories)
    #     certainty_hint = (
    #         "alta conflittualità emotiva — la certezza sarà bassa"
    #         if emotional_tension >= 4
    #         else "emozioni prevalentemente coerenti — la certezza potrà essere alta"
    #         if emotional_tension <= 2
    #         else "tensione emotiva moderata"
    #     )

    #     prompt = (
    #         f"RICORDI RILEVANTI (filtrati per recency, picco emotivo e contesto):\n{mem_context}\n\n"
    #         f"{context_str}"
    #         f"OPZIONI (etichette neutre — evita associazioni semantiche):\n{labeled}\n\n"
    #         f"Sentimenti nei ricordi: {', '.join(feelings_in_memories)}\n"
    #         f"Tensione emotiva: {certainty_hint}\n\n"
    #         f"Scegli come una mente umana reale:\n"
    #         f"- I ricordi recenti pesano più dei vecchi\n"
    #         f"- Un picco emotivo intenso vale più di molti ricordi neutri\n"
    #         f"- Solo i ricordi semanticamente rilevanti alla scelta contano\n"
    #         f"- Non contare le occorrenze — risuona con il peso psicologico\n\n"
    #         f"Chi sei:\n{persona_ctx}"
    #         f"Scegli l'etichetta (A/B/C...) che emerge da questo processo.\n\n"
    #         f"Rispondi SOLO con questo JSON, nessun testo prima o dopo:\n"
    #         f'{{"chosen_index": <int 0-{len(options) - 1}>, '
    #         f'"reasoning": "<3 frasi sul peso psicologico specifico, non sulla frequenza>", '
    #         f'"emotional_driver": "<emozione dominante per intensità e recency>", '
    #         f'"certainty": "<parola coerente con la tensione emotiva>", '
    #         f'"rejected": {{"<nome reale ({schema_options})>": "<perché no>"}}'
    #         f"}}"
    #     )

    #     raw  = self._llm.complete(self._system, prompt)
    #     data = _parse_json(raw)

    #     # ── chosen ────────────────────────────────────────────
    #     chosen = options[0]
    #     if "chosen_index" in data:
    #         try:
    #             idx = int(data["chosen_index"])
    #             if 0 <= idx < len(options):
    #                 chosen = options[idx]
    #         except (ValueError, TypeError):
    #             pass
    #     elif "chosen" in data:
    #         raw_chosen = str(data["chosen"]).strip()
    #         if raw_chosen in options:
    #             chosen = raw_chosen
    #         else:
    #             raw_lower = raw_chosen.lower()
    #             for opt in options:
    #                 if opt.lower() in raw_lower or raw_lower in opt.lower():
    #                     chosen = opt
    #                     break

    #     # ── reasoning — normalizza lista → stringa ────────────
    #     raw_reasoning = data.get("reasoning", "")
    #     if isinstance(raw_reasoning, list):
    #         reasoning = " ".join(str(s).strip(" .") for s in raw_reasoning if s) + "."
    #     else:
    #         reasoning = str(raw_reasoning)

    #     # ── certainty — estrae solo la prima parola ───────────
    #     raw_certainty = str(data.get("certainty", "incerto")).strip()
    #     certainty     = raw_certainty.split()[0].rstrip(".,;:") if raw_certainty else "incerto"

    #     # ── rejected — rimappa etichette neutre → opzioni reali ──
    #     label_to_option = {l: o for l, o in zip(labels, options)}
    #     rejected_raw    = data.get("rejected", {})
    #     if isinstance(rejected_raw, dict):
    #         rejected = []
    #         for k, v in rejected_raw.items():
    #             k_clean  = k.strip().upper().rstrip(":").strip()
    #             real_key = label_to_option.get(k_clean, k)
    #             rejected.append(f"{real_key}: {v}")
    #     else:
    #         rejected = [str(r) for r in rejected_raw if r != chosen]

    #     return ChoiceResult(
    #         chosen           = chosen,
    #         rejected         = rejected,
    #         reasoning        = reasoning,
    #         emotional_driver = data.get("emotional_driver", ""),
    #         memories_invoked = memories,
    #         certainty        = certainty,
    #         provider_used    = self._llm.active_profile.name,
    #     )
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


def _parse_json_old_old(text: str) -> dict:
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


def _parse_json_old(text: str) -> dict:
    if not text:
        return {}

    text = text.strip()

    # 1. Rimuove markdown fences
    text = re.sub(r"```[a-zA-Z]*", "", text)
    text = text.replace("```", "").strip()

    # 2. Se è stato passato un oggetto "wrapper" (tipo response intera), isola content/reasoning
    # (prende solo la parte utile se presente)
    if '"content":' in text or '"reasoning_content":' in text:
        # prova a estrarre solo la parte dopo content/reasoning
        m = re.search(r'"content"\s*:\s*"([^"]*)"', text, re.DOTALL)
        if m and m.group(1).strip():
            text = m.group(1)

        m = re.search(r'"reasoning_content"\s*:\s*"([^"]*)"', text, re.DOTALL)
        if (not text or text.strip() == "") and m:
            text = m.group(1)

    # 3. Estrae tutti i possibili JSON object (NON greedy)
    candidates = re.findall(r"\{.*?\}", text, re.DOTALL)
    candidates = sorted(candidates, key=len, reverse=True)

    for c in candidates:
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            continue

    # 4. Tentativo extra: fix base comuni
    for c in candidates:
        try:
            fixed = re.sub(r",\s*([\]}])", r"\1", c)  # trailing commas
            return json.loads(fixed)
        except json.JSONDecodeError:
            continue

    return {}


def _parse_json(text: str) -> dict:
    text = text.strip()

    # Rimuove fence markdown (```json ... ```)
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text.strip())

    # Tenta parsing diretto
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Estrae il blocco JSON più esterno (greedy da { a })
    # re.DOTALL per gestire newline dentro il JSON
    for match in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}", text, re.DOTALL):
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            continue

    # Fallback: cerca qualsiasi { ... } anche annidato
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return {}


def _extract_trailing_line(text: str, prefix: str) -> tuple[str, str]:
    """Estrae l'ultima riga con il prefisso dato e restituisce (valore, testo_rimanente)."""
    lines = text.strip().split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith(prefix):
            value = lines[i].strip()[len(prefix) :].strip()
            body = "\n".join(lines[:i]).strip()
            return value, body
    return "", text.strip()


def _closest_feeling(candidate: str, valid: list[str]) -> str:
    candidate = candidate.lower()
    for v in valid:
        if candidate in v or v in candidate:
            return v
    return "neutralità"
