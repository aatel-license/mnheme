# MNHĒMĒ — MCP Server

Collega qualsiasi LLM compatibile MCP a MNHĒMĒ come layer di memoria persistente.

---

## Requisiti

- Python 3.12+
- Repository MNHĒMĒ clonato localmente
- `pip install mcp`
- `pip install starlette uvicorn` *(solo per trasporto SSE)*

Posiziona `mnheme_mcp.py` nella root del repository, accanto a `mnheme.py`.

---

## Configurazione

Aggiungi queste variabili al `.env` esistente di MNHĒMĒ:

```env
# Path del database (default: mnheme.mnheme)
MNHEME_DB_PATH=mente.mnheme

# Directory file multimediali (default: <db_stem>_files/)
MNHEME_FILES_DIR=mente_files/

# Attiva il layer cognitivo Brain/LLM (default: false)
BRAIN_ENABLED=false
```

Se `BRAIN_ENABLED=true`, configura anche un provider LLM nello stesso `.env`
(LM Studio, Groq, Anthropic, ecc.) seguendo la documentazione principale.

---

## Avvio

### stdio *(Claude Desktop, Cursor, Zed, Continue, ecc.)*

```bash
python mnheme_mcp.py
```

### SSE *(connessioni HTTP remote)*

```bash
python mnheme_mcp.py --sse --port 8765
```

Il server sarà raggiungibile su `http://0.0.0.0:8765/sse`.

### Override del database a runtime

```bash
python mnheme_mcp.py --db /percorso/diverso/mente.mnheme
```

---

## Integrazione con i client MCP

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` su macOS,
`%APPDATA%\Claude\claude_desktop_config.json` su Windows.

```json
{
  "mcpServers": {
    "mnheme": {
      "command": "python",
      "args": ["/percorso/assoluto/mnheme/mnheme_mcp.py"],
      "env": {
        "MNHEME_DB_PATH": "/percorso/assoluto/mente.mnheme",
        "BRAIN_ENABLED": "false"
      }
    }
  }
}
```

### Cursor / Zed / Continue

```json
{
  "mcp": {
    "servers": {
      "mnheme": {
        "command": "python",
        "args": ["/percorso/assoluto/mnheme/mnheme_mcp.py"]
      }
    }
  }
}
```

### SSE (client HTTP generici)

```
http://tuo-server:8765/sse
```

---

## Tool disponibili

### Scrittura

| Tool | Descrizione |
|------|-------------|
| `remember` | Registra un ricordo con concept, feeling e content. Append-only, immutabile. |

### Lettura

| Tool | Descrizione |
|------|-------------|
| `recall` | Richiama i ricordi di un concetto. Filtrabile per feeling, limit, ordine. |
| `recall_by_feeling` | Tutti i ricordi associati a un sentimento. |
| `recall_by_tag` | Ricordi che contengono un tag specifico. |
| `search` | Ricerca full-text in content, concept e note. |

### Statistiche

| Tool | Descrizione |
|------|-------------|
| `list_concepts` | Tutti i concetti con distribuzione emotiva e totale ricordi. |
| `feeling_distribution` | Mappa globale sentimento → numero di ricordi. |
| `concept_timeline` | Evoluzione emotiva di un concetto nel tempo. |
| `storage_info` | Path, dimensione del log, numero di record, file allegati. |

### Brain *(richiede `BRAIN_ENABLED=true`)*

| Tool | Descrizione |
|------|-------------|
| `brain_perceive` | Testo grezzo → ricordo strutturato. L'LLM estrae concept, feeling e tags e arricchisce il contenuto. Il ricordo viene salvato automaticamente. |
| `brain_ask` | RAG sulla memoria personale. Risponde usando solo i ricordi reali come contesto. |
| `brain_reflect` | Analisi dell'arco emotivo di un concetto nel tempo. |
| `brain_dream` | Connessioni latenti tra ricordi di sentimenti diversi. |
| `brain_introspect` | Ritratto psicologico completo: pattern, tensioni, concetti dominanti, mappa emotiva. |

---

## Sentimenti validi

`gioia` · `tristezza` · `rabbia` · `paura` · `nostalgia` · `amore` · `malinconia` · `serenità` · `sorpresa` · `ansia` · `gratitudine` · `vergogna` · `orgoglio` · `noia` · `curiosità`

---

## Note

- Il database è **append-only**: i ricordi non vengono mai modificati o cancellati dopo la scrittura.
- Il trasporto **stdio** è quello consigliato per client locali. Il trasporto **SSE** serve per deployment remoti o multi-client.
- I tool Brain sono opzionali e indipendenti dalla memoria base: puoi usare `remember` e `recall` senza alcun LLM configurato.
- In caso di errore di validazione (feeling non valido, concept vuoto, ecc.) il tool restituisce un oggetto `{"error": "..."}` senza crashare il server.
