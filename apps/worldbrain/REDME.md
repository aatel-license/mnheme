# WorldBrain

**MNHEME-powered emotional memory engine for narrative worlds**

WorldBrain is a standalone browser app that gives every character in your fictional world a persistent emotional memory archive — built on the [MNHEME](https://github.com/aatel-license/mnheme) data model. Record what each character lived, search it, visualise it, and interrogate it through an LLM Brain that stays faithful to the archive.

---

## What it does

Traditional worldbuilding tools track facts. WorldBrain tracks **felt experience**.

Each memory entry has three required fields and one optional one:

| Field | What it captures |
|---|---|
| `concept` | The theme or subject — *Betrayal, Home, War, Father* |
| `feeling` | One of 15 emotions drawn from MNHEME's vocabulary |
| `content` | The lived moment, in the character's own voice |
| `note` | Optional world context, location, or narrative note |

Every entry is **append-only and immutable** — the same principle as MNHEME's binary storage engine. You can't overwrite a memory; you can only add new ones that layer on top.

---

## Features

### Memories
Record emotional memories for each character. The archive grows chronologically, with each entry tagged by concept and feeling.

### Brain
Chat with an LLM (via LM Studio) that uses the character's actual memory archive as its only context. The Brain answers questions about the character's psychology, emotional arcs, hidden fears, and relationships — but never invents experiences outside the archive.

### Analytics
- **Emotional distribution** — bar chart of feelings across all entries
- **Concept map** — dominant feeling per concept, ranked by frequency
- **Memory timeline** — full chronological view with emotional colour-coding

### 20 themes
10 light, 10 dark — switchable from the sidebar. Parchment is the default.

| Light | Dark |
|---|---|
| Parchment, Arctic, Linen, Sage, Rose | Obsidian, Midnight, Ember, Forest, Void |
| Slate, Sand, Ivory, Lavender, Moss | Crimson, Ocean, Dusk, Copper, Noir |

### i18n
Full interface translation in 4 languages, switchable at runtime:

| Code | Language |
|---|---|
| `EN` | English |
| `IT` | Italiano |
| `ES` | Español |
| `中` | 中文 |

Dates are formatted with the correct locale. The Brain is instructed to reply in the same language as the user's question. Language preference is persisted in `localStorage`.

### Responsive
Works on desktop, tablet, and mobile. On narrow screens the sidebar becomes a slide-over overlay with a hamburger toggle, the LM Studio bar collapses, and the memory form stacks above the archive list.

---

## Project structure

```
worldbrain/
├── index.html    — HTML shell, no logic
├── style.css     — all styles + 20 CSS-variable themes
└── app.js        — all application logic, translations, render functions
```

Zero dependencies. No build step. No CDN. Open `index.html` directly in any modern browser.

---

## Getting started

```bash
# clone or download, then just open the file
open worldbrain/index.html          # macOS
start worldbrain/index.html         # Windows
xdg-open worldbrain/index.html      # Linux
```

For the **Brain** tab you need [LM Studio](https://lmstudio.ai) running locally:

1. Download and open LM Studio
2. Load a model (any instruction-tuned model works well — `mistral-7b-instruct`, `llama-3`, etc.)
3. Start the local server on port 1234 (default)
4. In WorldBrain, enter the model name in the LM Studio bar and click **SAVE**

The endpoint defaults to `http://localhost:1234/v1/chat/completions` — the OpenAI-compatible API that LM Studio exposes. No API key required.

---

## LM Studio bar

| Field | Default | Notes |
|---|---|---|
| URL | `http://localhost:1234/v1/chat/completions` | Change if you run LM Studio on a different port |
| Model name | *(blank = auto)* | Must match the model name shown in LM Studio |

Settings are saved to `localStorage` and restored on reload.

---

## Supported feelings

The 15 feelings from MNHEME's vocabulary, translated across all four languages:

| Key | EN | IT | ES | 中 |
|---|---|---|---|---|
| `gioia` | Joy | Gioia | Alegría | 喜悦 |
| `tristezza` | Sadness | Tristezza | Tristeza | 悲伤 |
| `rabbia` | Rage | Rabbia | Rabia | 愤怒 |
| `paura` | Fear | Paura | Miedo | 恐惧 |
| `nostalgia` | Nostalgia | Nostalgia | Nostalgia | 怀旧 |
| `amore` | Love | Amore | Amor | 爱 |
| `malinconia` | Melancholy | Malinconia | Melancolía | 忧郁 |
| `serenità` | Serenity | Serenità | Serenidad | 宁静 |
| `sorpresa` | Surprise | Sorpresa | Sorpresa | 惊讶 |
| `ansia` | Anxiety | Ansia | Ansiedad | 焦虑 |
| `gratitudine` | Gratitude | Gratitudine | Gratitud | 感恩 |
| `vergogna` | Shame | Vergogna | Vergüenza | 羞耻 |
| `orgoglio` | Pride | Orgoglio | Orgullo | 自豪 |
| `noia` | Boredom | Noia | Aburrimiento | 无聊 |
| `curiosità` | Curiosity | Curiosità | Curiosidad | 好奇 |

---

## Data persistence

All data is stored in `localStorage` under the key `mnheme-wb4`. The schema:

```json
{
  "characters": [
    { "id": "abc12345", "name": "Elara Voss", "archetype": "Exiled healer", "createdAt": 1700000000000 }
  ],
  "memories": {
    "abc12345": [
      {
        "id":        "def67890",
        "concept":   "Betrayal",
        "feeling":   "rabbia",
        "content":   "She burned the letter without reading it.",
        "note":      "Northern fortress, winter",
        "timestamp": 1700000001000
      }
    ]
  },
  "chats": {
    "abc12345": [
      { "role": "user",      "content": "What is Elara's relationship with trust?" },
      { "role": "assistant", "content": "..." }
    ]
  }
}
```

User preferences (theme, language, LM Studio config) are stored separately:

| Key | Value |
|---|---|
| `wb-theme` | theme id, e.g. `parchment` |
| `wb-lang` | language code, e.g. `it` |
| `wb-lm-url` | LM Studio endpoint URL |
| `wb-lm-model` | model name string |

---

## Brain system prompt

When you send a message in the Brain tab, WorldBrain assembles a system prompt from the character's full memory archive and sends it to LM Studio along with the conversation history. The prompt instructs the model to:

- Stay faithful to the memories in the archive
- Never fabricate experiences not present in the archive
- Speak with psychological depth and narrative richness
- Acknowledge gaps honestly when the archive is sparse
- Reply in the same language as the user's question

The last 30 memories are included in context (most recent first).

---

## MNHEME

WorldBrain is built on the concepts from [MNHEME](https://github.com/aatel-license/mnheme) — an open-source Python database that models human memory as append-only, emotionally-tagged records. The Brain tab replicates the `brain.ask()` RAG pattern in pure browser JavaScript.

> *"La memoria non si sovrascrive. Si stratifica."*
> Memory does not overwrite. It stratifies.

---

## License

See the MNHEME repository for licensing information.