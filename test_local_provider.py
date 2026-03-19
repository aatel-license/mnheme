"""
lmstudio_test.py
================
Test live contro LM Studio (o qualsiasi server OpenAI-compat locale).
Fa chiamate REALI al server — serve LM Studio avviato con un modello caricato.

Esegui con:
    python lmstudio_test.py
    python lmstudio_test.py --url http://localhost:1234 --model my-model
    python lmstudio_test.py --verbose
"""

import sys
import os
import json
import argparse
import time
import pathlib

PROJECT_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# ─────────────────────────────────────────────
# ARGS
# ─────────────────────────────────────────────

parser = argparse.ArgumentParser(description="MNHEME — Live test LM Studio")
parser.add_argument("--url",     default=None,  help="Base URL LM Studio (es: http://localhost:1234)")
parser.add_argument("--model",   default=None,  help="Nome modello (es: local-model)")
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--db",      default=None,  help="Path database (default: temp)")
args = parser.parse_args()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

GREEN  = "\033[0;32m"
RED    = "\033[0;31m"
YELLOW = "\033[0;33m"
CYAN   = "\033[0;36m"
GOLD   = "\033[0;33m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
NC     = "\033[0m"
SEP    = "─" * 65


def ok(msg):   print(f"  {GREEN}✓{NC}  {msg}")
def err(msg):  print(f"  {RED}✗{NC}  {msg}")
def info(msg): print(f"  {CYAN}→{NC}  {msg}")
def warn(msg): print(f"  {YELLOW}⚠{NC}  {msg}")
def head(msg): print(f"\n{SEP}\n{BOLD}  {msg}{NC}\n{SEP}")


# ─────────────────────────────────────────────
# 1. RISOLVI CONFIGURAZIONE
# ─────────────────────────────────────────────

head("Configurazione")

from llm_provider import load_env, discover_providers, LLMProvider, ProviderProfile

# Carica .env se esiste
env_path = PROJECT_DIR / ".env"
env      = load_env(env_path) if env_path.exists() else {}

# Override da argomenti CLI
if args.url:
    base = args.url.rstrip("/")
    env["LM_STUDIO_URL"]   = f"{base}/v1/chat/completions"
    env["LOCAL_LLM_URL"]   = f"{base}/v1/chat/completions"
if args.model:
    env["LM_STUDIO_MODEL"] = args.model
    env["LOCAL_LLM_MODEL"] = args.model

# Trova il primo provider locale disponibile nell'env
profiles = discover_providers(env)
local_providers = {
    name: p for name, p in profiles.items()
    if p.is_local and p.available
}

if not local_providers:
    # Fallback: costruisci un profilo LM Studio con i default
    url   = args.url or "http://localhost:1234"
    model = args.model or "local-model"
    info(f"Nessun provider locale nel .env — uso default: {url}")
    profile = ProviderProfile(
        name        = "lm-studio",
        url         = f"{url.rstrip('/')}/v1/chat/completions",
        model       = model,
        api_key     = "",
        rpm         = 60,
        temperature = 0.3,
        max_tokens  = 512,
    )
    local_providers = {"lm-studio": profile}
    profiles["lm-studio"] = profile

# Scegli il provider: preferisci lm-studio, poi local-llm, poi il primo locale
preferred = next(
    (name for name in ["lm-studio", "local-llm"] if name in local_providers),
    next(iter(local_providers))
)
active_profile = local_providers[preferred]

info(f"Provider selezionato:  {BOLD}{active_profile.name}{NC}")
info(f"URL:                   {active_profile.url}")
info(f"Modello:               {active_profile.model}")
info(f"Temperature:           {active_profile.temperature}")
info(f"Max tokens:            {active_profile.max_tokens}")

# ─────────────────────────────────────────────
# 2. PING SERVER
# ─────────────────────────────────────────────

head("Ping server")

import urllib.request, urllib.error

# Prova a raggiungere l'endpoint /v1/models (LM Studio lo espone)
base_url = active_profile.url.replace("/v1/chat/completions", "")
models_url = f"{base_url}/v1/models"

info(f"GET {models_url}")
try:
    req  = urllib.request.Request(models_url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        body   = json.loads(resp.read())
        models = [m.get("id", "?") for m in body.get("data", [])]
        ok(f"Server raggiungibile — {len(models)} modello/i caricato/i")
        for m in models:
            info(f"  modello disponibile: {DIM}{m}{NC}")
        if models and not args.model:
            # Usa il primo modello disponibile
            active_profile = ProviderProfile(
                name        = active_profile.name,
                url         = active_profile.url,
                model       = models[0],
                api_key     = active_profile.api_key,
                rpm         = active_profile.rpm,
                temperature = active_profile.temperature,
                max_tokens  = active_profile.max_tokens,
            )
            info(f"Uso automaticamente: {BOLD}{models[0]}{NC}")
except urllib.error.URLError as e:
    err(f"Server non raggiungibile a {base_url}")
    err(f"Dettaglio: {e.reason}")
    print()
    print(f"  {YELLOW}Assicurati che LM Studio sia avviato con 'Local Server' attivo.{NC}")
    print(f"  {YELLOW}Di default gira su http://localhost:1234{NC}")
    print()
    sys.exit(1)
except Exception as e:
    warn(f"Endpoint /v1/models non disponibile ({e}) — continuo comunque")

# ─────────────────────────────────────────────
# 3. CHIAMATA DIRETTA HTTP
# ─────────────────────────────────────────────

head("Chiamata HTTP diretta (senza MNHEME)")

from llm_provider import call_provider

info(f"POST {active_profile.url}")
info(f"Modello: {active_profile.model}")
print()

t0 = time.perf_counter()
try:
    response = call_provider(
        active_profile,
        system = "You are a concise assistant. Reply in one sentence.",
        user   = "Say hello and confirm you are working.",
        max_tokens  = 80,
        temperature = 0.1,
    )
    elapsed = (time.perf_counter() - t0) * 1000
    ok(f"Risposta ricevuta in {elapsed:.0f}ms")
    print(f"\n  {DIM}Risposta:{NC}")
    print(f"  {CYAN}{response.strip()}{NC}\n")
except Exception as e:
    err(f"Chiamata fallita: {e}")
    if args.verbose:
        import traceback; traceback.print_exc()
    sys.exit(1)

# ─────────────────────────────────────────────
# 4. LLMPROVIDER
# ─────────────────────────────────────────────

head("LLMProvider.complete()")

provider = LLMProvider.from_profile(active_profile)
info(f"{provider}")

t0 = time.perf_counter()
try:
    resp = provider.complete(
        "Sei un assistente sintetico. Rispondi in italiano in una riga.",
        "Dimmi cos'è MNHEME in una sola frase.",
        max_tokens  = 100,
        temperature = 0.2,
    )
    elapsed = (time.perf_counter() - t0) * 1000
    ok(f"LLMProvider.complete() → {elapsed:.0f}ms")
    print(f"\n  {DIM}Risposta:{NC}")
    print(f"  {CYAN}{resp.strip()}{NC}\n")
except Exception as e:
    err(f"LLMProvider.complete() fallito: {e}")
    if args.verbose:
        import traceback; traceback.print_exc()
    sys.exit(1)

# ─────────────────────────────────────────────
# 5. BRAIN — operazioni reali
# ─────────────────────────────────────────────

head("Brain — operazioni cognitive REALI")

from mnheme import MemoryDB, Feeling
from brain  import Brain
import tempfile, shutil

db_path = pathlib.Path(args.db) if args.db else pathlib.Path(tempfile.mktemp(suffix=".mnheme"))
cleanup_db = args.db is None

db    = MemoryDB(db_path)
brain = Brain(db, provider, language="italiano")
info(f"Database: {db_path}")
info(f"Provider: {provider.active_profile.name} / {provider.active_profile.model}")
print()

# ── perceive ──────────────────────────────────
print(f"  {BOLD}perceive(){NC}")
info("Input: 'Ho aperto la busta dalla banca stamattina. Le mani mi tremavano.'")
t0 = time.perf_counter()
try:
    r = brain.perceive(
        "Ho aperto la busta dalla banca stamattina. Le mani mi tremavano.",
        note="Test live LM Studio"
    )
    elapsed = (time.perf_counter() - t0) * 1000
    ok(f"percepito in {elapsed:.0f}ms")
    print(f"    concept:   {CYAN}{r.extracted_concept}{NC}")
    print(f"    feeling:   {CYAN}{r.extracted_feeling}{NC}")
    print(f"    tags:      {CYAN}{r.extracted_tags}{NC}")
    print(f"    enriched:  {DIM}{r.enriched_content[:120]}{'...' if len(r.enriched_content)>120 else ''}{NC}")
    print(f"    memory_id: {DIM}{r.memory.memory_id}{NC}")
except Exception as e:
    err(f"perceive() fallito: {e}")
    if args.verbose:
        import traceback; traceback.print_exc()

# Aggiungi altri ricordi per ask/reflect/dream
db.remember("Debito",   Feeling.SERENITA, "Ho finalmente saldato l'ultimo rate.", tags=["libertà"])
db.remember("Famiglia", Feeling.AMORE,    "Il sorriso di mia figlia stamattina.", tags=["figlia"])
db.remember("Lavoro",   Feeling.ORGOGLIO, "Il progetto è andato. Hanno applaudito.", tags=["successo"])
db.remember("Viaggio",  Feeling.NOSTALGIA,"Il tramonto a Santorini.", tags=["grecia"])

print()

# ── ask ────────────────────────────────────────
print(f"  {BOLD}ask(){NC}")
domanda = "Come mi sento rispetto al denaro e al debito?"
info(f"Domanda: '{domanda}'")
t0 = time.perf_counter()
try:
    ans = brain.ask(domanda)
    elapsed = (time.perf_counter() - t0) * 1000
    ok(f"risposta in {elapsed:.0f}ms  ({len(ans.memories_used)} ricordi usati come contesto)")
    print(f"\n    {DIM}Risposta:{NC}")
    for line in ans.answer.strip().split("\n"):
        print(f"    {CYAN}{line}{NC}")
    if ans.confidence_note:
        print(f"    {DIM}{ans.confidence_note}{NC}")
except Exception as e:
    err(f"ask() fallito: {e}")
    if args.verbose:
        import traceback; traceback.print_exc()

print()

# ── reflect ────────────────────────────────────
print(f"  {BOLD}reflect(){NC}")
concetto = "Debito"
info(f"Concetto: '{concetto}'")
t0 = time.perf_counter()
try:
    ref = brain.reflect(concetto)
    elapsed = (time.perf_counter() - t0) * 1000
    ok(f"riflessione in {elapsed:.0f}ms  ({len(ref.memories)} ricordi)")
    if ref.arc:
        print(f"    {DIM}Arco:{NC}  {CYAN}{ref.arc}{NC}")
    print(f"\n    {DIM}Riflessione:{NC}")
    preview = ref.reflection.strip()[:300]
    for line in preview.split("\n"):
        print(f"    {CYAN}{line}{NC}")
    if len(ref.reflection) > 300:
        print(f"    {DIM}[...]{NC}")
except Exception as e:
    err(f"reflect() fallito: {e}")
    if args.verbose:
        import traceback; traceback.print_exc()

print()

# ── dream ──────────────────────────────────────
print(f"  {BOLD}dream(){NC}")
info("Campiona ricordi da sentimenti diversi, trova connessioni...")
t0 = time.perf_counter()
try:
    dream = brain.dream(n_memories=4)
    elapsed = (time.perf_counter() - t0) * 1000
    ok(f"associazioni in {elapsed:.0f}ms  ({len(dream.memories)} ricordi campionati)")
    print(f"    {DIM}Ricordi:{NC}")
    for m in dream.memories:
        print(f"      [{m.concept}/{m.feeling}] {m.content[:50]}")
    print(f"\n    {DIM}Connessioni trovate:{NC}")
    preview = dream.connections.strip()[:250]
    for line in preview.split("\n"):
        print(f"    {CYAN}{line}{NC}")
    if len(dream.connections) > 250:
        print(f"    {DIM}[...]{NC}")
except Exception as e:
    err(f"dream() fallito: {e}")
    if args.verbose:
        import traceback; traceback.print_exc()

print()

# ── introspect ─────────────────────────────────
print(f"  {BOLD}introspect(){NC}")
info(f"Analisi su {db.count()} ricordi totali...")
t0 = time.perf_counter()
try:
    intro = brain.introspect()
    elapsed = (time.perf_counter() - t0) * 1000
    ok(f"ritratto in {elapsed:.0f}ms")
    print(f"    {DIM}Concetti dominanti:{NC}  {CYAN}{intro.dominant_concepts}{NC}")
    print(f"    {DIM}Mappa emotiva:{NC}       {CYAN}{dict(list(intro.emotional_map.items())[:5])}{NC}")
    print(f"\n    {DIM}Ritratto:{NC}")
    preview = intro.portrait.strip()[:300]
    for line in preview.split("\n"):
        print(f"    {CYAN}{line}{NC}")
    if len(intro.portrait) > 300:
        print(f"    {DIM}[...]{NC}")
except Exception as e:
    err(f"introspect() fallito: {e}")
    if args.verbose:
        import traceback; traceback.print_exc()

# ─────────────────────────────────────────────
# 6. STATO FINALE DB
# ─────────────────────────────────────────────

head("Stato database")

info_db = db.storage_info()
info(f"File:      {info_db['log_path']}")
info(f"Records:   {info_db['total_records']}")
info(f"Dimensione:{info_db['log_size_kb']} KB")
print()

print(f"  {DIM}Concetti:{NC}")
for c in db.list_concepts():
    fs = "  ".join(f"{f}({n})" for f,n in c["feelings"].items())
    print(f"    {CYAN}{c['concept']:15}{NC} {DIM}{c['total']} ricordi  [{fs}]{NC}")

# Cleanup
if cleanup_db:
    db_path.unlink(missing_ok=True)
    files_dir = pathlib.Path(str(db_path).replace(".mnheme","_files"))
    if files_dir.exists():
        shutil.rmtree(files_dir, ignore_errors=True)

print(f"\n{SEP}")
print(f"  {GREEN}{BOLD}Test completati.{NC}  Server LM Studio funzionante con MNHEME.")
print(f"{SEP}\n")