#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# MNHEME Digital Twin — run.sh
# Lancia da dentro apps/twin/
#
#   ./run.sh
#   ./run.sh --db ../../data/vita.mnheme
#   ./run.sh --port 8002 --no-setup
#   ./run.sh --name "Mario Rossi" --birth-year 1942 --death-year 2024
#   ./run.sh --host 0.0.0.0 --reload
# ─────────────────────────────────────────────────────────────

set -euo pipefail

# ── Colori ───────────────────────────────────────────────────
GRN="\033[32m"; RED="\033[31m"; YLW="\033[33m"
CYN="\033[36m"; DIM="\033[2m";  BOLD="\033[1m"; NC="\033[0m"

ok()   { echo -e "  ${GRN}✓${NC}  $*"; }
err()  { echo -e "  ${RED}✗${NC}  $*" >&2; }
info() { echo -e "  ${CYN}→${NC}  $*"; }
warn() { echo -e "  ${YLW}⚠${NC}  $*"; }
head() { echo -e "\n${BOLD}$*${NC}"; }

# ── Defaults ─────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"   # root del progetto

PORT="${PORT:-8001}"
HOST="${HOST:-127.0.0.1}"
RELOAD=""
DO_SETUP=true

# Parametri profilo (tutti opzionali — il setup li inferisce dai ricordi)
SETUP_NAME=""
SETUP_BIRTH=""
SETUP_DEATH=""
SETUP_LANGUAGE=""
SETUP_VOICE=""
SETUP_VALUES=""
SETUP_EPITAPH=""
SETUP_CURATOR=""
SETUP_EMBARGO="0"

# ── Parsing argomenti ─────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --db)           export MNHEME_DB="$2";         shift 2 ;;
    --env)          export MNHEME_ENV="$2";        shift 2 ;;
    --provider)     export TWIN_LLM_PROVIDER="$2"; shift 2 ;;
    --profile)      export TWIN_PROFILE="$2";      shift 2 ;;
    --port)         PORT="$2";                     shift 2 ;;
    --host)         HOST="$2";                     shift 2 ;;
    --reload)       RELOAD="--reload";             shift   ;;
    --no-setup)     DO_SETUP=false;                shift   ;;
    --name)         SETUP_NAME="$2";               shift 2 ;;
    --birth-year)   SETUP_BIRTH="$2";              shift 2 ;;
    --death-year)   SETUP_DEATH="$2";              shift 2 ;;
    --language)     SETUP_LANGUAGE="$2";           shift 2 ;;
    --voice)        SETUP_VOICE="$2";              shift 2 ;;
    --values)       SETUP_VALUES="$2";             shift 2 ;;  # "famiglia,lavoro,onestà"
    --epitaph)      SETUP_EPITAPH="$2";            shift 2 ;;
    --curator)      SETUP_CURATOR="$2";            shift 2 ;;
    --embargo)      SETUP_EMBARGO="$2";            shift 2 ;;
    -h|--help)
      echo ""
      echo -e "${BOLD}MNHEME Digital Twin — run.sh${NC}"
      echo ""
      echo "  Uso: ./run.sh [opzioni]"
      echo ""
      echo "  SERVER"
      echo "    --port PORT          Porta uvicorn (default: 8001)"
      echo "    --host HOST          Host uvicorn (default: 127.0.0.1)"
      echo "    --reload             Abilita auto-reload uvicorn"
      echo "    --no-setup           Salta il setup — usa profilo esistente"
      echo ""
      echo "  DATABASE & CONFIG"
      echo "    --db PATH            Path al file .mnheme (default: ../../mnheme.mnheme)"
      echo "    --env PATH           Path al file .env    (default: ../../.env)"
      echo "    --provider NAME      Provider LLM attivo  (es: lm-studio, groq)"
      echo "    --profile PATH       Path al file profilo .json"
      echo ""
      echo "  PROFILO TWIN (opzionali — il resto viene inferito dai ricordi)"
      echo "    --name NAME          Nome completo"
      echo "    --birth-year YEAR    Anno di nascita"
      echo "    --death-year YEAR    Anno di morte"
      echo "    --language LANG      Lingua (default: italiano)"
      echo "    --voice NOTES        Note sulla voce narrativa"
      echo "    --values LIST        Valori separati da virgola (es: famiglia,lavoro)"
      echo "    --epitaph TEXT       Frase epitaffio"
      echo "    --curator NAME       Nome del curatore"
      echo "    --embargo N          Anni di embargo post-mortem (default: 0)"
      echo ""
      echo "  ESEMPI"
      echo "    ./run.sh"
      echo "    ./run.sh --name 'Mario Rossi' --birth-year 1942 --death-year 2024"
      echo "    ./run.sh --db ../../data/vita.mnheme --port 8002"
      echo "    ./run.sh --no-setup --reload"
      echo "    ./run.sh --provider lm-studio --host 0.0.0.0"
      echo ""
      exit 0
      ;;
    *)
      err "Argomento sconosciuto: $1"
      echo "  Usa --help per la lista delle opzioni."
      exit 1
      ;;
  esac
done

# ── Risolvi paths ─────────────────────────────────────────────
export PYTHONPATH="${ROOT_DIR}"

MNHEME_DB="${MNHEME_DB:-${ROOT_DIR}/mnheme.mnheme}"
MNHEME_ENV="${MNHEME_ENV:-${ROOT_DIR}/.env}"
export MNHEME_DB MNHEME_ENV

# ── Banner ────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}MNHEME Digital Twin${NC}  ${DIM}v1.0${NC}"
echo "────────────────────────────────────────────────"
info "Root progetto:  ${ROOT_DIR}"
info "Database:       ${MNHEME_DB}"
info "Config (.env):  ${MNHEME_ENV}"
info "Server:         http://${HOST}:${PORT}"
[[ -n "${TWIN_LLM_PROVIDER:-}" ]] && info "Provider LLM:   ${TWIN_LLM_PROVIDER}"

# ── Prerequisiti ─────────────────────────────────────────────
head "Prerequisiti"

# Python
if ! command -v python3 &>/dev/null; then
  err "python3 non trovato"; exit 1
fi
ok "Python $(python3 --version 2>&1 | cut -d' ' -f2)"

# uvicorn
if ! python3 -c "import uvicorn" 2>/dev/null; then
  warn "uvicorn non installato — installo…"
  pip install uvicorn fastapi --quiet
fi
ok "uvicorn disponibile"

# Database
if [[ ! -f "${MNHEME_DB}" ]]; then
  warn "Database non trovato: ${MNHEME_DB}"
  warn "Il twin partirà con un database vuoto."
else
  # Conta i ricordi (approssimativo dal file size)
  DB_SIZE=$(du -sh "${MNHEME_DB}" 2>/dev/null | cut -f1)
  ok "Database trovato (${DB_SIZE})"
fi

# .env
if [[ ! -f "${MNHEME_ENV}" ]]; then
  warn ".env non trovato: ${MNHEME_ENV}"
else
  ok ".env trovato"
  # Legge ACTIVE_PROVIDER dal .env se non già impostato
  if [[ -z "${TWIN_LLM_PROVIDER:-}" ]]; then
    ACTIVE=$(grep -E "^ACTIVE_PROVIDER=" "${MNHEME_ENV}" 2>/dev/null | cut -d= -f2 | tr -d ' "' || true)
    [[ -n "${ACTIVE}" ]] && info "Provider dal .env: ${ACTIVE}"
  fi
fi

# ── Setup profilo ─────────────────────────────────────────────
if [[ "${DO_SETUP}" == "true" ]]; then
  head "Setup profilo"

  # Attendi che il server sia pronto (lo avviamo dopo)
  # Il setup viene fatto via curl dopo l'avvio

  # Costruisce il JSON di setup con i parametri forniti
  SETUP_JSON="{"
  SETUP_JSON+="\"embargo_years\": ${SETUP_EMBARGO}"
  [[ -n "${SETUP_NAME}"     ]] && SETUP_JSON+=", \"name\": \"${SETUP_NAME}\""
  [[ -n "${SETUP_BIRTH}"    ]] && SETUP_JSON+=", \"birth_year\": ${SETUP_BIRTH}"
  [[ -n "${SETUP_DEATH}"    ]] && SETUP_JSON+=", \"death_year\": ${SETUP_DEATH}"
  [[ -n "${SETUP_LANGUAGE}" ]] && SETUP_JSON+=", \"language\": \"${SETUP_LANGUAGE}\""
  [[ -n "${SETUP_VOICE}"    ]] && SETUP_JSON+=", \"voice_notes\": \"${SETUP_VOICE}\""
  [[ -n "${SETUP_EPITAPH}"  ]] && SETUP_JSON+=", \"epitaph\": \"${SETUP_EPITAPH}\""
  [[ -n "${SETUP_CURATOR}"  ]] && SETUP_JSON+=", \"curator_name\": \"${SETUP_CURATOR}\""

  # Converti --values "famiglia,lavoro" → ["famiglia","lavoro"]
  if [[ -n "${SETUP_VALUES}" ]]; then
    VALUES_JSON=$(echo "${SETUP_VALUES}" | python3 -c "
import sys, json
vals = [v.strip() for v in sys.stdin.read().split(',') if v.strip()]
print(json.dumps(vals))
")
    SETUP_JSON+=", \"values\": ${VALUES_JSON}"
  fi

  SETUP_JSON+="}"

  info "Parametri setup:"
  echo "${SETUP_JSON}" | python3 -m json.tool 2>/dev/null | sed 's/^/    /' || echo "    ${SETUP_JSON}"

  # Verifica se esiste già un profilo
  DB_STEM=$(basename "${MNHEME_DB}" .mnheme)
  DB_DIR=$(dirname "${MNHEME_DB}")
  PROFILE_AUTO="${DB_DIR}/${DB_STEM}-twin_profile.json"

  if [[ -f "${PROFILE_AUTO}" ]] && [[ -z "${SETUP_NAME}${SETUP_BIRTH}${SETUP_DEATH}" ]]; then
    warn "Profilo già esistente: ${PROFILE_AUTO}"
    warn "Usa --no-setup per usarlo, o passa --name/--birth-year per rigenerarlo."
    read -r -p "  Rigenera il profilo? [s/N] " CONFIRM
    if [[ "${CONFIRM}" != "s" && "${CONFIRM}" != "S" ]]; then
      info "Profilo esistente mantenuto."
      DO_SETUP=false
    fi
  fi
fi

# ── Avvia server ─────────────────────────────────────────────
head "Avvio server"

# Avvia uvicorn in background per il setup
if [[ "${DO_SETUP}" == "true" ]]; then
  info "Avvio server temporaneo per setup…"

  # Avvia in background
  python3 -m uvicorn twin_api:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --log-level warning \
    &
  SERVER_PID=$!

  # Attendi che il server risponda
  MAX_WAIT=30
  ELAPSED=0
  printf "  Attendo server"
  while ! curl -sf "http://${HOST}:${PORT}/twin/stats" &>/dev/null 2>&1; do
    sleep 0.5
    ELAPSED=$((ELAPSED + 1))
    printf "."
    if [[ ${ELAPSED} -gt ${MAX_WAIT} ]]; then
      echo ""
      err "Server non risponde dopo ${MAX_WAIT}s"
      kill "${SERVER_PID}" 2>/dev/null || true
      exit 1
    fi
  done
  echo ""
  ok "Server pronto"

  # Esegui il setup
  info "Esecuzione POST /twin/setup…"
  SETUP_RESPONSE=$(curl -sf -X POST \
    "http://${HOST}:${PORT}/twin/setup" \
    -H "Content-Type: application/json" \
    -d "${SETUP_JSON}" 2>&1) || {
    err "Setup fallito: ${SETUP_RESPONSE}"
    kill "${SERVER_PID}" 2>/dev/null || true
    exit 1
  }

  # Mostra risultato setup
  echo ""
  echo -e "  ${BOLD}Profilo generato:${NC}"
  echo "${SETUP_RESPONSE}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'    Nome:           {d.get(\"twin\", \"?\")}')
    print(f'    Nascita:        {d.get(\"birth_year\", \"?\")}')
    print(f'    Morte:          {d.get(\"death_year\") or \"in vita\"}')
    print(f'    Lingua:         {d.get(\"language\", \"?\")}')
    print(f'    Valori:         {\", \".join(d.get(\"values\") or [])}')
    if d.get('epitaph'):
        print(f'    Epitaffio:      \"{d[\"epitaph\"]}\"')
    inferred = d.get('inferred_fields', [])
    if inferred:
        print(f'    Inferiti:       {\", \".join(inferred)}')
    print(f'    Profilo salvato: {d.get(\"profile_file\", \"?\")}')
    print(f'    Ricordi:        {d.get(\"memories\", \"?\")}')
except Exception as e:
    print(sys.stdin.read())
" 2>/dev/null || echo "    ${SETUP_RESPONSE}"

  echo ""

  # Ferma il server background e riavvia in foreground
  kill "${SERVER_PID}" 2>/dev/null || true
  wait "${SERVER_PID}" 2>/dev/null || true
  sleep 0.5
fi

# ── Avvio finale in foreground ────────────────────────────────
echo "────────────────────────────────────────────────"
info "Twin API:   http://${HOST}:${PORT}"
info "Swagger UI: http://${HOST}:${PORT}/docs"
info "Twin UI:    apri twin_ui.html nel browser"
echo "────────────────────────────────────────────────"
echo ""

exec python3 -m uvicorn twin_api:app \
  --host "${HOST}" \
  --port "${PORT}" \
  ${RELOAD} \
  --log-level info