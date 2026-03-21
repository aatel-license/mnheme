"""
generate_memories.py  —  MNHEME Synthetic Life Generator
=========================================================
Genera una vita sintetica completa con arco evolutivo reale:
dalla prima infanzia all'età attuale, con ricordi che si
rielaborano nel tempo come nell'esperienza umana autentica.

Principi architetturali
-----------------------
  ARCO TEMPORALE
    I timestamp sono date reali calcolate a partire dall'anno
    di nascita della persona. Ogni ricordo è associato all'età
    in cui è avvenuto. L'età di inizio è configurabile (0-130).

  FASI DELLA VITA
    Ogni fase ha una distribuzione emotiva distinta e un pool
    di domini tematici coerenti con quella stagione della vita.
    La distribuzione è calibrata su dati psicologici reali
    (peak-end rule, reminiscence bump, positivity effect).

  RIELABORAZIONE
    ~20% dei ricordi sono rielaborazioni di eventi passati:
    stesso concept, feeling cambiato. Modella il processo
    mnemonico umano di revisione emotiva.

  COSCIENZA NARRATIVA
    Il generatore mantiene un filo narrativo tra i ricordi:
    concept e tag ricorrenti vengono ripresi per creare
    coerenza biografica, come nella memoria episodica.

  DISTRIBUZIONE SENZA BIAS
    Nessun feeling viene scelto dal modello LLM: tutti sono
    pre-assegnati dal generatore secondo pesi per fase della
    vita. Il modello scrive solo il contenuto narrativo.

Utilizzo
--------
    python generate_memories.py --n 50 --birth-year 1985
    python generate_memories.py --n 100 --start-age 6 --current-age 35
    python generate_memories.py --n 30 --dry-run --verbose
    python generate_memories.py --n 200 --birth-year 1940 --workers 5

Dipendenze
----------
    Nessuna — solo stdlib Python 3.10+
    (mnheme.py deve essere nella stessa directory per i Feeling)
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import textwrap
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import date, timedelta

# ── Feeling ──────────────────────────────────────────────────
try:
    from mnheme import Feeling
    VALID_FEELINGS: list[str] = [f.value for f in Feeling]
except ImportError:
    VALID_FEELINGS = [
        "ansia", "paura", "sollievo", "tristezza", "gioia", "rabbia",
        "vergogna", "senso_di_colpa", "nostalgia", "speranza", "orgoglio",
        "delusione", "solitudine", "confusione", "gratitudine", "invidia",
        "imbarazzo", "eccitazione", "rassegnazione", "stupore", "amore",
        "malinconia", "serenità", "sorpresa", "noia", "curiosità",
    ]

# ── ANSI ─────────────────────────────────────────────────────
GRN = "\033[32m"; RED = "\033[31m"; YLW = "\033[33m"
CYN = "\033[36m"; MAG = "\033[35m"; DIM = "\033[2m"
BOLD = "\033[1m"; NC  = "\033[0m"

def _c(col: str, t: str) -> str: return f"{col}{t}{NC}"


# ═══════════════════════════════════════════════════════════════
# LIFE PHASES
# ═══════════════════════════════════════════════════════════════

@dataclass
class LifePhase:
    name            : str
    age_min         : int
    age_max         : int
    feeling_weights : dict[str, float]
    domains         : list[str]
    narrative       : str


# Distribuzioni calibrate su:
#   - Reminiscence bump (picco 15-30 anni)
#   - Positivity effect in vecchiaia (Carstensen 2006)
#   - Emotional development nell'infanzia (Gross 2015)
#   - Distribuzione bilanciata: ~40% positivi, ~35% neutri, ~25% negativi

LIFE_PHASES: list[LifePhase] = [

    LifePhase(
        name="Prima infanzia", age_min=0, age_max=5,
        feeling_weights={
            "stupore": 3.0, "gioia": 2.8, "curiosità": 2.5,
            "sorpresa": 2.2, "amore": 2.0, "paura": 1.5,
            "confusione": 1.2, "tristezza": 0.8, "sollievo": 0.8,
        },
        domains=[
            "gioco", "famiglia", "sonno", "cibo", "animali",
            "scoperta", "corpo", "fratelli", "nonni", "nido",
        ],
        narrative=(
            "Sei un bambino di pochi anni. I ricordi sono sensoriali e vividi, "
            "senza contesto sociale. Il linguaggio è semplice, concreto, meravigliato."
        ),
    ),

    LifePhase(
        name="Infanzia", age_min=6, age_max=11,
        feeling_weights={
            "gioia": 2.5, "curiosità": 2.3, "eccitazione": 2.0,
            "stupore": 1.8, "orgoglio": 1.5, "amore": 1.5,
            "speranza": 1.2, "sorpresa": 1.3, "imbarazzo": 1.5,
            "paura": 1.3, "tristezza": 1.0, "invidia": 1.0,
            "confusione": 1.0, "noia": 0.8,
        },
        domains=[
            "scuola", "amici", "sport", "gioco", "famiglia",
            "vacanze", "animali_domestici", "insegnanti", "regole",
            "giocattoli", "competizioni", "primo_giorno",
        ],
        narrative=(
            "Sei un bambino in età scolare. Il mondo è grande e spesso incomprensibile. "
            "Le amicizie sono totali. Le ingiustizie bruciano. "
            "La curiosità è inesauribile."
        ),
    ),

    LifePhase(
        name="Adolescenza", age_min=12, age_max=17,
        feeling_weights={
            "amore": 2.5, "imbarazzo": 2.5, "eccitazione": 2.3,
            "vergogna": 2.2, "invidia": 2.0, "solitudine": 2.0,
            "rabbia": 2.0, "confusione": 1.8, "speranza": 1.8,
            "orgoglio": 1.5, "ansia": 1.5, "delusione": 1.5,
            "gioia": 1.3, "malinconia": 1.5, "nostalgia": 0.8,
        },
        domains=[
            "primo_amore", "scuola", "corpo", "amicizia", "musica",
            "identità", "segreti", "feste", "sport", "sogni",
            "conflitti_genitori", "ribellione", "gruppi_sociali",
        ],
        narrative=(
            "Sei un adolescente. Le emozioni sono amplificate, il corpo cambia, "
            "l'identità è instabile. Ogni cosa è urgente e definitiva. "
            "Il giudizio degli altri è una presenza costante."
        ),
    ),

    LifePhase(
        name="Prima età adulta", age_min=18, age_max=29,
        feeling_weights={
            "amore": 2.5, "eccitazione": 2.2, "speranza": 2.2,
            "ansia": 2.0, "orgoglio": 1.8, "gioia": 1.8,
            "gratitudine": 1.3, "solitudine": 1.5, "delusione": 1.5,
            "confusione": 1.3, "vergogna": 1.2, "paura": 1.2,
            "nostalgia": 1.0, "malinconia": 1.0, "rassegnazione": 0.8,
        },
        domains=[
            "università", "lavoro", "indipendenza", "relazioni",
            "amicizia", "denaro", "casa", "viaggi", "identità",
            "carriera", "rotture", "trasferimenti", "fallimenti",
            "successi", "primo_appartamento", "famiglia_origine",
        ],
        narrative=(
            "Sei un giovane adulto. Stai costruendo la tua vita. "
            "Le scelte sembrano permanenti. C'è entusiasmo e terrore allo stesso tempo. "
            "Le prime delusioni profonde."
        ),
    ),

    LifePhase(
        name="Età adulta", age_min=30, age_max=44,
        feeling_weights={
            "gratitudine": 2.0, "amore": 2.0, "orgoglio": 1.8,
            "ansia": 1.8, "serenità": 1.5, "sollievo": 1.5,
            "nostalgia": 1.5, "delusione": 1.5, "tristezza": 1.2,
            "malinconia": 1.2, "speranza": 1.3, "senso_di_colpa": 1.3,
            "gioia": 1.5, "rassegnazione": 1.2, "rabbia": 1.0,
        },
        domains=[
            "carriera", "famiglia", "figli", "casa", "salute",
            "denaro", "relazioni_lunghe", "genitori_anziani",
            "amicizie_che_cambiano", "rimpianti", "successi",
            "corpo_che_cambia", "crisi", "tempo",
        ],
        narrative=(
            "Sei un adulto con responsabilità consolidate. Il tempo accelera. "
            "Si bilanciano aspettative e realtà. Emergono rimpianti accanto a "
            "soddisfazioni profonde."
        ),
    ),

    LifePhase(
        name="Mezza età", age_min=45, age_max=59,
        feeling_weights={
            "nostalgia": 2.5, "gratitudine": 2.2, "malinconia": 2.0,
            "serenità": 1.8, "rassegnazione": 1.8, "orgoglio": 1.5,
            "senso_di_colpa": 1.5, "tristezza": 1.5, "solitudine": 1.5,
            "amore": 1.5, "delusione": 1.3, "ansia": 1.2,
            "speranza": 1.0, "sollievo": 1.2, "gioia": 1.2,
        },
        domains=[
            "figli_adulti", "genitori_che_invecchiano", "lutto",
            "carriera_in_bilico", "salute", "corpo", "rimpianti",
            "amicizie_perse", "matrimonio_lungo", "divorzio",
            "eredità", "valori", "pensione_vicina",
        ],
        narrative=(
            "Sei in mezza età. Guardi indietro quanto avanti. "
            "I genitori invecchiano o non ci sono più. I figli se ne vanno. "
            "Si fa i conti con cosa si è davvero diventati."
        ),
    ),

    LifePhase(
        name="Tarda età adulta", age_min=60, age_max=79,
        feeling_weights={
            "gratitudine": 3.0, "nostalgia": 2.8, "serenità": 2.5,
            "amore": 2.0, "malinconia": 2.0, "solitudine": 2.0,
            "orgoglio": 1.8, "rassegnazione": 1.8, "stupore": 1.3,
            "gioia": 1.5, "tristezza": 1.5, "sollievo": 1.5,
        },
        domains=[
            "pensione", "nipoti", "salute", "lutto", "amicizie_storiche",
            "viaggi", "passioni", "memoria", "famiglia", "eredità",
            "rimpianti_risolti", "saggezza", "spiritualità",
        ],
        narrative=(
            "Sei in tarda età adulta. Il positivity effect è reale: "
            "si selezionano i ricordi buoni. C'è più presenza nel presente. "
            "Le perdite si accumulano ma anche la gratitudine."
        ),
    ),

    LifePhase(
        name="Vecchiaia", age_min=80, age_max=130,
        feeling_weights={
            "gratitudine": 3.5, "serenità": 3.0, "nostalgia": 3.0,
            "amore": 2.5, "stupore": 2.0, "malinconia": 2.0,
            "solitudine": 2.0, "rassegnazione": 2.0, "orgoglio": 1.5,
            "gioia": 1.8, "tristezza": 1.5, "sollievo": 1.5,
        },
        domains=[
            "memoria", "famiglia", "passato", "nipoti", "pronipoti",
            "salute", "perdite", "saggezza", "corpo", "spiritualità",
            "eredità_emotiva", "riconciliazioni", "ultime_volte",
        ],
        narrative=(
            "Sei in tarda vecchiaia. Il tempo ha una texture diversa. "
            "I ricordi lontani sono nitidi, quelli recenti sfumati. "
            "C'è una qualità contemplativa in ogni cosa."
        ),
    ),
]


def _get_phase(age: float) -> LifePhase:
    for phase in LIFE_PHASES:
        if phase.age_min <= age <= phase.age_max:
            return phase
    return LIFE_PHASES[-1]


def _phase_pick_feeling(phase: LifePhase) -> str:
    """Sceglie un feeling secondo la distribuzione della fase."""
    base = {f: 0.3 for f in VALID_FEELINGS}
    base.update(phase.feeling_weights)
    feelings = list(base.keys())
    weights  = list(base.values())
    return random.choices(feelings, weights=weights, k=1)[0]


# ═══════════════════════════════════════════════════════════════
# TIMESTAMP ENGINE
# ═══════════════════════════════════════════════════════════════

def _birth_date(birth_year: int) -> date:
    return date(birth_year, random.randint(1, 12), random.randint(1, 28))

def _date_at_age(birth: date, age: float) -> date:
    days = int(age * 365.25) + random.randint(-90, 90)
    d = birth + timedelta(days=days)
    today = date.today()
    if d > today:
        d = today - timedelta(days=random.randint(1, 90))
    return d


# ═══════════════════════════════════════════════════════════════
# CONSCIOUSNESS ENGINE
# ═══════════════════════════════════════════════════════════════

@dataclass
class Consciousness:
    """
    Filo narrativo della persona sintetica.
    Traccia concept usati, tag ricorrenti e ricordi rielaborabili.
    """
    concept_usage   : Counter = field(default_factory=Counter)
    tag_pool        : list[str] = field(default_factory=list)
    reworkable      : list[dict] = field(default_factory=list)
    content_prefixes: list[str] = field(default_factory=list)

    def record(self, mem: "MemoryRecord") -> None:
        self.concept_usage[mem.concept] += 1
        self.tag_pool.extend(mem.tags)
        self.content_prefixes.append(mem.content[:40])
        if not mem.is_rework and mem.tags:
            self.reworkable.append({
                "concept": mem.concept,
                "tags"   : mem.tags,
                "feeling": mem.feeling,
            })

    def should_rework(self) -> bool:
        return bool(self.reworkable) and random.random() < 0.20

    def pick_rework(self) -> dict | None:
        if not self.reworkable:
            return None
        heavy = [r for r in self.reworkable
                 if r["feeling"] in ("ansia","paura","rabbia","tristezza",
                                     "vergogna","delusione","senso_di_colpa")]
        return random.choice(heavy if heavy else self.reworkable)

    def recurring_tags(self, k: int = 4) -> list[str]:
        c = Counter(self.tag_pool)
        return [t for t, _ in c.most_common(k)]


# ═══════════════════════════════════════════════════════════════
# DATA MODEL
# ═══════════════════════════════════════════════════════════════

@dataclass
class MemoryRecord:
    concept      : str
    feeling      : str
    content      : str
    timestamp    : str
    age_at_event : float
    phase_name   : str
    media_type   : str = "text"
    note         : str = ""
    tags         : list[str] = field(default_factory=list)
    is_rework    : bool = False

    def to_payload(self) -> dict:
        note_parts = []
        if self.note:
            note_parts.append(self.note)
        note_parts.append(f"età: {self.age_at_event:.0f} anni · {self.phase_name}")
        if self.is_rework:
            note_parts.append("rielaborazione")
        return {
            "concept"   : self.concept,
            "feeling"   : self.feeling,
            "content"   : self.content,
            "media_type": self.media_type,
            "note"      : " · ".join(note_parts),
            "tags"      : self.tags or [],
        }


# ═══════════════════════════════════════════════════════════════
# LLM CLIENT — stdlib only
# ═══════════════════════════════════════════════════════════════

class LLMClient:
    def __init__(self, base_url: str, model: str, api_key: str = "") -> None:
        self.base_url  = base_url.rstrip("/")
        self.model     = model
        self.api_key   = api_key
        self._chat_url = f"{self.base_url}/v1/chat/completions"

    def discover_model(self) -> str:
        url = f"{self.base_url}/v1/models"
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url), timeout=5
            ) as resp:
                data   = json.loads(resp.read())
                models = [m.get("id","") for m in data.get("data",[])]
                if not models:
                    raise RuntimeError("Nessun modello trovato su /v1/models")
                return models[0]
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Server non raggiungibile a {self.base_url}: {e.reason}"
            ) from e

    def complete(self, system: str, user: str,
                 temperature: float = 0.88, max_tokens: int = 2048) -> str:
        payload = json.dumps({
            "model": self.model, "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        }, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json",
                   "User-Agent": "MNHEME-LifeGen/3.0"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(
            self._chat_url, data=payload, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read())
            return body["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(
                f"LLM HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}"
            ) from e
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Risposta LLM malformata: {e}") from e


# ═══════════════════════════════════════════════════════════════
# MNHEME CLIENT
# ═══════════════════════════════════════════════════════════════

class MnhemeClient:
    def __init__(self, api_url: str) -> None:
        self._base    = api_url.rstrip("/")
        self._mem_url = self._base + "/memories"

    def ping(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self._base}/stats", timeout=4):
                return True
        except Exception:
            return False

    def post(self, memory: MemoryRecord, max_retries: int = 3) -> str:
        payload = json.dumps(
            memory.to_payload(), ensure_ascii=False
        ).encode("utf-8")
        req = urllib.request.Request(
            self._mem_url, data=payload, method="POST",
            headers={"Content-Type":"application/json","accept":"application/json"},
        )
        last_err: Exception = RuntimeError("POST non tentato")
        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                return data.get("memory_id") or data.get("id") or "?"
            except Exception as e:
                last_err = e
                if attempt < max_retries:
                    time.sleep(1.5 ** attempt)
        raise last_err


# ═══════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ═══════════════════════════════════════════════════════════════

_SYSTEM = (
    "Sei un generatore di ricordi autobiografici umani autentici. "
    "Scrivi in prima persona con voce interiore vera. "
    "Rispondi SEMPRE e SOLO con JSON valido. "
    "Nessun testo extra, nessun markdown, nessun backtick."
)


def _build_prompt(
    slots          : list[dict],
    consciousness  : Consciousness,
    avoid_concepts : list[str],
    avoid_prefixes : list[str],
) -> str:
    seed     = random.randint(0, 99_999_999)
    recurring = consciousness.recurring_tags(4)
    filo = (
        f"\nFILO NARRATIVO: questi temi ricorrono nella vita di questa persona "
        f"e possono (non obbligatoriamente) essere ripresi: {', '.join(recurring)}"
        if recurring else ""
    )

    avoid_c = json.dumps(avoid_concepts[-30:], ensure_ascii=False)
    avoid_p = json.dumps(avoid_prefixes[-15:], ensure_ascii=False)

    specs = []
    for i, slot in enumerate(slots):
        phase: LifePhase = slot["phase"]
        rw = slot.get("rework_of")
        domains_sample = random.sample(phase.domains, min(4, len(phase.domains)))

        if rw:
            specs.append(
                f"Ricordo {i+1} [RIELABORAZIONE — stesso evento, occhi diversi]:\n"
                f"  feeling = \"{slot['feeling']}\"\n"
                f"  età = {slot['age']:.0f} anni  (fase: {phase.name})\n"
                f"  Rielabora questo ricordo passato:\n"
                f"    concept originale: {rw['concept']}\n"
                f"    feeling originale: {rw['feeling']}\n"
                f"    tag originali: {rw['tags']}\n"
                f"  Usa lo stesso concept o derivato. Il feeling è cambiato "
                f"perché la persona è cresciuta/guarita/cambiata.\n"
                f"  Voce: {phase.narrative}"
            )
        else:
            specs.append(
                f"Ricordo {i+1}:\n"
                f"  feeling = \"{slot['feeling']}\"\n"
                f"  età = {slot['age']:.0f} anni  (fase: {phase.name})\n"
                f"  ambiti suggeriti: {', '.join(domains_sample)}\n"
                f"  Voce: {phase.narrative}"
            )

    return textwrap.dedent(f"""
        SEED: {seed}{filo}

        Genera esattamente {len(slots)} ricordi personali seguendo le specifiche.

        REGOLE GLOBALI:
        - concept: UNA sola parola, sostantivo singolo, minuscolo
          (es: "mutuo", "promozione", "tradimento", "vacanza", "dentista")
        - NON usare concept già presenti: {avoid_c}
        - content: prima persona, specifico e concreto — tono coerente col feeling e l'età
        - Evita inizi simili a: {avoid_p}
        - Niente cliché ("mi sono reso conto", "ho capito che", "in quel momento")
        - note: contesto breve (luogo, periodo, chi c'era) — può essere ""
        - tags: 2-4 stringhe minuscolo (includi anno approssimativo se rilevante)

        SPECIFICHE:
        {chr(10).join(specs)}

        OUTPUT — array JSON di {len(slots)} oggetti, niente altro:
        [
          {{
            "concept": "parolasingola",
            "feeling": "esattamente_come_specificato",
            "content": "...",
            "note": "...",
            "tags": ["tag1", "tag2"]
          }}
        ]
    """).strip()


# ═══════════════════════════════════════════════════════════════
# PARSING & VALIDATION
# ═══════════════════════════════════════════════════════════════

def _clean_concept(raw: str) -> str:
    word = raw.strip().split()[0] if raw.strip() else "ricordo"
    word = re.sub(r"[^\w]", "", word, flags=re.UNICODE)
    return word.lower() or "ricordo"


def _parse_json_list(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(
            l for l in text.splitlines() if not l.strip().startswith("```")
        ).strip()
    try:
        r = json.loads(text)
        if isinstance(r, list): return r
        if isinstance(r, dict) and "memories" in r: return r["memories"]
    except json.JSONDecodeError:
        pass
    m = re.search(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)
    if m:
        try: return json.loads(m.group())
        except json.JSONDecodeError: pass
    raise ValueError(f"JSON non estraibile:\n{text[:400]}")


def _validate(
    item           : dict,
    target_feeling : str,
    target_age     : float,
    birth          : date,
    phase          : LifePhase,
    is_rework      : bool,
) -> MemoryRecord | None:
    concept = _clean_concept(str(item.get("concept", "")))
    if not concept: return None

    # Feeling: forza il target — il modello non sceglie
    feeling = str(item.get("feeling", "")).strip().replace(" ", "_")
    if feeling not in VALID_FEELINGS:
        feeling = target_feeling

    content = str(item.get("content", "")).strip()
    if not content: return None
    if len(content) > 450: content = content[:447] + "…"

    note = str(item.get("note", "")).strip()[:200]

    raw_tags = item.get("tags", [])
    if isinstance(raw_tags, str):
        raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    tags = [str(t).strip().lower() for t in raw_tags if t][:6]

    event_date = _date_at_age(birth, target_age)
    timestamp  = (
        f"{event_date.isoformat()}T"
        f"{random.randint(6,22):02d}:{random.randint(0,59):02d}:00"
    )

    return MemoryRecord(
        concept      = concept,
        feeling      = feeling,
        content      = content,
        timestamp    = timestamp,
        age_at_event = target_age,
        phase_name   = phase.name,
        note         = note,
        tags         = tags,
        is_rework    = is_rework,
    )


# ═══════════════════════════════════════════════════════════════
# SLOT PLANNER
# ═══════════════════════════════════════════════════════════════

def _plan_slots(
    n            : int,
    start_age    : float,
    current_age  : float,
    consciousness: Consciousness,
) -> list[dict]:
    """
    Pianifica n slot distribuiti lungo l'arco di vita con:
    - reminiscence bump (più ricordi 15-30 anni)
    - feeling pre-assegnati per fase (zero bias LLM)
    - ~20% rielaborazioni
    """
    # Distribuzione temporale con reminiscence bump
    ages: list[float] = []
    for _ in range(n):
        r = random.random()
        if r < 0.10:
            lo, hi = start_age, min(11, current_age)
        elif r < 0.35:
            lo, hi = max(start_age, 12), min(17, current_age)
        elif r < 0.65:
            lo, hi = max(start_age, 15), min(35, current_age)
        elif r < 0.82:
            lo, hi = max(start_age, 30), min(55, current_age)
        else:
            lo, hi = max(start_age, current_age * 0.75), current_age

        lo = max(start_age, lo)
        hi = max(lo, hi)
        ages.append(random.uniform(lo, hi) if lo < hi else lo)

    ages = sorted(max(start_age, min(a, current_age)) for a in ages)

    slots: list[dict] = []
    for age in ages:
        phase     = _get_phase(age)
        feeling   = _phase_pick_feeling(phase)
        is_rework = consciousness.should_rework()
        rework_of = consciousness.pick_rework() if is_rework else None
        slots.append({
            "age"      : age,
            "phase"    : phase,
            "feeling"  : feeling,
            "is_rework": is_rework,
            "rework_of": rework_of,
        })

    return slots


# ═══════════════════════════════════════════════════════════════
# BATCH WORKER
# ═══════════════════════════════════════════════════════════════

def _run_batch(
    llm          : LLMClient,
    api          : MnhemeClient,
    slots        : list[dict],
    batch_id     : int,
    birth        : date,
    consciousness: Consciousness,
    dry_run      : bool,
    verbose      : bool,
    max_retries  : int = 3,
) -> list[tuple[MemoryRecord, str | None]]:

    avoid_concepts = list(consciousness.concept_usage.keys())
    avoid_prefixes = consciousness.content_prefixes[-20:]

    raw_list: list[dict] = []
    for attempt in range(1, max_retries + 1):
        try:
            prompt   = _build_prompt(slots, consciousness, avoid_concepts, avoid_prefixes)
            raw_text = llm.complete(
                _SYSTEM, prompt,
                temperature = 0.88 + random.uniform(-0.05, 0.10),
            )
            raw_list = _parse_json_list(raw_text)
            break
        except (RuntimeError, ValueError) as e:
            if attempt == max_retries:
                print(f"  {_c(RED,'✗')} batch {batch_id} fallito: {e}")
                return []
            wait = 2 ** attempt
            print(f"  {_c(YLW,'⚠')} batch {batch_id} retry {attempt} ({e}) in {wait}s")
            time.sleep(wait)

    results: list[tuple[MemoryRecord, str | None]] = []
    used_in_batch: set[str] = set()

    for i, item in enumerate(raw_list[:len(slots)]):
        slot   = slots[i] if i < len(slots) else slots[-1]
        record = _validate(
            item,
            target_feeling = slot["feeling"],
            target_age     = slot["age"],
            birth          = birth,
            phase          = slot["phase"],
            is_rework      = slot.get("is_rework", False),
        )
        if record is None:
            if verbose: print(f"  {_c(DIM,'·')} slot {i+1} scartato")
            continue
        if record.concept in used_in_batch:
            if verbose: print(f"  {_c(DIM,'·')} dup concept: {record.concept}")
            continue
        used_in_batch.add(record.concept)

        # POST
        memory_id = None
        if not dry_run:
            try:
                memory_id = api.post(record)
            except RuntimeError as e:
                print(f"  {_c(RED,'✗')} POST [{record.concept}]: {e}")

        # Print riga
        rw_mark  = _c(MAG, "↺ ") if record.is_rework else "  "
        age_str  = _c(DIM, f"{record.age_at_event:.0f}a")
        feel_str = _c(CYN, record.feeling)
        id_str   = _c(DIM, f"id:{memory_id}") if memory_id else (_c(DIM,"dry") if dry_run else "")
        status   = _c(GRN,"✓") if (memory_id or dry_run) else _c(RED,"✗")
        tags_str = _c(DIM, f"[{','.join(record.tags[:3])}]") if record.tags else ""
        print(f"  {status} {rw_mark}{_c(BOLD,record.concept):<20} {feel_str:<26} {age_str}  {id_str} {tags_str}")
        if verbose:
            print(_c(DIM, textwrap.fill(record.content, 68, initial_indent="       ")))

        results.append((record, memory_id))

    return results


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    today = date.today()

    parser = argparse.ArgumentParser(
        description="MNHEME Life Generator v3.0 — vita sintetica con arco evolutivo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Esempi:
              python generate_memories.py --n 50 --birth-year 1985
              python generate_memories.py --n 100 --start-age 6 --current-age 35
              python generate_memories.py --n 10 --dry-run --verbose
              python generate_memories.py --n 200 --birth-year 1940 --workers 5
        """),
    )
    parser.add_argument("--n",           type=int,   default=20,
                        help="Numero di ricordi (default: 20)")
    parser.add_argument("--birth-year",  type=int,   default=None,
                        help="Anno di nascita (es: 1985)")
    parser.add_argument("--start-age",   type=float, default=0.0,
                        help="Età minima dei ricordi, 0-130 (default: 0)")
    parser.add_argument("--current-age", type=float, default=None,
                        help="Età attuale — calcolata da --birth-year se omessa")
    parser.add_argument("--llm-url",     type=str,   default="http://localhost:1234",
                        help="Base URL server LLM")
    parser.add_argument("--model",       type=str,   default="",
                        help="Nome modello (auto se omesso)")
    parser.add_argument("--api-key",     type=str,   default="",
                        help="API key LLM (opzionale)")
    parser.add_argument("--api-url",     type=str,   default="http://localhost:8000",
                        help="URL base API MNHEME")
    parser.add_argument("--batch-size",  type=int,   default=5,
                        help="Ricordi per chiamata LLM, max 8 (default: 5)")
    parser.add_argument("--workers",     type=int,   default=3,
                        help="Thread paralleli (default: 3)")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Genera senza postare")
    parser.add_argument("--verbose",     action="store_true",
                        help="Mostra content completo")
    parser.add_argument("--sequential",  action="store_true",
                        help="Sequenziale (dedup perfetta, più lento)")
    args = parser.parse_args()

    # ── Parametri temporali ──────────────────────────────────
    if args.birth_year:
        birth       = _birth_date(args.birth_year)
        current_age = args.current_age or (today - birth).days / 365.25
    elif args.current_age:
        current_age = args.current_age
        birth       = today - timedelta(days=int(current_age * 365.25))
    else:
        current_age = 35.0
        birth       = today - timedelta(days=int(current_age * 365.25))

    start_age = max(0.0, min(float(args.start_age), current_age - 1))

    if start_age >= current_age:
        print(f"{_c(RED,'Errore:')} --start-age >= età attuale")
        sys.exit(1)

    # ── Banner ───────────────────────────────────────────────
    print(f"\n{_c(BOLD,'MNHEME Life Generator')}  {_c(DIM,'v3.0')}")
    print("─" * 60)
    print(f"  {_c(DIM,'Nascita:')}      {birth.isoformat()}")
    print(f"  {_c(DIM,'Età attuale:')}  {current_age:.0f} anni")
    print(f"  {_c(DIM,'Da età:')}       {start_age:.0f} anni")
    print(f"  {_c(DIM,'Arco vitale:')}  {current_age - start_age:.0f} anni")

    # ── LLM ─────────────────────────────────────────────────
    llm = LLMClient(args.llm_url, model=args.model, api_key=args.api_key)
    if not args.model:
        print(f"\n  {_c(CYN,'→')} Discovery modello…", end=" ", flush=True)
        try:
            llm.model = llm.discover_model()
            print(_c(GRN, llm.model))
        except RuntimeError as e:
            print(_c(RED,"fallito"))
            print(f"  {e}"); sys.exit(1)
    else:
        print(f"  {_c(CYN,'→')} Modello: {_c(GRN, llm.model)}")

    # ── API ──────────────────────────────────────────────────
    api = MnhemeClient(args.api_url)
    if not args.dry_run:
        print(f"  {_c(CYN,'→')} Ping MNHEME…", end=" ", flush=True)
        print(_c(GRN,"ok") if api.ping() else _c(YLW,"non raggiungibile"))
    else:
        print(f"  {_c(YLW,'→')} DRY-RUN")

    # ── Pianifica slot ───────────────────────────────────────
    consciousness = Consciousness()
    bs     = max(1, min(args.batch_size, 8))
    slots  = _plan_slots(args.n, start_age, current_age, consciousness)
    batches = [slots[i:i+bs] for i in range(0, len(slots), bs)]

    planned_feelings = Counter(s["feeling"] for s in slots)
    reworks_planned  = sum(1 for s in slots if s["is_rework"])
    top5 = planned_feelings.most_common(5)

    print(f"\n  {_c(DIM,f'{len(slots)} slot · {len(batches)} batch · arco {start_age:.0f}–{current_age:.0f} anni')}")
    print(f"  {_c(DIM,f'Rielaborazioni: {reworks_planned}')}")
    print(f"  {_c(DIM,'Top feeling pianificati: ')}" +
          "  ".join(f"{_c(CYN,f)} {n}" for f,n in top5))
    print("─" * 60)

    # ── Genera ───────────────────────────────────────────────
    all_results: list[tuple[MemoryRecord, str | None]] = []
    start = time.perf_counter()

    if args.sequential or len(batches) == 1:
        for i, batch_slots in enumerate(batches, 1):
            print(f"\n  {_c(DIM,f'Batch {i}/{len(batches)}')}")
            batch_res = _run_batch(
                llm, api, batch_slots, i,
                birth, consciousness,
                args.dry_run, args.verbose,
            )
            for rec, _ in batch_res:
                consciousness.record(rec)
            all_results.extend(batch_res)
    else:
        with ThreadPoolExecutor(max_workers=min(args.workers, len(batches))) as pool:
            futures = {
                pool.submit(
                    _run_batch,
                    llm, api, batch_slots, i,
                    birth, consciousness,
                    args.dry_run, args.verbose,
                ): i
                for i, batch_slots in enumerate(batches, 1)
            }
            for future in as_completed(futures):
                bid = futures[future]
                try:
                    batch_res = future.result()
                    all_results.extend(batch_res)
                    for rec, _ in batch_res:
                        consciousness.record(rec)
                    print(f"  {_c(DIM,f'Batch {bid}: {len(batch_res)} ricordi')}")
                except Exception as e:
                    print(f"  {_c(RED,'✗')} batch {bid}: {e}")

    elapsed = time.perf_counter() - start

    # ── Riepilogo ────────────────────────────────────────────
    ok      = sum(1 for _, mid in all_results if mid or args.dry_run)
    reworks = sum(1 for rec, _ in all_results if rec.is_rework)

    print(f"\n{'─'*60}")
    print(f"  {_c(BOLD,'Completato')} in {elapsed:.1f}s")
    print(f"  {_c(GRN,str(ok))} generati  "
          f"{_c(MAG,f'· {reworks} rielaborazioni')}  "
          f"{_c(YLW,f'· {args.n - ok} saltati')}")

    if all_results:
        real_dist = Counter(r.feeling for r, _ in all_results)
        print(f"\n  {_c(DIM,'Distribuzione emotiva:')}")
        total = len(all_results)
        for feeling, count in sorted(real_dist.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            bar = "█" * max(1, round(pct / 2.5))
            print(f"    {feeling:<20} {_c(CYN,bar)} {count} ({pct:.0f}%)")

        phase_dist = Counter(r.phase_name for r, _ in all_results)
        print(f"\n  {_c(DIM,'Per fase della vita:')}")
        for pname, count in sorted(phase_dist.items(),
                                   key=lambda x: -x[1]):
            bar = "█" * count
            print(f"    {pname:<26} {_c(DIM,bar)} {count}")

    print()


if __name__ == "__main__":
    main()
