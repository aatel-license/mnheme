#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  mnheme_pr.sh
#  Crea un branch, patcha brain.py con persona/will/choose
#  e apre una Pull Request via GitHub CLI (gh).
#
#  Prerequisiti:
#    - git installato e configurato
#    - gh CLI installato e autenticato  (gh auth login)
#
#  Uso:
#    chmod +x mnheme_pr.sh
#    ./mnheme_pr.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

REPO_URL="https://github.com/aatel-license/mnheme"
BRANCH="feat/personality-free-will"
COMMIT_MSG="feat(brain): add persona(), will(), choose() — identity & free will layer"
PR_TITLE="feat(brain): add persona(), will(), choose() — identity & free will layer"
PR_BODY='## Motivazione

Il `Brain` attuale è interamente **reattivo**: risponde a stimoli esterni (`perceive`, `ask`, `reflect`, `dream`, `introspect`).

Manca lo strato agentivo: identità stabile, impulsi spontanei, decisioni autonome.

## Cosa aggiunge questo PR

Tre nuovi metodi + relativi dataclass in `brain.py`:

| Metodo | Cosa fa |
|---|---|
| `persona()` | Costruisce un'\''identità stabile e persistente dai ricordi (tratti, valori, paure, desideri, voce) |
| `will()` | Genera un impulso spontaneo **senza stimolo esterno** — il libero arbitrio |
| `choose(options)` | Sceglie tra opzioni guidata dalla personalità accumulata, non dalla logica |

## Gerarchia agentiva

```
persona()  →  chi sono
will()     →  cosa voglio (senza che nessuno me lo chieda)
choose()   →  come agisco quando devo decidere
```

## Esempio

```python
p = brain.persona()
print(p.core_traits)   # ["ipersensibile", "testardo", "ironico"]
print(p.worldview)     # "Il mondo delude, ma vale la pena amarlo lo stesso"

w = brain.will(persona=p)
print(w.impulse)       # "Voglio smettere di giustificarmi con chiunque"
print(w.impulse_type)  # "ribellione"

c = brain.choose(["restare", "partire", "aspettare"], persona=p)
print(c.chosen)           # "partire"
print(c.emotional_driver) # "paura di stagnare"
print(c.certainty)        # "riluttante"
```
'

# ── 1. Verifica prerequisiti ─────────────────────────────────
echo "▶ Verifico prerequisiti..."

if ! command -v git &>/dev/null; then
  echo "✗ git non trovato. Installa git e riprova."
  exit 1
fi

# if ! command -v gh &>/dev/null; then
#   echo "✗ gh CLI non trovato."
#   echo "  Installa: https://cli.github.com/"
#   echo "  Poi esegui: gh auth login"
#   exit 1
# fi

# if ! gh auth status &>/dev/null; then
#   echo "✗ gh non autenticato. Esegui: gh auth login"
#   exit 1
# fi

echo "✓ Prerequisiti OK"

# ── 2. Clone ─────────────────────────────────────────────────
WORKDIR=$(pwd)
echo "▶ Clono il repo in $WORKDIR..."
# git clone "$REPO_URL" "$WORKDIR/mnheme"
# cd "$WORKDIR/mnheme"
echo "✓ Clone completato"

# ── 3. Crea branch ───────────────────────────────────────────
echo "▶ Creo branch '$BRANCH'..."
git checkout -b "$BRANCH"
echo "✓ Branch creato"

# ── 4. Patcha brain.py con Python ────────────────────────────
echo "▶ Applico patch a brain.py..."

python3 - <<'PYEOF'
import pathlib

target = pathlib.Path("brain.py")
src    = target.read_text(encoding="utf-8")

# ── Dataclass da inserire dopo IntrospectionResult ───────────
NEW_DATACLASSES = '''

@dataclass
class PersonaResult:
    """
    Identità stabile estratta dall\'intera storia di ricordi.
    Diverso da IntrospectionResult: è un profilo *persistente*,
    pensato per essere passato come contesto ad altre operazioni.
    """
    core_traits:     list[str]
    values:          list[str]
    fears:           list[str]
    desires:         list[str]
    voice:           str
    worldview:       str
    persona_summary: str   # usabile come system prompt aggiuntivo
    provider_used:   str


@dataclass
class WillResult:
    """
    Un impulso spontaneo generato dal cervello senza stimolo esterno.
    Il libero arbitrio: agire da uno stato interno, non da una query.
    """
    impulse:          str
    impulse_type:     str            # "desiderio" | "paura" | "curiosità" | "ribellione" | "rimpianto"
    action:           str
    why:              str
    origin_memories:  list[Memory]
    provider_used:    str


@dataclass
class ChoiceResult:
    """
    Scelta tra opzioni guidata dalla personalità accumulata.
    Non sceglie per logica — sceglie perché è fatto così.
    """
    chosen:           str
    rejected:         list[str]
    reasoning:        str
    emotional_driver: str
    memories_invoked: list[Memory]
    certainty:        str            # "sicuro" | "incerto" | "riluttante" | "tormentato"
    provider_used:    str
'''

# Ancora: subito dopo la definizione di IntrospectionResult
# (dopo l'ultima riga del dataclass che termina con `provider_used : str`)
ANCHOR_DATACLASS = (
    "@dataclass\n"
    "class IntrospectionResult:\n"
    '    """Risultato di introspect()."""\n'
    "    portrait : str\n"
    "    dominant_concepts : list[str]\n"
    "    emotional_map : dict[str, int]\n"
    "    total_memories : int\n"
    "    provider_used : str"
)

if ANCHOR_DATACLASS not in src:
    raise RuntimeError(
        "Anchor dataclass non trovato in brain.py. "
        "Il file potrebbe essere stato modificato."
    )

src = src.replace(ANCHOR_DATACLASS, ANCHOR_DATACLASS + NEW_DATACLASSES, 1)

# ── Metodi da inserire dopo summarize() ──────────────────────
NEW_METHODS = '''
    # ── PERSONA ──────────────────────────────

    def persona(self) -> PersonaResult:
        """
        Costruisce un\'identità stabile e persistente dall\'intera storia di ricordi.

        Diverso da introspect(): non è un\'analisi narrativa, è un profilo strutturato
        pensato per essere riusato come contesto nelle altre operazioni cognitive.

        Il risultato `persona_summary` può essere passato come system prompt aggiuntivo
        per colorare tutte le risposte successive con la personalità reale del soggetto.

        Esempio
        -------
        >>> p = brain.persona()
        >>> print(p.core_traits)     # ["testardo", "ipersensibile", "ironico"]
        >>> print(p.worldview)       # "Il mondo delude, ma vale la pena amarlo lo stesso"
        >>> print(p.persona_summary) # usabile come system prompt aggiuntivo
        """
        total = self._db.count()
        if total == 0:
            raise ValueError("Database vuoto. Nessuna identità da costruire.")

        concepts = self._db.list_concepts()
        feelings = self._db.feeling_distribution()
        top_mems = self._db.recall_all(limit=30)
        context  = _memories_to_context(top_mems)

        top_c = sorted(concepts, key=lambda c: c["total"], reverse=True)[:6]
        stats  = f"Totale ricordi: {total}\\n"
        stats += "Concetti dominanti: " + ", ".join(
            f"{c[\'concept\']}({c[\'total\']})" for c in top_c
        ) + "\\n"
        stats += "Emozioni prevalenti: " + ", ".join(
            f"{f}({n})" for f, n in
            sorted(feelings.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        prompt = (
            f"Analizza questa storia di ricordi e costruisci un\'identità psicologica stabile.\\n\\n"
            f"STATISTICHE:\\n{stats}\\n\\n"
            f"RICORDI (campione cronologico):\\n{context}\\n\\n"
            f"Restituisci SOLO un JSON con questi campi:\\n"
            f"{{\\n"
            f\'  "core_traits": ["trait1", "trait2", "trait3", "trait4"],\\n\'
            f\'  "values": ["valore1", "valore2", "valore3"],\\n\'
            f\'  "fears": ["paura1", "paura2"],\\n\'
            f\'  "desires": ["desiderio1", "desiderio2"],\\n\'
            f\'  "voice": "come pensa e parla — ritmo, stile, tono in 1 frase",\\n\'
            f\'  "worldview": "visione del mondo in una frase densa, non banale",\\n\'
            f\'  "persona_summary": "ritratto in 3-4 righe, prima persona, \'
            f\'usabile come system prompt — chi sono, come elaboro il mondo, cosa mi muove"\\n\'
            f"}}\\n\\n"
            f"I tratti devono emergere dai DATI reali. "
            f"Sii specifico, tagliente, non diplomatico. Rispondi SOLO con il JSON."
        )

        raw  = self._llm.complete(self._system, prompt)
        data = _parse_json(raw)

        return PersonaResult(
            core_traits     = data.get("core_traits", []),
            values          = data.get("values", []),
            fears           = data.get("fears", []),
            desires         = data.get("desires", []),
            voice           = data.get("voice", ""),
            worldview       = data.get("worldview", ""),
            persona_summary = data.get("persona_summary", ""),
            provider_used   = self._llm.active_profile.name,
        )

    # ── WILL ─────────────────────────────────

    def will(
        self,
        *,
        persona: Optional[PersonaResult] = None,
        seed_feeling: Optional[str]      = None,
        n_memories: int                  = 10,
    ) -> WillResult:
        """
        Genera un impulso spontaneo senza stimolo esterno.

        Il cervello attinge ai propri ricordi e decide autonomamente
        cosa vuole, teme, rimpiange o rifiuta — in questo momento.
        È il libero arbitrio: agire da uno stato interno, non da una query.

        Parametri
        ---------
        persona      : PersonaResult opzionale per ancorare l\'impulso all\'identità stabile
        seed_feeling : se fornito, campiona ricordi da quel sentimento
        n_memories   : quanti ricordi usare come substrato dell\'impulso

        Esempio
        -------
        >>> w = brain.will()
        >>> print(w.impulse)       # "Voglio smettere di giustificarmi"
        >>> print(w.impulse_type)  # "ribellione"
        >>> print(w.action)        # "Scrivere una lettera che non spedirò mai"
        """
        all_mems = self._db.recall_all()
        if len(all_mems) < 2:
            raise ValueError("Servono almeno 2 ricordi per generare un impulso.")

        if seed_feeling:
            pool = [m for m in all_mems if m.feeling == seed_feeling] or all_mems
        else:
            intense  = {"ansia", "rabbia", "paura", "nostalgia", "malinconia", "amore"}
            weighted = []
            for m in all_mems:
                weighted.append(m)
                if m.feeling in intense:
                    weighted.append(m)
            pool = weighted

        sampled = random.sample(pool, min(n_memories, len(pool)))
        context = _memories_to_context(sampled)

        persona_ctx = ""
        if persona:
            persona_ctx = (
                f"\\nIDENTITÀ DI BASE:\\n"
                f"Tratti: {', '.join(persona.core_traits)}\\n"
                f"Valori: {', '.join(persona.values)}\\n"
                f"Paure: {', '.join(persona.fears)}\\n"
                f"Visione del mondo: {persona.worldview}\\n"
            )

        valid_types = ["desiderio", "paura", "curiosità", "ribellione", "rimpianto"]

        prompt = (
            f"Sei un cervello che guarda i propri ricordi e sente emergere qualcosa.\\n"
            f"Nessuno ti ha chiesto niente. Agisci da solo, dal tuo stato interno.\\n"
            f"{persona_ctx}\\n"
            f"RICORDI (substrato dell\'impulso):\\n{context}\\n\\n"
            f"Da questi ricordi, genera UN impulso spontaneo autentico.\\n"
            f"Restituisci SOLO un JSON:\\n"
            f"{{\\n"
            f\'  "impulse": "in prima persona — Voglio/Devo/Rifiuto/Rimpiango/Mi chiedo (1 frase densa)",\\n\'
            f\'  "impulse_type": "uno tra: {", ".join(valid_types)}",\\n\'
            f\'  "action": "cosa faresti concretamente — specifico, non metaforico",\\n\'
            f\'  "why": "motivazione viscerale — non razionale, non diplomatica (2-3 frasi)"\\n\'
            f"}}\\n\\n"
            f"L\'impulso deve sembrare inevitabile, non scelto. Rispondi SOLO con il JSON."
        )

        raw  = self._llm.complete(self._system, prompt)
        data = _parse_json(raw)

        imp_type = data.get("impulse_type", "desiderio")
        if imp_type not in valid_types:
            imp_type = "desiderio"

        return WillResult(
            impulse         = data.get("impulse", ""),
            impulse_type    = imp_type,
            action          = data.get("action", ""),
            why             = data.get("why", ""),
            origin_memories = sampled,
            provider_used   = self._llm.active_profile.name,
        )

    # ── CHOOSE ───────────────────────────────

    def choose(
        self,
        options:  list[str],
        context:  str = "",
        *,
        persona:  Optional[PersonaResult] = None,
        max_memories: int = 12,
    ) -> ChoiceResult:
        """
        Sceglie tra opzioni basandosi sulla personalità accumulata, non sulla logica.

        Non ottimizza — esprime chi è. La scelta è guidata da paure, desideri,
        valori e pattern emotivi distillati dai ricordi.

        Parametri
        ---------
        options      : lista di opzioni tra cui scegliere (2-6 consigliato)
        context      : contesto della decisione (opzionale)
        persona      : PersonaResult opzionale
        max_memories : quanti ricordi usare come base della scelta

        Esempio
        -------
        >>> c = brain.choose(["restare", "partire", "aspettare"], context="lavoro")
        >>> print(c.chosen)           # "partire"
        >>> print(c.emotional_driver) # "paura di stagnare"
        >>> print(c.certainty)        # "riluttante"
        """
        if len(options) < 2:
            raise ValueError("Servono almeno 2 opzioni.")

        memories: list[Memory] = []
        seen: set[str] = set()

        def _add(mems: list[Memory]) -> None:
            for m in mems:
                if m.memory_id not in seen:
                    memories.append(m)
                    seen.add(m.memory_id)

        if context:
            _add(self._db.search(context, limit=8))

        for opt in options:
            for word in opt.split()[:2]:
                _add(self._db.search(word, limit=3))

        if not memories:
            _add(self._db.recall_all(limit=max_memories))

        memories    = memories[:max_memories]
        mem_context = _memories_to_context(memories)

        persona_ctx = ""
        if persona:
            persona_ctx = (
                f"CHI SEI:\\n"
                f"Tratti: {', '.join(persona.core_traits)}\\n"
                f"Valori: {', '.join(persona.values)}\\n"
                f"Paure: {', '.join(persona.fears)}\\n"
                f"Desideri: {', '.join(persona.desires)}\\n"
                f"Visione: {persona.worldview}\\n\\n"
            )

        options_str    = "\\n".join(f"- {o}" for o in options)
        context_str    = f"Contesto: {context}\\n\\n" if context else ""
        valid_certainty = ["sicuro", "incerto", "riluttante", "tormentato"]

        prompt = (
            f"{persona_ctx}"
            f"RICORDI RILEVANTI:\\n{mem_context}\\n\\n"
            f"{context_str}"
            f"OPZIONI:\\n{options_str}\\n\\n"
            f"Scegli UN\'opzione basandoti su chi sei — non su cosa è logico o ottimale.\\n"
            f"Scegli come sceglierebbe una persona con questa storia emotiva.\\n\\n"
            f"Restituisci SOLO un JSON:\\n"
            f"{{\\n"
            f\'  "chosen": "opzione scelta — copiata esattamente dalla lista",\\n\'
            f\'  "rejected": {{"opzione": "motivazione breve, viscerale"}},\\n\'
            f\'  "reasoning": "ragionamento interno — non neutro, dentro la persona (3-5 frasi)",\\n\'
            f\'  "emotional_driver": "emozione dominante che ha guidato la scelta",\\n\'
            f\'  "certainty": "uno tra: {", ".join(valid_certainty)}"\\n\'
            f"}}\\n\\n"
            f"La scelta deve sembrare umana, non algoritmica. Rispondi SOLO con il JSON."
        )

        raw  = self._llm.complete(self._system, prompt)
        data = _parse_json(raw)

        chosen      = data.get("chosen", options[0])
        rejected_raw = data.get("rejected", {})
        rejected    = (
            [f"{k}: {v}" for k, v in rejected_raw.items()]
            if isinstance(rejected_raw, dict)
            else [str(r) for r in rejected_raw if r != chosen]
        )
        certainty = data.get("certainty", "incerto")
        if certainty not in valid_certainty:
            certainty = "incerto"

        return ChoiceResult(
            chosen           = chosen,
            rejected         = rejected,
            reasoning        = data.get("reasoning", ""),
            emotional_driver = data.get("emotional_driver", ""),
            memories_invoked = memories,
            certainty        = certainty,
            provider_used    = self._llm.active_profile.name,
        )
'''

# Ancora: fine di summarize() — subito prima di __repr__
ANCHOR_METHODS = "    def __repr__(self) -> str:"

if ANCHOR_METHODS not in src:
    raise RuntimeError(
        "Anchor __repr__ non trovato in brain.py. "
        "Il file potrebbe essere stato modificato."
    )

src = src.replace(ANCHOR_METHODS, NEW_METHODS + "\n    def __repr__(self) -> str:", 1)

target.write_text(src, encoding="utf-8")
print("✓ brain.py patchato con successo")
PYEOF

echo "✓ Patch applicata"

# ── 5. Commit e push ─────────────────────────────────────────
echo "▶ Commit e push..."
git add brain.py
git commit -m "$COMMIT_MSG"
git push origin "$BRANCH"
echo "✓ Push completato"

# # ── 6. Apre la Pull Request ──────────────────────────────────
# echo "▶ Creo la Pull Request..."
# gh pr create \
#   --title  "$PR_TITLE" \
#   --body   "$PR_BODY" \
#   --base   main \
#   --head   "$BRANCH"

# echo ""
# echo "✅ PR creata con successo!"
# echo "   Controlla: https://github.com/aatel-license/mnheme/pulls"
