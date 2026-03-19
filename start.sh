#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  MNHEME — Start Script
#  Human Memory Database
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colori ─────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
GOLD='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ── Configurazione ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
ENV_FILE="${SCRIPT_DIR}/.env"
ENV_EXAMPLE="${SCRIPT_DIR}/.env.example"
DB_DEFAULT="${SCRIPT_DIR}/mente.mnheme"
LOG_DIR="${SCRIPT_DIR}/logs"
PID_FILE="${SCRIPT_DIR}/.mnheme_api.pid"

# ── Banner ─────────────────────────────────────────────────────
print_banner() {
  echo ""
  echo -e "${GOLD}${BOLD}"
  echo "  ███╗   ███╗███╗   ██╗██╗  ██╗███████╗███╗   ███╗███████╗"
  echo "  ████╗ ████║████╗  ██║██║  ██║██╔════╝████╗ ████║██╔════╝"
  echo "  ██╔████╔██║██╔██╗ ██║███████║█████╗  ██╔████╔██║█████╗  "
  echo "  ██║╚██╔╝██║██║╚██╗██║██╔══██║██╔══╝  ██║╚██╔╝██║██╔══╝  "
  echo "  ██║ ╚═╝ ██║██║ ╚████║██║  ██║███████╗██║ ╚═╝ ██║███████╗"
  echo "  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚══════╝"
  echo -e "${NC}"
  echo -e "${DIM}  Human Memory Database — append-only, immutabile, senziente${NC}"
  echo -e "${DIM}  ─────────────────────────────────────────────────────────${NC}"
  echo ""
}

# ── Helpers ────────────────────────────────────────────────────
ok()   { echo -e "  ${GREEN}✓${NC}  $*"; }
err()  { echo -e "  ${RED}✗${NC}  $*" >&2; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $*"; }
info() { echo -e "  ${CYAN}→${NC}  $*"; }
step() { echo -e "\n${GOLD}${BOLD}  [$1]${NC}  ${BOLD}$2${NC}"; }
die()  { err "$*"; exit 1; }

# ── Controllo Python ───────────────────────────────────────────
check_python() {
  step "1/6" "Verifica Python"

  local py=""
  for cmd in python3.12 python3.11 python3 python; do
    if command -v "$cmd" &>/dev/null; then
      local ver
      ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
      local major minor
      major=$(echo "$ver" | cut -d. -f1)
      minor=$(echo "$ver" | cut -d. -f2)
      if [[ $major -ge 3 && $minor -ge 11 ]]; then
        py="$cmd"
        break
      fi
    fi
  done

  if [[ -z "$py" ]]; then
    die "Python 3.11+ non trovato. Installa Python: https://www.python.org"
  fi

  PYTHON="$py"
  local version
  version=$("$PYTHON" --version 2>&1)
  ok "$version trovato → $PYTHON"
}

# ── Virtual environment ────────────────────────────────────────
setup_venv() {
  step "2/6" "Virtual Environment"

  if [[ -d "$VENV_DIR" ]]; then
    ok "venv già presente → ${VENV_DIR}"
  else
    info "Creazione venv in ${VENV_DIR}..."
    "$PYTHON" -m venv "$VENV_DIR"
    ok "venv creato"
  fi

  # Attiva venv
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
  ok "venv attivato → $(python --version)"
}

# ── Dipendenze ─────────────────────────────────────────────────
install_deps() {
  step "3/6" "Dipendenze"

  # Core: zero dipendenze obbligatorie
  ok "Core MNHEME: nessuna dipendenza esterna richiesta"

  # Opzionali: API REST
  local install_api=false
  if [[ "${MODE:-}" == "api" || "${1:-}" == "--api" ]]; then
    install_api=true
  fi

  if $install_api; then
    info "Installazione dipendenze API (fastapi, uvicorn)..."
    pip install --quiet fastapi uvicorn 2>&1 | tail -1
    ok "FastAPI + Uvicorn installati"
  else
    # Controlla se già installati
    if python -c "import fastapi" 2>/dev/null; then
      ok "FastAPI già installato (API disponibile)"
    else
      warn "FastAPI non installato — API REST non disponibile"
      info "Per abilitare l'API: $0 --api  oppure  pip install fastapi uvicorn"
    fi
  fi
}

# ── File .env ──────────────────────────────────────────────────
setup_env() {
  step "4/6" "Configurazione .env"

  if [[ -f "$ENV_FILE" ]]; then
    ok ".env trovato → ${ENV_FILE}"
    # Mostra provider configurati (non mostrare le chiavi)
    local configured=0
    while IFS= read -r line; do
      if [[ "$line" =~ ^[A-Z_]+_URL=http && ! "$line" =~ ^# ]]; then
        local name
        name=$(echo "$line" | sed 's/_URL=.*//')
        local url
        url=$(echo "$line" | sed 's/.*_URL=//')
        info "  Provider: ${CYAN}${name}${NC} → ${DIM}${url}${NC}"
        ((configured++)) || true
      fi
    done < "$ENV_FILE"
    if [[ $configured -eq 0 ]]; then
      warn "Nessun provider configurato nel .env"
      info "Modifica ${ENV_FILE} e aggiungi almeno un blocco NOME_URL + NOME_MODEL"
    fi
  else
    warn ".env non trovato"
    if [[ -f "$ENV_EXAMPLE" ]]; then
      info "Copio .env.example → .env"
      cp "$ENV_EXAMPLE" "$ENV_FILE"
      warn "Modifica ${ENV_FILE} con le tue API key prima di usare il Brain"
    else
      warn "Crea un file .env con almeno:"
      echo ""
      echo "      LM_STUDIO_URL=http://localhost:1234/v1/chat/completions"
      echo "      LM_STUDIO_MODEL=local-model"
      echo ""
    fi
  fi
}

# ── Test veloce ────────────────────────────────────────────────
smoke_test() {
  step "5/6" "Verifica sistema"

  python - <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd())

errors = []

try:
    from mnheme import MemoryDB, Feeling, MediaType
    import tempfile, os, pathlib, shutil
    tmp = pathlib.Path(tempfile.mktemp(suffix='.mnheme'))
    db = MemoryDB(tmp)
    m  = db.remember("Test", Feeling.CURIOSITA, "Smoke test OK")
    assert db.count() == 1
    assert m.concept == "Test"
    tmp.unlink(missing_ok=True)
    files_dir = pathlib.Path(str(tmp).replace('.mnheme', '_files'))
    if files_dir.exists():
        shutil.rmtree(files_dir)
    print("  \033[0;32m✓\033[0m  MemoryDB OK")
except Exception as e:
    errors.append(f"MemoryDB: {e}")
    print(f"  \033[0;31m✗\033[0m  MemoryDB: {e}")

try:
    from storage import StorageEngine
    print("  \033[0;32m✓\033[0m  StorageEngine OK")
except Exception as e:
    errors.append(f"StorageEngine: {e}")

try:
    from index import IndexEngine
    print("  \033[0;32m✓\033[0m  IndexEngine OK")
except Exception as e:
    errors.append(f"IndexEngine: {e}")

try:
    from fsprobe import FsProbe
    probe = FsProbe("/tmp")
    caps  = probe.detect()
    print(f"  \033[0;32m✓\033[0m  FsProbe OK → fs={caps.fs_type.value}  strategy={caps.strategy.value}")
except Exception as e:
    errors.append(f"FsProbe: {e}")

try:
    from filestore import FileStore
    print("  \033[0;32m✓\033[0m  FileStore OK")
except Exception as e:
    errors.append(f"FileStore: {e}")

try:
    from llm_provider import LLMProvider, load_env
    print("  \033[0;32m✓\033[0m  LLMProvider OK")
except Exception as e:
    errors.append(f"LLMProvider: {e}")

try:
    from brain import Brain
    print("  \033[0;32m✓\033[0m  Brain OK")
except Exception as e:
    errors.append(f"Brain: {e}")

if errors:
    print(f"\n  \033[0;31mErrori: {len(errors)}\033[0m")
    sys.exit(1)
else:
    print(f"\n  \033[0;32mTutti i moduli OK\033[0m")
EOF
}

# ── Avvio ──────────────────────────────────────────────────────
start_service() {
  step "6/6" "Avvio"

  case "${MODE:-interactive}" in

    # ── Shell interattiva Python ──────────────
    interactive | shell | "")
      ok "Avvio shell Python interattiva con MNHEME precaricato"
      echo ""
      echo -e "${DIM}  Database: ${DB_DEFAULT}${NC}"
      echo -e "${DIM}  Digita 'exit()' per uscire${NC}"
      echo ""

      python - <<EOF
import sys, os
sys.path.insert(0, '${SCRIPT_DIR}')
os.chdir('${SCRIPT_DIR}')

from mnheme import MemoryDB, Feeling, MediaType, Memory
from llm_provider import LLMProvider
from brain import Brain

print("\033[0;33m  MNHEME caricato.\033[0m")
print("\033[2m  Oggetti disponibili: MemoryDB, Feeling, MediaType, LLMProvider, Brain\033[0m")
print()

# Database pronto
db = MemoryDB('${DB_DEFAULT}')
print(f"\033[0;36m  db = {db}\033[0m")

# Provider (se .env esiste)
try:
    llm = LLMProvider.from_env('${ENV_FILE}')
    brain = Brain(db, llm)
    print(f"\033[0;36m  brain = {llm.active_profile.name} → {llm.active_profile.model}\033[0m")
except Exception as e:
    print(f"\033[2m  brain non disponibile: {e}\033[0m")
    llm = None
    brain = None

print()
EOF
      exec python -i -c "
import sys, os
sys.path.insert(0, '${SCRIPT_DIR}')
os.chdir('${SCRIPT_DIR}')
from mnheme import MemoryDB, Feeling, MediaType
from llm_provider import LLMProvider
from brain import Brain
db = MemoryDB('${DB_DEFAULT}')
try:
    llm   = LLMProvider.from_env('${ENV_FILE}')
    brain = Brain(db, llm)
except:
    llm   = None
    brain = None
"
      ;;

    # ── API REST ──────────────────────────────
    api)
      if ! python -c "import fastapi" 2>/dev/null; then
        die "FastAPI non installato. Esegui: $0 --api per installarlo automaticamente"
      fi

      local host="${API_HOST:-0.0.0.0}"
      local port="${API_PORT:-8000}"

      mkdir -p "$LOG_DIR"
      local log="${LOG_DIR}/mnheme_api.log"

      info "Avvio API REST su http://${host}:${port}"
      info "Swagger UI: http://localhost:${port}/docs"
      info "Log: ${log}"
      info "Stop: $0 --stop  oppure  Ctrl+C"
      echo ""

      # Esporta variabili per il processo API
      export MNHEME_DB_PATH="${DB_DEFAULT}"

      uvicorn mnheme_api:app \
        --host "$host" \
        --port "$port" \
        --reload \
        --log-level info \
        2>&1 | tee "$log" &

      local api_pid=$!
      echo "$api_pid" > "$PID_FILE"
      ok "API avviata (PID ${api_pid})"

      # Aspetta che sia pronta
      local retries=10
      while [[ $retries -gt 0 ]]; do
        if curl -sf "http://localhost:${port}/stats" &>/dev/null; then
          ok "API risponde su http://localhost:${port}"
          break
        fi
        sleep 1
        ((retries--)) || true
      done

      wait "$api_pid"
      ;;

    # ── Benchmark ─────────────────────────────
    benchmark)
      local records="${BENCH_RECORDS:-2000}"
      local output="${BENCH_OUTPUT:-}"

      info "Avvio benchmark con ${records} record..."
      if [[ -n "$output" ]]; then
        python mnheme_benchmark.py --records "$records" --output "$output"
        ok "Report salvato in: ${output}"
      else
        python mnheme_benchmark.py --records "$records"
      fi
      ;;

    # ── Examples ──────────────────────────────
    examples)
      info "Esecuzione esempi..."
      python examples.py
      ;;

    # ── Tests ─────────────────────────────────
    test | tests)
      info "Esecuzione test suite..."
      echo ""
      python test_llm_provider.py
      echo ""
      python test_fsprobe.py
      echo ""
      ok "Tutti i test completati"
      ;;

    *)
      die "Modalità sconosciuta: ${MODE}. Usa: interactive | api | benchmark | examples | test"
      ;;
  esac
}

# ── Stop API ───────────────────────────────────────────────────
stop_api() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid"
      rm -f "$PID_FILE"
      ok "API fermata (PID ${pid})"
    else
      warn "Processo ${pid} non trovato (già terminato?)"
      rm -f "$PID_FILE"
    fi
  else
    warn "Nessuna istanza API trovata (${PID_FILE} non esiste)"
  fi
}

# ── Aiuto ──────────────────────────────────────────────────────
print_help() {
  print_banner
  echo -e "${BOLD}  UTILIZZO${NC}"
  echo ""
  echo "    ./start.sh [opzioni]"
  echo ""
  echo -e "${BOLD}  MODALITÀ${NC}"
  echo ""
  echo "    (nessuna)           Shell Python interattiva con MNHEME precaricato"
  echo "    --api               Avvia il server API REST (FastAPI + uvicorn)"
  echo "    --benchmark         Esegui la suite di benchmark"
  echo "    --examples          Esegui gli esempi"
  echo "    --test              Esegui i test"
  echo "    --stop              Ferma il server API"
  echo ""
  echo -e "${BOLD}  OPZIONI${NC}"
  echo ""
  echo "    --api               Installa fastapi/uvicorn se mancanti e avvia l'API"
  echo "    --host HOST         Host per l'API (default: 0.0.0.0)"
  echo "    --port PORT         Porta per l'API (default: 8000)"
  echo "    --db PATH           Path al file database (default: mente.mnheme)"
  echo "    --records N         Numero record per il benchmark (default: 2000)"
  echo "    --output FILE       Salva output benchmark in JSON"
  echo "    --help, -h          Mostra questo aiuto"
  echo ""
  echo -e "${BOLD}  ESEMPI${NC}"
  echo ""
  echo "    ./start.sh                          # shell interattiva"
  echo "    ./start.sh --api                    # API REST su :8000"
  echo "    ./start.sh --api --port 9000        # API su porta custom"
  echo "    ./start.sh --benchmark              # benchmark 2000 record"
  echo "    ./start.sh --benchmark --records 10000 --output bench.json"
  echo "    ./start.sh --test                   # test suite"
  echo "    ./start.sh --stop                   # ferma l'API"
  echo ""
}

# ── Parsing argomenti ──────────────────────────────────────────
parse_args() {
  MODE="interactive"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --api)        MODE="api" ;;
      --benchmark)  MODE="benchmark" ;;
      --examples)   MODE="examples" ;;
      --test|--tests) MODE="test" ;;
      --stop)       stop_api; exit 0 ;;
      --host)       API_HOST="$2"; shift ;;
      --port)       API_PORT="$2"; shift ;;
      --db)         DB_DEFAULT="$2"; shift ;;
      --records)    BENCH_RECORDS="$2"; shift ;;
      --output)     BENCH_OUTPUT="$2"; shift ;;
      --help|-h)    print_help; exit 0 ;;
      *)            die "Opzione sconosciuta: $1. Usa --help per la lista opzioni." ;;
    esac
    shift
  done
}

# ── Main ───────────────────────────────────────────────────────
main() {
  parse_args "$@"
  print_banner
  cd "$SCRIPT_DIR"
  check_python
  setup_venv
  install_deps "$@"
  setup_env
  smoke_test
  start_service
}

main "$@"
