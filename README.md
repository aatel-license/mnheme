# MNHEME — Human Memory Database
![Alt text](https://github.com/aatel-license/mnheme/blob/main/imgs/mnheme_dark.png "mnheme")
# USE IT AT YOU OWN RISK
> *"La memoria non si sovrascrive. Si stratifica."*

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-c4933a?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-5a8f6a?style=flat-square)](https://github.com)
[![License: AATEL](https://img.shields.io/badge/license-aatel-yellow)](LICENSE)
[![Append Only](https://img.shields.io/badge/storage-append--only-c25444?style=flat-square)](#architecture)

**MNHEME** è un database ispirato alla memoria umana: append-only, immutabile, senziente.  
Nessun SQLite. Nessun ORM. Engine binario scritto da zero.  
Un cervello LLM agnostico per percepire, ricordare, riflettere.

---

## Perché MNHEME?

I database tradizionali trattano i dati come oggetti mutabili: si scrive, si aggiorna, si cancella. Ma i ricordi non funzionano così. Non puoi sovrascrivere ciò che hai vissuto — puoi solo ricordarlo in modo diverso, con un sentimento diverso, in un momento diverso.

MNHEME traduce questo principio in un sistema di storage:

- **Nessun `UPDATE`** — i dati sono immutabili dopo la scrittura
- **Nessun `DELETE`** — i ricordi si accumulano, non spariscono
- **Ogni ricordo porta un sentimento** — non solo dati, ma emozione
- **L'LLM è il cervello** — percepisce, associa, riflette sui dati

---

## Architettura

```
┌────────────────────────────────────────────────────┐
│                      Brain                          │
│   perceive · ask(RAG) · reflect · dream · introspect│
└──────────┬──────────────────────────────────────────┘
           │
  ┌────────┴────────────────────────┐
  │         LLMProvider              │
  │  agnostico .env · 30+ provider   │
  │  rate limiting · fallback        │
  └────────┬────────────────────────┘
           │
  ┌────────┴────────────────────────┐
  │          MemoryDB                │
  │  remember · recall · search      │
  │  reflect · export · import       │
  └──────┬──────────┬───────────────┘
         │          │
  ┌──────▼──┐  ┌────▼──────┐  ┌────────────┐
  │ Storage │  │   Index   │  │  FileStore │
  │ Engine  │  │  Engine   │  │  (media)   │
  │ .mnheme │  │  (RAM)    │  │  FsProbe   │
  └─────────┘  └───────────┘  └────────────┘
```

### Livelli

| Livello | File | Responsabilità |
|---------|------|----------------|
| **Brain** | `brain.py` | Operazioni cognitive LLM |
| **LLMProvider** | `llm_provider.py` | Provider agnostico da `.env` |
| **MemoryDB** | `mnheme.py` | API pubblica del database |
| **StorageEngine** | `storage.py` | Log binario append-only |
| **IndexEngine** | `index.py` | Indici in RAM per lookup O(1) |
| **FileStore** | `filestore.py` | Storage file fisici (media) |
| **FsProbe** | `fsprobe.py` | Rilevamento filesystem live |

---

## Quickstart

```python
from mnheme import MemoryDB, Feeling, MediaType

# Crea o apri un database
db = MemoryDB("mente.mnheme")

# Registra un ricordo — append-only, mai sovrascritto
mem = db.remember(
    concept    = "Debito",
    feeling    = Feeling.ANSIA,
    content    = "Ho firmato il mutuo oggi. 25 anni.",
    note       = "Era un mercoledì piovoso.",
    tags       = ["casa", "mutuo", "2024"],
)

# Richiama i ricordi di un concetto
ricordi = db.recall("Debito")
ricordi = db.recall("Debito", feeling=Feeling.ANSIA)
ricordi = db.recall("Debito", limit=5, oldest_first=True)

# Richiama per sentimento
tutti_i_nostalgici = db.recall_by_feeling(Feeling.NOSTALGIA)

# Ricerca full-text
results = db.search("mutuo")
results = db.search("natale", in_concept=False)

# Statistiche
db.list_concepts()          # concept → distribuzione emotiva
db.feeling_distribution()   # sentimento → count
db.concept_timeline("Debito")  # evoluzione emotiva nel tempo
db.count(concept="Debito", feeling="ansia")
```

---

## Il Brain — LLM come strato cognitivo

```python
from mnheme       import MemoryDB
from llm_provider import LLMProvider
from brain        import Brain

db    = MemoryDB("mente.mnheme")
llm   = LLMProvider.from_env(".env")   # legge il .env
brain = Brain(db, llm)
```

### `perceive()` — input grezzo → ricordo strutturato

```python
# L'LLM estrae concept, feeling, tags e arricchisce il testo
r = brain.perceive("Ho aperto la busta dalla banca. Le mani tremavano.")

print(r.extracted_concept)   # "Debito"
print(r.extracted_feeling)   # "paura"
print(r.extracted_tags)      # ["banca", "corpo", "ansia"]
print(r.enriched_content)    # testo arricchito con profondità psicologica
# Il ricordo è già salvato in MemoryDB — immutabile
```

### `ask()` — RAG su memoria personale

```python
# Risponde usando SOLO i ricordi reali come contesto
ans = brain.ask("Come mi sento rispetto al denaro?")

print(ans.answer)           # risposta basata sui tuoi ricordi
print(ans.memories_used)    # ricordi usati come contesto RAG
print(ans.confidence_note)  # "Certezza: alta — dati diretti dai ricordi"
```

### `reflect()` — analisi emotiva nel tempo

```python
ref = brain.reflect("Debito")
print(ref.arc)         # "da terrore silenzioso a serenità conquistata"
print(ref.reflection)  # analisi profonda dell'arco emotivo
```

### `dream()` — connessioni oniriche

```python
# Campiona ricordi da sentimenti diversi, trova il filo nascosto
dream = brain.dream(n_memories=8)
print(dream.connections)  # associazioni inattese, tema latente
```

### `introspect()` — ritratto psicologico

```python
intro = brain.introspect()
print(intro.portrait)          # chi sei, pattern, tensioni, risorse
print(intro.dominant_concepts) # ["Famiglia", "Lavoro", "Debito"]
print(intro.emotional_map)     # {"ansia": 8, "amore": 5, ...}
```

---

## LLMProvider — agnostico per design

Nessun SDK esterno. Solo `urllib` stdlib. Un solo `.env`.

```bash
# .env — compila quello che hai, lascia vuoto il resto

# Locale — nessuna chiave API necessaria
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=local-model
LM_STUDIO_RPM=60

# Cloud
GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...
GROQ_RPM=30

# Anthropic (rilevato automaticamente dall'URL)
ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_RPM=5

# Fallback a cascata
USE_MULTI_PROVIDER=true
TEMPERATURE=0.3
```

```python
llm = LLMProvider.from_env(".env")

# Cambia provider a runtime senza riavviare
llm.use("groq")
llm.use("lm-studio")   # zero costi, locale
llm.use("anthropic")

# Vedi tutti i provider disponibili
llm.list_providers()

# Priority personalizzata per il fallback
llm = LLMProvider.from_env(".env",
    priority=["lm-studio", "groq", "anthropic"])
```

**Provider supportati** (30+): LM Studio, Ollama, Anthropic, OpenAI, Groq, Mistral, Codestral, SambaNova, OpenRouter, Google AI Studio, Cerebras, NVIDIA NIM, Hugging Face, GitHub Models, Cohere, Together, Fireworks, Nebius, Hyperbolic, Novita, Upstage, Scaleway, Aliyun, AI21, Inference.net, Cloudflare, Vertex AI, e qualsiasi endpoint OpenAI-compatibile custom.

---

## FileStore — storage media adattivo

```python
# Allega un file fisico a un ricordo
mem, fe = db.remember_file(
    "Famiglia", Feeling.AMORE,
    "/foto/natale2024.jpg",
    note="Tutti insieme al pranzo"
)

# Allega dati binari direttamente (es. upload da API)
with open("voce.mp3", "rb") as f:
    mem, fe = db.remember_bytes("Viaggio", Feeling.NOSTALGIA, f.read(), "voce.mp3")

# Lettura
path = db.files.get_path(mem.memory_id)
data = db.files.get_bytes(mem.memory_id)
info = db.files.info()
```

### Strategia adattiva per filesystem

MNHEME rileva il filesystem al boot ed esegue probe live delle capabilities:

| Filesystem | Strategia | Note |
|------------|-----------|------|
| ext4, ZFS, NFS, 9p | **HARDLINK** | zero byte, stesso inode |
| btrfs, xfs, APFS | **REFLINK** | Copy-on-Write, zero blocchi |
| NTFS | **HARDLINK** | via `CreateHardLinkW` |
| FAT32, exFAT | **COPY_ATOMIC** | tmp + `os.replace()` |
| HDFS, S3FS, GCSFuse | **COPY_ATOMIC** | no inode locali |

---

## Formato fisico del file `.mnheme`

Il database è un file binario append-only:

```
┌──────────────┬──────────┬───────────────────┐
│  MAGIC (4B)  │ SIZE (4B)│  PAYLOAD (SIZE B) │
└──────────────┴──────────┴───────────────────┘

MAGIC   : [0x4D, 0x4E, 0x45, 0xE0]  — firma record
SIZE    : uint32 big-endian          — lunghezza payload
PAYLOAD : JSON UTF-8                 — dati del ricordo
```

Ogni scrittura è atomica e `fsync`-ata. I record troncati (crash mid-write) vengono saltati silenziosamente al riavvio. Gli indici in RAM vengono ricostruiti scansionando il file dall'inizio.

---

## Benchmark

Misurati su 2.000 record, Python 3.12, filesystem 9p:

| Operazione | Media | Throughput |
|-----------|-------|------------|
| `remember()` con fsync | 1.8 ms | 552 ops/s |
| `remember()` senza fsync | 0.2 ms | 4.632 ops/s |
| `count()` — pura RAM | ~0 ms | 2.774.322 ops/s |
| `feeling_distribution()` | 0.003 ms | 277.865 ops/s |
| `recall(concept, limit=10)` | 1.5 ms | 636 ops/s |
| `recall_by_feeling(limit=20)` | 3.0 ms | 332 ops/s |
| `recall_all()` — 2.000 record | 300 ms | 3 ops/s |
| `search()` full-text | 40 ms | ~49k record/s |
| `search(limit=5)` | 0.1 ms | 8.348 ops/s |
| Cold start (2.000 rec) | 40 ms | 49k rec/s indicizzati |

**Dimensione file:** ~374 B/record → ~36 MB per 100k record, ~357 MB per 1M record.

```bash
# Esegui i benchmark
python mnheme_benchmark.py --records 5000
python mnheme_benchmark.py --records 10000 --output report.json
```

---

## API REST (opzionale)

```bash
pip install fastapi uvicorn
uvicorn mnheme_api:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

```
POST /memories              → registra un ricordo
GET  /memories              → tutti i ricordi (filtri: feeling, limit)
GET  /memories/search?q=    → ricerca full-text
GET  /concepts              → lista concetti con statistiche
GET  /concepts/{concept}    → ricordi di un concetto
GET  /concepts/{concept}/timeline  → evoluzione emotiva
GET  /feelings              → sentimenti con statistiche
GET  /feelings/distribution → sentimento → count
GET  /stats                 → statistiche generali
GET  /export                → esporta JSON
```

---

## Struttura del progetto

```
mnheme/
├── mnheme.py           # Core — MemoryDB, Feeling, MediaType, Memory
├── storage.py          # Engine binario append-only
├── index.py            # Indici in RAM
├── fsprobe.py          # Rilevamento filesystem
├── filestore.py        # Storage file fisici
├── llm_provider.py     # Provider LLM agnostico da .env
├── brain.py            # Strato cognitivo LLM
├── mnheme_api.py       # REST API FastAPI (opzionale)
├── mnheme_benchmark.py # Suite di benchmark
├── examples.py         # Esempi d'uso
├── .env.example        # Template configurazione provider
└── tests/
    ├── test_llm_provider.py
    └── test_fsprobe.py
```

---

## Sentimenti supportati

`gioia` · `tristezza` · `rabbia` · `paura` · `nostalgia` · `amore` · `malinconia` · `serenità` · `sorpresa` · `ansia` · `gratitudine` · `vergogna` · `orgoglio` · `noia` · `curiosità`

## Tipi di media

`TEXT` · `IMAGE` · `VIDEO` · `AUDIO` · `DOC`

---

## Requisiti

- Python 3.12+
- Nessuna dipendenza esterna obbligatoria
- `fastapi` + `uvicorn` solo per l'API REST (opzionale)

---
## LOCAL TEST USING LM_STUDIO
# Usa LM Studio su localhost:1234 con il modello già caricato
python test_local_provider.py

# URL custom
python test_local_provider.py --url http://localhost:1234

# Forza un modello specifico
python test_local_provider.py --model "mistral-7b-instruct"

# Salva il database invece di cancellarlo dopo il test
python test_local_provider.py --db mente.mnheme

# Output verbose con traceback se qualcosa va male
python test_local_provider.py --verbose

---

## Licenza

AATEL — vedi [LICENSE](LICENSE)

---

<p align="center">
  <sub>MNHEME — dalla musa greca della memoria</sub><br>
  <sub><em>"Non puoi sovrascrivere ciò che hai vissuto. Puoi solo ricordarlo diversamente."</em></sub>
</p>
