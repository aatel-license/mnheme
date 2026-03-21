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
            llm    = LLMProvider.from_env(".env", active="lm-studio")
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
    concept    : str           = Field(...,  example="Debito")
    feeling    : str           = Field(...,  example="ansia")
    content    : str           = Field(...,  example="Ho firmato il mutuo oggi.")
    media_type : str           = Field("text", example="text")
    note       : Optional[str] = Field("",  example="Era un mercoledì piovoso")
    tags       : List[str]     = Field(default_factory=list, example=["casa","2024"])

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
    raw_input  : str            = Field(...,   example="Ho aperto la busta dalla banca. Le mani tremavano.")
    concept    : Optional[str] = Field(None,  example="Debito")
    feeling    : Optional[str] = Field(None,  example="paura")
    tags       : List[str]     = Field(default_factory=list)
    note       : str           = Field("",    example="Appunto manuale")
    # Campi vision/media — opzionali
    media_type : str           = Field("text", example="image",
                                       description="text | image | video | audio | doc")
    media_data : Optional[str] = Field(None,
                                       description="Data URL completo (data:mime;base64,...) "
                                                   "oppure base64 puro del file allegato")
    media_mime : Optional[str] = Field(None,  example="image/jpeg",
                                       description="MIME type del file (obbligatorio se media_data presente)")

class PerceiveOut(BaseModel):
    memory_id         : str
    extracted_concept : str
    extracted_feeling : str
    extracted_tags    : List[str]
    enriched_content  : str
    raw_input         : str

class AskIn(BaseModel):
    question     : str           = Field(..., example="Come mi sento rispetto al denaro?")
    max_memories : int           = Field(15,  example=15)
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
    concept : Optional[str] = Field(None,       example="Famiglia")
    feeling : Optional[str] = Field(None,       example="amore")
    style   : str           = Field("narrativo", example="narrativo")
    limit   : int           = Field(20,          example=20)

class BrainStatusOut(BaseModel):
    available     : bool
    provider      : Optional[str]
    model         : Optional[str]
    total_memories: int


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
            note       = body.note,
            media_type = body.media_type or "text",
            media_data = body.media_data or None,
            media_mime = body.media_mime or None,
        )
        return PerceiveOut(
            memory_id         = r.memory.memory_id,
            extracted_concept = r.extracted_concept,
            extracted_feeling = r.extracted_feeling,
            extracted_tags    = r.extracted_tags,
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
