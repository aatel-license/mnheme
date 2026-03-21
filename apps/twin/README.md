# MNHEME Digital Twin

Sistema per creare un gemello digitale emotivo di una persona reale — consultabile dai discendenti dopo la morte. Non è un chatbot: risponde **esclusivamente** con quello che la persona ha davvero vissuto e registrato in MNHEME. Se non ha ricordi su un tema, lo dichiara esplicitamente.

---

## File del sistema

```
apps/twin/
├── run.sh              ← script di avvio (lancia da qui)
├── twin_api.py         ← REST API FastAPI (porta 8001)
├── digital_twin.py     ← motore cognitivo
└── twin_ui.html        ← interfaccia per i discendenti
```

Il twin legge lo stesso database `.mnheme` di MNHEME — nessuna duplicazione dei dati.

---

## Avvio rapido

```bash
cd apps/twin
chmod +x run.sh

# Setup automatico — inferisce tutto dai ricordi
./run.sh

# Con parametri espliciti
./run.sh --name "Mario Rossi" --birth-year 1942 --death-year 2024
```

Poi apri `twin_ui.html` nel browser.
API docs: `http://localhost:8001/docs`

---

## Opzioni `run.sh`

### Server

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--port PORT` | `8001` | Porta uvicorn |
| `--host HOST` | `127.0.0.1` | Host (usa `0.0.0.0` per rete locale) |
| `--reload` | off | Auto-reload uvicorn (sviluppo) |
| `--no-setup` | off | Salta il setup, usa profilo esistente |

### Database e config

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--db PATH` | `../../mnheme.mnheme` | Path al database |
| `--env PATH` | `../../.env` | Path al file `.env` con i provider LLM |
| `--provider NAME` | dal `.env` | Provider LLM (es: `lm-studio`, `groq`) |
| `--profile PATH` | auto | Path al file profilo `.json` |

### Profilo twin — tutti opzionali

I campi non forniti vengono **inferiti automaticamente** analizzando i ricordi nel database via LLM.

| Flag | Descrizione |
|------|-------------|
| `--name NAME` | Nome completo della persona |
| `--birth-year YEAR` | Anno di nascita |
| `--death-year YEAR` | Anno di morte (`None` = ancora in vita) |
| `--language LANG` | Lingua delle risposte (default: rilevata dai ricordi) |
| `--voice NOTES` | Note sulla voce narrativa (tono, stile, modi di dire) |
| `--values LIST` | Valori separati da virgola: `famiglia,lavoro,onestà` |
| `--epitaph TEXT` | Frase epitaffio |
| `--curator NAME` | Nome del curatore del twin |
| `--embargo N` | Anni di embargo post-mortem per ricordi intimi (default: `0`) |

### Esempi

```bash
# Tutto inferito dai ricordi
./run.sh

# Parametri biografici certi, il resto inferito
./run.sh --name "Mario Rossi" --birth-year 1942 --death-year 2024

# Database non standard
./run.sh --db ../../data/vita.mnheme --port 8002

# Riavvio senza rigenerare il profilo
./run.sh --no-setup

# Sviluppo con auto-reload
./run.sh --no-setup --reload

# Esposto sulla rete locale
./run.sh --host 0.0.0.0 --provider lm-studio

# Più twin contemporaneamente
./run.sh --db ../../mario.mnheme --port 8001
./run.sh --db ../../maria.mnheme --port 8002
```

---

## Come funziona il setup

Il `run.sh` esegue queste fasi in sequenza:

```
1. Controlla prerequisiti (Python, uvicorn, .mnheme, .env)
2. Avvia il server in background
3. Attende che risponda (max 30s)
4. POST /twin/setup con i parametri forniti
   └── per ogni campo non fornito → LLM analizza i ricordi e inferisce
5. Mostra il profilo generato con i campi inferiti evidenziati
6. Riavvia il server in foreground (Ctrl+C per fermare)
```

Il profilo viene salvato come `<db>-twin_profile.json` nella stessa directory del database:

```
mnheme.mnheme                  ← database ricordi
mnheme-twin_profile.json       ← profilo generato (persiste tra i riavvii)
```

Ai prossimi avvii con `--no-setup` il profilo viene caricato direttamente senza invocare l'LLM.

---

## Livelli di accesso

Ogni richiesta specifica un livello di accesso che determina quali ricordi sono visibili.

| Tier | Valore | Accesso |
|------|--------|---------|
| Pubblico | `public` | Solo ricordi con feeling positivi e senza tag `privato`, `intimo`, `segreto`, `riservato` |
| Familiare | `family` | Tutti i ricordi tranne quelli con tag `privato`, `intimo`, `segreto` |
| Intimo | `intimate` | Tutti i ricordi tranne quelli con tag `segreto` |
| Completo | `full` | Accesso totale — per ricercatori o terapeuti designati |

### Embargo post-mortem

Con `--embargo N`, i ricordi con feeling pesanti (vergogna, imbarazzo, senso di colpa) e tag `intimo` rimangono inaccessibili ai tier PUBLIC e FAMILY per N anni dalla morte. Utile per proteggere informazioni sensibili nelle fasi iniziali del lutto.

### Marcare i ricordi

Aggiungi questi tag ai ricordi in MNHEME per controllare la visibilità:

```
tag: privato     → nascosto a PUBLIC e FAMILY
tag: intimo      → nascosto a PUBLIC e FAMILY (soggetto a embargo)
tag: segreto     → nascosto a tutti tranne FULL
tag: pubblico    → visibile a PUBLIC anche se feeling negativo
tag: riservato   → nascosto a PUBLIC
```

---

## API REST

Server: `http://localhost:8001`
Documentazione interattiva: `http://localhost:8001/docs`

### `POST /twin/setup`

Configura il profilo del twin. Tutti i campi sono opzionali — quelli mancanti vengono inferiti dai ricordi.

```bash
curl -X POST http://localhost:8001/twin/setup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mario Rossi",
    "birth_year": 1942,
    "death_year": 2024
  }'
```

Risposta:
```json
{
  "twin": "Mario Rossi",
  "birth_year": 1942,
  "language": "italiano",
  "values": ["famiglia", "lavoro", "onestà"],
  "epitaph": "Ho fatto quello che ho potuto.",
  "inferred_fields": ["language", "values", "epitaph", "voice_notes"],
  "profile_file": "mnheme-twin_profile.json",
  "memories": 247
}
```

### `GET /twin/profile`

Stato e identità del twin.

```bash
curl http://localhost:8001/twin/profile
```

### `POST /twin/ask`

Domanda al twin. Risponde in prima persona basandosi **solo** sui ricordi reali.

```bash
curl -X POST http://localhost:8001/twin/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Cosa ti ha insegnato la perdita di tuo padre?",
    "tier": "family"
  }'
```

Risposta:
```json
{
  "response": "Quando mio padre è morto avevo 34 anni...",
  "confidence": "alta — 5 ricordi diretti",
  "caveat": "",
  "memories_used": 5,
  "tier": "family"
}
```

Se i ricordi non bastano, il twin risponde: *"Non ho ricordi che mi permettano di rispondere a questa domanda."* — mai inventa.

### `POST /twin/letter`

Genera una lettera scritta dal twin, ancorata ai ricordi reali.

```bash
curl -X POST http://localhost:8001/twin/letter \
  -H "Content-Type: application/json" \
  -d '{
    "to": "mia figlia Elena",
    "theme": "il coraggio",
    "tier": "family"
  }'
```

### `GET /twin/legacy`

Eredità emotiva completa: ritratto, valori vissuti, tensioni irrisolte, messaggio finale, arco emotivo.

```bash
curl "http://localhost:8001/twin/legacy?tier=family"
```

### `GET /twin/timeline/{concept}`

Arco emotivo di un concept nel tempo — come è cambiato il rapporto emotivo con quel tema lungo tutta la vita.

```bash
curl "http://localhost:8001/twin/timeline/lavoro?tier=family"
curl "http://localhost:8001/twin/timeline/padre?tier=intimate"
```

### `GET /twin/memories`

Ricordi accessibili per tier, con excerpt.

```bash
curl "http://localhost:8001/twin/memories?tier=family&limit=20"
curl "http://localhost:8001/twin/memories?tier=family&concept=famiglia"
```

### `GET /twin/stats`

Statistiche della memoria per tier (totale ricordi visibili, distribuzione emotiva, concetti dominanti).

---

## Interfaccia utente (`twin_ui.html`)

Apri `twin_ui.html` nel browser. Si connette automaticamente a `localhost:8001`.

Quattro sezioni:

- **Consulta** — chat in prima persona con il twin. Ogni risposta mostra il numero di ricordi usati come contesto e il livello di confidenza.
- **Lettera** — genera una lettera a un destinatario su un tema specifico.
- **Eredità** — ritratto psicologico completo con valori, irrisolto e messaggio finale.
- **Arco nel tempo** — timeline emotiva di un concept con colori per feeling.

Il selettore del tier è sempre visibile in sidebar — il discendente sa esattamente quale profondità sta accedendo.

---

## Struttura del codice

```
digital_twin.py
│
├── AccessTier           public | family | intimate | full
├── TwinProfile          identità, voce, embargo, epitaffio
├── TwinVault            filtra MemoryDB per tier e embargo
│
├── ConsultationResult   risposta ask()
├── LetterResult         lettera generata
├── LegacyResult         eredità emotiva completa
├── TimelineResult       arco emotivo di un concept
│
└── DigitalTwin          motore principale
    ├── ask()            RAG con risposta in prima persona
    ├── letter()         lettera ancorata ai ricordi
    ├── legacy()         analisi completa della vita
    └── timeline()       evoluzione emotiva nel tempo

twin_api.py
│
├── _infer_profile_from_db()   inferisce profilo dai ricordi via LLM
├── _resolve_profile_path()    trova il file profilo (.twin_profile.json)
├── _make_llm()                costruisce il provider dal .env
│
├── POST /twin/setup           configura o rigenera il profilo
├── GET  /twin/profile         stato del twin
├── POST /twin/ask             consulta il twin
├── POST /twin/letter          genera lettera
├── GET  /twin/legacy          eredità emotiva
├── GET  /twin/timeline/{c}    arco emotivo
├── GET  /twin/memories        ricordi accessibili
└── GET  /twin/stats           statistiche per tier
```

---

## Principi etici

Il sistema è costruito attorno a cinque principi:

1. **Fedeltà** — il twin risponde solo con ricordi reali. Mai inferenze generiche del modello.
2. **Voce** — risponde in prima persona con la voce della persona, non del modello LLM.
3. **Accesso graduato** — quattro tier con regole precise su cosa è visibile a chi.
4. **Embargo** — periodo configurabile durante cui certi ricordi intimi rimangono inaccessibili.
5. **Trasparenza** — ogni risposta indica quanti ricordi sono stati usati e con quale confidenza.