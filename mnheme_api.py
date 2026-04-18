"""
mnheme_api.py — REST API con FastAPI
=====================================
Avvia con:
    pip install fastapi uvicorn
    uvicorn mnheme_api:app --reload --port 8000

Documentazione interattiva: http://localhost:8000/docs

Endpoint Brain richiedono un .env con almeno un provider LLM configurato.
"""

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("Installa FastAPI: pip install fastapi uvicorn")

from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from typing import Optional, List
from mnheme       import MemoryDB, Feeling, MediaType, MnhemeError
from llm_provider import LLMProvider
from brain        import Brain

db = MemoryDB("mnheme.mnheme")

# Brain — opzionale: attivo solo se .env è configurato
_brain: Optional[Brain] = None

def get_brain() -> Brain:
    global _brain
    if _brain is None:
        try:
            llm    = LLMProvider.from_env(str(Path(__file__).parent / ".env"), active="lm-studio")
            _brain = Brain(db, llm)
        except Exception as e:
            raise HTTPException(503, detail=f"Brain non disponibile: {e}. Configura .env con almeno un provider LLM.")
    return _brain

app = FastAPI(
    title="MNHEME API",
    description="Database di ricordi umani — append-only, immutabile, senziente.",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST"], allow_headers=["*"])

# ── Schemi DB ────────────────────────────────────

class MemoryIn(BaseModel):
    concept    : str           = Field(..., json_schema_extra={"example": "Debito"})
    feeling    : str           = Field(..., json_schema_extra={"example": "ansia"})
    content    : str           = Field(..., json_schema_extra={"example": "Ho firmato il mutuo oggi."})
    media_type : str           = Field("text", json_schema_extra={"example": "text"})
    note       : Optional[str] = Field("",  json_schema_extra={"example": "Era un mercoledì piovoso"})
    tags       : List[str]     = Field(default_factory=list, json_schema_extra={"example": ["casa","2024"]})

class MemoryOut(BaseModel):
    memory_id  : str
    concept    : str
    feeling    : str
    media_type : str
    content    : str
    note       : str
    tags       : List[str]
    timestamp  : str
    checksum   : str

def _out(m) -> MemoryOut:
    d = m.to_dict()
    return MemoryOut(**d)

# ── Endpoints ───────────────────────────────────

@app.post("/memories", response_model=MemoryOut, status_code=201,
          summary="Registra un nuovo ricordo (append-only)")
def create_memory(body: MemoryIn):
    try:
        m = db.remember(
            concept=body.concept, feeling=body.feeling,
            content=body.content, media_type=body.media_type,
            note=body.note or "", tags=body.tags,
        )
        return _out(m)
    except MnhemeError as e:
        raise HTTPException(400, detail=str(e))


@app.get("/memories", response_model=List[MemoryOut],
         summary="Tutti i ricordi (filtri opzionali)")
def get_all(
    feeling      : Optional[str] = Query(None),
    limit        : Optional[int] = Query(None),
    oldest_first : bool          = Query(False),
):
    if feeling:
        return [_out(m) for m in db.recall_by_feeling(feeling, limit=limit, oldest_first=oldest_first)]
    return [_out(m) for m in db.recall_all(limit=limit, oldest_first=oldest_first)]


@app.get("/memories/search", response_model=List[MemoryOut],
         summary="Ricerca full-text")
def search(q: str = Query(...), limit: Optional[int] = Query(None)):
    return [_out(m) for m in db.search(q, limit=limit)]


@app.get("/memories/by-tag/{tag}", response_model=List[MemoryOut],
         summary="Ricordi per tag")
def by_tag(tag: str, limit: Optional[int] = Query(None)):
    return [_out(m) for m in db.recall_by_tag(tag, limit=limit)]


@app.get("/concepts", summary="Tutti i concetti con statistiche")
def get_concepts():
    return db.list_concepts()


@app.get("/concepts/{concept}", response_model=List[MemoryOut],
         summary="Ricordi di un concetto")
def get_by_concept(
    concept      : str,
    feeling      : Optional[str] = Query(None),
    limit        : Optional[int] = Query(None),
    oldest_first : bool          = Query(False),
):
    try:
        return [_out(m) for m in db.recall(concept, feeling=feeling, limit=limit, oldest_first=oldest_first)]
    except MnhemeError as e:
        raise HTTPException(400, detail=str(e))


@app.get("/concepts/{concept}/timeline",
         summary="Cronologia emotiva di un concetto")
def get_timeline(concept: str):
    return db.concept_timeline(concept)


@app.get("/feelings", summary="Sentimenti con statistiche")
def get_feelings():
    return db.list_feelings()


@app.get("/feelings/distribution", summary="sentimento → count")
def get_distribution():
    return db.feeling_distribution()


@app.get("/stats", summary="Statistiche generali del database")
def get_stats():
    return {
        "total_memories": db.count(),
        "concepts":       len(db.list_concepts()),
        "feelings_used":  len(db.feeling_distribution()),
        "distribution":   db.feeling_distribution(),
        "storage":        db.storage_info(),
    }


@app.get("/export", summary="Esporta ricordi in JSON")
def export(
    concept         : Optional[str] = Query(None),
    feeling         : Optional[str] = Query(None),
    include_content : bool          = Query(True),
):
    return db.export_json(concept=concept, feeling=feeling, include_content=include_content)


# ── Schemi Brain ─────────────────────────────────

class PerceiveIn(BaseModel):
    raw_input  : str            = Field(...,   json_schema_extra={"example": "Ho aperto la busta dalla banca. Le mani tremavano."})
    concept    : Optional[str] = Field(None,  json_schema_extra={"example": "Debito"})
    feeling    : Optional[str] = Field(None,  json_schema_extra={"example": "paura"})
    tags       : List[str]     = Field(default_factory=list)
    note       : str           = Field("",    json_schema_extra={"example": "Appunto manuale"})
    # Campi vision/media — opzionali
    media_type : str           = Field("text", json_schema_extra={"example": "image"},
                                        description="text | image | video | audio | doc")
    media_data : Optional[str] = Field(None,
                                       description="Data URL completo (data:mime;base64,...) "
                                                   "oppure base64 puro del file allegato")
    media_mime : Optional[str] = Field(None,  json_schema_extra={"example": "image/jpeg"},
                                        description="MIME type del file (obbligatorio se media_data presente)")

class PerceiveOut(BaseModel):
    memory_id         : str
    extracted_concept : str
    extracted_feeling : str
    extracted_tags    : List[str]
    extracted_note    : str
    enriched_content  : str
    raw_input         : str

class AskIn(BaseModel):
    question     : str           = Field(..., json_schema_extra={"example": "Come mi sento rispetto al denaro?"})
    max_memories : int           = Field(15,  json_schema_extra={"example": 15})
    concepts     : Optional[List[str]] = Field(None)

class AskOut(BaseModel):
    question        : str
    answer          : str
    memories_used   : int
    provider_used   : str
    confidence_note : str

class ReflectOut(BaseModel):
    concept    : str
    reflection : str
    arc        : str
    memories   : int

class DreamOut(BaseModel):
    connections  : str
    provider_used: str
    memories     : int

class IntrospectOut(BaseModel):
    portrait          : str
    dominant_concepts : List[str]
    emotional_map     : dict
    total_memories    : int
    provider_used     : str

class SummarizeIn(BaseModel):
    concept : Optional[str] = Field(None,       json_schema_extra={"example": "Famiglia"})
    feeling : Optional[str] = Field(None,       json_schema_extra={"example": "amore"})
    style   : str           = Field("narrativo", json_schema_extra={"example": "narrativo"})
    limit   : int           = Field(20,          json_schema_extra={"example": 20})

class BrainStatusOut(BaseModel):
    available     : bool
    provider      : Optional[str]
    model         : Optional[str]
    total_memories: int

# ── Schemi Brain — Persona, Will, Choose ────────

class PersonaOut(BaseModel):
    core_traits     : List[str]
    values          : List[str]
    fears           : List[str]
    desires         : List[str]
    voice           : str
    worldview       : str
    persona_summary : str
    provider_used   : str

class WillIn(BaseModel):
    seed_feeling : Optional[str] = Field(
        None,
        json_schema_extra={"example": "rabbia"},
        description="Se fornito, campiona ricordi da questo sentimento specifico",
    )
    n_memories   : int = Field(
        10,
        json_schema_extra={"example": 10},
        description="Numero di ricordi usati come substrato dell'impulso",
    )

class WillOut(BaseModel):
    impulse       : str
    impulse_type  : str
    action        : str
    why           : str
    memories_used : int
    provider_used : str

class ChooseIn(BaseModel):
    options      : List[str] = Field(
        ...,
        min_length=2,
        json_schema_extra={"example": ["restare", "partire", "aspettare"]},
        description="Le opzioni tra cui scegliere (minimo 2)",
    )
    context      : str = Field(
        "",
        json_schema_extra={"example": "Devo decidere se lasciare il lavoro attuale"},
        description="Contesto opzionale che orienta la scelta",
    )
    max_memories : int = Field(
        12,
        json_schema_extra={"example": 12},
        description="Numero massimo di ricordi usati per la scelta",
    )

class ChooseOut(BaseModel):
    chosen           : str
    rejected         : List[str]
    reasoning        : str
    emotional_driver : str
    certainty        : str
    memories_used    : int
    provider_used    : str


# ── Brain endpoints ──────────────────────────────

@app.get("/brain/status", response_model=BrainStatusOut,
         summary="Verifica se il Brain LLM è disponibile")
def brain_status():
    try:
        b = get_brain()
        p = b._llm.active_profile
        return BrainStatusOut(
            available      = True,
            provider       = p.name,
            model          = p.model,
            total_memories = db.count(),
        )
    except HTTPException:
        return BrainStatusOut(available=False, provider=None, model=None, total_memories=db.count())


@app.post("/brain/perceive", response_model=PerceiveOut, status_code=201,
          summary="Percepisci un input grezzo — LLM estrae concept, feeling, tags e arricchisce. "
                  "Supporta media vision: invia media_data (data URL base64) e media_mime per image/doc.")
def brain_perceive(body: PerceiveIn):
    b = get_brain()
    try:
        r = b.perceive(
            body.raw_input,
            concept    = body.concept    or None,
            feeling    = body.feeling    or None,
            tags       = body.tags       or None,
            note       = body.note       or None,
            media_type = body.media_type or "text",
            media_data = body.media_data or None,
            media_mime = body.media_mime or None,
        )
        return PerceiveOut(
            memory_id         = r.memory.memory_id,
            extracted_concept = r.extracted_concept,
            extracted_feeling = r.extracted_feeling,
            extracted_tags    = r.extracted_tags,
            extracted_note     = r.extracted_note,
            enriched_content  = r.enriched_content,
            raw_input         = r.raw_input,
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/brain/ask", response_model=AskOut,
          summary="RAG su memoria personale — risponde usando solo i ricordi reali")
def brain_ask(body: AskIn):
    b = get_brain()
    try:
        r = b.ask(body.question, max_memories=body.max_memories, concepts=body.concepts)
        return AskOut(
            question        = r.question,
            answer          = r.answer,
            memories_used   = len(r.memories_used),
            provider_used   = r.provider_used,
            confidence_note = r.confidence_note,
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/brain/reflect/{concept}", response_model=ReflectOut,
         summary="Analisi emotiva di un concetto nel tempo")
def brain_reflect(concept: str):
    b = get_brain()
    try:
        r = b.reflect(concept)
        return ReflectOut(
            concept    = r.concept,
            reflection = r.reflection,
            arc        = r.arc,
            memories   = len(r.memories),
        )
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/brain/dream", response_model=DreamOut,
         summary="Associazione libera — connessioni inattese tra ricordi distanti")
def brain_dream(n_memories: int = Query(8, ge=2, le=30)):
    b = get_brain()
    try:
        r = b.dream(n_memories=n_memories)
        return DreamOut(
            connections   = r.connections,
            provider_used = r.provider_used,
            memories      = len(r.memories),
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/brain/introspect", response_model=IntrospectOut,
         summary="Ritratto psicologico completo basato su tutti i ricordi")
def brain_introspect():
    b = get_brain()
    try:
        r = b.introspect()
        return IntrospectOut(
            portrait          = r.portrait,
            dominant_concepts = r.dominant_concepts,
            emotional_map     = r.emotional_map,
            total_memories    = r.total_memories,
            provider_used     = r.provider_used,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/brain/summarize",
          summary="Riassume un gruppo di ricordi — narrativo, analitico o poetico")
def brain_summarize(body: SummarizeIn):
    b = get_brain()
    try:
        if body.concept:
            memories = db.recall(body.concept, feeling=body.feeling, limit=body.limit)
        elif body.feeling:
            memories = db.recall_by_feeling(body.feeling, limit=body.limit)
        else:
            memories = db.recall_all(limit=body.limit)
        text = b.summarize(memories, style=body.style)
        return {"text": text, "memories_used": len(memories), "style": body.style}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/brain/persona", response_model=PersonaOut,
         summary="Identità psicologica stabile — tratti, valori, paure, desideri, visione del mondo")
def brain_persona():
    """
    Costruisce un profilo identitario strutturato dall'intera storia di ricordi.
    Diverso da /brain/introspect: non è narrativo, è un profilo persistente
    riusabile come contesto per will e choose.
    """
    b = get_brain()
    try:
        r = b.persona()
        return PersonaOut(
            core_traits     = r.core_traits,
            values          = r.values,
            fears           = r.fears,
            desires         = r.desires,
            voice           = r.voice,
            worldview       = r.worldview,
            persona_summary = r.persona_summary,
            provider_used   = r.provider_used,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/brain/will", response_model=WillOut,
          summary="Libero arbitrio — impulso spontaneo generato dallo stato interno della memoria")
def brain_will(body: WillIn):
    """
    Il cervello attinge ai propri ricordi e genera un impulso autonomo:
    cosa vuole, teme, rimpiange o rifiuta — senza stimolo esterno.

    Parametri opzionali:
    - `seed_feeling`: forza il campionamento da un sentimento specifico
    - `n_memories`: quanti ricordi usare come substrato
    """
    b = get_brain()
    try:
        r = b.will(
            seed_feeling = body.seed_feeling or None,
            n_memories   = body.n_memories,
        )
        return WillOut(
            impulse       = r.impulse,
            impulse_type  = r.impulse_type,
            action        = r.action,
            why           = r.why,
            memories_used = len(r.origin_memories),
            provider_used = r.provider_used,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/brain/choose", response_model=ChooseOut,
          summary="Scelta guidata dalla personalità — decide tra opzioni usando il peso emotivo dei ricordi")
def brain_choose(body: ChooseIn):
    """
    Sceglie tra le opzioni fornite come farebbe una mente umana reale:
    - recency bias (ricordi recenti pesano di più)
    - peak feeling (emozioni rare e intense valgono di più)
    - congruenza emotiva con il contesto
    - rumore stocastico (stessa situazione, esito leggermente diverso)

    Minimo 2 opzioni richieste.
    """
    b = get_brain()
    if len(body.options) < 2:
        raise HTTPException(400, detail="Servono almeno 2 opzioni.")
    try:
        r = b.choose(
            options      = body.options,
            context      = body.context,
            max_memories = body.max_memories,
        )
        return ChooseOut(
            chosen           = r.chosen,
            rejected         = r.rejected,
            reasoning        = r.reasoning,
            emotional_driver = r.emotional_driver,
            certainty        = r.certainty,
            memories_used    = len(r.memories_invoked),
            provider_used    = r.provider_used,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


def main():
    import uvicorn
    uvicorn.run(
        "mnheme_api:app",
        host="0.0.0.0",
        port=8123,
        reload=True
    )

if __name__ == "__main__":
    main()