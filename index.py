"""
mnheme/index.py
==============
Indici in memoria con persistenza su disco e indice invertito full-text.

Struttura degli indici in RAM
------------------------------
  concept_index   : { "Debito":            [offset1, offset2, ...] }
  feeling_index   : { "ansia":             [offset1, offset3, ...] }
  tag_index       : { "casa":              [offset1, ...] }
  cf_index        : { ("Debito","ansia"):  [offset1, ...] }
  timestamp_index : [ (timestamp_str, offset), ... ]  ← ordinato per tempo
  word_index      : { "mutuo":             [offset1, ...] }  ← full-text invertito

Persistenza su disco — punto 1
-------------------------------
Al boot, se esiste un file <db>.index.json e il .mnheme non è cresciuto
dall'ultimo salvataggio, l'indice viene caricato direttamente senza
riscansionare il log. Cold start: da O(n) a O(1).

Il file indice viene aggiornato:
  - Dopo ogni append singolo (index_record)
  - Dopo ogni append_batch (rebuild parziale degli ultimi N)
  - Alla chiusura del DB (flush finale)

Il formato su disco è compatto: gli offset sono liste di interi,
serializzati come JSON. Per 20k record l'indice pesa ~2-4 MB.

Indice invertito full-text — punto 5
--------------------------------------
Durante index_record() le parole di content, concept e note vengono
tokenizzate (split + lowercase + filtro <3 chars) e inserite in
word_index. Questo rende search() O(k) dove k = occorrenze della parola,
invece di O(n) su tutto il file.
"""

from __future__ import annotations

import json
import re
import threading
from collections import defaultdict
from pathlib import Path
from typing import Iterator, Optional


# Minima lunghezza token per l'indice invertito
_MIN_TOKEN_LEN = 3
# Pattern per tokenizzare — solo caratteri alfanumerici e accenti comuni
_TOKEN_RE = re.compile(r"[a-zA-ZàáâäãåæçèéêëìíîïòóôöõùúûüýÿñÀÁÂÄÃÅÆÇÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝÑ]{3,}", re.UNICODE)


def _tokenize(text: str) -> set[str]:
    """Estrae token univoci dal testo per l'indice invertito."""
    return {m.lower() for m in _TOKEN_RE.findall(text)}


class IndexEngine:
    """
    Gestisce tutti gli indici in memoria con persistenza su disco.

    Parametri
    ---------
    index_path : path del file indice su disco (es. "mente.mnheme.index.json")
                 Se None, la persistenza è disabilitata.
    """

    def __init__(self, index_path: Optional[str | Path] = None) -> None:
        self._concept  : dict[str, list[int]]           = defaultdict(list)
        self._feeling  : dict[str, list[int]]           = defaultdict(list)
        self._tag      : dict[str, list[int]]           = defaultdict(list)
        self._cf       : dict[tuple[str,str], list[int]]= defaultdict(list)
        self._timeline : list[tuple[str, int]]          = []
        self._all      : list[int]                      = []
        self._word     : dict[str, list[int]]           = defaultdict(list)  # indice invertito

        self._index_path : Optional[Path] = Path(index_path) if index_path else None
        self._dirty      : bool           = False   # segnala modifiche non ancora flush
        self._lock       : threading.Lock = threading.Lock()

    # ── BUILD ─────────────────────────────────────────────────

    def index_record(self, offset: int, record: dict) -> None:
        """
        Indicizza un singolo record.
        Chiamato dopo ogni append — aggiorna anche l'indice invertito.
        """
        concept   = record.get("concept", "")
        feeling   = record.get("feeling", "")
        tags      = record.get("tags", [])
        timestamp = record.get("timestamp", "")

        self._concept[concept].append(offset)
        self._feeling[feeling].append(offset)
        self._cf[(concept, feeling)].append(offset)
        self._timeline.append((timestamp, offset))
        self._all.append(offset)

        for tag in tags:
            if tag:
                self._tag[tag].append(offset)

        # Indice invertito: tokenizza content + concept + note
        tokens = (
            _tokenize(record.get("content", ""))
            | _tokenize(record.get("concept", ""))
            | _tokenize(record.get("note", ""))
        )
        for token in tokens:
            self._word[token].append(offset)

        self._dirty = True

    def rebuild(self, scan_iter: Iterator[tuple[int, dict]]) -> int:
        """
        Ricostruisce tutti gli indici da zero scansionando il log.
        Ritorna il numero di record indicizzati.
        """
        self._concept.clear()
        self._feeling.clear()
        self._tag.clear()
        self._cf.clear()
        self._timeline.clear()
        self._all.clear()
        self._word.clear()

        count = 0
        for offset, record in scan_iter:
            self.index_record(offset, record)
            count += 1

        self._timeline.sort(key=lambda x: x[0])
        self._dirty = True
        return count

    # ── QUERY ──────────────────────────────────────────────────

    def offsets_by_concept(
        self,
        concept      : str,
        *,
        feeling      : str | None = None,
        oldest_first : bool = False,
    ) -> list[int]:
        if feeling:
            offsets = list(self._cf.get((concept, feeling), []))
        else:
            offsets = list(self._concept.get(concept, []))
        return offsets if oldest_first else list(reversed(offsets))

    def offsets_by_feeling(
        self,
        feeling      : str,
        *,
        oldest_first : bool = False,
    ) -> list[int]:
        offsets = list(self._feeling.get(feeling, []))
        return offsets if oldest_first else list(reversed(offsets))

    def offsets_by_tag(self, tag: str, limit: Optional[int] = None) -> list[int]:
        """Offset dei record che contengono un tag, più recenti prima."""
        offsets = list(reversed(self._tag.get(tag, [])))
        return offsets[:limit] if limit else offsets

    def offsets_by_word(self, word: str, limit: Optional[int] = None) -> list[int]:
        """
        Offset dei record che contengono il token (indice invertito).
        Ritorna i più recenti prima.
        Usato da search() per evitare la scansione lineare.
        """
        offsets = list(reversed(self._word.get(word.lower(), [])))
        return offsets[:limit] if limit else offsets

    def has_word(self, word: str) -> bool:
        """True se il token esiste nell'indice invertito."""
        return word.lower() in self._word

    def all_offsets(self, *, oldest_first: bool = False) -> list[int]:
        if oldest_first:
            return list(self._all)
        return list(reversed(self._all))

    def timeline_offsets(self, concept: str) -> list[int]:
        """Offset del concetto ordinati per timestamp (oldest first)."""
        concept_set = set(self._concept.get(concept, []))
        return [off for (_, off) in self._timeline if off in concept_set]

    # ── STATS ──────────────────────────────────────────────────

    def all_concepts(self) -> list[str]:
        return sorted(self._concept.keys())

    def all_feelings(self) -> list[str]:
        return sorted(self._feeling.keys())

    def all_tags(self) -> list[str]:
        return sorted(self._tag.keys())

    def count(self, *, concept: str | None = None, feeling: str | None = None) -> int:
        if concept and feeling:
            return len(self._cf.get((concept, feeling), []))
        if concept:
            return len(self._concept.get(concept, []))
        if feeling:
            return len(self._feeling.get(feeling, []))
        return len(self._all)

    def concept_feeling_matrix(self) -> dict[str, dict[str, int]]:
        matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for (concept, feeling), offsets in self._cf.items():
            matrix[concept][feeling] = len(offsets)
        return {c: dict(f) for c, f in matrix.items()}

    def feeling_distribution(self) -> dict[str, int]:
        return {f: len(offs) for f, offs in self._feeling.items()}

    # ── PERSISTENZA SU DISCO ──────────────────────────────────

    def try_load(self, log_size: int) -> bool:
        """
        Tenta di caricare l'indice dal file su disco.
        Ritorna True se il caricamento ha avuto successo e l'indice è valido.

        Valido significa: il file indice esiste, non è corrotto,
        e il log_size salvato corrisponde a quello attuale del file .mnheme.
        Se il log è cresciuto dall'ultimo salvataggio (es. riavvio dopo crash
        o append da un altro processo), ritorna False e si fa rebuild normale.
        """
        if not self._index_path or not self._index_path.exists():
            return False

        try:
            raw  = self._index_path.read_text("utf-8")
            data = json.loads(raw)

            # Verifica che il log non sia cresciuto
            if data.get("log_size") != log_size:
                return False

            # Ricostruisce le strutture dati dagli array serializzati
            self._concept  = defaultdict(list, {k: v for k, v in data["concept"].items()})
            self._feeling  = defaultdict(list, {k: v for k, v in data["feeling"].items()})
            self._tag      = defaultdict(list, {k: v for k, v in data["tag"].items()})
            self._word     = defaultdict(list, {k: v for k, v in data.get("word", {}).items()})
            self._all      = data["all"]
            self._timeline = [tuple(x) for x in data["timeline"]]

            # Ricostruisce cf_index (chiave tupla non serializzabile direttamente)
            self._cf = defaultdict(list)
            for k, v in data["cf"].items():
                concept, feeling = k.split("\x00", 1)
                self._cf[(concept, feeling)] = v

            self._dirty = False
            return True

        except (json.JSONDecodeError, KeyError, OSError, ValueError):
            return False

    def flush(self, log_size: int) -> None:
        """
        Salva l'indice su disco con scrittura atomica (tmp + rename).
        log_size: dimensione attuale del file .mnheme, usata per invalidare
        l'indice se il log cresce prima del prossimo caricamento.
        """
        if not self._index_path or not self._dirty:
            return

        # Serializza cf_index con chiave stringa (JSON non supporta tuple)
        cf_serial = {
            f"{concept}\x00{feeling}": offsets
            for (concept, feeling), offsets in self._cf.items()
        }

        payload = json.dumps(
            {
                "log_size": log_size,
                "concept":  dict(self._concept),
                "feeling":  dict(self._feeling),
                "tag":      dict(self._tag),
                "word":     dict(self._word),
                "cf":       cf_serial,
                "all":      self._all,
                "timeline": [[ts, off] for ts, off in self._timeline],
            },
            ensure_ascii=False,
            separators=(",", ":"),   # compact — non indent per risparmiare spazio
        )

        tmp = self._index_path.with_suffix(".tmp")
        try:
            tmp.write_text(payload, encoding="utf-8")
            tmp.replace(self._index_path)
            self._dirty = False
        except OSError:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
