# PHANTOM ARCHIVE

**An emotional memory investigation game powered by MNHEME**

PHANTOM ARCHIVE is a standalone browser mystery game. An unknown character's emotional memory archive has been recovered and anonymised. You have 10 questions to interrogate the archive through an LLM Brain. Each answer unlocks a new memory fragment. When you're ready, file your verdict — name the phantom and reconstruct their psychological profile.

---

## How to play

1. Open `index.html` in any modern browser
2. Configure LM Studio (see below)
3. Choose a case
4. Ask questions in the interrogation panel
5. Every 2 questions, a new memory fragment is unlocked in the archive
6. When you've used all 10 questions (or decide you know enough), click **Close Case**
7. File your verdict: name the character and describe their psychological arc
8. The true identity is revealed alongside an AI evaluation of your profile

---

## Project structure

```
phantom-archive/
├── index.html   — HTML shell, all structure, no logic
├── style.css    — all styles, 20 CSS-variable themes, animations
├── app.js       — cases, i18n, themes, game logic, LM Studio integration
└── README.md
```

Zero dependencies. No build step. No CDN. Works from `file://` in any modern browser.

---

## LM Studio setup

PHANTOM ARCHIVE uses [LM Studio](https://lmstudio.ai) as its local AI backend — free, private, no API key required.

1. Download and open LM Studio
2. Load any instruction-tuned model (`mistral-7b-instruct`, `llama-3.1-8b`, `phi-3-mini`, etc.)
3. Start the local server on port 1234 (default)
4. In the app, enter the exact model name in the **MODEL** field and click **SAVE**

| Field | Default | Description |
|---|---|---|
| URL | `http://localhost:1234/v1/chat/completions` | LM Studio's OpenAI-compatible endpoint |
| Model | *(blank = auto)* | Must match the model name shown in LM Studio |

Settings persist across sessions via `localStorage`.

---

## The cases

Three classic literary characters have been anonymised. Their emotional archive survives — their name does not.

| Case | Title | Description |
|---|---|---|
| A | The Broken Prince | A ruler who lost everything to the one he trusted most |
| B | The Lighthouse Woman | A woman who stopped time and let her heart rot with the house |
| C | The Monster's Architect | The creator who fled his creation and was hunted by his own guilt |

Each case contains **10 memory fragments** structured as MNHEME records:

```
concept   → the emotional theme (Betrayal, Death, Love…)
feeling   → one of 15 emotions from the MNHEME vocabulary
content   → the lived moment, in the character's own voice
note      → narrative context or location
daysAgo   → relative timestamp
```

---

## Game mechanics

| Mechanic | Value |
|---|---|
| Questions per case | 10 |
| Fragments unlocked at start | 2 |
| New fragment every | 2 questions |
| Max fragments | 10 |
| Score for correct identity | 80 base + up to 20 bonus |
| Bonus | +2 per unused question |
| Max score | 100 |

The Brain is instructed to:
- Answer only from the unlocked memory fragments
- Never reveal the character's name or source text
- Keep responses to 2–4 sentences
- Reply in the user's current language

After you submit your verdict, the Brain performs a second AI call to evaluate your psychological profile against the official one.

---

## Themes

20 themes switchable from the **THEME** button on the intro screen. Preference persists across sessions.

| # | Light | # | Dark |
|---|---|---|---|
| 1 | Manuscript (default) | 11 | Noir |
| 2 | Birch | 12 | Midnight |
| 3 | Fog | 13 | Ember |
| 4 | Sepia | 14 | Catacombs |
| 5 | Ash | 15 | Abyss |
| 6 | Rose Dust | 16 | Blood |
| 7 | Vellum | 17 | Absinthe |
| 8 | Dusk Rose | 18 | Amethyst |
| 9 | Sand Court | 19 | Iron |
| 10 | Chalk | 20 | Candle |

---

## i18n

Full interface translation in 4 languages, switchable at runtime from the **EN/IT/ES/中** button.

| Code | Language | Notes |
|---|---|---|
| `EN` | English | Default |
| `IT` | Italiano | All UI, feeling labels, date formatting |
| `ES` | Español | All UI, feeling labels, date formatting |
| `中` | 中文 | All UI, feeling labels, date formatting (`zh-CN`) |

Language selection persists via `localStorage`. The Brain system prompt instructs the model to reply in the selected language.

**Translated elements:**
- All labels, buttons, placeholders, and messages
- All 15 MNHEME feeling labels
- Case titles and descriptions
- Date formatting (e.g. `3d ago` → `3g fa` → `hace 3d` → `3天前`)
- Verdict and result screen
- AI evaluation prompt language

---

## Feelings reference

The 15 feelings from the MNHEME vocabulary used across all cases:

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

## Adding new cases

New cases are plain JavaScript objects in `app.js` inside the `CASES` array. Each case requires:

```javascript
{
  id:       'D',                        // unique letter
  title_en: 'The ...',                  // title in all 4 languages
  title_it: '...',
  title_es: '...',
  title_zh: '...',
  desc_en:  '...',                      // short description (4 langs)
  desc_it:  '...', desc_es:'...', desc_zh:'...',
  identity: 'Character Name (Source)',  // revealed at the end
  profile:  '...',                      // official psychological profile
  archetype:'...',                      // one-line archetype (used in Brain prompt)
  memories: [                           // 10 entries recommended
    {
      concept:  'Betrayal',
      feeling:  'rabbia',               // must be a key from FEELING_COLORS
      content:  'The character\'s words, in first person.',
      note:     'Context or location.', // optional
      daysAgo:  30,                     // relative time (display only)
    },
    // …
  ]
}
```

---

## MNHEME connection

PHANTOM ARCHIVE is a game-layer on top of the [MNHEME](https://github.com/aatel-license/mnheme) data model. Each memory entry directly mirrors MNHEME's core schema: `concept`, `feeling`, `content`, and temporal metadata. The Brain interrogation replicates the `brain.ask()` RAG pattern — using the character's archive as the only context window.

> *"La memoria non si sovrascrive. Si stratifica."*
> Memory does not overwrite. It stratifies.

---

## License

See the MNHEME repository for licensing information.
