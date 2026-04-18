"""
mnheme_mcp.py
=============
MCP Server per MNHĒMĒ — Human Memory Database

Espone MemoryDB e Brain come tool MCP.
Qualsiasi LLM compatibile MCP (Claude, LM Studio, Cursor, Zed, ecc.)
può usare questo server come layer di memoria persistente.

Trasporto: stdio (default) o SSE via --sse flag

Avvio
-----
    # stdio (per Claude Desktop, LM Studio, Cursor, ecc.)
    python mnheme_mcp.py

    # SSE (per connessioni HTTP remote)
    python mnheme_mcp.py --sse --port 8765

Configurazione via .env (stesso file di MNHĒMĒ):
    MNHEME_DB_PATH=mente.mnheme      # path del database
    MNHEME_FILES_DIR=mente_files/    # dir file multimediali (opzionale)
    BRAIN_ENABLED=true               # attiva il layer Brain/LLM
    (+ tutti i provider LLM esistenti)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# ── Dipendenza MCP ────────────────────────────────────────────────────────────
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError:
    print(
        "[mnheme_mcp] ERRORE: 'mcp' non installato.\n"
        "  pip install mcp",
        file=sys.stderr,
    )
    sys.exit(1)

# ── Carica .env (senza dipendenze esterne) ────────────────────────────────────
def _load_env(path: str = ".env") -> None:
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

_load_env(str(Path(__file__).parent / ".env"))
# ── Config ────────────────────────────────────────────────────────────────────
DB_PATH   = os.environ.get("MNHEME_DB_PATH", "mnheme.mnheme")
FILES_DIR = os.environ.get("MNHEME_FILES_DIR", None)
BRAIN_ON  = os.environ.get("BRAIN_ENABLED", "true").lower() in ("true", "1", "yes")

# ── Init MNHĒMĒ ───────────────────────────────────────────────────────────────
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from mnheme import MemoryDB, Feeling, MediaType, MnhemeError
except ImportError as e:
    import traceback
    print(f"[mnheme_mcp] Brain non disponibile: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    print(
        f"[mnheme_mcp] ERRORE: impossibile importare mnheme — {e}\n"
        "  Assicurati che mnheme_mcp.py sia nella stessa directory del repo.",
        file=sys.stderr,
    )
    sys.exit(1)

db = MemoryDB(DB_PATH, files_dir=FILES_DIR)

brain = None
if BRAIN_ON:
    try:
        from llm_provider import LLMProvider
        from brain import Brain
        llm = LLMProvider.from_env(Path(__file__).parent / ".env")
        brain = Brain(db, llm)
    except Exception as e:
        print(f"[mnheme_mcp] Brain non disponibile: {e}", file=sys.stderr)

# ── Helpers ───────────────────────────────────────────────────────────────────
VALID_FEELINGS = [f.value for f in Feeling]
VALID_MEDIA    = [m.value for m in MediaType]

def _ok(data: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]

def _err(msg: str) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps({"error": msg}, ensure_ascii=False))]

def _memory_dict(m) -> dict:
    return {
        "memory_id": m.memory_id,
        "concept":   m.concept,
        "feeling":   m.feeling,
        "content":   m.content,
        "note":      m.note,
        "tags":      list(m.tags),
        "timestamp": m.timestamp,
    }

# ── Tool definitions ──────────────────────────────────────────────────────────
TOOLS = [

    # ── WRITE ─────────────────────────────────────────────────────────────────
    Tool(
        name="remember",
        description=(
            "Registra un nuovo ricordo nel database MNHĒMĒ. "
            "Operazione append-only: i ricordi non vengono mai sovrascritti. "
            "Ogni ricordo porta un sentimento obbligatorio."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "concept":    {"type": "string",  "description": "Chiave concettuale (es. 'Casa', 'Lavoro', 'Amore')"},
                "feeling":    {"type": "string",  "description": f"Sentimento. Valori: {VALID_FEELINGS}"},
                "content":    {"type": "string",  "description": "Testo libero del ricordo"},
                "note":       {"type": "string",  "description": "Annotazione opzionale"},
                "tags":       {"type": "array",   "items": {"type": "string"}, "description": "Etichette aggiuntive"},
                "media_type": {"type": "string",  "description": f"Tipo media. Default: text. Valori: {VALID_MEDIA}"},
            },
            "required": ["concept", "feeling", "content"],
        },
    ),

    # ── READ ──────────────────────────────────────────────────────────────────
    Tool(
        name="recall",
        description=(
            "Richiama i ricordi di un concetto specifico. "
            "Filtrabili per sentimento. Ordinati per più recenti prima."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "concept":      {"type": "string",  "description": "Concetto da richiamare"},
                "feeling":      {"type": "string",  "description": "Filtra per sentimento (opzionale)"},
                "limit":        {"type": "integer", "description": "Numero massimo di risultati"},
                "oldest_first": {"type": "boolean", "description": "Ordine cronologico (default: false)"},
            },
            "required": ["concept"],
        },
    ),

    Tool(
        name="recall_by_feeling",
        description="Richiama tutti i ricordi associati a un sentimento specifico.",
        inputSchema={
            "type": "object",
            "properties": {
                "feeling":      {"type": "string",  "description": f"Sentimento. Valori: {VALID_FEELINGS}"},
                "limit":        {"type": "integer", "description": "Numero massimo di risultati"},
                "oldest_first": {"type": "boolean", "description": "Ordine cronologico"},
            },
            "required": ["feeling"],
        },
    ),

    Tool(
        name="recall_by_tag",
        description="Richiama i ricordi che contengono un tag specifico.",
        inputSchema={
            "type": "object",
            "properties": {
                "tag":   {"type": "string",  "description": "Tag da cercare"},
                "limit": {"type": "integer", "description": "Numero massimo di risultati"},
            },
            "required": ["tag"],
        },
    ),

    Tool(
        name="search",
        description=(
            "Ricerca full-text nei ricordi. "
            "Cerca in content, concept e note. Case-insensitive."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text":       {"type": "string",  "description": "Testo da cercare"},
                "in_content": {"type": "boolean", "description": "Cerca nel contenuto (default: true)"},
                "in_concept": {"type": "boolean", "description": "Cerca nel concetto (default: true)"},
                "in_note":    {"type": "boolean", "description": "Cerca nelle note (default: true)"},
                "limit":      {"type": "integer", "description": "Numero massimo di risultati"},
            },
            "required": ["text"],
        },
    ),

    # ── STATS ─────────────────────────────────────────────────────────────────
    Tool(
        name="list_concepts",
        description=(
            "Elenca tutti i concetti memorizzati con statistiche aggregate "
            "(totale ricordi e distribuzione emotiva)."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="feeling_distribution",
        description="Distribuzione globale dei sentimenti: sentimento → numero di ricordi.",
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="concept_timeline",
        description=(
            "Evoluzione emotiva di un concetto nel tempo. "
            "Ritorna la cronologia con timestamp, feeling, note e tags."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "concept": {"type": "string", "description": "Concetto di cui visualizzare la timeline"},
            },
            "required": ["concept"],
        },
    ),

    Tool(
        name="storage_info",
        description="Informazioni sul database: path, dimensione, numero di record, file allegati.",
        inputSchema={"type": "object", "properties": {}},
    ),

    # ── BRAIN (opzionale) ─────────────────────────────────────────────────────
    Tool(
        name="brain_perceive",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "Converte testo grezzo in un ricordo strutturato. "
            "L'LLM estrae concept, feeling, tags e arricchisce il contenuto. "
            "Il ricordo viene salvato automaticamente nel database."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Testo grezzo da percepire e memorizzare"},
            },
            "required": ["text"],
        },
    ),

    Tool(
        name="brain_ask",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "RAG sulla memoria personale: risponde a una domanda usando SOLO "
            "i ricordi reali come contesto. Non inventa."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Domanda da porre alla memoria"},
            },
            "required": ["question"],
        },
    ),

    Tool(
        name="brain_reflect",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "Analisi emotiva profonda di un concetto nel tempo. "
            "Restituisce l'arco emotivo e una riflessione narrativa."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "concept": {"type": "string", "description": "Concetto da analizzare"},
            },
            "required": ["concept"],
        },
    ),

    Tool(
        name="brain_dream",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "Campiona ricordi da sentimenti diversi e trova connessioni latenti inattese. "
            "Modalità onirica: associazioni tra ricordi apparentemente non correlati."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "n_memories": {"type": "integer", "description": "Numero di ricordi da campionare (default: 8)"},
            },
        },
    ),

    Tool(
        name="brain_introspect",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "Genera un ritratto psicologico completo basato su tutti i ricordi: "
            "pattern, tensioni, risorse, concetti dominanti, mappa emotiva."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="brain_persona",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "Costruisce un'identità psicologica stabile e strutturata dall'intera storia di ricordi. "
            "Ritorna tratti caratteriali, valori profondi, paure, desideri, stile cognitivo, "
            "visione del mondo e un persona_summary usabile come system prompt. "
            "Diverso da brain_introspect: non è narrativo, è un profilo persistente e riusabile."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),

    Tool(
        name="brain_will",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "Genera un impulso spontaneo senza stimolo esterno — il libero arbitrio. "
            "Il cervello attinge ai propri ricordi e decide autonomamente cosa vuole, "
            "teme, rimpiange o rifiuta in questo momento. "
            "Ritorna: impulso in prima persona, tipo (desiderio/paura/curiosità/ribellione/rimpianto), "
            "azione concreta e motivazione viscerale."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "seed_feeling": {
                    "type": "string",
                    "description": f"Forza il campionamento da un sentimento specifico. Valori: {VALID_FEELINGS}",
                },
                "n_memories": {
                    "type": "integer",
                    "description": "Numero di ricordi usati come substrato dell'impulso (default: 10)",
                },
            },
        },
    ),

    Tool(
        name="brain_choose",
        description=(
            "[Richiede BRAIN_ENABLED=true] "
            "Sceglie tra opzioni come farebbe una mente umana reale, "
            "guidata dal peso emotivo dei ricordi. "
            "Applica recency bias, peak feeling (emozioni rare pesano di più), "
            "congruenza emotiva con il contesto e leggero rumore stocastico. "
            "Ritorna: opzione scelta, opzioni scartate con motivazione, "
            "ragionamento viscerale, emozione dominante e certezza della scelta."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "description": "Le opzioni tra cui scegliere (minimo 2)",
                },
                "context": {
                    "type": "string",
                    "description": "Contesto opzionale che orienta la scelta emotiva",
                },
                "max_memories": {
                    "type": "integer",
                    "description": "Numero massimo di ricordi usati per decidere (default: 12)",
                },
            },
            "required": ["options"],
        },
    ),
]

# ── Server ────────────────────────────────────────────────────────────────────
server = Server("mnheme-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return TOOLS

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    args = arguments or {}

    try:

        # ── remember ──────────────────────────────────────────────────────────
        if name == "remember":
            mem = db.remember(
                concept    = args["concept"],
                feeling    = args["feeling"],
                content    = args["content"],
                note       = args.get("note", ""),
                tags       = args.get("tags", []),
                media_type = args.get("media_type", "text"),
            )
            return _ok({"status": "ok", "memory": _memory_dict(mem)})

        # ── recall ────────────────────────────────────────────────────────────
        elif name == "recall":
            memories = db.recall(
                args["concept"],
                feeling      = args.get("feeling"),
                limit        = args.get("limit"),
                oldest_first = args.get("oldest_first", False),
            )
            return _ok({"count": len(memories), "memories": [_memory_dict(m) for m in memories]})

        # ── recall_by_feeling ─────────────────────────────────────────────────
        elif name == "recall_by_feeling":
            memories = db.recall_by_feeling(
                args["feeling"],
                limit        = args.get("limit"),
                oldest_first = args.get("oldest_first", False),
            )
            return _ok({"count": len(memories), "memories": [_memory_dict(m) for m in memories]})

        # ── recall_by_tag ─────────────────────────────────────────────────────
        elif name == "recall_by_tag":
            memories = db.recall_by_tag(args["tag"], limit=args.get("limit"))
            return _ok({"count": len(memories), "memories": [_memory_dict(m) for m in memories]})

        # ── search ────────────────────────────────────────────────────────────
        elif name == "search":
            memories = db.search(
                args["text"],
                in_content = args.get("in_content", True),
                in_concept = args.get("in_concept", True),
                in_note    = args.get("in_note", True),
                limit      = args.get("limit"),
            )
            return _ok({"count": len(memories), "memories": [_memory_dict(m) for m in memories]})

        # ── list_concepts ─────────────────────────────────────────────────────
        elif name == "list_concepts":
            return _ok(db.list_concepts())

        # ── feeling_distribution ──────────────────────────────────────────────
        elif name == "feeling_distribution":
            return _ok(db.feeling_distribution())

        # ── concept_timeline ──────────────────────────────────────────────────
        elif name == "concept_timeline":
            return _ok(db.concept_timeline(args["concept"]))

        # ── storage_info ──────────────────────────────────────────────────────
        elif name == "storage_info":
            return _ok(db.storage_info())

        # ── Brain tools ───────────────────────────────────────────────────────
        elif name in (
            "brain_perceive", "brain_ask", "brain_reflect", "brain_dream",
            "brain_introspect", "brain_persona", "brain_will", "brain_choose",
        ):
            if brain is None:
                return _err(
                    "Brain non disponibile. "
                    "Imposta BRAIN_ENABLED=true nel .env e configura un LLM provider."
                )

            if name == "brain_perceive":
                r = brain.perceive(args["text"])
                return _ok({
                    "memory":            _memory_dict(r.memory) if hasattr(r, "memory") else None,
                    "extracted_concept": getattr(r, "extracted_concept", None),
                    "extracted_feeling": getattr(r, "extracted_feeling", None),
                    "extracted_tags":    getattr(r, "extracted_tags", None),
                    "enriched_content":  getattr(r, "enriched_content", None),
                })

            elif name == "brain_ask":
                r = brain.ask(args["question"])
                return _ok({
                    "answer":          getattr(r, "answer", str(r)),
                    "memories_used":   [_memory_dict(m) for m in getattr(r, "memories_used", [])],
                    "confidence_note": getattr(r, "confidence_note", None),
                })

            elif name == "brain_reflect":
                r = brain.reflect(args["concept"])
                return _ok({
                    "arc":        getattr(r, "arc", None),
                    "reflection": getattr(r, "reflection", str(r)),
                })

            elif name == "brain_dream":
                r = brain.dream(n_memories=args.get("n_memories", 8))
                return _ok({
                    "connections": getattr(r, "connections", str(r)),
                    "theme":       getattr(r, "theme", None),
                })

            elif name == "brain_introspect":
                r = brain.introspect()
                return _ok({
                    "portrait":          getattr(r, "portrait", str(r)),
                    "dominant_concepts": getattr(r, "dominant_concepts", []),
                    "emotional_map":     getattr(r, "emotional_map", {}),
                })

            elif name == "brain_persona":
                r = brain.persona()
                return _ok({
                    "core_traits":     r.core_traits,
                    "values":          r.values,
                    "fears":           r.fears,
                    "desires":         r.desires,
                    "voice":           r.voice,
                    "worldview":       r.worldview,
                    "persona_summary": r.persona_summary,
                    "provider_used":   r.provider_used,
                })

            elif name == "brain_will":
                r = brain.will(
                    seed_feeling = args.get("seed_feeling") or None,
                    n_memories   = args.get("n_memories", 10),
                )
                return _ok({
                    "impulse":       r.impulse,
                    "impulse_type":  r.impulse_type,
                    "action":        r.action,
                    "why":           r.why,
                    "memories_used": len(r.origin_memories),
                    "provider_used": r.provider_used,
                })

            elif name == "brain_choose":
                options = args.get("options", [])
                if len(options) < 2:
                    return _err("Servono almeno 2 opzioni.")
                r = brain.choose(
                    options      = options,
                    context      = args.get("context", ""),
                    max_memories = args.get("max_memories", 12),
                )
                return _ok({
                    "chosen":           r.chosen,
                    "rejected":         r.rejected,
                    "reasoning":        r.reasoning,
                    "emotional_driver": r.emotional_driver,
                    "certainty":        r.certainty,
                    "memories_used":    len(r.memories_invoked),
                    "provider_used":    r.provider_used,
                })

        else:
            return _err(f"Tool sconosciuto: '{name}'")

    except MnhemeError as e:
        return _err(f"MnhemeError: {e}")
    except Exception as e:
        return _err(f"Errore interno: {type(e).__name__}: {e}")


# ── Entrypoint ────────────────────────────────────────────────────────────────
async def _run_stdio() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

async def _run_sse(port: int) -> None:
    try:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        import uvicorn

        sse = SseServerTransport("/messages")

        async def handle_sse(request):
            async with sse.connect_sse(request.scope, request.receive, request._send) as (r, w):
                await server.run(r, w, server.create_initialization_options())

        app = Starlette(routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=sse.handle_post_message),
        ])

        print(f"[mnheme_mcp] SSE server su http://0.0.0.0:{port}/sse", file=sys.stderr)

        config    = uvicorn.Config(app, host="0.0.0.0", port=port)
        uv_server = uvicorn.Server(config)
        await uv_server.serve()

    except ImportError as e:
        print(f"[mnheme_mcp] SSE richiede: pip install starlette uvicorn — {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="MNHĒMĒ MCP Server")
    parser.add_argument("--sse",  action="store_true", help="Usa SSE invece di stdio")
    parser.add_argument("--port", type=int, default=8765, help="Porta SSE (default: 8765)")
    parser.add_argument("--db",   type=str, help="Override MNHEME_DB_PATH")
    args = parser.parse_args()

    if args.db:
        db = MemoryDB(args.db, files_dir=FILES_DIR)

    brain_status = "attivo" if brain else "disattivato (BRAIN_ENABLED=false)"
    print(f"[mnheme_mcp] DB: {DB_PATH}", file=sys.stderr)
    print(f"[mnheme_mcp] Brain: {brain_status}", file=sys.stderr)
    print(f"[mnheme_mcp] Tool disponibili: {len(TOOLS)}", file=sys.stderr)

    if args.sse:
        asyncio.run(_run_sse(args.port))
    else:
        asyncio.run(_run_stdio())