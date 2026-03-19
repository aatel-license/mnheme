"""
mnheme/index.py
==============
Indici in memoria costruiti scansionando il log al boot.

Struttura degli indici
----------------------

  concept_index   : { "Debito":    [offset1, offset2, ...] }
  feeling_index   : { "ansia":     [offset1, offset3, ...] }
  tag_index       : { "casa":      [offset1, ...] }
  cf_index        : { ("Debito","ansia"): [offset1, ...] }   ← concept+feeling
  timestamp_index : [ (timestamp_str, offset), ... ]          ← ordinato per tempo

Gli offset puntano direttamente alle posizioni fisiche nel file .mnheme,
permettendo accesso O(1) ai record tramite StorageEngine.read_at().

Gli indici vengono ricostruiti in RAM ogni volta che il processo parte.
La ricostruzione è veloce: solo una scansione sequenziale del file.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterator


class IndexEngine:
    """
    Gestisce tutti gli indici in memoria.

    Non persiste su disco: viene ricostruito dal log a ogni avvio.
    """

    def __init__(self) -> None:
        self._concept   : dict[str, list[int]]            = defaultdict(list)
        self._feeling   : dict[str, list[int]]            = defaultdict(list)
        self._tag       : dict[str, list[int]]            = defaultdict(list)
        self._cf        : dict[tuple[str,str], list[int]] = defaultdict(list)
        self._timeline  : list[tuple[str, int]]           = []  # (timestamp, offset)
        self._all       : list[int]                       = []  # tutti gli offset in ordine

    # ── BUILD ────────────────────────────────────

    def index_record(self, offset: int, record: dict) -> None:
        """
        Indicizza un singolo record dato il suo offset nel file.
        Chiamato durante la scansione iniziale o dopo ogni append.
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

        count = 0
        for offset, record in scan_iter:
            self.index_record(offset, record)
            count += 1

        # Ordina timeline per timestamp (ISO 8601 → ordinamento lessicografico)
        self._timeline.sort(key=lambda x: x[0])

        return count

    # ── QUERY ────────────────────────────────────

    def offsets_by_concept(
        self,
        concept      : str,
        *,
        feeling      : str | None = None,
        oldest_first : bool = False,
    ) -> list[int]:
        """Offset dei record per un dato concetto."""
        if feeling:
            offsets = list(self._cf.get((concept, feeling), []))
        else:
            offsets = list(self._concept.get(concept, []))

        if oldest_first:
            return offsets
        return list(reversed(offsets))

    def offsets_by_feeling(
        self,
        feeling      : str,
        *,
        oldest_first : bool = False,
    ) -> list[int]:
        """Offset dei record per un dato sentimento."""
        offsets = list(self._feeling.get(feeling, []))
        if oldest_first:
            return offsets
        return list(reversed(offsets))

    def offsets_by_tag(self, tag: str) -> list[int]:
        """Offset dei record che contengono un tag."""
        return list(reversed(self._tag.get(tag, [])))

    def all_offsets(self, *, oldest_first: bool = False) -> list[int]:
        """Tutti gli offset in ordine cronologico."""
        if oldest_first:
            return list(self._all)
        return list(reversed(self._all))

    def timeline_offsets(self, concept: str) -> list[int]:
        """
        Offset del concetto ordinati per timestamp (oldest first).
        Usato per la timeline emotiva di un concetto.
        """
        concept_set = set(self._concept.get(concept, []))
        return [off for (_, off) in self._timeline if off in concept_set]

    # ── STATS ────────────────────────────────────

    def all_concepts(self) -> list[str]:
        return sorted(self._concept.keys())

    def all_feelings(self) -> list[str]:
        return sorted(self._feeling.keys())

    def all_tags(self) -> list[str]:
        return sorted(self._tag.keys())

    def count(
        self,
        *,
        concept : str | None = None,
        feeling : str | None = None,
    ) -> int:
        if concept and feeling:
            return len(self._cf.get((concept, feeling), []))
        if concept:
            return len(self._concept.get(concept, []))
        if feeling:
            return len(self._feeling.get(feeling, []))
        return len(self._all)

    def concept_feeling_matrix(self) -> dict[str, dict[str, int]]:
        """
        Matrice concetto → { sentimento → count }.
        Utile per statistiche aggregate.
        """
        matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for (concept, feeling), offsets in self._cf.items():
            matrix[concept][feeling] = len(offsets)
        return {c: dict(feelings) for c, feelings in matrix.items()}

    def feeling_distribution(self) -> dict[str, int]:
        """sentimento → count totale."""
        return {f: len(offs) for f, offs in self._feeling.items()}
