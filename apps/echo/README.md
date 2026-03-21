# ECHO

**MNHEME Narrative Content Generator**

ECHO turns emotional memory archives into literary content. You feed it MNHEME records — concept, feeling, content — and it generates letters, journal entries, interior monologues, fiction scenes, therapy transcripts, or poems. The writing is grounded exclusively in the emotions of the archive: the memories are the soil, the output is what grows from them.

---

## How it works

1. Open `index.html` in any browser
2. Add emotional memories to the archive panel (or load a preset)
3. Choose a **format**, **tone**, and **length**
4. Click **Generate** — the LLM writes from the archive
5. Copy, or regenerate with different settings

---

## Project structure

```
echo/
├── index.html   — HTML shell, structure only
├── style.css    — 20 CSS-variable themes, all layout
├── app.js       — i18n, themes, presets, generation logic
└── README.md
```

Zero dependencies. No build step. No internet required except for LM Studio.

---

## LM Studio setup

ECHO uses [LM Studio](https://lmstudio.ai) as its local LLM backend.

1. Open LM Studio and load any instruction-tuned model
2. Start the local server (default port 1234)
3. Enter the model name in the LM Studio field and click **Save**

| Field | Default |
|---|---|
| URL | `http://localhost:1234/v1/chat/completions` |
| Model | *(blank = auto)* |

LM Studio settings persist via `localStorage`.

---

## Formats

| Key | EN | IT | ES | 中 |
|---|---|---|---|---|
| `letter` | Letter | Lettera | Carta | 信件 |
| `journal` | Journal entry | Diario | Diario | 日记 |
| `monologue` | Monologue | Monologo | Monólogo | 内心独白 |
| `scene` | Fiction scene | Scena fiction | Escena de ficción | 小说场景 |
| `therapy` | Therapy transcript | Trascrizione terapia | Transcripción de terapia | 心理咨询记录 |
| `poem` | Poem | Poesia | Poema | 诗歌 |

---

## Tones

| Key | Description |
|---|---|
| `raw` | Confessional, unpolished, high temperature |
| `polished` | Literary, careful sentence craft, lower temperature |
| `fragmented` | Non-linear, broken sentences, white space |
| `distant` | Detached, third-person-observational |

---

## Lengths

| Setting | Target length |
|---|---|
| Short | 100–150 words |
| Medium | 250–350 words |
| Long | 500–700 words |

---

## Preset archives

Three classic literary characters are pre-loaded as sample archives — the same anonymised profiles used in PHANTOM ARCHIVE:

| Preset | Character | Dominant themes |
|---|---|---|
| Hamlet | Hamlet, Prince of Denmark | Father, Betrayal, Purpose, Love, Fate |
| Havisham | Miss Havisham (Great Expectations) | Time, Wedding, Estella, Love, Regret |
| Frankenstein | Victor Frankenstein | Creation, Guilt, Ambition, Ice, Science |

Presets demonstrate the emotional range possible. Your own memories are always more powerful.

---

## i18n

Full interface translation in 4 languages:

| Code | Language |
|---|---|
| `EN` | English |
| `IT` | Italiano |
| `ES` | Español |
| `中` | 中文 |

The LLM generation prompt includes a language instruction, so output is in the selected language. Feeling labels, format names, tone names, length labels, and all UI strings are translated. Preset archive names are also translated in the UI.

---

## Themes

20 themes, switchable from the sidebar footer.

| # | Light | # | Dark |
|---|---|---|---|
| 1 | Ivory (default) | 11 | Obsidian |
| 2 | Paper | 12 | Midnight |
| 3 | Mint | 13 | Ember |
| 4 | Rose | 14 | Void |
| 5 | Slate | 15 | Forest |
| 6 | Cream | 16 | Crimson |
| 7 | Stone | 17 | Amethyst |
| 8 | Lilac | 18 | Graphite |
| 9 | Dawn | 19 | Candle |
| 10 | Sage | 20 | Ocean |

---

## The generation prompt

For each generation, ECHO builds a system prompt and a user message:

**System:**
```
You are a literary writer working from an emotional memory archive.
Generate content grounded ONLY in the emotional memories provided.
Do not invent events outside the archive.
Do not include titles, headings, or meta-commentary.
[Write in English / Italian / Spanish / Chinese]
```

**User:**
```
Write a letter in a raw, confessional style. Keep it short (100–150 words).

The piece must be emotionally grounded in this archive:

CONCEPT: Father | FEELING: Love
"He used to wake me before dawn to watch the sea fog lift…"

CONCEPT: Betrayal | FEELING: Rage
"The same cup. The same smile…"
```

Temperature is adjusted by tone: `raw` = 0.9, `fragmented` = 0.95, `polished` = 0.65, `distant` = 0.75.

---

## MNHEME

ECHO is built on the [MNHEME](https://github.com/aatel-license/mnheme) data model — an open-source Python database that models human memory as append-only, emotionally-tagged records. Each memory card in ECHO is a MNHEME record: concept + feeling + content.

> *"La memoria non si sovrascrive. Si stratifica."*
> Memory does not overwrite. It stratifies.

---

## License

See the MNHEME repository for licensing information.
