"""
twin_api.py — Digital Twin REST API
=====================================
API dedicata al Digital Twin — separata dalla console MNHEME base.

Avvia con:
    uvicorn twin_api:app --reload --port 8001

Documentazione interattiva: http://localhost:8001/docs

Endpoints principali:
    POST /twin/setup          — configura il profilo del twin
    GET  /twin/profile        — stato e identità del twin
    POST /twin/ask            — domanda al twin
    POST /twin/letter         — genera una lettera
    GET  /twin/legacy         — eredità emotiva completa
    GET  /twin/timeline/{concept} — arco emotivo di un concept
"""

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("pip install fastapi uvicorn")

import os
import sys
import json
from pathlib import Path
from typing import Optional, List

sys.path.insert(0, os.path.dirname(__file__))

from mnheme        import MemoryDB
from llm_provider  import LLMProvider
from digital_twin  import (
    DigitalTwin, TwinProfile, TwinVault,
    AccessTier, ConsultationResult, LetterResult,
    LegacyResult, TimelineResult,
)

# ── Config ──────────────────────────────────────────────────
_DB_PATH        = os.environ.get("MNHEME_DB",        "mnheme.mnheme")
_ENV_PATH       = os.environ.get("MNHEME_ENV",       ".env")
_LLM_PROVIDER   = os.environ.get("TWIN_LLM_PROVIDER", None)

# Directory radice dei personaggi — struttura:
#   apps/twins/character/<nome>/<nome>-twin_profile.json
#                               <nome>.mnheme  (opzionale, link o copia del db)
#
# Priorità risoluzione:
#   1. TWIN_PROFILE     env var — path assoluto al json
#   2. TWIN_CHARACTER   env var — nome del personaggio (cerca in CHARACTERS_DIR)
#   3. <db_stem> come nome — cerca in CHARACTERS_DIR/<db_stem>/
#   4. Legacy fallback   — <db_stem>-twin_profile.json accanto al db
_CHARACTERS_DIR = Path(os.environ.get(
    "TWIN_CHARACTERS_DIR",
    str(Path(__file__).parent / "character")   # apps/twins/character/
))


def _character_dir(name: str) -> Path:
    """Ritorna apps/twins/character/<name>/ (slug sicuro per filesystem)."""
    import re
    slug = re.sub(r"[^\w\-]", "_", name.lower().strip()).strip("_") or "unknown"
    return _CHARACTERS_DIR / slug


def _resolve_profile_path() -> Path:
    """
    Risolve il path del profilo JSON nell'ordine:
    1. $TWIN_PROFILE          — path esplicito
    2. $TWIN_CHARACTER        — nome personaggio → cerca in character/<name>/
    3. stem del DB            — usa il nome del .mnheme come nome personaggio
    4. Legacy                 — <db_stem>-twin_profile.json accanto al db
    """
    # 1. Path esplicito
    if os.environ.get("TWIN_PROFILE"):
        return Path(os.environ["TWIN_PROFILE"])

    # 2. Nome personaggio esplicito
    char_name = os.environ.get("TWIN_CHARACTER", "").strip()
    if char_name:
        p = _character_dir(char_name) / f"{_slugify(char_name)}-twin_profile.json"
        if p.exists():
            return p
        # Anche se non esiste ancora, questo è il path target
        return p

    # 3. Usa il nome del database come nome personaggio
    db_stem = Path(_DB_PATH).stem
    auto    = _character_dir(db_stem) / f"{db_stem}-twin_profile.json"
    if auto.exists():
        return auto

    # 4. Legacy: accanto al db
    legacy = Path(_DB_PATH).parent / f"{db_stem}-twin_profile.json"
    if legacy.exists():
        return legacy

    # Default target per il prossimo setup
    return _character_dir(db_stem) / f"{db_stem}-twin_profile.json"


def _slugify(name: str) -> str:
    import re
    return re.sub(r"[^\w\-]", "_", name.lower().strip()).strip("_") or "unknown"


_TWIN_PROFILE_FILE = _resolve_profile_path()


def _make_llm() -> LLMProvider:
    """
    Costruisce il provider LLM rispettando questa priorità:
    1. Variabile d'ambiente TWIN_LLM_PROVIDER
    2. Variabile ACTIVE_PROVIDER nel file .env
    3. Primo provider disponibile nel .env
    """
    from llm_provider import load_env
    env    = load_env(_ENV_PATH)
    active = _LLM_PROVIDER or env.get("ACTIVE_PROVIDER") or None
    return LLMProvider.from_env(_ENV_PATH, active=active)


db    = MemoryDB(_DB_PATH)
_twin: Optional[DigitalTwin] = None


def _load_or_create_twin() -> Optional[DigitalTwin]:
    """
    Carica il twin dal profilo su disco.

    Cerca il file profilo in questo ordine:
    1. TWIN_PROFILE env var
    2. <db_name>.twin.json  accanto al database
    3. twin_profile.json nella cwd

    Stampa il path usato all'avvio per chiarezza.
    """
    profile_path = _resolve_profile_path()

    if not profile_path.exists():
        db_stem  = Path(_DB_PATH).stem
        char_name = os.environ.get("TWIN_CHARACTER", db_stem)
        char_dir  = _character_dir(char_name)
        print(
            f"[twin] Profilo non trovato.\n"
            f"  Struttura attesa: apps/twins/character/<nome>/<nome>-twin_profile.json\n"
            f"  Cercato in:\n"
            f"    1. $TWIN_PROFILE      = {os.environ.get('TWIN_PROFILE', '(non impostato)')}\n"
            f"    2. $TWIN_CHARACTER    → {char_dir / (db_stem + '-twin_profile.json')}\n"
            f"    3. {profile_path}\n"
            f"  Chiama POST /twin/setup per generarlo automaticamente dai ricordi."
        )
        return None

    try:
        data    = json.loads(profile_path.read_text("utf-8"))
        profile = TwinProfile(**data)
        llm     = _make_llm()
        twin    = DigitalTwin(db, llm, profile)
        print(
            f"[twin] Profilo caricato: {profile.name} "
            f"({profile.birth_year}–{profile.death_year or 'oggi'}) "
            f"← {profile_path}"
        )
        return twin
    except Exception as e:
        print(f"[twin] Errore caricamento profilo da {profile_path}: {e}")
        return None


def get_twin() -> DigitalTwin:
    global _twin
    if _twin is None:
        _twin = _load_or_create_twin()
    if _twin is None:
        raise HTTPException(
            503,
            detail="Twin non configurato. Chiama POST /twin/setup per inizializzare."
        )
    return _twin


# ── App ─────────────────────────────────────────────────────
app = FastAPI(
    title       = "MNHEME Digital Twin API",
    description = (
        "Interfaccia di consultazione del gemello digitale emotivo. "
        "Ogni risposta è basata esclusivamente sui ricordi reali registrati."
    ),
    version     = "1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = False,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
    expose_headers    = ["*"],
)

# Tenta di caricare il twin all'avvio
_twin = _load_or_create_twin()


# ═══════════════════════════════════════════════════════════════
# SCHEMI
# ═══════════════════════════════════════════════════════════════

class TwinSetupIn(BaseModel):
    """
    Tutti i campi sono opzionali — quelli non forniti vengono inferiti
    automaticamente analizzando i ricordi nel database via LLM.
    """
    name          : Optional[str]       = Field(None, example="Maria Rossi",
                                               description="Nome completo. Se omesso viene inferito dai ricordi.")
    birth_year    : Optional[int]       = Field(None, example=1942,
                                               description="Anno di nascita. Se omesso viene inferito dai timestamp.")
    death_year    : Optional[int]       = Field(None, example=2024,
                                               description="Anno di morte. None = persona ancora in vita.")
    language      : Optional[str]       = Field(None, example="italiano",
                                               description="Lingua delle risposte. Default: rilevata dai ricordi.")
    voice_notes   : Optional[str]       = Field(None, example="Parla in modo diretto, con humour sobrio.",
                                               description="Note sulla voce narrativa. Inferita se omessa.")
    values        : Optional[List[str]] = Field(None, example=["famiglia", "onestà"],
                                               description="Valori centrali. Inferiti dai ricordi se omessi.")
    embargo_years : int                 = Field(0,    example=2,
                                               description="Anni di embargo post-mortem per ricordi intimi.")
    epitaph       : Optional[str]       = Field(None, example="Ho vissuto come ho voluto.",
                                               description="Frase epitaffio. Generata se omessa.")
    curator_name  : str                 = Field("",   example="Luca Rossi",
                                               description="Nome del curatore del twin.")


class TwinProfileOut(BaseModel):
    name              : str            = "Sconosciuto"
    born              : Optional[int]  = None
    died              : Optional[int]  = None
    age_at_death      : Optional[int]  = None
    language          : str            = "italiano"
    total_memories    : int            = 0
    embargo_active    : bool           = False
    embargo_until     : Optional[int]  = None
    dominant_concepts : List[str]      = []
    emotional_map     : dict           = {}
    curator           : str            = ""
    epitaph           : str            = ""
    character_slug    : str            = ""
    character_dir     : str            = ""


class AskIn(BaseModel):
    question : str           = Field(..., example="Cosa ti ha insegnato la guerra?")
    tier     : str           = Field("family", example="family",
                                    description="public | family | intimate | full")
    language : Optional[str] = Field(None, example="italiano")


class AskOut(BaseModel):
    question       : str
    response       : str
    tier           : str
    confidence     : str
    caveat         : str
    memories_used  : int


class LetterIn(BaseModel):
    to       : str  = Field(..., example="mia figlia Elena")
    theme    : str  = Field(..., example="il coraggio e la paura")
    tier     : str  = Field("family", example="family")


class LetterOut(BaseModel):
    to            : str
    theme         : str
    text          : str
    memories_used : int


class LegacyOut(BaseModel):
    portrait          : str
    core_values       : str
    unresolved        : str
    message           : str
    dominant_concepts : List[str]
    emotional_arc     : str


class TimelineEntryOut(BaseModel):
    date    : str
    feeling : str
    concept : str
    excerpt : str
    tags    : List[str]


class TimelineOut(BaseModel):
    concept : str
    arc     : str
    entries : List[TimelineEntryOut]


class AccessibleMemoryOut(BaseModel):
    memory_id  : str
    concept    : str
    feeling    : str
    excerpt    : str
    timestamp  : str
    tags       : List[str]


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════


def _infer_profile_from_db(llm, overrides: dict) -> dict:
    """
    Analizza il database dei ricordi e inferisce via LLM i campi del profilo
    non forniti esplicitamente dall'utente.

    overrides: dizionario con i campi già forniti dall'utente (non vengono sovrascritti).
    Ritorna un dizionario completo con tutti i campi del profilo.
    """
    import re as _re

    memories    = db.recall_all(limit=60)
    total       = db.count()
    concepts    = db.list_concepts()
    feelings    = db.feeling_distribution()
    timestamps  = sorted([m.timestamp[:10] for m in memories if m.timestamp])

    if not memories:
        raise ValueError("Database vuoto — impossibile inferire il profilo.")

    # Campione ricordi per il prompt
    sample_lines = []
    for m in memories[:25]:
        mt = getattr(m, "media_type", "text") or "text"
        content_preview = (
            f"[{mt.upper()}]" if mt != "text" and len(m.content) > 100
            else m.content[:120]
        )
        sample_lines.append(
            f"  [{m.timestamp[:10]}] {m.concept} / {m.feeling}: {content_preview}"
        )
    sample = "\n".join(sample_lines)

    top_concepts = ", ".join(c["concept"] for c in sorted(
        concepts, key=lambda x: x["total"], reverse=True
    )[:10])
    feel_dist = "  ".join(
        f"{f}({n})" for f, n in
        sorted(feelings.items(), key=lambda x: -x[1])[:8]
    )
    date_range = f"{timestamps[0]} → {timestamps[-1]}" if timestamps else "sconosciuto"

    # Determina quali campi inferire
    need = [
        f for f in ["name","birth_year","language","voice_notes","values","epitaph"]
        if f not in overrides or overrides[f] is None
    ]
    if not need:
        return overrides  # tutto già fornito

    need_str = ", ".join(need)

    system = (
        "Sei un analista di memorie autobiografiche. "
        "Deduci informazioni biografiche SOLO dai ricordi forniti. "
        "Rispondi SOLO con JSON valido, nessun testo extra."
    )

    prompt = (
        f"Analizza questi {total} ricordi personali e inferisci i campi richiesti.\n\n"
        f"STATISTICHE:\n"
        f"  Arco temporale: {date_range}\n"
        f"  Concetti dominanti: {top_concepts}\n"
        f"  Distribuzione emotiva: {feel_dist}\n\n"
        f"CAMPIONE RICORDI:\n{sample}\n\n"
        f"CAMPI DA INFERIRE: {need_str}\n\n"
        f"Produci un JSON con SOLO i campi richiesti:\n"
        f"{{\n"
        f'  "name": "Nome Cognome (es. da come la persona parla di se stessa, o generico ''Persona sconosciuta'')",\n'
        f'  "birth_year": anno intero (stima da timestamp più vecchio e contesto),\n'
        f'  "language": "lingua dei ricordi (es. italiano, english)",\n'
        f'  "voice_notes": "Come parla questa persona — tono, stile, modi di dire caratteristici (2-3 frasi)",\n'
        f'  "values": ["valore1", "valore2", "valore3"] (max 5, dai ricordi reali),\n'
        f'  "epitaph": "Una frase che cattura l\'essenza di questa vita (breve, non retorica)"\n'
        f"}}\n\n"
        f"Includi SOLO i campi in: {need_str}. "
        f"Non inventare — se non riesci a inferire un campo usa null."
    )

    try:
        raw  = llm.complete(system, prompt, temperature=0.3)
        # Parse JSON
        raw  = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(
                l for l in raw.splitlines() if not l.strip().startswith("```")
            ).strip()
        inferred = json.loads(raw)
    except Exception as e:
        print(f"[twin] Inferenza LLM fallita ({e}), uso defaults")
        inferred = {}

    # Stima birth_year dai timestamp se LLM non riesce
    if "birth_year" in need and not inferred.get("birth_year"):
        if timestamps:
            oldest_year = int(timestamps[0][:4])
            # Assume prima memoria ~ 5-10 anni di età
            inferred["birth_year"] = oldest_year - 7
        else:
            inferred["birth_year"] = 1970

    # Merge: overrides hanno precedenza su inferiti
    result = dict(inferred)
    result.update({k: v for k, v in overrides.items() if v is not None})

    # Defaults finali per campi ancora mancanti
    result.setdefault("name",        "Persona sconosciuta")
    result.setdefault("birth_year",  1970)
    result.setdefault("death_year",  None)
    result.setdefault("language",    "italiano")
    result.setdefault("voice_notes", "")
    result.setdefault("values",      [])
    result.setdefault("epitaph",     "")
    result.setdefault("embargo_years", overrides.get("embargo_years", 0))
    result.setdefault("curator_name",  overrides.get("curator_name", ""))

    # Normalizza values: deve essere lista di stringhe
    if isinstance(result.get("values"), str):
        result["values"] = [v.strip() for v in result["values"].split(",") if v.strip()]

    return result


@app.post(
    "/twin/setup",
    summary     = "Configura il profilo del Digital Twin",
    description = (
        "Crea o aggiorna il profilo della persona. "
        "Il profilo viene salvato su disco e persiste tra i riavvii."
    ),
)
def setup_twin(body: TwinSetupIn):
    """
    Configura il Digital Twin.

    I campi non forniti vengono inferiti automaticamente analizzando
    i ricordi nel database via LLM. Il profilo viene salvato come:
        <nome_db>-twin_profile.json
    nella stessa directory del database.
    """
    global _twin
    try:
        llm = _make_llm()

        # Raccoglie i campi esplicitamente forniti dall'utente
        explicit = {
            k: v for k, v in body.dict().items()
            if v is not None and v != "" and v != [] and v != 0
        }
        # embargo_years e curator_name passano sempre anche se 0/""
        explicit["embargo_years"] = body.embargo_years
        explicit["curator_name"]  = body.curator_name

        # Inferisce i campi mancanti dai ricordi
        print(f"[twin] Analisi database ({db.count()} ricordi) per inferire profilo…")
        inferred = _infer_profile_from_db(llm, explicit)

        profile = TwinProfile(
            name          = inferred["name"],
            birth_year    = int(inferred["birth_year"]),
            death_year    = inferred.get("death_year") or body.death_year,
            language      = inferred["language"],
            voice_notes   = inferred["voice_notes"],
            values        = inferred["values"] or [],
            embargo_years = inferred["embargo_years"],
            epitaph       = inferred["epitaph"],
            curator_name  = inferred["curator_name"],
        )
        _twin = DigitalTwin(db, llm, profile)

        # Salva il profilo in apps/twins/character/<nome>/<nome>-twin_profile.json
        char_name = _slugify(profile.name)
        char_dir  = _character_dir(profile.name)
        char_dir.mkdir(parents=True, exist_ok=True)
        save_path = char_dir / f"{char_name}-twin_profile.json"
        save_path.write_text(
            json.dumps(inferred, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"[twin] Profilo salvato → {save_path}")
        print(f"[twin] Cartella personaggio: {char_dir}")

        # Aggiorna le env var per i prossimi avvii
        os.environ["TWIN_PROFILE"]   = str(save_path)
        os.environ["TWIN_CHARACTER"] = char_name

        return {
            "status"       : "ok",
            "twin"         : profile.name,
            "birth_year"   : profile.birth_year,
            "death_year"   : profile.death_year,
            "language"     : profile.language,
            "voice_notes"  : profile.voice_notes,
            "values"       : profile.values,
            "epitaph"      : profile.epitaph,
            "memories"     : db.count(),
            "profile_file" : str(save_path),
            "inferred_fields": [
                k for k in ["name","birth_year","language","voice_notes","values","epitaph"]
                if k not in {kk for kk, vv in body.dict().items()
                             if vv is not None and vv != "" and vv != []}
            ],
            "message": f"Twin '{profile.name}' configurato con {db.count()} ricordi.",
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get(
    "/twin/profile",
    response_model = TwinProfileOut,
    summary        = "Stato e identità del Digital Twin",
)
def get_profile():
    twin = get_twin()
    s    = twin.profile_summary()
    char_name = os.environ.get("TWIN_CHARACTER", Path(_DB_PATH).stem)
    char_slug = _slugify(char_name)
    char_dir  = _character_dir(char_name)
    return TwinProfileOut(
        name              = s.get("name")              or "Sconosciuto",
        born              = s.get("born"),
        died              = s.get("died"),
        age_at_death      = s.get("age_at_death"),
        language          = s.get("language")          or "italiano",
        total_memories    = s.get("total_memories")    or 0,
        embargo_active    = s.get("embargo_active")    or False,
        embargo_until     = s.get("embargo_until"),
        dominant_concepts = s.get("dominant_concepts") or [],
        emotional_map     = s.get("emotional_map")     or {},
        curator           = s.get("curator")           or "",
        epitaph           = s.get("epitaph")           or "",
        character_slug    = char_slug,
        character_dir     = str(char_dir),
    )


@app.post(
    "/twin/ask",
    response_model = AskOut,
    summary        = "Poni una domanda al Digital Twin",
    description    = (
        "Il twin risponde in prima persona basandosi esclusivamente "
        "sui ricordi reali registrati. Non inventa mai. "
        "Se i ricordi non bastano, lo dichiara esplicitamente."
    ),
)
def ask_twin(body: AskIn):
    twin = get_twin()
    try:
        tier = AccessTier(body.tier)
    except ValueError:
        raise HTTPException(400, detail=f"Tier non valido: {body.tier}. Usa: public, family, intimate, full")
    try:
        r = twin.ask(body.question, tier=tier, language=body.language)
        return AskOut(
            question      = r.question,
            response      = r.response,
            tier          = r.tier.value,
            confidence    = r.confidence,
            caveat        = r.caveat,
            memories_used = len(r.memories_used),
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post(
    "/twin/letter",
    response_model = LetterOut,
    summary        = "Genera una lettera scritta dal Twin",
    description    = (
        "Produce una lettera personale ancorata ai ricordi reali. "
        "Ogni frase riflette qualcosa che la persona ha davvero vissuto."
    ),
)
def generate_letter(body: LetterIn):
    twin = get_twin()
    try:
        tier = AccessTier(body.tier)
    except ValueError:
        raise HTTPException(400, detail=f"Tier non valido: {body.tier}")
    try:
        r = twin.letter(body.to, body.theme, tier=tier)
        return LetterOut(
            to           = r.to,
            theme        = r.theme,
            text         = r.text,
            memories_used= len(r.memories_used),
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get(
    "/twin/legacy",
    response_model = LegacyOut,
    summary        = "Eredità emotiva completa",
    description    = (
        "Analizza l'intera memoria e produce il ritratto definitivo: "
        "chi era questa persona, cosa ha vissuto, cosa lascia."
    ),
)
def get_legacy(tier: str = Query("family")):
    twin = get_twin()
    try:
        access_tier = AccessTier(tier)
    except ValueError:
        raise HTTPException(400, detail=f"Tier non valido: {tier}")
    try:
        r = twin.legacy(tier=access_tier)
        return LegacyOut(
            portrait          = r.portrait,
            core_values       = r.core_values,
            unresolved        = r.unresolved,
            message           = r.message,
            dominant_concepts = r.dominant_concepts,
            emotional_arc     = r.emotional_arc,
        )
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get(
    "/twin/timeline/{concept}",
    response_model = TimelineOut,
    summary        = "Arco emotivo di un concept nel tempo",
)
def get_timeline(
    concept : str,
    tier    : str = Query("family"),
):
    twin = get_twin()
    try:
        access_tier = AccessTier(tier)
    except ValueError:
        raise HTTPException(400, detail=f"Tier non valido: {tier}")
    try:
        r = twin.timeline(concept, tier=access_tier)
        return TimelineOut(
            concept = r.concept,
            arc     = r.arc,
            entries = [TimelineEntryOut(**e) for e in r.entries],
        )
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get(
    "/twin/memories",
    response_model = List[AccessibleMemoryOut],
    summary        = "Ricordi accessibili per tier",
)
def get_accessible_memories(
    tier    : str           = Query("family"),
    concept : Optional[str] = Query(None),
    limit   : int           = Query(20),
):
    twin = get_twin()
    try:
        access_tier = AccessTier(tier)
    except ValueError:
        raise HTTPException(400, detail=f"Tier non valido: {tier}")

    memories = twin._vault.recall_accessible(access_tier, concept=concept, limit=limit)
    return [
        AccessibleMemoryOut(
            memory_id = m.memory_id,
            concept   = m.concept,
            feeling   = m.feeling,
            excerpt   = m.content[:150] + ("…" if len(m.content) > 150 else ""),
            timestamp = m.timestamp,
            tags      = list(m.tags),
        )
        for m in memories
    ]


@app.get(
    "/twin/characters",
    summary = "Lista dei personaggi disponibili in apps/twins/character/",
    description = (
        "Scansiona la directory character/ e ritorna tutti i personaggi "
        "con profilo configurato. Usato dalla UI per il selettore personaggio."
    ),
)
def get_characters():
    """
    Ritorna la lista dei personaggi in TWIN_CHARACTERS_DIR.
    Ogni entry ha: slug, name, birth_year, death_year, active (= personaggio corrente).
    """
    chars = []
    current_slug = _slugify(
        os.environ.get("TWIN_CHARACTER", Path(_DB_PATH).stem)
    )

    if not _CHARACTERS_DIR.exists():
        return {"characters": [], "directory": str(_CHARACTERS_DIR)}

    for subdir in sorted(_CHARACTERS_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        # Cerca il profilo JSON nella cartella
        profile_files = list(subdir.glob("*-twin_profile.json"))
        if not profile_files:
            continue
        try:
            data = json.loads(profile_files[0].read_text("utf-8"))
            chars.append({
                "slug"       : subdir.name,
                "name"       : data.get("name") or subdir.name,
                "birth_year" : data.get("birth_year"),
                "death_year" : data.get("death_year"),
                "language"   : data.get("language", "italiano"),
                "epitaph"    : data.get("epitaph", ""),
                "profile_file": str(profile_files[0]),
                "active"     : subdir.name == current_slug,
            })
        except Exception:
            continue

    return {
        "characters": chars,
        "directory" : str(_CHARACTERS_DIR),
        "current"   : current_slug,
    }


@app.get(
    "/twin/stats",
    summary = "Statistiche della memoria del twin per tier",
)
def get_stats(tier: str = Query("family")):
    twin = get_twin()
    try:
        access_tier = AccessTier(tier)
    except ValueError:
        raise HTTPException(400, detail=f"Tier non valido: {tier}")
    return twin._vault.stats(access_tier)


@app.get(
    "/twin/characters",
    summary = "Lista dei personaggi disponibili nella cartella character/",
)
def list_characters():
    """
    Scansiona TWIN_CHARACTERS_DIR e ritorna tutti i personaggi
    che hanno un file *-twin_profile.json nella loro cartella.
    """
    chars = []
    if not _CHARACTERS_DIR.exists():
        return {"characters": [], "directory": str(_CHARACTERS_DIR)}

    for char_dir in sorted(_CHARACTERS_DIR.iterdir()):
        if not char_dir.is_dir():
            continue
        # Cerca il profilo JSON nella cartella
        profiles = list(char_dir.glob("*-twin_profile.json"))
        if not profiles:
            continue
        profile_path = profiles[0]
        try:
            data = json.loads(profile_path.read_text("utf-8"))
            chars.append({
                "slug"        : char_dir.name,
                "name"        : data.get("name") or char_dir.name,
                "birth_year"  : data.get("birth_year"),
                "death_year"  : data.get("death_year"),
                "language"    : data.get("language", "italiano"),
                "epitaph"     : data.get("epitaph", ""),
                "profile_file": str(profile_path),
                "active"      : (
                    char_dir.name == _slugify(
                        os.environ.get("TWIN_CHARACTER", Path(_DB_PATH).stem)
                    )
                ),
            })
        except Exception:
            continue

    return {
        "characters": chars,
        "directory" : str(_CHARACTERS_DIR),
        "active"    : os.environ.get("TWIN_CHARACTER", Path(_DB_PATH).stem),
    }