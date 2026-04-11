# MNHEME — Human Memory Database
![Alt text](https://github.com/aatel-license/mnheme/blob/main/imgs/mnheme_dark.png "mnheme")

# USE IT AT YOUR OWN RISK
> *"Memory is not overwritten. It accumulates in layers."*

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-c4933a?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-5a8f6a?style=flat-square)](https://github.com)
[![License: AATEL](https://img.shields.io/badge/license-aatel-yellow)](LICENSE)
[![Append Only](https://img.shields.io/badge/storage-append--only-c25444?style=flat-square)](#architecture)

**MNHEME** is a database inspired by human memory: append-only, immutable, sentient.  
No SQLite. No ORM. Binary engine written from scratch.  
An LLM-agnostic brain to perceive, remember, and reflect.

---

## Why MNHEME?

Traditional databases treat data as mutable objects: you write, update, delete. But memories don't work that way. You can't overwrite what you've lived through — you can only remember it differently, with a different feeling, at a different moment.

MNHEME translates this principle into a storage system:

- **No `UPDATE`** — data is immutable after writing
- **No `DELETE`** — memories accumulate, they don't disappear
- **Every memory carries a feeling** — not just data, but emotion
- **The LLM is the brain** — it perceives, associates, reflects on the data

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│                      Brain                          │
│   perceive · ask(RAG) · reflect · dream · introspect│
└──────────┬──────────────────────────────────────────┘
           │
  ┌────────┴────────────────────────┐
  │         LLMProvider              │
  │  agnostic .env · 30+ providers   │
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

### Layers

| Layer | File | Responsibility |
|-------|------|----------------|
| **Brain** | `brain.py` | LLM cognitive operations |
| **LLMProvider** | `llm_provider.py` | Provider agnostic via `.env` |
| **MemoryDB** | `mnheme.py` | Public database API |
| **StorageEngine** | `storage.py` | Append-only binary log |
| **IndexEngine** | `index.py` | In-RAM indexes for O(1) lookup |
| **FileStore** | `filestore.py` | Physical file storage (media) |
| **FsProbe** | `fsprobe.py` | Live filesystem detection |

---

## Quickstart

```python
from mnheme import MemoryDB, Feeling, MediaType

# Create or open a database
db = MemoryDB("mind.mnheme")

# Store a memory — append-only, never overwritten
mem = db.remember(
    concept    = "Debt",
    feeling    = Feeling.ANXIETY,
    content    = "I signed the mortgage today. 25 years.",
    note       = "It was a rainy Wednesday.",
    tags       = ["home", "mortgage", "2024"],
)

# Recall memories for a concept
memories = db.recall("Debt")
memories = db.recall("Debt", feeling=Feeling.ANXIETY)
memories = db.recall("Debt", limit=5, oldest_first=True)

# Recall by feeling
all_nostalgic = db.recall_by_feeling(Feeling.NOSTALGIA)

# Full-text search
results = db.search("mortgage")
results = db.search("christmas", in_concept=False)

# Statistics
db.list_concepts()             # concept → emotional distribution
db.feeling_distribution()      # feeling → count
db.concept_timeline("Debt")    # emotional evolution over time
db.count(concept="Debt", feeling="anxiety")
```

---

## The Brain — LLM as cognitive layer

```python
from mnheme       import MemoryDB
from llm_provider import LLMProvider
from brain        import Brain

db    = MemoryDB("mind.mnheme")
llm   = LLMProvider.from_env(".env")   # reads from .env
brain = Brain(db, llm)
```

### `perceive()` — raw input → structured memory

```python
# The LLM extracts concept, feeling, tags and enriches the text
r = brain.perceive("I opened the envelope from the bank. My hands were shaking.")

print(r.extracted_concept)   # "Debt"
print(r.extracted_feeling)   # "fear"
print(r.extracted_tags)      # ["bank", "body", "anxiety"]
print(r.enriched_content)    # text enriched with psychological depth
# The memory is already saved in MemoryDB — immutable
```

### `ask()` — RAG on personal memory

```python
# Answers using ONLY real memories as context
ans = brain.ask("How do I feel about money?")

print(ans.answer)           # answer based on your memories
print(ans.memories_used)    # memories used as RAG context
print(ans.confidence_note)  # "Confidence: high — direct data from memories"
```

### `reflect()` — emotional analysis over time

```python
ref = brain.reflect("Debt")
print(ref.arc)         # "from silent terror to hard-won serenity"
print(ref.reflection)  # deep analysis of the emotional arc
```

### `dream()` — dream-like connections

```python
# Samples memories from different feelings, finds the hidden thread
dream = brain.dream(n_memories=8)
print(dream.connections)  # unexpected associations, latent theme
```

### `introspect()` — psychological portrait

```python
intro = brain.introspect()
print(intro.portrait)          # who you are, patterns, tensions, resources
print(intro.dominant_concepts) # ["Family", "Work", "Debt"]
print(intro.emotional_map)     # {"anxiety": 8, "love": 5, ...}
```

---

## LLMProvider — agnostic by design

No external SDK. Just stdlib `urllib`. A single `.env`.

```bash
# .env — fill in what you have, leave the rest empty

# Local — no API key required
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=local-model
LM_STUDIO_RPM=60

# Cloud
GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...
GROQ_RPM=30

# Anthropic (auto-detected from URL)
ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_RPM=5

# Cascading fallback
USE_MULTI_PROVIDER=true
TEMPERATURE=0.3
```

```python
llm = LLMProvider.from_env(".env")

# Switch provider at runtime without restarting
llm.use("groq")
llm.use("lm-studio")   # zero cost, local
llm.use("anthropic")

# See all available providers
llm.list_providers()

# Custom priority for fallback
llm = LLMProvider.from_env(".env",
    priority=["lm-studio", "groq", "anthropic"])
```

**Supported providers** (30+): LM Studio, Ollama, Anthropic, OpenAI, Groq, Mistral, Codestral, SambaNova, OpenRouter, Google AI Studio, Cerebras, NVIDIA NIM, Hugging Face, GitHub Models, Cohere, Together, Fireworks, Nebius, Hyperbolic, Novita, Upstage, Scaleway, Aliyun, AI21, Inference.net, Cloudflare, Vertex AI, and any custom OpenAI-compatible endpoint.

---

## FileStore — adaptive media storage

```python
# Attach a physical file to a memory
mem, fe = db.remember_file(
    "Family", Feeling.LOVE,
    "/photos/christmas2024.jpg",
    note="Everyone together at lunch"
)

# Attach binary data directly (e.g. API upload)
with open("voice.mp3", "rb") as f:
    mem, fe = db.remember_bytes("Trip", Feeling.NOSTALGIA, f.read(), "voice.mp3")

# Reading
path = db.files.get_path(mem.memory_id)
data = db.files.get_bytes(mem.memory_id)
info = db.files.info()
```

### Adaptive filesystem strategy

MNHEME detects the filesystem at boot and runs live capability probes:

| Filesystem | Strategy | Notes |
|------------|----------|-------|
| ext4, ZFS, NFS, 9p | **HARDLINK** | zero bytes, same inode |
| btrfs, xfs, APFS | **REFLINK** | Copy-on-Write, zero blocks |
| NTFS | **HARDLINK** | via `CreateHardLinkW` |
| FAT32, exFAT | **COPY_ATOMIC** | tmp + `os.replace()` |
| HDFS, S3FS, GCSFuse | **COPY_ATOMIC** | no local inodes |

---

## Physical `.mnheme` file format

The database is an append-only binary file:

```
┌──────────────┬──────────┬───────────────────┐
│  MAGIC (4B)  │ SIZE (4B)│  PAYLOAD (SIZE B) │
└──────────────┴──────────┴───────────────────┘

MAGIC   : [0x4D, 0x4E, 0x45, 0xE0]  — record signature
SIZE    : uint32 big-endian          — payload length
PAYLOAD : JSON UTF-8                 — memory data
```

Every write is atomic and `fsync`-ed. Truncated records (crash mid-write) are silently skipped on restart. In-RAM indexes are rebuilt by scanning the file from the beginning.

---

## Benchmarks

Measured on 2,000 records, Python 3.12, 9p filesystem:

| Operation | Average | Throughput |
|-----------|---------|------------|
| `remember()` with fsync | 1.8 ms | 552 ops/s |
| `remember()` without fsync | 0.2 ms | 4,632 ops/s |
| `count()` — pure RAM | ~0 ms | 2,774,322 ops/s |
| `feeling_distribution()` | 0.003 ms | 277,865 ops/s |
| `recall(concept, limit=10)` | 1.5 ms | 636 ops/s |
| `recall_by_feeling(limit=20)` | 3.0 ms | 332 ops/s |
| `recall_all()` — 2,000 records | 300 ms | 3 ops/s |
| `search()` full-text | 40 ms | ~49k records/s |
| `search(limit=5)` | 0.1 ms | 8,348 ops/s |
| Cold start (2,000 rec) | 40 ms | 49k rec/s indexed |

**File size:** ~374 B/record → ~36 MB per 100k records, ~357 MB per 1M records.

```bash
# Run benchmarks
python mnheme_benchmark.py --records 5000
python mnheme_benchmark.py --records 10000 --output report.json
```

---

## REST API (optional)

```bash
pip install fastapi uvicorn
uvicorn mnheme_api:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

```
POST /memories              → store a memory
GET  /memories              → all memories (filters: feeling, limit)
GET  /memories/search?q=    → full-text search
GET  /concepts              → concept list with statistics
GET  /concepts/{concept}    → memories for a concept
GET  /concepts/{concept}/timeline  → emotional evolution
GET  /feelings              → feelings with statistics
GET  /feelings/distribution → feeling → count
GET  /stats                 → general statistics
GET  /export                → export JSON
```

---

## Project structure

```
mnheme/
├── mnheme.py           # Core — MemoryDB, Feeling, MediaType, Memory
├── storage.py          # Append-only binary engine
├── index.py            # In-RAM indexes
├── fsprobe.py          # Filesystem detection
├── filestore.py        # Physical file storage
├── llm_provider.py     # LLM provider agnostic via .env
├── brain.py            # LLM cognitive layer
├── mnheme_api.py       # FastAPI REST API (optional)
├── mnheme_benchmark.py # Benchmark suite
├── examples.py         # Usage examples
├── .env.example        # Provider configuration template
└── tests/
    ├── test_llm_provider.py
    └── test_fsprobe.py
```

---

## Supported feelings

`joy` · `sadness` · `anger` · `fear` · `nostalgia` · `love` · `melancholy` · `serenity` · `surprise` · `anxiety` · `gratitude` · `shame` · `pride` · `boredom` · `curiosity`

## Media types

`TEXT` · `IMAGE` · `VIDEO` · `AUDIO` · `DOC`

---

## Requirements

- Python 3.12+
- No mandatory external dependencies
- `fastapi` + `uvicorn` only for the REST API (optional)

---

## Local test using LM Studio

```bash
# Use LM Studio on localhost:1234 with the model already loaded
python test_local_provider.py

# Custom URL
python test_local_provider.py --url http://localhost:1234

# Force a specific model
python test_local_provider.py --model "mistral-7b-instruct"

# Keep the database instead of deleting it after the test
python test_local_provider.py --db mind.mnheme

# Verbose output with traceback if something goes wrong
python test_local_provider.py --verbose
```

---

## Advanced human simulator

### Real timeline
- Timestamps are no longer "today".
- Each memory computes the exact date based on `birth_date + age_in_days ± random variation of 90 days`.
- With `--birth-year 1975`, a memory at age 8 will have a timestamp around 1983, one at age 35 around 2010.
- 8 life phases with distinct emotional distributions:
  Early childhood (0–5), Childhood (6–11), Adolescence (12–17), Early adulthood (18–29), Adulthood (30–44), Middle age (45–59), Late adulthood (60–79), Old age (80–130).
- Each phase has weights calibrated on real psychological data: adolescence weights embarrassment/shame/love, old age weights gratitude/serenity/nostalgia (Carstensen's positivity effect).

### Reminiscence bump
- The temporal distribution of memories is not uniform: 30% falls in the 15–35 age range, reflecting the psychological phenomenon whereby adults disproportionately remember events from that period.

### Narrative consciousness
- Maintains used concepts, recurring tags, and a list of "reprocessable" memories. The narrative thread is injected into the prompt: if tags like `work`, `father`, `Milan` recur throughout a life, the model knows they may reappear in subsequent memories, creating biographical coherence.

### Reprocessings (~20%)
- Memories with heavy feelings (anxiety, fear, anger, shame) are placed in a reworkable queue. With ~20% probability, a new slot is marked as a reprocessing: same concept, changed feeling, written from a growth/healing perspective. The prompt explicitly states "same event seen with different eyes at age X".

### Zero LLM bias
- The model never chooses the feeling — it receives it as an explicit constraint slot by slot. The actual distribution depends solely on the per-phase weights. The model only writes narrative content consistent with the assigned feeling and age.

---

## License

AATEL — see [LICENSE](LICENSE)

---

## Thanks

A special thanks to @KnightNiwrem https://github.com/knightniwrem  
whose questions led to discovering a critical bug triggered by a crash during the write phase.

---

<p align="center">
  <sub>MNHEME — from the Greek muse of memory</sub><br>
  <sub><em>"You cannot overwrite what you have lived. You can only remember it differently."</em></sub>
</p>
