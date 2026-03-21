# MNHEME — Life Generator

Genera una vita sintetica completa con arco evolutivo reale: dalla prima infanzia all'età attuale, con ricordi che si distribuiscono nel tempo, si rielaborano e si intrecciano come nell'esperienza umana autentica.

---

## Requisiti

- **Python 3.10+**
- Un server LLM locale con endpoint OpenAI-compatibile ([LM Studio](https://lmstudio.ai), [Ollama](https://ollama.com), llama.cpp, vLLM…)
- API MNHEME in esecuzione (`uvicorn mnheme_api:app --port 8000`)
- **Nessuna dipendenza esterna** — solo stdlib Python (`urllib`, `json`, `concurrent.futures`, `datetime`)
- `mnheme.py` nella stessa directory per importare i 26 `Feeling` validi (usa un fallback hardcoded se assente)

---

## Installazione

```bash
# Nessun pip install necessario
python advanced_human_simulator_memories_generator.py --help
```

---

## Utilizzo rapido

```bash
# Persona nata nel 1985, genera 50 ricordi dall'infanzia ad oggi
python advanced_human_simulator_memories_generator.py --n 50 --birth-year 1985

# Specifica età di inizio e attuale
python advanced_human_simulator_memories_generator.py --n 80 --start-age 6 --current-age 38

# Dry-run verbose — genera e valida senza postare nulla
python advanced_human_simulator_memories_generator.py --n 10 --dry-run --verbose

# Anziano con lunga storia, più parallelismo
python advanced_human_simulator_memories_generator.py --n 200 --birth-year 1940 --workers 5

# Solo ricordi dall'adolescenza in poi
python advanced_human_simulator_memories_generator.py --n 60 --start-age 12 --current-age 45
```

---

## Opzioni CLI

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--n` | `20` | Numero totale di ricordi da generare |
| `--birth-year` | *(nessuno)* | Anno di nascita (es: `1985`). Calcola automaticamente `current-age` |
| `--start-age` | `0` | Età minima dei ricordi, da `0` a `130` |
| `--current-age` | `35` | Età attuale. Calcolata da `--birth-year` se non specificata |
| `--llm-url` | `http://localhost:1234` | Base URL del server LLM |
| `--model` | *(auto)* | Nome modello. Se omesso viene rilevato via `/v1/models` |
| `--api-key` | *(vuoto)* | API key LLM (opzionale per server locali) |
| `--api-url` | `http://localhost:8000` | URL base API MNHEME |
| `--batch-size` | `5` | Ricordi per chiamata LLM, massimo 8 |
| `--workers` | `3` | Thread paralleli per i batch |
| `--dry-run` | off | Genera e valida senza postare sull'API |
| `--verbose` | off | Mostra il campo `content` completo di ogni ricordo |
| `--sequential` | off | Disabilita il parallelismo (dedup perfetta, più lento) |

---

## Principi architetturali

### 1. Arco temporale reale

I timestamp non sono mai "oggi". Ogni ricordo riceve una data calcolata in base all'anno di nascita e all'età al momento dell'evento, con una variazione casuale di ±90 giorni per realismo:

```
nascita: 1985-03-14
ricordo a  8 anni  →  timestamp: 1993-07-22T14:23:00
ricordo a 22 anni  →  timestamp: 2007-11-05T09:41:00
ricordo a 38 anni  →  timestamp: 2023-02-17T18:07:00
```

### 2. Fasi della vita con distribuzioni emotive distinte

Il generatore divide la vita in 8 fasi. Ogni fase ha pesi emotivi calibrati su ricerca psicologica:

| Età | Fase | Emozioni dominanti |
|-----|------|--------------------|
| 0–5 | Prima infanzia | stupore · gioia · curiosità · sorpresa |
| 6–11 | Infanzia | gioia · curiosità · eccitazione · stupore |
| 12–17 | Adolescenza | amore · imbarazzo · eccitazione · vergogna |
| 18–29 | Prima età adulta | amore · eccitazione · speranza · ansia |
| 30–44 | Età adulta | gratitudine · amore · orgoglio · ansia |
| 45–59 | Mezza età | nostalgia · gratitudine · malinconia · serenità |
| 60–79 | Tarda età adulta | gratitudine · nostalgia · serenità · amore |
| 80–130 | Vecchiaia | gratitudine · serenità · nostalgia · amore |

La calibrazione segue:
- **Positivity effect** (Carstensen 2006): nelle fasi anziane i pesi positivi aumentano drasticamente
- **Reminiscence bump**: la fascia 15–30 anni è sovrarappresentata nella distribuzione temporale
- **Emotional development** (Gross 2015): i pesi negativi nell'infanzia sono limitati

### 3. Distribuzione senza bias

Il modello LLM **non sceglie mai il feeling**. Il feeling è pre-assegnato dallo slot planner prima di ogni chiamata. Il prompt è esplicito:

```
Ricordo 3:
  feeling = "gratitudine"
  età = 34 anni  (fase: Età adulta)
  ambiti suggeriti: carriera, famiglia, casa, salute
```

Il modello scrive solo il contenuto narrativo coerente con il feeling e l'età dati. Questo elimina completamente il bias del modello verso le emozioni drammatiche.

### 4. Reminiscence bump

La distribuzione dei ricordi nel tempo non è uniforme. Segue il fenomeno psicologico per cui gli adulti ricordano sproporzionatamente gli eventi tra i 15 e i 35 anni:

```
Distribuzione su 100 ricordi (vita 0–40 anni):

   0–4  ██████  6
   5–9  █████   5
  10–14 ██████████████████  18
  15–19 █████████████████  17
  20–24 ██████████████  14
  25–29 █████  5
  30–34 ████████████  12
  35–39 ███████████████████████  23
```

### 5. Coscienza narrativa

La classe `Consciousness` mantiene il filo biografico tra i batch:

- **Concept già usati** — passati al modello come lista nera per evitare ripetizioni
- **Tag ricorrenti** — i 4 tag più frequenti vengono iniettati nel prompt come *filo narrativo* suggerito (es: `lavoro`, `padre`, `Milano`), creando continuità biografica senza forzarla
- **Dedup dei contenuti** — i prefissi dei contenuti già generati evitano inizi troppo simili tra ricordi diversi

### 6. Rielaborazioni (~20%)

I ricordi con feeling pesanti (ansia, paura, rabbia, vergogna, delusione, senso di colpa) entrano in una coda `reworkable`. Con probabilità ~20%, un nuovo slot viene marcato come **rielaborazione**: stesso concept o derivato diretto, feeling cambiato perché la persona è cresciuta o guarita.

Il prompt per una rielaborazione specifica esplicitamente:

```
Ricordo 7 [RIELABORAZIONE — stesso evento, occhi diversi]:
  feeling = "gratitudine"
  età = 41 anni  (fase: Età adulta)
  Rielabora questo ricordo passato:
    concept originale: licenziamento
    feeling originale: paura
    tag originali: [lavoro, 2008, crisi]
  Il feeling è cambiato perché la persona è cresciuta/guarita/cambiata.
```

Nel terminal output le rielaborazioni sono marcate con `↺`. Nel campo `note` del ricordo postato appare `· rielaborazione`.

---

## Output terminale

```
MNHEME Life Generator  v3.0
────────────────────────────────────────────────────────────
  Nascita:      1985-07-22
  Età attuale:  39 anni
  Da età:       0 anni
  Arco vitale:  39 anni
  → Discovery modello… nvidia/nemotron-mini-4b-instruct
  → Ping MNHEME… ok

  50 slot · 10 batch · arco 0–39 anni
  Rielaborazioni: 9
  Top feeling pianificati:  amore 6  nostalgia 5  orgoglio 5  ansia 4  gioia 4
────────────────────────────────────────────────────────────

  Batch 1/10
  ✓    promozione           orgoglio         28a  id:a3f9bc12  [lavoro,2013,ufficio]
  ✓    dentista             paura             9a  id:b7e2d401  [infanzia,1994]
  ✓ ↺  licenziamento        gratitudine      38a  id:c1a8f033  [lavoro,2008,rielaborazione]
  ✓    bacio                amore            16a  id:d2c7e901  [adolescenza,2001,scuola]
  ...

────────────────────────────────────────────────────────────
  Completato in 47.3s
  50 generati · 9 rielaborazioni · 0 saltati

  Distribuzione emotiva:
    gratitudine          ████████ 8 (16%)
    amore                ███████ 7 (14%)
    orgoglio             ██████ 6 (12%)
    nostalgia            █████ 5 (10%)
    ansia                ████ 4  (8%)
    ...

  Per fase della vita:
    Adolescenza                █████████████████  17
    Età adulta                 ████████████  12
    Prima età adulta           ██████████  10
    Infanzia                   ███████  7
    ...
```

---

## I 26 feeling disponibili

```
Positivi:    gioia · amore · serenità · gratitudine · orgoglio · speranza
             eccitazione · sollievo · stupore · curiosità · sorpresa

Ambivalenti: nostalgia · malinconia · rassegnazione · confusione · noia

Negativi:    tristezza · ansia · paura · solitudine · delusione · rabbia
             vergogna · imbarazzo · invidia · senso_di_colpa
```

---

## Compatibilità LLM

| Server | URL | Note |
|--------|-----|------|
| **LM Studio** | `http://localhost:1234` | Auto-discovery modello |
| **Ollama** | `http://localhost:11434` | `--llm-url http://localhost:11434` |
| **llama.cpp** | `http://localhost:8080` | `--llm-url http://localhost:8080` |
| **vLLM** | variabile | Specificare `--api-url` su porta diversa |
| **Groq / Mistral** | endpoint cloud | `--llm-url <url> --api-key <key>` |

Per risultati ottimali si raccomandano modelli instruction-tuned da almeno 7B parametri. Con modelli più piccoli (3–4B) usare `--batch-size 3` per ridurre la probabilità di JSON malformato o troncato.

---

## Esempi avanzati

```bash
# Vita completa: dall'infanzia (6 anni) ai 45 anni
python advanced_human_simulator_memories_generator.py \
  --n 120 \
  --birth-year 1979 \
  --start-age 6 \
  --batch-size 6 \
  --workers 4

# Anziano: ricordi a partire dai 70 anni
python advanced_human_simulator_memories_generator.py \
  --n 40 \
  --birth-year 1930 \
  --start-age 70 \
  --sequential

# Solo adolescenza e prima età adulta
python advanced_human_simulator_memories_generator.py \
  --n 50 \
  --start-age 13 \
  --current-age 28

# Test qualità del modello senza scrivere sul database
python advanced_human_simulator_memories_generator.py \
  --n 5 \
  --birth-year 1990 \
  --dry-run \
  --verbose \
  --sequential

# Con Ollama e llama3
python advanced_human_simulator_memories_generator.py \
  --n 60 \
  --birth-year 1985 \
  --llm-url http://localhost:11434 \
  --model llama3.1:8b
```

---

## Struttura del codice

```
advanced_human_simulator_memories_generator.py
│
├── LIFE_PHASES          8 fasi con feeling_weights, domains, narrative
│
├── Consciousness        filo narrativo cross-batch
│   ├── concept_usage    Counter dei concept già usati
│   ├── tag_pool         pool di tag per il filo narrativo
│   ├── reworkable       coda ricordi candidati a rielaborazione
│   ├── should_rework()  probabilità ~20%
│   └── pick_rework()    preferisce feeling pesanti come candidati
│
├── MemoryRecord         dataclass con timestamp reale e metadata di fase
│   └── to_payload()     serializza per l'API MNHEME
│
├── LLMClient            client HTTP stdlib — nessun SDK esterno
│   ├── discover_model() GET /v1/models → primo modello disponibile
│   └── complete()       POST /v1/chat/completions
│
├── MnhemeClient         POST /memories con retry backoff esponenziale
│
├── _plan_slots()        pianifica tutti gli slot prima della generazione
│                        · reminiscence bump nella distribuzione temporale
│                        · feeling pre-assegnati per fase (zero bias LLM)
│                        · identifica slot rielaborazione
│
├── _build_prompt()      costruisce prompt con slot espliciti + filo narrativo
│
├── _validate()          normalizza ogni campo e forza il feeling target
│
└── _run_batch()         genera → valida → posta, con retry esponenziale
```
