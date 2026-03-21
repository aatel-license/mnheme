# MEMORIA

**Personal MNHEME Emotional Dashboard**

MEMORIA is a standalone browser app for recording and analysing your own emotional life through the MNHEME data model. Every memory you record carries a concept, a feeling, content, and an optional note — and the dashboard turns your archive into a living map of your inner patterns.

---

## What it does

| Feature | Description |
|---|---|
| **Quick capture** | Record a memory in seconds from the sidebar |
| **Emotional calendar** | GitHub-style heatmap of the full year, each day coloured by its dominant feeling |
| **Stat cards** | Total entries, unique concepts, current day streak, dominant feeling this week |
| **Concept cloud** | All concepts sized by frequency, coloured by their dominant emotion — click any to see its arc |
| **Feeling distribution** | Horizontal bar chart of all 15 MNHEME feelings across your archive |
| **Emotional arc** | Timeline of a selected concept's emotional evolution — how your feeling toward "Work" or "Family" has shifted |
| **Brain** | Ask LM Studio about your emotional patterns, based on your real archive |

---

## Getting started

```bash
open memoria/index.html          # macOS
start memoria/index.html         # Windows
xdg-open memoria/index.html      # Linux
```

No build step. No CDN. No internet required after first open (fonts are system fonts).

For the **Brain** panel, [LM Studio](https://lmstudio.ai) must be running locally:

1. Open LM Studio and load any instruction-tuned model
2. Start the local server (default port 1234)
3. In MEMORIA, enter the model name in the LM Studio bar and click **Save**

---

## Project structure

```
memoria/
├── index.html   — HTML shell, all structure
├── style.css    — 20 CSS-variable themes, all layout and component styles
├── app.js       — i18n, theme logic, data model, all chart rendering
└── README.md
```

---

## Themes

20 themes switchable from the **Theme** button in the sidebar footer.

| # | Light | # | Dark |
|---|---|---|---|
| 1 | Pearl (default) | 11 | Obsidian |
| 2 | Latte | 12 | Midnight |
| 3 | Sky | 13 | Ember |
| 4 | Bloom | 14 | Void |
| 5 | Sage | 15 | Forest |
| 6 | Sand | 16 | Crimson |
| 7 | Violet | 17 | Amethyst |
| 8 | Chalk | 18 | Ocean |
| 9 | Peach | 19 | Graphite |
| 10 | Fog | 20 | Candle |

Theme preference persists via `localStorage`.

---

## i18n

Full interface translation in 4 languages, switchable at runtime from the language button in the sidebar footer.

| Code | Language |
|---|---|
| `EN` | English (default) |
| `IT` | Italiano |
| `ES` | Español |
| `中` | 中文 |

Translated elements include all labels, buttons, placeholders, stat descriptions, the 15 feeling labels, month and day abbreviations in the calendar, and the Brain system prompt language instruction.

---

## Data model

Each memory entry follows the MNHEME schema:

```json
{
  "id":       "abc12345",
  "concept":  "Work",
  "feeling":  "ansia",
  "content":  "Presented the quarterly results. My hands were shaking the whole time.",
  "note":     "Conference room B, Tuesday morning",
  "date":     "2025-11-12",
  "ts":       1731369600000
}
```

All data is stored in `localStorage` under the key `memoria-v1`.

User preferences persist separately:

| Key | Value |
|---|---|
| `mem-theme` | theme id, e.g. `pearl` |
| `mem-lang` | language code, e.g. `it` |
| `mem-lm-url` | LM Studio endpoint |
| `mem-lm-model` | model name |

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

## Emotional calendar

The calendar heatmap covers the past 53 weeks (one full year). Each cell represents one day:

- **Coloured**: at least one memory recorded that day, colour = dominant feeling
- **Grey**: no memories recorded
- **Hover tooltip**: shows the date and feeling breakdown

The calendar uses the same append-only principle as MNHEME — days are never rewritten, only accumulated.

---

## Emotional arc

The arc panel visualises how your feeling toward a specific concept has evolved over time. Each dot on the timeline is one memory entry, coloured by feeling. Clicking a concept in the concept cloud automatically selects it in the arc.

This directly mirrors MNHEME's `brain.reflect()` operation — but visually, without the LLM layer.

---

## Brain system prompt

When you ask a question in the Brain panel, MEMORIA builds a system prompt from your last 40 entries and sends it to LM Studio:

```
You are the MEMORIA Brain — a psychological intelligence embedded in a
personal emotional memory archive.

ARCHIVE SUMMARY:
- Total entries: N
- Concepts tracked: Work, Family, Health…
- Most frequent feeling: Anxiety

RECENT ENTRIES (up to 40):
[2025-11-12] CONCEPT: Work | FEELING: Anxiety
"Presented the quarterly results…"
…

Answer based ONLY on this archive. Be insightful, warm, and honest.
Keep responses to 3–5 sentences. [Reply in English / Italian / …]
```

---

## MNHEME

MEMORIA is built on the [MNHEME](https://github.com/aatel-license/mnheme) data model — an open-source Python database that models human memory as append-only, emotionally-tagged records.

> *"La memoria non si sovrascrive. Si stratifica."*
> Memory does not overwrite. It stratifies.

---

## License

See the MNHEME repository for licensing information.
