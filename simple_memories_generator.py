"""
generate_memories.py
====================
Generatore di ricordi sintetici per MNHEME.

Usa un modello LLM locale (LM Studio / Ollama / qualsiasi endpoint
OpenAI-compatibile) per produrre ricordi realistici e li posta
direttamente sulla REST API di MNHEME.

Utilizzo
--------
    # Genera 20 ricordi con il modello auto-rilevato
    python generate_memories.py --n 20

    # Specifica server LLM e API MNHEME
    python generate_memories.py --n 50 --llm-url http://localhost:1234 --api-url http://localhost:8000

    # Fissa il modello (utile se il server ne ha più di uno caricato)
    python generate_memories.py --n 30 --model my-model-name

    # Dry-run: genera senza postare
    python generate_memories.py --n 10 --dry-run

    # Stampa output dettagliato
    python generate_memories.py --n 10 --verbose

Dipendenze
----------
    pip install openai requests
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
import textwrap
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

# ── Import Feeling dal progetto ──────────────────────────────
try:
    from mnheme import Feeling
    VALID_FEELINGS: list[str] = [f.value for f in Feeling]
except ImportError:
    # Fallback se mnheme non è nel path — lista hardcoded
    VALID_FEELINGS = [
        "ansia", "paura", "sollievo", "tristezza", "gioia", "rabbia",
        "vergogna", "senso_di_colpa", "nostalgia", "speranza", "orgoglio",
        "delusione", "solitudine", "confusione", "gratitudine", "invidia",
        "imbarazzo", "eccitazione", "rassegnazione", "stupore", "amore",
        "malinconia", "serenità", "sorpresa", "noia", "curiosità",
    ]

# ── ANSI colors ──────────────────────────────────────────────
GRN  = "\033[32m"
RED  = "\033[31m"
YLW  = "\033[33m"
CYN  = "\033[36m"
DIM  = "\033[2m"
BOLD = "\033[1m"
NC   = "\033[0m"

def _c(color: str, text: str) -> str:
    return f"{color}{text}{NC}"


# ────────────────────────────────────────────────────────────
# DATA MODEL
# ────────────────────────────────────────────────────────────

@dataclass
class MemoryRecord:
    concept    : str
    feeling    : str
    content    : str
    media_type : str       = "text"
    note       : str       = ""
    tags       : List[str] = field(default_factory=list)

    def to_payload(self) -> dict:
        """Serializza nel formato atteso dall'API MNHEME."""
        return {
            "concept":    self.concept,
            "feeling":    self.feeling,
            "content":    self.content,
            "media_type": self.media_type,
            "note":       self.note,
            "tags":       self.tags or [],
        }


# ────────────────────────────────────────────────────────────
# LLM CLIENT — chiama il modello locale
# ────────────────────────────────────────────────────────────

class LLMClient:
    """
    Client minimale per endpoint OpenAI-compatibili.
    Non dipende dall'SDK openai — usa solo urllib (stdlib).
    Compatibile con LM Studio, Ollama, llama.cpp, vLLM, ecc.
    """

    def __init__(self, base_url: str, model: str, api_key: str = "") -> None:
        self.base_url   = base_url.rstrip("/")
        self.model      = model
        self.api_key    = api_key
        self._chat_url  = f"{self.base_url}/v1/chat/completions"
        self._models_url= f"{self.base_url}/v1/models"

    # ── Auto-discovery del modello ────────────────────────

    def discover_model(self) -> str:
        """
        Interroga /v1/models e restituisce il primo modello disponibile.
        Lancia RuntimeError se il server non è raggiungibile.
        """
        try:
            req  = urllib.request.Request(self._models_url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data   = json.loads(resp.read())
                models = [m.get("id", "") for m in data.get("data", [])]
                if not models:
                    raise RuntimeError("Nessun modello trovato su /v1/models")
                return models[0]
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Server LLM non raggiungibile a {self.base_url}: {e.reason}\n"
                "Assicurati che LM Studio (o Ollama) sia avviato."
            ) from e

    # ── Completamento testuale ────────────────────────────

    def complete(
        self,
        system     : str,
        user       : str,
        temperature: float = 0.9,
        max_tokens : int   = 2048,
    ) -> str:
        """
        Chiama il modello con il prompt dato e restituisce il testo.
        Lancia LLMError su errori HTTP o risposta malformata.
        """
        payload = json.dumps({
            "model":       self.model,
            "temperature": temperature,
            "max_tokens":  max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        }, ensure_ascii=False).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "User-Agent":   "MNHEME-Generator/2.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            self._chat_url, data=payload, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read())
            return body["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(
                f"LLM HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}"
            ) from e
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Risposta LLM malformata: {e}") from e


# ────────────────────────────────────────────────────────────
# MNHEME API CLIENT
# ────────────────────────────────────────────────────────────

class MnhemeClient:
    """Posta ricordi sulla REST API MNHEME."""

    def __init__(self, api_url: str) -> None:
        self.api_url = api_url.rstrip("/")
        self._mem_url = f"{self.api_url}/memories"

    def ping(self) -> bool:
        """Verifica che il server MNHEME sia raggiungibile."""
        try:
            with urllib.request.urlopen(
                f"{self.api_url}/stats", timeout=4
            ):
                return True
        except Exception:
            return False

    def post(self, memory: MemoryRecord) -> str:
        """
        Posta un ricordo e ritorna il memory_id assegnato.
        Lancia RuntimeError su errori HTTP.
        """
        payload = json.dumps(
            memory.to_payload(), ensure_ascii=False
        ).encode("utf-8")

        req = urllib.request.Request(
            self._mem_url,
            data    = payload,
            headers = {
                "Content-Type": "application/json",
                "accept":       "application/json",
            },
            method = "POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            return (
                data.get("memory_id")
                or data.get("id")
                or data.get("_id")
                or "?"
            )
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            raise RuntimeError(f"API HTTP {e.code}: {body}") from e


# ────────────────────────────────────────────────────────────
# GENERATOR
# ────────────────────────────────────────────────────────────

# ── Distribuzione target dei feeling ────────────────────────
# Rispecchia la distribuzione emotiva umana realistica:
# ~40% positivi, ~35% negativi, ~25% neutri/ambivalenti
_FEELING_WEIGHTS: dict[str, float] = {
    # Positivi
    "gioia"        : 1.6,
    "amore"        : 1.5,
    "serenità"     : 1.4,
    "gratitudine"  : 1.3,
    "orgoglio"     : 1.2,
    "speranza"     : 1.2,
    "eccitazione"  : 1.1,
    "sollievo"     : 1.1,
    "stupore"      : 1.0,
    "curiosità"    : 1.0,
    "sorpresa"     : 0.9,
    # Neutri / ambivalenti
    "nostalgia"    : 1.1,
    "malinconia"   : 0.9,
    "rassegnazione": 0.8,
    "confusione"   : 0.8,
    "noia"         : 0.7,
    # Negativi (tenuti sotto controllo)
    "tristezza"    : 0.8,
    "ansia"        : 0.6,
    "paura"        : 0.6,
    "solitudine"   : 0.6,
    "delusione"    : 0.6,
    "rabbia"       : 0.5,
    "vergogna"     : 0.5,
    "imbarazzo"    : 0.5,
    "invidia"      : 0.4,
    "senso_di_colpa": 0.4,
}

def _pick_feelings_for_batch(n: int, used_feelings: list[str]) -> list[str]:
    """
    Sceglie n feeling per un batch rispettando la distribuzione target.
    I feeling già molto usati vengono penalizzati ulteriormente.
    """
    # Conta quante volte ogni feeling è già stato usato
    usage: dict[str, int] = {}
    for f in used_feelings:
        usage[f] = usage.get(f, 0) + 1
    max_used = max(usage.values(), default=1)

    # Peso finale = peso base / (1 + volte usato normalizzato)
    weights = []
    for f in VALID_FEELINGS:
        base   = _FEELING_WEIGHTS.get(f, 0.7)
        used_n = usage.get(f, 0)
        penalty = 1 + (used_n / max(max_used, 1)) * 2
        weights.append(base / penalty)

    # Campiona n feeling con rimpiazzo (permette ripetizioni solo se necessario)
    chosen = random.choices(VALID_FEELINGS, weights=weights, k=n)
    return chosen


def _build_prompt(
    n                    : int,
    used_concepts        : list[str],
    used_contents_prefix : list[str],
    target_feelings      : list[str],
) -> str:
    """Costruisce il prompt per generare n ricordi con feeling pre-assegnati."""
    domains_sample = random.sample(_DOMAINS, min(6, len(_DOMAINS)))
    seed = random.randint(0, 99_999_999)

    avoid_concepts = json.dumps(used_concepts[-40:], ensure_ascii=False)
    avoid_prefixes = json.dumps(
        [c[:30] for c in used_contents_prefix[-20:]], ensure_ascii=False
    )

    # Costruisce le assegnazioni feeling→slot esplicite
    assignments = "\n".join(
        f"  Ricordo {i+1}: feeling = \"{f}\""
        for i, f in enumerate(target_feelings)
    )

    return textwrap.dedent(f"""
        SEED: {seed}
        AMBITI SUGGERITI (scegli liberamente tra questi e altri): {', '.join(domains_sample)}

        Genera esattamente {n} ricordi personali COMPLETAMENTE DISTINTI.

        ASSEGNAZIONE FEELING OBBLIGATORIA — usa ESATTAMENTE questi valori nell'ordine:
{assignments}

        REGOLE CONCEPT:
        - Una sola parola (sostantivo singolo, minuscolo, senza articoli)
        - Esempi buoni: "mutuo", "promozione", "tradimento", "vacanza", "dentista"
        - NON ripetere: {avoid_concepts}

        REGOLE CONTENT:
        - Prima persona, specifico e concreto (1-3 righe, max 200 caratteri)
        - Il tono DEVE essere coerente con il feeling assegnato
        - Evita inizi troppo simili a: {avoid_prefixes}
        - Niente cliché ("mi sono reso conto", "ho capito che", "oggi ho scoperto")

        REGOLE NOTE:
        - Contesto aggiuntivo breve (luogo, data approssimativa, chi c'era)
        - Può essere vuota ""

        REGOLE TAGS:
        - Lista di 1-4 stringhe, minuscolo, specifiche
        - Esempi: ["2019", "Milano", "lavoro", "collega"]

        OUTPUT — array JSON di {n} oggetti, niente altro:
        [
          {{
            "concept": "parolasingola",
            "feeling": "esattamente_come_assegnato",
            "content": "...",
            "note": "...",
            "tags": ["tag1", "tag2"]
          }}
        ]
    """).strip()


def _clean_concept(raw: str) -> str:
    """Normalizza il concept: prima parola, minuscolo, solo alfanumerici."""
    word = raw.strip().split()[0] if raw.strip() else "ricordo"
    # rimuove caratteri non-word
    import re
    word = re.sub(r"[^\w]", "", word, flags=re.UNICODE)
    return word.lower() or "ricordo"


def _parse_memories(text: str) -> list[dict]:
    """
    Estrae la lista JSON dal testo del modello.
    Gestisce: risposta già JSON, JSON annidato in testo, array parziale.
    """
    text = text.strip()

    # Rimuovi eventuali code fences
    if text.startswith("```"):
        lines = [l for l in text.splitlines() if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # Tentativo 1: parse diretto
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "memories" in result:
            return result["memories"]
    except json.JSONDecodeError:
        pass

    # Tentativo 2: estrai il primo array JSON valido
    import re
    match = re.search(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Impossibile estrarre JSON dalla risposta:\n{text[:400]}")


def _validate_record(item: dict) -> MemoryRecord | None:
    """
    Valida e normalizza un oggetto ricordo.
    Restituisce None se il record è irrecuperabile.
    """
    concept = _clean_concept(str(item.get("concept", "")))
    if not concept:
        return None

    feeling = str(item.get("feeling", "")).strip()
    if feeling not in VALID_FEELINGS:
        # Prova a correggere feeling parziale (es. "senso di colpa" → "senso_di_colpa")
        feeling_norm = feeling.replace(" ", "_")
        if feeling_norm in VALID_FEELINGS:
            feeling = feeling_norm
        else:
            feeling = random.choice(VALID_FEELINGS)

    content = str(item.get("content", "")).strip()
    if not content:
        return None

    # Tronca content se troppo lungo
    if len(content) > 400:
        content = content[:397] + "…"

    note = str(item.get("note", "")).strip()[:200]

    # Tags: assicura lista di stringhe
    raw_tags = item.get("tags", [])
    if isinstance(raw_tags, str):
        raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    tags = [str(t).strip().lower() for t in raw_tags if t][:6]

    return MemoryRecord(
        concept    = concept,
        feeling    = feeling,
        content    = content,
        media_type = "text",
        note       = note,
        tags       = tags,
    )


# ────────────────────────────────────────────────────────────
# BATCH WORKER
# ────────────────────────────────────────────────────────────

def _generate_batch(
    llm            : LLMClient,
    api            : MnhemeClient,
    batch_size     : int,
    batch_id       : int,
    used_concepts  : list[str],
    used_feelings  : list[str],
    used_contents  : list[str],
    target_feelings: list[str],
    dry_run        : bool,
    verbose        : bool,
    max_retries    : int = 3,
) -> list[tuple[MemoryRecord, str | None]]:
    """
    Genera un batch di ricordi e li posta sull'API.
    target_feelings: lista di feeling pre-assegnati per questo batch
    (uno per slot) — garantisce la distribuzione target globale.
    """
    results: list[tuple[MemoryRecord, str | None]] = []

    for attempt in range(1, max_retries + 1):
        try:
            prompt = _build_prompt(
                batch_size, used_concepts, used_contents, target_feelings
            )
            raw = llm.complete(
                _SYSTEM_PROMPT, prompt,
                temperature = 0.95 + random.uniform(-0.05, 0.15),
                max_tokens  = 2048,
            )
            raw_list = _parse_memories(raw)
            break
        except (RuntimeError, ValueError) as e:
            if attempt == max_retries:
                print(f"  {_c(RED,'✗')} batch {batch_id} fallito dopo {max_retries} tentativi: {e}")
                return []
            wait = 2 ** attempt
            print(f"  {_c(YLW,'⚠')} batch {batch_id} tentativo {attempt} fallito ({e}), retry in {wait}s…")
            time.sleep(wait)

    validated: list[MemoryRecord] = []
    for i, item in enumerate(raw_list):
        record = _validate_record(item)
        if record is None:
            if verbose:
                print(f"  {_c(DIM,'·')} record scartato: {json.dumps(item, ensure_ascii=False)[:80]}")
            continue
        # Se il modello ha ignorato il feeling assegnato, forzalo
        if i < len(target_feelings) and record.feeling != target_feelings[i]:
            if verbose:
                print(f"  {_c(DIM,'·')} feeling corretto: {record.feeling} → {target_feelings[i]}")
            record.feeling = target_feelings[i]
        # Dedup locale
        if record.concept in [r.concept for r in validated]:
            if verbose:
                print(f"  {_c(DIM,'·')} concept duplicato in batch: {record.concept}")
            continue
        validated.append(record)

    for record in validated[:batch_size]:
        memory_id = None
        if not dry_run:
            for attempt in range(1, max_retries + 1):
                try:
                    memory_id = api.post(record)
                    break
                except RuntimeError as e:
                    if attempt == max_retries:
                        print(f"  {_c(RED,'✗')} POST fallito per [{record.concept}]: {e}")
                    else:
                        time.sleep(1.5 ** attempt)

        status = _c(GRN, "✓") if (memory_id or dry_run) else _c(RED, "✗")
        id_str = _c(DIM, f"id: {memory_id}") if memory_id else (_c(DIM, "dry-run") if dry_run else "")
        feeling_col = _c(CYN, record.feeling)
        tags_str = _c(DIM, f"[{', '.join(record.tags)}]") if record.tags else ""

        print(f"  {status} {_c(BOLD, record.concept):<22} {feeling_col:<24} {id_str} {tags_str}")
        if verbose:
            wrapped = textwrap.fill(record.content, width=72, initial_indent="     ")
            print(_c(DIM, wrapped))

        results.append((record, memory_id))

    return results


# ────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera ricordi sintetici per MNHEME via LLM locale.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Esempi:
              python generate_memories.py --n 20
              python generate_memories.py --n 50 --llm-url http://localhost:1234
              python generate_memories.py --n 10 --dry-run --verbose
              python generate_memories.py --n 100 --batch-size 8 --workers 4
        """),
    )
    parser.add_argument("--n",           type=int,   default=10,                        help="Numero totale di ricordi da generare (default: 10)")
    parser.add_argument("--llm-url",     type=str,   default="http://localhost:1234",    help="Base URL del server LLM (default: http://localhost:1234)")
    parser.add_argument("--model",       type=str,   default="",                        help="Nome modello (default: auto-discovery da /v1/models)")
    parser.add_argument("--api-key",     type=str,   default="",                        help="API key per il server LLM (opzionale)")
    parser.add_argument("--api-url",     type=str,   default="http://localhost:8000",    help="URL base API MNHEME (default: http://localhost:8000)")
    parser.add_argument("--batch-size",  type=int,   default=5,                         help="Ricordi per batch LLM (default: 5)")
    parser.add_argument("--workers",     type=int,   default=3,                         help="Thread paralleli per i batch (default: 3)")
    parser.add_argument("--dry-run",     action="store_true",                            help="Genera senza postare sull'API")
    parser.add_argument("--verbose",     action="store_true",                            help="Stampa il content completo di ogni ricordo")
    parser.add_argument("--sequential",  action="store_true",                            help="Disabilita la generazione parallela (utile per debug)")
    args = parser.parse_args()

    # ── Banner ──────────────────────────────────────────────
    print(f"\n{_c(BOLD,'MNHEME — Memory Generator')}  {_c(DIM,'v2.0')}")
    print("─" * 55)

    # ── Setup LLM ───────────────────────────────────────────
    llm = LLMClient(args.llm_url, model=args.model, api_key=args.api_key)

    if not args.model:
        print(f"  {_c(CYN,'→')} Auto-discovery modello da {args.llm_url}…", end=" ", flush=True)
        try:
            llm.model = llm.discover_model()
            print(_c(GRN, llm.model))
        except RuntimeError as e:
            print(_c(RED, "fallito"))
            print(f"\n  {_c(RED,'Errore:')} {e}")
            sys.exit(1)
    else:
        print(f"  {_c(CYN,'→')} Modello: {_c(GRN, llm.model)}")

    # ── Setup API ───────────────────────────────────────────
    api = MnhemeClient(args.api_url)

    if not args.dry_run:
        print(f"  {_c(CYN,'→')} Ping MNHEME API {args.api_url}…", end=" ", flush=True)
        if api.ping():
            print(_c(GRN, "ok"))
        else:
            print(_c(YLW, "non raggiungibile — continuo comunque"))
    else:
        print(f"  {_c(YLW,'→')} Modalità DRY-RUN — nessun POST all'API")

    # ── Calcola batch ────────────────────────────────────────
    bs         = max(1, min(args.batch_size, 10))  # cap a 10 per qualità
    n_batches  = (args.n + bs - 1) // bs
    batch_sizes = [bs] * n_batches
    batch_sizes[-1] = args.n - bs * (n_batches - 1)

    print(f"\n  {_c(DIM,f'Generando {args.n} ricordi in {n_batches} batch da {bs} · {args.workers} worker paralleli')}")
    print("─" * 55)

    # ── Pre-calcola distribuzione feeling per TUTTI i batch ─
    # Genera l'assegnazione feeling globale una volta sola, poi
    # la spezza per batch. Questo garantisce la distribuzione
    # target rispettata sull'intera sessione, non solo per batch.
    all_target_feelings = _pick_feelings_for_batch(args.n, used_feelings=[])
    batch_target_feelings: list[list[str]] = []
    pos = 0
    for size in batch_sizes:
        batch_target_feelings.append(all_target_feelings[pos:pos + size])
        pos += size

    # ── Stato condiviso per evitare duplicati cross-batch ───
    all_results: list[tuple[MemoryRecord, str | None]] = []
    used_concepts: list[str] = []
    used_feelings: list[str] = []
    used_contents: list[str] = []

    start = time.perf_counter()

    if args.sequential or n_batches == 1:
        # ── Modalità sequenziale ─────────────────────────────
        for i, (size, tgt_feelings) in enumerate(zip(batch_sizes, batch_target_feelings), 1):
            print(f"\n  {_c(DIM, f'Batch {i}/{n_batches} ({size} ricordi · {tgt_feelings})')}")
            batch_res = _generate_batch(
                llm, api, size, i,
                list(used_concepts), list(used_feelings), list(used_contents),
                tgt_feelings,
                args.dry_run, args.verbose,
            )
            for rec, mid in batch_res:
                used_concepts.append(rec.concept)
                used_feelings.append(rec.feeling)
                used_contents.append(rec.content)
            all_results.extend(batch_res)
    else:
        # ── Modalità parallela ───────────────────────────────
        snapshot_concepts = list(used_concepts)
        snapshot_contents = list(used_contents)

        with ThreadPoolExecutor(max_workers=min(args.workers, n_batches)) as pool:
            futures = {
                pool.submit(
                    _generate_batch,
                    llm, api, size, i,
                    snapshot_concepts + [r.concept for r, _ in all_results],
                    [],   # feeling già gestiti dai target pre-assegnati
                    snapshot_contents + [r.content for r, _ in all_results],
                    tgt_feelings,
                    args.dry_run, args.verbose,
                ): i
                for i, (size, tgt_feelings) in enumerate(
                    zip(batch_sizes, batch_target_feelings), 1
                )
            }
            for future in as_completed(futures):
                batch_id = futures[future]
                try:
                    batch_res = future.result()
                    all_results.extend(batch_res)
                    print(f"  {_c(DIM, f'Batch {batch_id} completato: {len(batch_res)} ricordi')}")
                except Exception as e:
                    print(f"  {_c(RED,'✗')} batch {batch_id} eccezione: {e}")

    elapsed = time.perf_counter() - start

    # ── Riepilogo finale ─────────────────────────────────────
    ok      = sum(1 for _, mid in all_results if mid or args.dry_run)
    failed  = len(all_results) - ok
    skipped = args.n - len(all_results)

    print(f"\n{'─'*55}")
    print(f"  {_c(BOLD,'Completato')} in {elapsed:.1f}s")
    print(f"  {_c(GRN, str(ok))} postati  ·  "
          f"{_c(RED, str(failed))} falliti  ·  "
          f"{_c(YLW, str(skipped))} saltati")

    if all_results:
        concepts_used = sorted({r.concept for r, _ in all_results})
        feelings_dist: dict[str, int] = {}
        for r, _ in all_results:
            feelings_dist[r.feeling] = feelings_dist.get(r.feeling, 0) + 1

        print(f"\n  {_c(DIM,'Concetti generati:')} {', '.join(concepts_used)}")
        print(f"  {_c(DIM,'Distribuzione emotiva:')}")
        for feeling, count in sorted(feelings_dist.items(), key=lambda x: -x[1]):
            bar = "█" * count
            print(f"    {feeling:<20} {_c(CYN, bar)} {count}")

    print()


if __name__ == "__main__":
    main()
