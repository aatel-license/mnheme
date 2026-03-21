# MNHEME — Le 4 Funzioni Cognitive

MNHEME è un sistema di memoria digitale umana. Le 4 funzioni rappresentano processi cognitivi distinti, tutti implementati in `src/core/brain.js` (web) e `brain.py` (Python), esposti tramite componenti React.

---

## 1. PERCEIVE — Acquisizione e Arricchimento Ricordi

**Cosa fa**: Prende il testo grezzo dell'utente e lo trasforma in un ricordo strutturato e arricchito.

**Flusso**:
1. L'utente scrive un pensiero/esperienza/emozione
2. Il testo viene inviato all'LLM con temperatura 0.3 (bassa, per estrazione consistente)
3. L'LLM analizza e restituisce un JSON con:
   - **concept**: concetto chiave astratto (1-3 parole, es. "Debito", "Famiglia")
   - **feeling**: emozione da una lista di 15 sentimenti italiani
   - **tags**: tag tematici
   - **enriched**: il testo riscritto in prima persona con profondità psicologica
4. Il feeling viene validato (se l'LLM ne restituisce uno non valido, `closestFeeling()` trova il più vicino)
5. Il ricordo viene salvato nel DB con UUID, checksum SHA-256, timestamp — ed è **immutabile** (append-only)

**Chiamate LLM**: 1 (estrazione + arricchimento)

**Output**: Oggetto Memory congelato + metadati (concept, feeling, tags, enriched)

---

## 2. ASK — Domande con RAG (Retrieval-Augmented Generation)

**Cosa fa**: Risponde a domande personali cercando nei ricordi rilevanti e usandoli come contesto per l'LLM. È un sistema RAG completo.

**Flusso** (2 chiamate LLM):
1. **Chiamata 1 — Estrazione keyword**: L'LLM analizza la domanda ed estrae `keywords` e `concepts`
2. **Ricerca ricordi**:
   - Per ogni concept → `db.recall(concept)` (max 5 risultati)
   - Per ogni keyword → `db.search(keyword)` usando l'indice invertito (max 5 risultati)
   - Deduplicazione per memory_id
   - Fallback: tutti i ricordi se nessun match
   - Limite: 15 ricordi massimi
3. **Chiamata 2 — Generazione risposta**: L'LLM riceve i ricordi formattati cronologicamente + la domanda, con istruzione di rispondere **solo** basandosi sui ricordi forniti
4. Estrae il livello di certezza dalla risposta ("Certezza: alta/media/bassa — motivazione")

**Chiamate LLM**: 2 (estrazione keyword + generazione risposta)

**Output**: Risposta + ricordi usati + livello di certezza. **Non salva nulla**.

---

## 3. REFLECT — Introspezione Emotiva su un Concetto

**Cosa fa**: Analizza come i sentimenti verso un concetto si sono evoluti nel tempo. È un motore di introspezione.

**Flusso**:
1. L'utente seleziona un concetto (con autocomplete dai concetti esistenti)
2. Recupera **tutti** i ricordi per quel concetto in ordine cronologico (più vecchi prima)
3. Estrae la timeline dei sentimenti (es. "rabbia → tristezza → serenità")
4. L'LLM riceve ricordi + sequenza emotiva e analizza:
   - Come è cambiato il rapporto emotivo nel tempo?
   - Quali pattern ricorrenti esistono?
   - Cosa resta irrisolto?
   - Qual è il significato psicologico di questo percorso?
5. Estrae l'"Arco" — un breve riassunto dell'evoluzione emotiva

**Chiamate LLM**: 1 (analisi dell'evoluzione emotiva)

**Output**: Riflessione dettagliata + arco emotivo + tutti i ricordi. **Non salva nulla**.

---

## 4. DREAM — Scoperta di Connessioni Nascoste

**Cosa fa**: Simula il sogno — prende ricordi apparentemente non correlati e trova connessioni sorprendenti, come la consolidazione della memoria durante il sonno.

**Flusso**:
1. Recupera **tutti** i ricordi dal DB
2. **Campionamento per diversità emotiva**:
   - Raggruppa i ricordi per feeling
   - Mescola casualmente l'ordine dei feeling (Fisher-Yates shuffle)
   - Campiona ~(8 / numero_feeling) ricordi da ciascun feeling
   - Questo garantisce che il "sogno" tocchi emozioni diverse
3. Mescola casualmente la selezione finale (default: 8 ricordi)
4. L'LLM riceve questi ricordi con l'istruzione: *"Questi ricordi sembrano non correlati. Trova il filo nascosto."*
   - Connessione più inaspettata e profonda
   - Tema latente che li attraversa tutti
   - Cosa rivelano insieme che nessuno rivela da solo
   - Metafora o immagine che li contiene tutti
5. L'LLM scrive come un'analisi onirica — suggestiva, non banale

**Chiamate LLM**: 1 (analisi onirica)

**Output**: Testo delle connessioni trovate + i ricordi usati. **Non salva nulla**.

---

## Sentimenti Supportati (15)

`gioia` · `tristezza` · `rabbia` · `paura` · `nostalgia` · `amore` · `malinconia` · `serenità` · `sorpresa` · `ansia` · `gratitudine` · `vergogna` · `orgoglio` · `noia` · `curiosità`

---

## Architettura a Strati

```
Componenti React (Perceive, Ask, Reflect, Dream)
         │
    useBrain Hook (stato loading/errore)
         │
    Brain (logica cognitiva, prompt LLM)
         │
    MemoryDB (mnheme.js / mnheme.py) ← append-only, immutabile
    ├── StorageEngine (localStorage / file binario .mnheme)
    └── IndexEngine (7 indici: concept, feeling, tag, cf, timeline, all, word)
         │
    LLMProvider → API OpenAI-compatibile o Anthropic Claude
```

### Nota chiave

**Perceive** è l'unica funzione che scrive nel database. Le altre tre (Ask, Reflect, Dream) sono solo lettura e analisi, ciascuna con una prospettiva diversa sui ricordi memorizzati:

| Funzione | Scrive? | Prospettiva |
|----------|---------|-------------|
| **Perceive** | Si | Acquisizione e strutturazione |
| **Ask** | No | Interrogazione RAG |
| **Reflect** | No | Introspezione temporale |
| **Dream** | No | Associazione onirica |
