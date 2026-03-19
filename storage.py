"""
mnheme/storage.py
================
Storage engine append-only scritto da zero.

Formato fisico del file .mnheme
------------------------------
Il file è una sequenza continua di record binari.
Ogni record ha questo layout:

  ┌──────────────┬──────────┬───────────────────┐
  │  MAGIC (4B)  │ SIZE (4B)│  PAYLOAD (SIZE B) │
  └──────────────┴──────────┴───────────────────┘

  MAGIC   : [0x4D, 0x4E, 0x45, 0xE0]  — firma record (4 byte fissi)
  SIZE    : uint32 big-endian — lunghezza del payload in byte
  PAYLOAD : JSON UTF-8        — dati del ricordo

Nessun record viene mai modificato o cancellato.
Ogni append è atomica: scriviamo tutto in una sola chiamata a write().
"""

from __future__ import annotations

import json
import os
import struct
import threading
from pathlib import Path
from typing import Iterator

# Firma univoca di ogni record — evita letture corrotte
MAGIC = bytes([0x4D, 0x4E, 0x45, 0xE0])  # M N E — firma record


class CorruptedRecordError(Exception):
    """Sollevata quando un record non supera la validazione."""


class StorageEngine:
    """
    Motore di storage append-only.

    - Ogni scrittura aggiunge un record in coda al file.
    - La lettura scansiona sequenzialmente il file dal byte 0.
    - Thread-safe tramite lock in scrittura.
    - Resistente a crash: i record troncati vengono saltati.

    Parametri
    ---------
    path : percorso del file fisico (es. "mente.mnheme")
    """

    HEADER_SIZE = 8  # 4 byte MAGIC + 4 byte SIZE

    def __init__(self, path: str | Path) -> None:
        self._path   = Path(path)
        self._lock   = threading.Lock()
        # Crea il file se non esiste
        self._path.touch(exist_ok=True)

    # ── WRITE ────────────────────────────────────

    def append(self, record: dict) -> int:
        """
        Serializza e scrive un record in fondo al file.

        Ritorna l'offset (in byte) dove il record è stato scritto.
        Utile per costruire indici in memoria.
        """
        payload = json.dumps(record, ensure_ascii=False).encode("utf-8")
        size    = len(payload)
        header  = MAGIC + struct.pack(">I", size)  # big-endian uint32
        frame   = header + payload

        with self._lock:
            with open(self._path, "ab") as f:
                offset = f.tell()
                f.write(frame)
                f.flush()
                os.fsync(f.fileno())   # garantisce flush su disco
            return offset

    # ── READ ─────────────────────────────────────

    def scan(self) -> Iterator[tuple[int, dict]]:
        """
        Generatore che scansiona il file dall'inizio alla fine.
        Yield: (offset, record_dict)

        Salta silenziosamente i record troncati o corrotti.
        """
        with open(self._path, "rb") as f:
            while True:
                offset = f.tell()
                header = f.read(self.HEADER_SIZE)

                if len(header) == 0:
                    break  # fine file

                if len(header) < self.HEADER_SIZE:
                    break  # record troncato — file corrotto parzialmente

                magic = header[:4]
                if magic != MAGIC:
                    # Salta byte e cerca il prossimo magic
                    f.seek(offset + 1)
                    continue

                size = struct.unpack(">I", header[4:])[0]
                payload_bytes = f.read(size)

                if len(payload_bytes) < size:
                    break  # payload troncato

                try:
                    record = json.loads(payload_bytes.decode("utf-8"))
                    yield offset, record
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue  # record corrotto, ignorato

    def read_at(self, offset: int) -> dict | None:
        """
        Legge un singolo record a partire dall'offset indicato.
        Usato dagli indici per accesso diretto O(1).
        """
        try:
            with open(self._path, "rb") as f:
                f.seek(offset)
                header = f.read(self.HEADER_SIZE)

                if len(header) < self.HEADER_SIZE:
                    return None
                if header[:4] != MAGIC:
                    return None

                size    = struct.unpack(">I", header[4:])[0]
                payload = f.read(size)

                if len(payload) < size:
                    return None

                return json.loads(payload.decode("utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    # ── INFO ─────────────────────────────────────

    def file_size(self) -> int:
        """Dimensione del file in byte."""
        return self._path.stat().st_size

    def record_count(self) -> int:
        """Conta i record scansionando il file (operazione lenta)."""
        return sum(1 for _ in self.scan())

    def __repr__(self) -> str:
        size_kb = self.file_size() / 1024
        return f"StorageEngine(path='{self._path}', size={size_kb:.1f}KB)"
