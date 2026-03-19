"""
mnheme_api.py — REST API con FastAPI
=====================================
Avvia con:
    pip install fastapi uvicorn
    uvicorn mnheme_api:app --reload --port 8000

Documentazione interattiva: http://localhost:8000/docs
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
from mnheme import MemoryDB, Feeling, MediaType, MnhemeError

db = MemoryDB("mnheme.mnheme")

app = FastAPI(
    title="MNHEME API",
    description="Database di ricordi umani — append-only, immutabile, senziente.",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST"], allow_headers=["*"])

# ── Schemi ──────────────────────────────────────

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
