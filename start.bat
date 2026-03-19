@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

:: ═══════════════════════════════════════════════════════════════
::  MNHEME — Start Script (Windows)
::  Human Memory Database
:: ═══════════════════════════════════════════════════════════════

:: ── Configurazione ─────────────────────────────────────────────
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "VENV_DIR=%SCRIPT_DIR%\.venv"
set "ENV_FILE=%SCRIPT_DIR%\.env"
set "ENV_EXAMPLE=%SCRIPT_DIR%\.env.example"
set "DB_DEFAULT=%SCRIPT_DIR%\mente.mnheme"
set "LOG_DIR=%SCRIPT_DIR%\logs"
set "PID_FILE=%SCRIPT_DIR%\.mnheme_api.pid"
set "API_HOST=0.0.0.0"
set "API_PORT=8000"
set "BENCH_RECORDS=2000"
set "BENCH_OUTPUT="
set "MODE=interactive"

:: ── Parsing argomenti ──────────────────────────────────────────
:parse_args
if "%~1"=="" goto :after_parse
if /i "%~1"=="--api"       ( set "MODE=api"       & shift & goto :parse_args )
if /i "%~1"=="--benchmark" ( set "MODE=benchmark"  & shift & goto :parse_args )
if /i "%~1"=="--examples"  ( set "MODE=examples"   & shift & goto :parse_args )
if /i "%~1"=="--test"      ( set "MODE=test"        & shift & goto :parse_args )
if /i "%~1"=="--tests"     ( set "MODE=test"        & shift & goto :parse_args )
if /i "%~1"=="--stop"      ( goto :stop_api )
if /i "%~1"=="--help"      ( goto :print_help )
if /i "%~1"=="-h"          ( goto :print_help )
if /i "%~1"=="--host"      ( set "API_HOST=%~2"      & shift & shift & goto :parse_args )
if /i "%~1"=="--port"      ( set "API_PORT=%~2"      & shift & shift & goto :parse_args )
if /i "%~1"=="--db"        ( set "DB_DEFAULT=%~2"   & shift & shift & goto :parse_args )
if /i "%~1"=="--records"   ( set "BENCH_RECORDS=%~2" & shift & shift & goto :parse_args )
if /i "%~1"=="--output"    ( set "BENCH_OUTPUT=%~2"  & shift & shift & goto :parse_args )
echo   [ERR] Opzione sconosciuta: %~1
echo   Usa --help per la lista opzioni.
exit /b 1
:after_parse

:: ── Banner ─────────────────────────────────────────────────────
:print_banner
echo.
echo   =====================================================
echo   M  N  H  E  M  E
echo   Human Memory Database
echo   append-only  .  immutabile  .  senziente
echo   =====================================================
echo.
goto :eof_banner
:eof_banner

call :print_banner

:: ── CD nella directory del progetto ───────────────────────────
cd /d "%SCRIPT_DIR%"

:: ── 1. Check Python ────────────────────────────────────────────
echo   [1/6] Verifica Python
echo.

set "PYTHON="
for %%P in (python3.12 python3.11 python3 python py) do (
    if "!PYTHON!"=="" (
        where %%P >nul 2>&1
        if not errorlevel 1 (
            for /f "tokens=*" %%V in ('%%P -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}')" 2^>nul') do (
                set "VER=%%V"
            )
            for /f "tokens=1,2 delims=." %%A in ("!VER!") do (
                set "MAJOR=%%A"
                set "MINOR=%%B"
            )
            if !MAJOR! GEQ 3 (
                if !MINOR! GEQ 11 (
                    set "PYTHON=%%P"
                )
            )
        )
    )
)

if "!PYTHON!"=="" (
    echo   [ERR] Python 3.11+ non trovato.
    echo   Scarica Python: https://www.python.org/downloads/
    echo   Oppure installa da Microsoft Store: ms-windows-store://pdp/?productid=9NRWMJLQARVP
    pause
    exit /b 1
)

for /f "tokens=*" %%V in ('!PYTHON! --version 2^>&1') do set "PY_VER=%%V"
echo   [OK] !PY_VER! trovato  ^(cmd: !PYTHON!^)
echo.

:: ── 2. Virtual Environment ─────────────────────────────────────
echo   [2/6] Virtual Environment
echo.

if exist "%VENV_DIR%\Scripts\python.exe" (
    echo   [OK] venv gia presente: %VENV_DIR%
) else (
    echo   [ ] Creazione venv in %VENV_DIR%...
    !PYTHON! -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo   [ERR] Creazione venv fallita
        pause
        exit /b 1
    )
    echo   [OK] venv creato
)

:: Attiva il venv
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo   [ERR] Attivazione venv fallita
    pause
    exit /b 1
)

for /f "tokens=*" %%V in ('python --version 2^>&1') do set "ACTIVE_PY=%%V"
echo   [OK] venv attivato  ^(%ACTIVE_PY%^)
echo.

:: ── 3. Dipendenze ──────────────────────────────────────────────
echo   [3/6] Dipendenze
echo.
echo   [OK] Core MNHEME: nessuna dipendenza esterna richiesta

if "%MODE%"=="api" (
    echo   [ ] Installazione dipendenze API ^(fastapi, uvicorn^)...
    pip install --quiet fastapi uvicorn
    if errorlevel 1 (
        echo   [ERR] Installazione dipendenze API fallita
        pause
        exit /b 1
    )
    echo   [OK] FastAPI + Uvicorn installati
) else (
    python -c "import fastapi" >nul 2>&1
    if not errorlevel 1 (
        echo   [OK] FastAPI gia installato  ^(API disponibile^)
    ) else (
        echo   [WARN] FastAPI non installato  ^(API REST non disponibile^)
        echo   [INFO] Per abilitare: start.bat --api  oppure  pip install fastapi uvicorn
    )
)
echo.

:: ── 4. File .env ───────────────────────────────────────────────
echo   [4/6] Configurazione .env
echo.

if exist "%ENV_FILE%" (
    echo   [OK] .env trovato: %ENV_FILE%

    :: Conta provider configurati
    set "CONFIGURED=0"
    for /f "usebackq tokens=1,* delims==" %%K in ("%ENV_FILE%") do (
        set "KEY=%%K"
        set "VAL=%%L"
        echo !KEY! | findstr /r "^[A-Z_]*_URL$" >nul 2>&1
        if not errorlevel 1 (
            if not "!VAL!"=="" (
                echo !VAL! | findstr /i "http" >nul 2>&1
                if not errorlevel 1 (
                    set /a CONFIGURED+=1
                    echo   [INFO] Provider: !KEY:_URL=!  -^>  !VAL!
                )
            )
        )
    )
    if !CONFIGURED!==0 (
        echo   [WARN] Nessun provider configurato nel .env
        echo   [INFO] Modifica %ENV_FILE% e aggiungi NOME_URL + NOME_MODEL
    )
) else (
    echo   [WARN] .env non trovato
    if exist "%ENV_EXAMPLE%" (
        echo   [ ] Copio .env.example -^> .env
        copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
        echo   [OK] .env creato da template
        echo   [WARN] Modifica %ENV_FILE% con le tue API key
    ) else (
        echo   [WARN] Crea un file .env con almeno:
        echo.
        echo      LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
        echo      LM_STUDIO_MODEL=local-model
        echo.
    )
)
echo.

:: ── 5. Smoke test ──────────────────────────────────────────────
echo   [5/6] Verifica sistema
echo.

python -c ^
"import sys; sys.path.insert(0,'.')" ^
"from mnheme import MemoryDB, Feeling, MediaType" ^
"db = MemoryDB(':memory:')" ^
"m  = db.remember('Test', Feeling.CURIOSITA, 'Smoke test OK')" ^
"assert db.count() == 1" ^
"print('  [OK] MemoryDB')"
if errorlevel 1 (
    echo   [ERR] MemoryDB smoke test fallito
    pause
    exit /b 1
)

python -c "import sys; sys.path.insert(0,'.'); from storage import StorageEngine; print('  [OK] StorageEngine')"
python -c "import sys; sys.path.insert(0,'.'); from index import IndexEngine; print('  [OK] IndexEngine')"
python -c "import sys; sys.path.insert(0,'.'); from fsprobe import FsProbe; p=FsProbe('.'); c=p.detect(); print(f'  [OK] FsProbe  fs={c.fs_type.value}  strategy={c.strategy.value}')"
python -c "import sys; sys.path.insert(0,'.'); from filestore import FileStore; print('  [OK] FileStore')"
python -c "import sys; sys.path.insert(0,'.'); from llm_provider import LLMProvider; print('  [OK] LLMProvider')"
python -c "import sys; sys.path.insert(0,'.'); from brain import Brain; print('  [OK] Brain')"

echo.
echo   [OK] Tutti i moduli verificati
echo.

:: ── 6. Avvio ───────────────────────────────────────────────────
echo   [6/6] Avvio
echo.

if "%MODE%"=="api"       goto :mode_api
if "%MODE%"=="benchmark" goto :mode_benchmark
if "%MODE%"=="examples"  goto :mode_examples
if "%MODE%"=="test"      goto :mode_test
goto :mode_interactive

:: ── Modalità: Shell interattiva ────────────────────────────────
:mode_interactive
echo   [OK] Avvio shell Python interattiva con MNHEME precaricato
echo   [INFO] Database: %DB_DEFAULT%
echo   [INFO] Digita exit() per uscire
echo.

python -i -c ^
"import sys, os; sys.path.insert(0,'%SCRIPT_DIR:\=/%'); os.chdir('%SCRIPT_DIR:\=/%')" ^
& python -i -c ^
"from mnheme import MemoryDB, Feeling, MediaType; from llm_provider import LLMProvider; from brain import Brain; db = MemoryDB('%DB_DEFAULT:\=/%'); print(f'db = {db}');^

try:^
  llm = LLMProvider.from_env('%ENV_FILE:\=/%'); brain = Brain(db,llm); print(f'brain = {llm.active_profile.name}')^
except Exception as e:^
  print(f'brain non disponibile: {e}'); llm=None; brain=None"

goto :end

:: ── Modalità: API REST ─────────────────────────────────────────
:mode_api
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo   [ERR] FastAPI non installato. Esegui: start.bat --api per installarlo
    pause
    exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set "LOG_FILE=%LOG_DIR%\mnheme_api.log"

echo   [OK] Avvio API REST su http://%API_HOST%:%API_PORT%
echo   [INFO] Swagger UI: http://localhost:%API_PORT%/docs
echo   [INFO] Log: %LOG_FILE%
echo   [INFO] Stop: Ctrl+C  oppure  start.bat --stop
echo.

set "MNHEME_DB_PATH=%DB_DEFAULT%"

:: Avvia uvicorn
start "MNHEME API" /b cmd /c ^
    "uvicorn mnheme_api:app --host %API_HOST% --port %API_PORT% --reload 2>&1 | tee %LOG_FILE%"

:: Salva PID (best effort su Windows)
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%API_PORT% " ^| findstr LISTENING 2^>nul') do (
    echo %%P > "%PID_FILE%"
    goto :api_started
)
:api_started
echo   [OK] API avviata
echo.

:: Attendi che risponda
set "RETRY=10"
:wait_api
if %RETRY% LEQ 0 goto :api_timeout
ping -n 2 127.0.0.1 >nul
curl -sf "http://localhost:%API_PORT%/stats" >nul 2>&1
if not errorlevel 1 (
    echo   [OK] API risponde su http://localhost:%API_PORT%
    start "" "http://localhost:%API_PORT%/docs"
    goto :end
)
set /a RETRY-=1
goto :wait_api
:api_timeout
echo   [WARN] API non risponde dopo 10 tentativi — controlla %LOG_FILE%
goto :end

:: ── Modalità: Benchmark ────────────────────────────────────────
:mode_benchmark
echo   [INFO] Avvio benchmark con %BENCH_RECORDS% record...
echo.

if "%BENCH_OUTPUT%"=="" (
    python mnheme_benchmark.py --records %BENCH_RECORDS%
) else (
    python mnheme_benchmark.py --records %BENCH_RECORDS% --output "%BENCH_OUTPUT%"
    echo.
    echo   [OK] Report salvato in: %BENCH_OUTPUT%
)
goto :end

:: ── Modalità: Examples ─────────────────────────────────────────
:mode_examples
echo   [INFO] Esecuzione esempi...
echo.
python examples.py
goto :end

:: ── Modalità: Test ─────────────────────────────────────────────
:mode_test
echo   [INFO] Esecuzione test suite...
echo.
python test_llm_provider.py
echo.
python test_fsprobe.py
echo.
echo   [OK] Tutti i test completati
goto :end

:: ── Stop API ───────────────────────────────────────────────────
:stop_api
echo   [INFO] Arresto API REST...
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    taskkill /PID !PID! /F >nul 2>&1
    del "%PID_FILE%"
    echo   [OK] API fermata ^(PID !PID!^)
) else (
    echo   [WARN] Nessuna istanza API trovata
    :: Prova a killare uvicorn per nome
    taskkill /IM uvicorn.exe /F >nul 2>&1
    if not errorlevel 1 (
        echo   [OK] Processo uvicorn terminato
    )
)
goto :end

:: ── Help ───────────────────────────────────────────────────────
:print_help
echo.
echo   UTILIZZO
echo     start.bat [opzioni]
echo.
echo   MODALITA'
echo     ^(nessuna^)           Shell Python interattiva con MNHEME precaricato
echo     --api               Avvia il server API REST ^(FastAPI + uvicorn^)
echo     --benchmark         Esegui la suite di benchmark
echo     --examples          Esegui gli esempi
echo     --test              Esegui i test
echo     --stop              Ferma il server API
echo.
echo   OPZIONI
echo     --host HOST         Host per l'API ^(default: 0.0.0.0^)
echo     --port PORT         Porta per l'API ^(default: 8000^)
echo     --db PATH           Path al file database ^(default: mente.mnheme^)
echo     --records N         Numero record per il benchmark ^(default: 2000^)
echo     --output FILE       Salva output benchmark in JSON
echo     --help, -h          Mostra questo aiuto
echo.
echo   ESEMPI
echo     start.bat                                  shell interattiva
echo     start.bat --api                            API REST su :8000
echo     start.bat --api --port 9000                API su porta custom
echo     start.bat --benchmark                      benchmark 2000 record
echo     start.bat --benchmark --records 10000 --output bench.json
echo     start.bat --test                           test suite
echo     start.bat --stop                           ferma API
echo.
goto :end

:: ── Fine ───────────────────────────────────────────────────────
:end
echo.
endlocal
