# MNHEME — Porting Multi-Linguaggio

Port completi del database di memoria umana [mnheme](https://github.com/aatel-license/mnheme)
in 6 linguaggi di programmazione.

Il file `.mnheme` è **100% compatibile cross-linguaggio**: puoi scrivere record con il
porting Rust e leggerli con il porting Go, Java, Node.js, Kotlin o C++ senza conversioni.

---

## Struttura

```
mnheme_ports/
├── rust/                    ← Rust (max performance)
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── storage.rs       ← StorageEngine
│       ├── index.rs         ← IndexEngine
│       ├── mnheme.rs        ← MemoryDB
│       └── main.rs          ← example
│
├── cpp/                     ← C++20 (max control)
│   ├── storage.hpp / .cpp
│   └── mnheme.hpp / .cpp    ← MemoryDB + IndexEngine
│
├── go/                      ← Go (best dev velocity)
│   ├── go.mod
│   └── mnheme/
│       ├── storage.go
│       ├── index.go
│       └── memorydb.go
│
├── java/                    ← Java 21 (enterprise)
│   └── mnheme/
│       ├── StorageEngine.java
│       ├── IndexEngine.java
│       ├── Memory.java
│       ├── Feeling.java
│       └── MemoryDB.java
│
├── nodejs/                  ← Node.js (rapid dev, I/O async)
│   ├── package.json
│   ├── storage.js
│   ├── index.js
│   ├── memorydb.js
│   └── main.js              ← example
│
└── kotlin/                  ← Kotlin/Android
    ├── StorageEngine.kt
    ├── IndexEngine.kt
    └── MemoryDB.kt
```

---

## Dipendenze per linguaggio

| Linguaggio | Dipendenze esterne |
|---|---|
| **Python** (originale) | nessuna |
| **Rust** | `serde_json`, `uuid`, `sha2`, `chrono`, `regex` |
| **C++20** | `nlohmann/json` (header-only), `OpenSSL` (SHA-256) |
| **Go** | `github.com/google/uuid` |
| **Java 21** | `jackson-databind` |
| **Node.js** | **nessuna** (zero deps, usa stdlib) |
| **Kotlin/Android** | `kotlinx-coroutines-android`, `org.json` (SDK built-in) |

---

## Come compilare

### Rust
```bash
cd rust
cargo build --release
cargo run
```

### C++
```bash
cd cpp
# Install: vcpkg install nlohmann-json openssl
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/mnheme
```

### Go
```bash
cd go
go mod tidy
go run ./cmd/main.go
```

### Java 21
```bash
cd java
# Maven: mvn compile exec:java -Dexec.mainClass="mnheme.Main"
# Gradle: gradle run
javac -cp jackson-databind.jar mnheme/*.java
```

### Node.js
```bash
cd nodejs
node main.js
```

### Kotlin / Android
Aggiungi i file `.kt` al modulo Android, poi:
```kotlin
// In una coroutine (es. ViewModel)
val db = MemoryDB.open(filesDir.resolve("mente.mnheme"))
val mem = db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.")
```

---

## API unificata (tutti i linguaggi)

```
// Apertura
db = open("mente.mnheme")

// Scrittura (append-only)
db.remember(concept, feeling, content, note?, tags?, mediaType?)

// Lettura
db.recall(concept, feeling?, limit?, oldestFirst?)
db.recallByFeeling(feeling, limit?, oldestFirst?)
db.recallAll(limit?, oldestFirst?)
db.search(text, inContent?, inConcept?, inNote?, limit?)

// Statistiche
db.count(concept?, feeling?)
db.feelingDistribution()
db.listConcepts()
db.conceptTimeline(concept)

// Export / Import
db.exportJson()
db.importJson(path)
```

---

## Formato fisico (compatibile cross-linguaggio)

```
┌──────────────┬──────────┬───────────────────┐
│  MAGIC (4B)  │ SIZE (4B)│  PAYLOAD (SIZE B) │
└──────────────┴──────────┴───────────────────┘

MAGIC   : [0x4D, 0x4E, 0x45, 0xE0]  — firma record
SIZE    : uint32 big-endian          — lunghezza payload
PAYLOAD : JSON UTF-8                 — dati del ricordo
```

I file `.mnheme` scritti da qualsiasi implementazione sono leggibili da tutte le altre.

---

## Guida alla scelta

| Caso d'uso | Linguaggio consigliato |
|---|---|
| Server ad alto throughput (>10k ops/s) | **Rust** |
| Sistema embedded / edge | **C++** |
| Microservice / API REST | **Go** |
| Backend enterprise / Spring | **Java 21** |
| Script / prototipazione rapida | **Node.js** |
| App Android nativa | **Kotlin** |
| AI brain / LLM integration | **Python** (originale) |

---

*MNHEME — dalla musa greca della memoria*
*"Non puoi sovrascrivere ciò che hai vissuto. Puoi solo ricordarlo diversamente."*
