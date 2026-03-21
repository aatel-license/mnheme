# STRATA

**Collective MNHEME Emotional Archive**

STRATA is a shared emotional memory platform for groups. A team, a neighbourhood, a family, a movement — any community can build a collective archive where each member records their emotional experience of shared events. The dashboard reveals where the group converges, where it diverges, and the emotional fingerprint of each voice.

---

## The social layer

Standard MNHEME records are personal and private. STRATA makes them collective:

- **Multiple voices** contribute memories about the **same events**
- The **consensus map** shows which events generated agreement and which generated split reactions
- The **divergence bars** visualise how feelings were distributed across each event
- **Voice fingerprints** show each person's dominant emotional patterns
- The **collective timeline** is a chronological record of the group's emotional life

---

## How to use with a group

Because STRATA is a local-first app (no backend), sharing works via the export/import mechanism:

1. One person starts the archive and adds their entries
2. They click **Export** → shares the `.json` file with the group
3. Others open STRATA, click **Import** → their own entries merge in
4. The merged archive can be re-exported and re-shared

For a real-time shared archive, host the HTML file on a local server and use a shared `localStorage` key — or integrate a simple backend to sync the JSON.

---

## Getting started

```bash
open strata/index.html          # macOS
start strata/index.html         # Windows
xdg-open strata/index.html      # Linux
```

No build step. No dependencies. No internet required.

---

## Project structure

```
strata/
├── index.html   — HTML shell
├── style.css    — 20 CSS-variable themes, full layout
├── app.js       — i18n, themes, data model, all visualisations
└── README.md
```

---

## Input fields

| Field | Description |
|---|---|
| **Community name** | The name of the group (e.g. "Research Team Alpha", "Via Roma neighbours") |
| **Name / alias** | The voice adding the memory — can be a name, role, or anonymous |
| **Anonymous** | Toggle to strip the name and record as "Anonymous" |
| **Event / topic** | The shared event being remembered (e.g. "The Layoffs", "Summer Camp 2024") |
| **Feeling** | One of 15 MNHEME emotions |
| **What you felt** | The emotional experience in the person's own words |

---

## Dashboard tabs

### Consensus
- **Consensus map**: all events ranked by number of voices, each voice shown as a coloured initial dot coloured by their dominant feeling on that event. Events are labelled Agreed / Mixed / Split based on feeling concentration.
- **Emotional divergence**: horizontal stacked bars for events with 2+ voices, showing the proportion of each feeling — wider bars = more entries, more fragmented = more disagreement.

### Voices
Individual emotional fingerprints for each contributor: avatar, entry count, and a mini bar chart of their top 4 feelings.

### Timeline
Chronological feed of all entries grouped by date, with event name, voice, feeling, and content.

---

## Themes

20 themes switchable from the sidebar footer.

| # | Light | # | Dark |
|---|---|---|---|
| 1 | Civic (default) | 11 | Night |
| 2 | Town | 12 | Slate |
| 3 | Meadow | 13 | Ember |
| 4 | Terracotta | 14 | Obsidian |
| 5 | Linen | 15 | Void |
| 6 | Sky | 16 | Crimson |
| 7 | Chalk | 17 | Amethyst |
| 8 | Blossom | 18 | Forest |
| 9 | Pearl | 19 | Ocean |
| 10 | Sand | 20 | Candle |

---

## i18n

| Code | Language |
|---|---|
| `EN` | English (default) |
| `IT` | Italiano |
| `ES` | Español |
| `中` | 中文 |

All labels, placeholders, consensus levels (Agreed/Mixed/Split), date formatting, and feeling labels are translated.

---

## Consensus levels

| Level | Condition | Meaning |
|---|---|---|
| **Agreed** | Top feeling ≥ 75% of entries | The group felt this largely the same way |
| **Mixed** | Top feeling 50–74% | Some agreement, some variation |
| **Split** | Top feeling < 50% | The group felt significantly differently about this event |

---

## Export / Import format

```json
{
  "community": "Research Team Alpha",
  "exported":  "2025-11-15T14:32:00.000Z",
  "entries": [
    {
      "id":      "abc12345",
      "voice":   "Maria",
      "event":   "The Reorganisation",
      "feeling": "ansia",
      "content": "Nobody told us anything for three weeks. The silence was the worst part.",
      "date":    "2025-10-14",
      "ts":      1728906000000
    }
  ]
}
```

Import merges entries by appending — existing entries are preserved. Duplicate IDs are naturally avoided because each entry has a random UID.

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

## MNHEME

STRATA extends the [MNHEME](https://github.com/aatel-license/mnheme) data model into the social dimension. MNHEME's core principle — that emotion is the primary data, not metadata — applies here at the collective level: the archive doesn't just record what happened, it records how each voice *felt* about what happened, and the difference between those feelings is the most interesting data of all.

> *"La memoria non si sovrascrive. Si stratifica."*
> Memory does not overwrite. It stratifies.

---

## License

See the MNHEME repository for licensing information.
