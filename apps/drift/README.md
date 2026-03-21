# DRIFT

**MNHEME Emotional Time Capsule**

DRIFT lets you seal a memory in time and unseal it in the future. Write what you feel today — honestly, with no intention of being read — and choose a date. The capsule locks. When that date arrives, you return, read what you wrote, add a re-entry note describing how you feel *now*, and the Brain analyses the gap between the two versions of you.

---

## The mechanic

```
Seal  →  [locked until date]  →  Unseal  →  Re-entry note  →  Brain analysis
```

1. **Seal** — write a concept, a feeling, and your honest emotional state. Choose a future date.
2. **Countdown** — the capsule shows a live countdown (days / hours / minutes / seconds). Content is inaccessible.
3. **Unseal** — when the date arrives, the capsule opens automatically. You read what past-you wrote.
4. **Re-entry** — write a note describing your current feeling about the same concept. Select a feeling for today.
5. **Brain** — ask LM Studio about the emotional arc between past-you and present-you.

---

## Getting started

```bash
open drift/index.html          # macOS
start drift/index.html         # Windows
xdg-open drift/index.html      # Linux
```

No build step. No dependencies. No internet required (except LM Studio for the Brain panel).

---

## Project structure

```
drift/
├── index.html   — HTML shell
├── style.css    — 20 CSS-variable themes, all layout and states
├── app.js       — i18n, themes, capsule logic, countdown, Brain
└── README.md
```

---

## LM Studio setup

The Brain panel requires [LM Studio](https://lmstudio.ai) running locally.

1. Open LM Studio and load any instruction-tuned model
2. Start the local server (default port 1234)
3. Enter the model name in the LM Studio field and click **Save**

| Field | Default |
|---|---|
| URL | `http://localhost:1234/v1/chat/completions` |
| Model | *(blank = auto)* |

The Brain system prompt includes both the original sealed memory and the re-entry note, so it can analyse the emotional distance between them. It responds in the user's selected language.

---

## Themes

20 themes, switchable from the sidebar footer.

| # | Light | # | Dark |
|---|---|---|---|
| 1 | Parchment (default) | 11 | Obsidian |
| 2 | Linen | 12 | Midnight |
| 3 | Cloud | 13 | Ember |
| 4 | Sage | 14 | Void |
| 5 | Blush | 15 | Forest |
| 6 | Sand | 16 | Crimson |
| 7 | Stone | 17 | Amethyst |
| 8 | Lilac | 18 | Graphite |
| 9 | Dawn | 19 | Candle |
| 10 | Chalk | 20 | Ocean |

---

## i18n

Full interface translation in 4 languages, switchable at runtime from the language button in the sidebar footer.

| Code | Language |
|---|---|
| `EN` | English (default) |
| `IT` | Italiano |
| `ES` | Español |
| `中` | 中文 |

**Translated elements:**
- All labels, buttons, placeholders, and status messages
- Countdown unit labels (d/h/m/s and full forms)
- Sealed hint and re-entry prompts
- Brain title, suggestions, and system prompt language instruction
- Date formatting with correct locale (`en-GB`, `it-IT`, `es-ES`, `zh-CN`)
- Feeling labels (all 15 MNHEME emotions)
- Status labels (sealed / unsealed / opens in / opened on)

---

## Data model

Each capsule follows the MNHEME schema with a time-lock extension:

```json
{
  "id":        "abc12345",
  "concept":   "Career",
  "feeling":   "ansia",
  "content":   "I handed in my notice today. No plan. Just could not stay.",
  "note":      "Tuesday morning, raining",
  "sealedAt":  1731369600000,
  "sealUntil": 1762905600000,
  "reentry": {
    "feeling": "serenità",
    "content": "Six months later. It was the right call. The fear was a signal.",
    "at":      1762920000000
  },
  "brainHistory": [
    { "role": "user",      "content": "What changed most?" },
    { "role": "assistant", "content": "The distance between…" }
  ]
}
```

All data is stored in `localStorage` under the key `drift-v1`.

User preferences persist separately:

| Key | Value |
|---|---|
| `drift-theme` | theme id, e.g. `parchment` |
| `drift-lang` | language code, e.g. `it` |
| `drift-lm-url` | LM Studio endpoint |
| `drift-lm-model` | model name |

---

## The 15 feelings

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

## Brain system prompt

When you ask a question in the Brain panel, DRIFT builds a context from both temporal layers:

```
PAST MEMORY (sealed on [date]):
CONCEPT: Career
FEELING then: Anxiety
"I handed in my notice today. No plan. Just could not stay."
Context: Tuesday morning, raining

RE-ENTRY NOTE (written today, [date]):
FEELING now: Serenity
"Six months later. It was the right call. The fear was a signal."

Analyze the emotional arc between past and present.
Be insightful, compassionate, and honest.
Keep responses to 3–5 sentences.
[Reply in English / Italian / Spanish / Chinese]
```

Pre-loaded suggestions for each capsule (translated per language):
- *What changed most in how I feel about "[concept]"?*
- *What would past-me think of this re-entry note?*
- *What does this capsule reveal about my emotional patterns?*

---

## MNHEME

DRIFT is built on the [MNHEME](https://github.com/aatel-license/mnheme) data model — an open-source Python database that models human memory as append-only, emotionally-tagged records. The time-lock mechanism extends MNHEME's core principle: not only does memory stratify (you can't overwrite it), it also *matures* — the same concept, felt differently across time, is the most interesting data in the archive.

> *"La memoria non si sovrascrive. Si stratifica."*
> Memory does not overwrite. It stratifies.

---

## License

See the MNHEME repository for licensing information.
