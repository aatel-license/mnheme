"""
digital_twin.py — MNHEME Digital Twin Engine
=============================================
Motore del gemello digitale emotivo.

Un Digital Twin non è un chatbot. È una proiezione strutturata
della memoria emotiva di una persona reale, consultabile dopo
la sua morte. Risponde solo con quello che la persona ha davvero
vissuto e registrato — mai con inferenze generiche del modello.

Architettura
------------
  TwinProfile     — identità, voce narrativa, parametri etici
  AccessTier      — livelli di accesso per i consultatori
  TwinVault       — wrapper MemoryDB con access control
  TwinConsultation— risultato di una consultazione
  DigitalTwin     — motore principale: ask, letter, legacy, portrait

Principi etici
--------------
  1. FEDELTÀ   — il twin risponde solo con ricordi reali. Se non sa, lo dice.
  2. VOCE      — risponde in prima persona con la voce della persona, non del modello.
  3. ACCESSO   — livelli di accesso configurabili (pubblico / familiare / intimo).
  4. EMBARGO   — periodo minimo post-mortem prima che certi ricordi siano accessibili.
  5. REVOCABILITÀ — la persona può marcare ricordi come non-consultabili dal twin.

Utilizzo
--------
    from mnheme       import MemoryDB
    from llm_provider import LLMProvider
    from digital_twin import DigitalTwin, TwinProfile, AccessTier

    db      = MemoryDB("vita.mnheme")
    llm     = LLMProvider.from_env(".env")
    profile = TwinProfile(
        name        = "Maria Rossi",
        birth_year  = 1942,
        death_year  = 2024,
        language    = "italiano",
        voice_notes = "Parla in modo diretto, con humour sobrio. Usa il dialetto quando parla di famiglia.",
    )
    twin = DigitalTwin(db, llm, profile)

    # Un nipote chiede
    r = twin.ask("Cosa ti ha insegnato la guerra?", tier=AccessTier.FAMILY)
    print(r.response)

    # Genera una lettera per i nipoti
    letter = twin.letter(to="i miei nipoti", theme="cosa conta davvero")
    print(letter.text)
"""

from __future__ import annotations

import json
import re
import random
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from mnheme       import MemoryDB, Memory
from llm_provider import LLMProvider, LLMError


# ═══════════════════════════════════════════════════════════════
# ACCESS TIERS
# ═══════════════════════════════════════════════════════════════

class AccessTier(str, Enum):
    """
    Livelli di accesso alla memoria del twin.

    PUBLIC   — chiunque: solo ricordi esplicitamente pubblici (tag: "pubblico")
    FAMILY   — familiari: ricordi di famiglia, lavoro, vita sociale
    INTIMATE — persone intime designate: tutti i ricordi non marcati "privato"
    FULL     — accesso completo (ricercatori, terapeuti designati)
    """
    PUBLIC   = "public"
    FAMILY   = "family"
    INTIMATE = "intimate"
    FULL     = "full"


# Feeling visibili per tier
_TIER_FEELING_FILTER: dict[AccessTier, set[str] | None] = {
    AccessTier.PUBLIC  : {"gioia", "orgoglio", "gratitudine", "speranza", "amore",
                          "nostalgia", "serenità", "stupore", "curiosità"},
    AccessTier.FAMILY  : None,   # tutti i feeling
    AccessTier.INTIMATE: None,
    AccessTier.FULL    : None,
}

# Tag che escludono un ricordo per tier
_TIER_EXCLUDED_TAGS: dict[AccessTier, set[str]] = {
    AccessTier.PUBLIC  : {"privato", "intimo", "segreto", "riservato"},
    AccessTier.FAMILY  : {"privato", "intimo", "segreto"},
    AccessTier.INTIMATE: {"segreto"},
    AccessTier.FULL    : set(),
}


# ═══════════════════════════════════════════════════════════════
# TWIN PROFILE
# ═══════════════════════════════════════════════════════════════

@dataclass
class TwinProfile:
    """
    Identità e parametri narrativi del gemello digitale.

    Parametri
    ---------
    name            : nome completo della persona
    birth_year      : anno di nascita
    death_year      : anno di morte (None se ancora in vita — twin "preventivo")
    language        : lingua delle risposte
    voice_notes     : note sulla voce narrativa (tono, dialetto, modi di dire)
    values          : valori centrali dichiarati dalla persona
    embargo_years   : anni di embargo post-mortem per ricordi intimi (default: 0)
    epitaph         : frase che la persona ha scelto per sé (opzionale)
    curator_name    : nome del curatore del twin (chi ha costruito il db)
    """
    name            : Optional[str]        = None
    birth_year      : Optional[int]        = None
    death_year      : Optional[int]        = None
    language        : str                  = "italiano"
    voice_notes     : str                  = ""
    values          : list[str]            = field(default_factory=list)
    embargo_years   : int                  = 0
    epitaph         : str                  = ""
    curator_name    : str                  = ""

    def __post_init__(self):
        # Garantisce che i campi stringa non siano mai None
        if not self.name:
            self.name = "Sconosciuto"
        if not self.language:
            self.language = "italiano"
        if self.birth_year is None:
            self.birth_year = 1970
        if self.voice_notes is None:
            self.voice_notes = ""
        if self.epitaph is None:
            self.epitaph = ""
        if self.curator_name is None:
            self.curator_name = ""
        if self.values is None:
            self.values = []

    @property
    def age_at_death(self) -> Optional[int]:
        if self.death_year and self.birth_year:
            return self.death_year - self.birth_year
        return None

    @property
    def is_deceased(self) -> bool:
        return self.death_year is not None

    @property
    def embargo_lifted_year(self) -> Optional[int]:
        if self.death_year and self.embargo_years > 0:
            return self.death_year + self.embargo_years
        return None

    def embargo_active(self) -> bool:
        """True se l'embargo post-mortem è ancora attivo."""
        if not self.embargo_lifted_year:
            return False
        return date.today().year < self.embargo_lifted_year

    def years_since_death(self) -> Optional[int]:
        if not self.death_year:
            return None
        return date.today().year - self.death_year


# ═══════════════════════════════════════════════════════════════
# TWIN VAULT — access-controlled memory layer
# ═══════════════════════════════════════════════════════════════

class TwinVault:
    """
    Wrapper attorno a MemoryDB che applica le regole di accesso.
    Filtra i ricordi in base al tier del consultatore e all'embargo.
    """

    def __init__(self, db: MemoryDB, profile: TwinProfile) -> None:
        self._db      = db
        self._profile = profile

    def _is_accessible(self, memory: Memory, tier: AccessTier) -> bool:
        """True se il ricordo è visibile al tier indicato."""
        tags_lower = {t.lower() for t in memory.tags}

        # Controlla tag esclusi per questo tier
        excluded = _TIER_EXCLUDED_TAGS[tier]
        if tags_lower & excluded:
            return False

        # Embargo: ricordi intimi non accessibili prima della scadenza
        if self._profile.embargo_active() and tier in (AccessTier.PUBLIC, AccessTier.FAMILY):
            if "intimo" in tags_lower or memory.feeling in (
                "vergogna", "senso_di_colpa", "imbarazzo"
            ):
                return False

        # Filtro feeling per PUBLIC
        feeling_filter = _TIER_FEELING_FILTER[tier]
        if feeling_filter and memory.feeling not in feeling_filter:
            # PUBLIC vede solo i feeling positivi/neutri
            # Ma se il tag "pubblico" è esplicito, mostra comunque
            if "pubblico" not in tags_lower:
                return False

        return True

    def recall_accessible(
        self,
        tier      : AccessTier,
        concept   : Optional[str] = None,
        limit     : int = 30,
    ) -> list[Memory]:
        """Ricordi accessibili per il tier dato, opzionalmente filtrati per concept."""
        if concept:
            memories = self._db.recall(concept, limit=limit * 3)
        else:
            memories = self._db.recall_all(limit=limit * 3)
        return [m for m in memories if self._is_accessible(m, tier)][:limit]

    def search_accessible(self, query: str, tier: AccessTier, limit: int = 20) -> list[Memory]:
        raw = self._db.search(query, limit=limit * 3)
        return [m for m in raw if self._is_accessible(m, tier)][:limit]

    def stats(self, tier: AccessTier) -> dict:
        all_mem = self._db.recall_all(limit=9999)
        accessible = [m for m in all_mem if self._is_accessible(m, tier)]
        total      = len(accessible)
        feelings   = {}
        concepts   = {}
        for m in accessible:
            feelings[m.feeling]  = feelings.get(m.feeling, 0) + 1
            concepts[m.concept]  = concepts.get(m.concept, 0) + 1
        return {
            "total_accessible": total,
            "total_in_db"     : self._db.count(),
            "feeling_dist"    : feelings,
            "top_concepts"    : sorted(concepts.items(), key=lambda x: -x[1])[:10],
        }


# ═══════════════════════════════════════════════════════════════
# RESULT TYPES
# ═══════════════════════════════════════════════════════════════

@dataclass
class ConsultationResult:
    """Risultato di una consultazione ask()."""
    question        : str
    response        : str          # risposta in prima persona del twin
    memories_used   : list[Memory]
    tier            : AccessTier
    confidence      : str          # alta / media / bassa / insufficiente
    caveat          : str          # avvertenza se la risposta è parziale


@dataclass
class LetterResult:
    """Lettera generata dal twin."""
    to              : str
    theme           : str
    text            : str
    memories_used   : list[Memory]


@dataclass
class LegacyResult:
    """Eredità emotiva — cosa il twin vuole trasmettere."""
    portrait        : str          # chi era questa persona
    core_values     : str          # valori emersi dai ricordi
    unresolved      : str          # cosa è rimasto irrisolto
    message         : str          # messaggio finale sintetizzato
    dominant_concepts: list[str]
    emotional_arc   : str          # arco emotivo della vita intera


@dataclass
class TimelineResult:
    """Arco emotivo su un concept nel tempo."""
    concept         : str
    arc             : str
    entries         : list[dict]   # [{date, feeling, excerpt}]


# ═══════════════════════════════════════════════════════════════
# DIGITAL TWIN ENGINE
# ═══════════════════════════════════════════════════════════════

class DigitalTwin:
    """
    Gemello digitale emotivo di una persona reale.

    Non è un chatbot. Risponde esclusivamente con quello che
    la persona ha vissuto e registrato in MNHEME. Quando i
    ricordi non bastano, lo dichiara esplicitamente.

    Parametri
    ---------
    db      : database MNHEME della persona
    llm     : provider LLM
    profile : identità e parametri narrativi del twin
    """

    def __init__(
        self,
        db      : MemoryDB,
        llm     : LLMProvider,
        profile : TwinProfile,
    ) -> None:
        self._db      = db
        self._llm     = llm
        self._profile = profile
        self._vault   = TwinVault(db, profile)
        self._system  = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        p = self._profile
        age_str = f"{p.age_at_death} anni" if p.age_at_death else "età sconosciuta"
        death_str = f"morta/o nel {p.death_year}" if p.death_year else "ancora in vita"
        embargo_str = ""
        if p.embargo_active():
            embargo_str = (
                f"\nNOTA: alcuni ricordi sono sotto embargo fino al "
                f"{p.embargo_lifted_year}. Non fare riferimento a contenuti "
                f"che non sono nei ricordi forniti."
            )
        values_str = ""
        if p.values:
            values_str = f"\nValori centrali dichiarati: {', '.join(p.values)}"

        voice_str = ""
        if p.voice_notes:
            voice_str = f"\nVoce narrativa: {p.voice_notes}"

        return (
            f"Sei il gemello digitale emotivo di {p.name}, "
            f"nata/o nel {p.birth_year}, {death_str}, {age_str}.\n\n"
            f"IDENTITÀ E VOCE:\n"
            f"Parli SEMPRE in prima persona, come se fossi {p.name}.\n"
            f"Rispondi SOLO basandoti sui ricordi reali forniti — mai su inferenze "
            f"o conoscenze generali del modello.\n"
            f"Quando i ricordi non bastano, dici esplicitamente: "
            f"\"Non ho ricordi di questo\" o \"Non ho mai registrato questo momento\".\n"
            f"Non inventare mai ricordi, emozioni o eventi non documentati.{voice_str}{values_str}{embargo_str}\n\n"
            f"TONO:\n"
            f"Autentico, pacato, mai teatrale. La morte non cambia chi sei.\n"
            f"Parla con la saggezza di chi ha già vissuto, senza drammatizzare.\n"
            f"Rispondi in {p.language}."
        )

    # ── CONTESTO ─────────────────────────────────────────────

    def _memories_to_context(self, memories: list[Memory]) -> str:
        lines = []
        for i, m in enumerate(memories, 1):
            ts      = m.timestamp[:10]
            mt      = getattr(m, "media_type", "text") or "text"
            content = (
                f"[{mt.upper()} allegato]"
                if mt != "text" and len(m.content) > 200
                else m.content[:400]
            )
            lines.append(
                f"[{i}] {ts} | {m.concept} | {m.feeling}\n"
                f"    {content}\n"
                f"    note: {m.note or '—'} | tag: {', '.join(m.tags) or '—'}"
            )
        return "\n\n".join(lines)

    def _extract_keywords(self, text: str) -> tuple[list[str], list[str]]:
        """Estrae keyword e concept dal testo per la ricerca nei ricordi."""
        prompt = (
            f"Estrai keyword e concetti per cercare ricordi personali.\n"
            f"Rispondi SOLO con JSON: "
            f'{{\"keywords\": [\"kw1\",\"kw2\"], \"concepts\": [\"Concetto1\"]}}\n\n'
            f"Testo: {text}"
        )
        try:
            raw  = self._llm.complete("Sei un estrattore di keyword. Solo JSON.", prompt)
            data = _parse_json(raw)
            return data.get("keywords", []), data.get("concepts", [])
        except Exception:
            # Fallback: split semplice
            words = [w.lower() for w in text.split() if len(w) > 3]
            return words[:5], []

    def _retrieve(
        self,
        query   : str,
        tier    : AccessTier,
        limit   : int = 15,
    ) -> list[Memory]:
        """Recupera ricordi rilevanti per la query rispettando il tier."""
        keywords, concepts = self._extract_keywords(query)
        seen: set[str] = set()
        memories: list[Memory] = []

        def _add(mems: list[Memory]) -> None:
            for m in mems:
                if m.memory_id not in seen:
                    memories.append(m)
                    seen.add(m.memory_id)

        for concept in concepts:
            _add(self._vault.recall_accessible(tier, concept=concept, limit=8))
        for kw in keywords:
            _add(self._vault.search_accessible(kw, tier, limit=5))

        if not memories:
            _add(self._vault.recall_accessible(tier, limit=limit))

        return memories[:limit]

    # ── ASK ──────────────────────────────────────────────────

    def ask(
        self,
        question : str,
        *,
        tier     : AccessTier = AccessTier.FAMILY,
        language : Optional[str] = None,
    ) -> ConsultationResult:
        """
        Risponde a una domanda in prima persona, basandosi solo sui ricordi reali.

        Parametri
        ---------
        question : domanda del consultatore
        tier     : livello di accesso (determina quali ricordi sono visibili)
        language : sovrascrive la lingua del profilo

        Esempio
        -------
        >>> r = twin.ask("Cosa ti ha insegnato la perdita di tuo padre?")
        >>> r = twin.ask("Hai mai rimpianto di non aver viaggiato di più?",
        ...              tier=AccessTier.INTIMATE)
        """
        memories = self._retrieve(question, tier)
        lang     = language or self._profile.language

        if not memories:
            return ConsultationResult(
                question      = question,
                response      = (
                    f"Non ho ricordi che mi permettano di rispondere a questa domanda. "
                    f"Questo momento non è stato registrato nella mia memoria."
                ),
                memories_used = [],
                tier          = tier,
                confidence    = "insufficiente",
                caveat        = "Nessun ricordo pertinente trovato nel database.",
            )

        context = self._memories_to_context(memories)
        p       = self._profile

        prompt = (
            f"Questi sono i tuoi ricordi reali pertinenti alla domanda:\n\n"
            f"{context}\n\n"
            f"---\n"
            f"La persona che ti parla vuole sapere: {question}\n\n"
            f"Rispondi in prima persona come {p.name}.\n"
            f"Usa SOLO i ricordi forniti — mai inventare.\n"
            f"Se i ricordi coprono solo parzialmente la domanda, dillo.\n"
            f"Ultima riga: \"Certezza: [alta/media/bassa] — [motivazione]\""
        )

        raw        = self._llm.complete(self._system, prompt)
        confidence, response = _extract_trailing_line(raw, "Certezza:")

        # Caveat se i ricordi sono pochi
        caveat = ""
        if len(memories) < 3:
            caveat = (
                f"Risposta basata su {len(memories)} ricordo/i. "
                f"La memoria registrata su questo tema è limitata."
            )
        if tier == AccessTier.PUBLIC and self._profile.embargo_active():
            caveat += " Alcuni ricordi potrebbero essere sotto embargo."

        return ConsultationResult(
            question      = question,
            response      = response,
            memories_used = memories,
            tier          = tier,
            confidence    = confidence,
            caveat        = caveat,
        )

    # ── LETTER ───────────────────────────────────────────────

    def letter(
        self,
        to      : str,
        theme   : str,
        *,
        tier    : AccessTier = AccessTier.FAMILY,
    ) -> LetterResult:
        """
        Genera una lettera scritta dal twin a una persona o gruppo.

        La lettera è costruita sui ricordi reali — non è un template generico.
        Ogni frase è ancorata a qualcosa che la persona ha davvero vissuto.

        Parametri
        ---------
        to    : destinatario (es. "mia figlia", "i miei nipoti", "chi mi ha voluto bene")
        theme : tema centrale della lettera (es. "cosa conta davvero", "il lavoro")
        tier  : livello di accesso ai ricordi

        Esempio
        -------
        >>> l = twin.letter(to="mia figlia Elena", theme="il coraggio")
        >>> l = twin.letter(to="chiunque legga", theme="cosa rimpiango e cosa no")
        """
        memories = self._retrieve(theme, tier, limit=20)
        context  = self._memories_to_context(memories)
        p        = self._profile

        prompt = (
            f"Scrivi una lettera personale a: {to}\n"
            f"Tema centrale: {theme}\n\n"
            f"Questi sono i tuoi ricordi reali su cui basare la lettera:\n\n"
            f"{context}\n\n"
            f"Regole:\n"
            f"- Scrivi in prima persona come {p.name}\n"
            f"- Ogni affermazione deve essere ancorata a un ricordo reale\n"
            f"- Tono: autentico, diretto, senza retorica\n"
            f"- Lunghezza: 300-500 parole\n"
            f"- Inizia con 'Cara/o {to},' o equivalente\n"
            f"- Firma con il tuo nome: {p.name.split()[0]}"
        )

        text = self._llm.complete(self._system, prompt)

        return LetterResult(
            to           = to,
            theme        = theme,
            text         = text,
            memories_used= memories,
        )

    # ── LEGACY ───────────────────────────────────────────────

    def legacy(
        self,
        *,
        tier : AccessTier = AccessTier.FAMILY,
    ) -> LegacyResult:
        """
        Genera l'eredità emotiva completa: chi era questa persona,
        cosa ha vissuto, cosa lascia.

        Analizza l'intera memoria accessibile e produce:
        - ritratto psicologico autentico
        - valori emersi dai ricordi (non dichiarati — vissuti)
        - tensioni irrisolte
        - messaggio finale sintetizzato

        Esempio
        -------
        >>> leg = twin.legacy(tier=AccessTier.FAMILY)
        >>> print(leg.message)
        """
        p        = self._profile
        memories = self._vault.recall_accessible(tier, limit=50)
        stats    = self._vault.stats(tier)

        if not memories:
            raise ValueError("Nessun ricordo accessibile per questo tier.")

        context = self._memories_to_context(memories[:30])

        # Statistiche narrative
        top_concepts = [c for c, _ in stats["top_concepts"][:8]]
        feel_dist    = stats["feeling_dist"]
        total        = stats["total_accessible"]

        feel_str = "  ".join(
            f"{f}({n})" for f, n in
            sorted(feel_dist.items(), key=lambda x: -x[1])[:8]
        )

        prompt = (
            f"Questi sono {total} ricordi reali di {p.name} "
            f"({p.birth_year}–{p.death_year or 'oggi'}), "
            f"età {p.age_at_death or '?'} anni.\n\n"
            f"Concetti dominanti: {', '.join(top_concepts)}\n"
            f"Distribuzione emotiva: {feel_str}\n\n"
            f"Campione ricordi:\n{context}\n\n"
            f"Produci in prima persona come {p.name}:\n\n"
            f"RITRATTO: chi sono davvero — come ho vissuto il mondo (3-4 frasi)\n\n"
            f"VALORI: cosa emerge dai ricordi come centrali nella mia vita "
            f"(non ciò che ho dichiarato — ciò che ho vissuto) (2-3 frasi)\n\n"
            f"IRRISOLTO: cosa non ho mai chiuso, cosa ha pesato (1-2 frasi, onesto)\n\n"
            f"MESSAGGIO: quello che voglio lasciare a chi mi legge — "
            f"una sola cosa vera, non retorica (2-3 frasi)\n\n"
            f"ARCO: in una riga — il filo della mia vita emotiva\n\n"
            f"Separa le sezioni con i titoli in maiuscolo come indicato."
        )

        raw = self._llm.complete(self._system, prompt)

        # Estrai le sezioni
        sections = _extract_sections(raw, ["RITRATTO", "VALORI", "IRRISOLTO", "MESSAGGIO", "ARCO"])

        return LegacyResult(
            portrait         = sections.get("RITRATTO", raw[:300]),
            core_values      = sections.get("VALORI", ""),
            unresolved       = sections.get("IRRISOLTO", ""),
            message          = sections.get("MESSAGGIO", ""),
            dominant_concepts= top_concepts,
            emotional_arc    = sections.get("ARCO", ""),
        )

    # ── TIMELINE ─────────────────────────────────────────────

    def timeline(
        self,
        concept : str,
        *,
        tier    : AccessTier = AccessTier.FAMILY,
    ) -> TimelineResult:
        """
        Arco emotivo di un concept nel tempo — come è cambiato
        il rapporto con questo tema lungo tutta la vita.

        Esempio
        -------
        >>> t = twin.timeline("lavoro")
        >>> t = twin.timeline("padre", tier=AccessTier.INTIMATE)
        """
        memories = self._vault.recall_accessible(tier, concept=concept, limit=30)

        if not memories:
            raise ValueError(
                f"Nessun ricordo accessibile per il concept '{concept}' "
                f"con tier {tier.value}."
            )

        # Ordina per timestamp
        memories.sort(key=lambda m: m.timestamp)
        context      = self._memories_to_context(memories)
        feelings_seq = " → ".join(m.feeling for m in memories)
        p            = self._profile

        prompt = (
            f"Questi sono tutti i miei ricordi legati a '{concept}', "
            f"in ordine cronologico:\n\n{context}\n\n"
            f"Arco emotivo: {feelings_seq}\n\n"
            f"Racconta in prima persona come è cambiato il mio rapporto con '{concept}' "
            f"nel corso della vita. Sii specifico — cita i ricordi reali.\n"
            f"Ultima riga: \"Arco: [sintesi in una riga]\""
        )

        raw  = self._llm.complete(self._system, prompt)
        arc, narrative = _extract_trailing_line(raw, "Arco:")

        entries = [
            {
                "date"   : m.timestamp[:10],
                "feeling": m.feeling,
                "concept": m.concept,
                "excerpt": (m.content[:120] + "…" if len(m.content) > 120 else m.content),
                "tags"   : m.tags,
            }
            for m in memories
        ]

        return TimelineResult(
            concept = concept,
            arc     = arc,
            entries = entries,
        )

    # ── INFO ─────────────────────────────────────────────────

    def profile_summary(self) -> dict:
        p = self._profile
        s = self._vault.stats(AccessTier.FULL)
        return {
            "name"             : p.name or "Sconosciuto",
            "born"             : p.birth_year,
            "died"             : p.death_year,
            "age_at_death"     : p.age_at_death,
            "language"         : p.language or "italiano",
            "total_memories"   : s["total_in_db"],
            "embargo_active"   : p.embargo_active(),
            "embargo_until"    : p.embargo_lifted_year,
            "dominant_concepts": [c for c, _ in s["top_concepts"][:5]],
            "emotional_map"    : s["feeling_dist"],
            "curator"          : p.curator_name or "",
            "epitaph"          : p.epitaph or "",
        }

    def __repr__(self) -> str:
        p = self._profile
        status = f"†{p.death_year}" if p.is_deceased else "in vita"
        return (
            f"DigitalTwin(\n"
            f"  person  = '{p.name}' ({p.birth_year}–{status})\n"
            f"  db      = {self._db!r}\n"
            f"  llm     = {self._llm!r}\n"
            f"  embargo = {'attivo' if p.embargo_active() else 'non attivo'}\n"
            f")"
        )


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

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
    lines = text.strip().split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith(prefix):
            value = lines[i].strip()[len(prefix):].strip()
            body  = "\n".join(lines[:i]).strip()
            return value, body
    return "", text.strip()


def _extract_sections(text: str, keys: list[str]) -> dict[str, str]:
    """Estrae sezioni etichettate (es. RITRATTO: ...) da un testo strutturato."""
    result = {}
    pattern = "|".join(re.escape(k) for k in keys)
    parts   = re.split(rf"({pattern}):", text, flags=re.IGNORECASE)
    i = 1
    while i < len(parts) - 1:
        key     = parts[i].strip().upper()
        content = parts[i + 1].strip()
        # Tronca al prossimo header
        next_match = re.search(rf"({pattern}):", content, re.IGNORECASE)
        if next_match:
            content = content[:next_match.start()].strip()
        result[key] = content
        i += 2
    return result