# MNHEME Digital Twin

Sistema per creare un gemello digitale emotivo di una persona reale — consultabile dai discendenti dopo la morte. Non è un chatbot: risponde **esclusivamente** con quello che la persona ha davvero vissuto e registrato in MNHEME. Se non ha ricordi su un tema, lo dichiara esplicitamente.

---

## File del sistema

```
apps/twins/
├── run.sh              ← script di avvio (lancia da qui)
├── twin_api.py         ← REST API FastAPI (porta 8001)
├── digital_twin.py     ← motore cognitivo
├── twin_ui.html        ← interfaccia per i discendenti
├── twin_ui.css         ← stili con 20 temi light/dark
├── twin_ui.js          ← logica UI
└── character/          ← cartella dei personaggi
    ├── mario_rossi/
    │   └── mario_rossi-twin_profile.json
    ├── maria_bianchi/
    │   └── maria_bianchi-twin_profile.json
    └── ...
```

Il twin legge lo stesso `.mnheme` di MNHEME — nessuna duplicazione dei dati.

---

## Avvio rapido

```bash
cd apps/twins
chmod +x run.sh

# Setup automatico — inferisce tutto dai ricordi
./run.sh

# Con nome e date esplicite
./run.sh --name "Mario Rossi" --birth-year 1942 --death-year 2024

# Riavvio rapido (profilo già creato)
./run.sh --character mario_rossi --no-setup
```

Poi apri `twin_ui.html` nel browser.
API docs: `http://localhost:8001/docs`

---

## Struttura dei personaggi

Ogni personaggio ha la sua cartella dedicata:

```
apps/twins/character/
└── mario_rossi/
    └── mario_rossi-twin_profile.json
```

Il nome della cartella è lo **slug** del nome completo (`Mario Rossi` → `mario_rossi`). Il profilo JSON viene creato automaticamente dal setup analizzando i ricordi.

Per avere più twin attivi contemporaneamente su porte diverse:

```bash
# Terminale 1
./run.sh --character mario_rossi --port 8001 --no-setup

# Terminale 2
./run.sh --character maria_bianchi --port 8002 --no-setup
```

---

## Opzioni `run.sh`

### Server

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--port PORT` | `8001` | Porta uvicorn |
| `--host HOST` | `0.0.0.0` | Host — `0.0.0.0` per rete locale |
| `--reload` | off | Auto-reload uvicorn (sviluppo) |
| `--no-setup` | off | Salta il setup, usa profilo esistente |

### Database e config

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--db PATH` | `../../mnheme.mnheme` | Path al database |
| `--env PATH` | `../../.env` | Path al file `.env` |
| `--provider NAME` | dal `.env` | Provider LLM (es: `lm-studio`, `groq`) |
| `--profile PATH` | auto | Path esplicito al file profilo `.json` |
| `--character NAME` | *(nessuno)* | Nome personaggio → cerca in `character/<slug>/` |
| `--characters-dir DIR` | `./character` | Directory radice dei personaggi |

### Profilo twin — tutti opzionali

I campi non forniti vengono **inferiti automaticamente** dai ricordi via LLM.

| Flag | Descrizione |
|------|-------------|
| `--name NAME` | Nome completo |
| `--birth-year YEAR` | Anno di nascita |
| `--death-year YEAR` | Anno di morte |
| `--language LANG` | Lingua delle risposte |
| `--voice NOTES` | Note sulla voce narrativa |
| `--values LIST` | Valori separati da virgola: `famiglia,lavoro,onestà` |
| `--epitaph TEXT` | Frase epitaffio |
| `--curator NAME` | Nome del curatore |
| `--embargo N` | Anni di embargo post-mortem (default: `0`) |

### Esempi

```bash
# Inferisce tutto dai ricordi
./run.sh

# Parametri biografici certi, resto inferito
./run.sh --name "Mario Rossi" --birth-year 1942 --death-year 2024

# Personaggio già configurato — riavvio senza LLM
./run.sh --character mario_rossi --no-setup

# Sviluppo
./run.sh --character mario_rossi --no-setup --reload

# DB non standard
./run.sh --db ../../data/vita.mnheme --port 8002

# Rete locale
./run.sh --host 0.0.0.0 --provider lm-studio
```

---

## Come funziona il setup

```
1. Controlla prerequisiti (Python, uvicorn, .mnheme, .env)
2. Avvia il server in background
3. Attende che risponda (max 30s)
4. POST /twin/setup — per ogni campo non fornito, il LLM
   analizza i ricordi e inferisce nome, voce, valori, epitaffio
5. Crea  character/<slug>/  e salva  <slug>-twin_profile.json
6. Mostra il profilo con i campi inferiti evidenziati
7. Riavvia il server in foreground (Ctrl+C per fermare)
```

Il profilo persiste tra i riavvii — `--no-setup` lo carica direttamente senza invocare l'LLM.

**Risoluzione del profilo (priorità):**
1. `$TWIN_PROFILE` — path esplicito
2. `$TWIN_CHARACTER` → `character/<slug>/<slug>-twin_profile.json`
3. Nome del `.mnheme` come slug → stesso schema
4. Legacy — `<db_stem>-twin_profile.json` accanto al db

---

## Livelli di accesso

| Tier | Valore | Accesso |
|------|--------|---------|
| Pubblico | `public` | Feeling positivi, nessun tag `privato/intimo/segreto/riservato` |
| Familiare | `family` | Tutto tranne `privato`, `intimo`, `segreto` |
| Intimo | `intimate` | Tutto tranne `segreto` |
| Completo | `full` | Accesso totale |

### Tag di controllo visibilità

Aggiungi questi tag ai ricordi in MNHEME:

| Tag | Effetto |
|-----|---------|
| `privato` | Nascosto a PUBLIC e FAMILY |
| `intimo` | Nascosto a PUBLIC e FAMILY, soggetto a embargo |
| `segreto` | Nascosto a tutti tranne FULL |
| `riservato` | Nascosto a PUBLIC |
| `pubblico` | Visibile a PUBLIC anche se feeling negativo |

### Embargo post-mortem

Con `--embargo N`, i ricordi intimi rimangono inaccessibili ai tier PUBLIC e FAMILY per N anni dalla morte.

---

## API REST

Server: `http://localhost:8001` — docs: `http://localhost:8001/docs`

### `POST /twin/setup`

Configura il profilo. Tutti i campi sono opzionali — i mancanti vengono inferiti dai ricordi.

```bash
curl -X POST http://localhost:8001/twin/setup \
  -H "Content-Type: application/json" \
  -d '{"name": "Mario Rossi", "birth_year": 1942, "death_year": 2024}'
```

Risposta:
```json
{
  "twin": "Mario Rossi",
  "birth_year": 1942,
  "values": ["famiglia", "lavoro", "onestà"],
  "epitaph": "Ho fatto quello che ho potuto.",
  "inferred_fields": ["language", "values", "epitaph", "voice_notes"],
  "profile_file": "apps/twins/character/mario_rossi/mario_rossi-twin_profile.json",
  "memories": 247
}
```

### `GET /twin/profile`

Stato e identità del twin. Include `character_slug` e `character_dir`.

### `POST /twin/ask`

Domanda al twin. Risponde in prima persona basandosi **solo** sui ricordi reali.

```bash
curl -X POST http://localhost:8001/twin/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Cosa ti ha insegnato la perdita di tuo padre?", "tier": "family"}'
```

Se i ricordi non bastano: *"Non ho ricordi che mi permettano di rispondere."* — mai inventa.

### `POST /twin/letter`

Lettera scritta dal twin, ancorata ai ricordi reali.

```bash
curl -X POST http://localhost:8001/twin/letter \
  -d '{"to": "mia figlia Elena", "theme": "il coraggio", "tier": "family"}'
```

### `GET /twin/legacy`

Eredità emotiva: ritratto, valori vissuti, tensioni irrisolte, messaggio finale, arco emotivo.

```bash
curl "http://localhost:8001/twin/legacy?tier=family"
```

### `GET /twin/timeline/{concept}`

Arco emotivo di un concept nel tempo.

```bash
curl "http://localhost:8001/twin/timeline/lavoro?tier=family"
```

### `GET /twin/characters`

Lista di tutti i personaggi in `character/`. Usato dalla UI per il selettore.

```bash
curl "http://localhost:8001/twin/characters"
```

Risposta:
```json
{
  "characters": [
    {
      "slug": "mario_rossi",
      "name": "Mario Rossi",
      "birth_year": 1942,
      "death_year": 2024,
      "active": true
    },
    {
      "slug": "maria_bianchi",
      "name": "Maria Bianchi",
      "birth_year": 1958,
      "death_year": null,
      "active": false
    }
  ],
  "directory": "apps/twins/character",
  "current": "mario_rossi"
}
```

### `GET /twin/memories`

Ricordi accessibili per tier.

```bash
curl "http://localhost:8001/twin/memories?tier=family&limit=20"
curl "http://localhost:8001/twin/memories?tier=family&concept=famiglia"
```

### `GET /twin/stats`

Statistiche memoria per tier.

---

## Interfaccia utente

Apri `twin_ui.html` nel browser — si connette automaticamente usando lo stesso host della pagina (evita problemi CORS `localhost` vs `127.0.0.1`).

### 20 temi

La UI include 20 temi selezionabili dalla griglia in fondo alla sidebar, salvati in `localStorage`:

**Light (10):** Pergamena *(default)*, Avorio, Lino, Salvia, Nuvola, Rosa, Sabbia, Menta, Pietra, Frumento

**Dark (10):** Ossidiana, Mezzanotte, Foresta, Brace, Ardesia, Seppia, Viola, Grafite, Oceano, Bronzo

### Selettore personaggio

Se `character/` contiene più personaggi configurati, compare un selettore in sidebar che mostra nome, date e personaggio attivo. Clic su un personaggio inattivo mostra il comando per riavviare il server su quel personaggio.

### Quattro viste

- **Consulta** — chat in prima persona. Ogni risposta mostra ricordi usati e livello di confidenza.
- **Lettera** — genera una lettera a un destinatario su un tema specifico.
- **Eredità** — ritratto psicologico completo: ritratto, valori vissuti, irrisolto, messaggio, arco emotivo.
- **Arco nel tempo** — timeline emotiva di un concept con colori per feeling.

---

## Struttura del codice

```
digital_twin.py
├── AccessTier           public | family | intimate | full
├── TwinProfile          identità, voce, embargo, epitaffio
├── TwinVault            filtra MemoryDB per tier e embargo
└── DigitalTwin
    ├── ask()            RAG → risposta in prima persona
    ├── letter()         lettera ancorata ai ricordi
    ├── legacy()         analisi completa della vita
    └── timeline()       evoluzione emotiva nel tempo

twin_api.py
├── _CHARACTERS_DIR      apps/twins/character/
├── _character_dir()     → character/<slug>/
├── _slugify()           normalizza nome a slug filesystem-safe
├── _resolve_profile_path()  risoluzione profilo in 4 livelli
├── _infer_profile_from_db() inferisce profilo dai ricordi via LLM
│
├── POST /twin/setup         configura o rigenera il profilo
├── GET  /twin/profile       stato + character_slug + character_dir
├── POST /twin/ask           consulta il twin
├── POST /twin/letter        genera lettera
├── GET  /twin/legacy        eredità emotiva
├── GET  /twin/timeline/{c}  arco emotivo
├── GET  /twin/memories      ricordi per tier
├── GET  /twin/characters    lista personaggi in character/
└── GET  /twin/stats         statistiche per tier

twin_ui.html / twin_ui.css / twin_ui.js
├── 20 temi CSS (10 light + 10 dark), salvati in localStorage
├── Selettore personaggio (da /twin/characters)
├── Selettore tier (public / family / intimate)
└── 4 viste: Consulta, Lettera, Eredità, Arco nel tempo
```

---

## Principi etici

1. **Fedeltà** — risponde solo con ricordi reali. Mai inferenze generiche del modello.
2. **Voce** — in prima persona con la voce della persona, non del modello LLM.
3. **Accesso graduato** — quattro tier con regole precise su cosa è visibile a chi.
4. **Embargo** — periodo configurabile durante cui i ricordi intimi restano inaccessibili.
5. **Trasparenza** — ogni risposta indica quanti ricordi sono stati usati e la confidenza.