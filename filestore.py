"""
mnheme/filestore.py
==================
FileStore che usa FsProbe per scegliere automaticamente
la strategia di storage ottimale per il filesystem corrente.

Strategia scelta automaticamente
---------------------------------
  REFLINK     → btrfs, xfs+reflink, APFS  — CoW, zero byte
  HARDLINK    → ext4, NTFS, 9p, NFS, ZFS  — hard link, stesso inode
  SYMLINK     → quando no hardlink, non remoto
  COPY_ATOMIC → FAT32, exFAT, HDFS, remoti — copia + rename atomico

Struttura su disco
------------------
  <base_dir>/
  ├── pool/                        ← un file per ogni contenuto unico (by sha256)
  │   ├── ab/                      ← prime 2 cifre dell'hash (sharding)
  │   │   └── ab3f9bc1_foto.jpg
  │   └── e4/
  │       └── e47d2a03_video.mp4
  ├── memories/                    ← un entry per memory_id
  │   └── <memory_id[:8]>/
  │       └── <memory_id>/
  │           └── foto.jpg         ← hard link / reflink / symlink / copia
  └── _index.json                  ← sha256 → pool_path, memory_id → [entries]
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fsprobe import FsProbe, FsCapabilities, LinkStrategy


# ─────────────────────────────────────────────
# MEDIA TYPES
# ─────────────────────────────────────────────

SUPPORTED_MEDIA: dict[str, str] = {
    ".jpg": "images",  ".jpeg": "images", ".png": "images",
    ".gif": "images",  ".webp": "images", ".bmp": "images",
    ".tiff": "images", ".heic": "images", ".svg": "images",
    ".mp4": "videos",  ".mov": "videos",  ".avi": "videos",
    ".mkv": "videos",  ".webm": "videos", ".m4v": "videos",
    ".mp3": "audio",   ".wav": "audio",   ".aac": "audio",
    ".ogg": "audio",   ".flac": "audio",  ".m4a": "audio",
    ".pdf": "docs",    ".txt": "docs",    ".md": "docs",
}


class UnsupportedMediaError(Exception):
    pass

class FileNotFoundInStoreError(Exception):
    pass


# ─────────────────────────────────────────────
# FILE ENTRY
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class FileEntry:
    memory_id     : str
    original_name : str
    pool_path     : str    # path relativo nella pool (by sha256)
    link_path     : str    # path relativo nella cartella memories/
    media_type    : str
    size_bytes    : int
    checksum      : str    # SHA-256
    inode         : int    # inode number al momento del salvataggio
    strategy_used : str    # quale strategia ha usato FileStore
    stored_at     : str

    def to_dict(self) -> dict:
        return {f: getattr(self, f) for f in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, d: dict) -> "FileEntry":
        return cls(**d)

    def __repr__(self) -> str:
        return (
            f"FileEntry({self.original_name!r}  "
            f"type={self.media_type}  "
            f"size={self.size_bytes/1024:.1f}KB  "
            f"strategy={self.strategy_used}  "
            f"inode={self.inode})"
        )


# ─────────────────────────────────────────────
# FILE STORE
# ─────────────────────────────────────────────

class FileStore:
    """
    Gestisce i file fisici allegati ai ricordi, adattandosi
    automaticamente al filesystem sottostante.

    Utilizzo
    --------
    >>> fs = FileStore("mnheme_files/")
    >>> print(fs.caps)                       # vedi filesystem e strategia
    >>> entry = fs.store(memory_id, "/foto/natale.jpg")
    >>> path  = fs.get_path(memory_id)
    >>> data  = fs.get_bytes(memory_id)

    Parametri
    ---------
    base_dir  : directory radice
    probe_dir : directory su cui eseguire il probe (default: base_dir)
                Utile se base_dir non esiste ancora e vuoi fare probe su /tmp
    """

    INDEX_FILE = "_index.json"

    def __init__(
        self,
        base_dir  : str | Path,
        *,
        probe_dir : Optional[str | Path] = None,
    ) -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

        # Cartelle strutturali
        (self._base / "pool").mkdir(exist_ok=True)
        (self._base / "memories").mkdir(exist_ok=True)

        # Probe del filesystem
        probe_target = Path(probe_dir) if probe_dir else self._base
        self._probe  = FsProbe(probe_target)
        self._caps   = self._probe.detect()

        # Indice in RAM
        self._index_path = self._base / self.INDEX_FILE
        self._idx_pool : dict[str, str]        = {}   # sha256 → pool_rel_path
        self._idx_mem  : dict[str, list[dict]] = {}   # memory_id → [FileEntry.to_dict()]
        self._load_index()

    @property
    def caps(self) -> FsCapabilities:
        """Capabilities del filesystem rilevate al boot."""
        return self._caps

    # ── SCRITTURA ────────────────────────────

    def store(
        self,
        memory_id   : str,
        source_path : str | Path,
        *,
        move        : bool = False,
    ) -> FileEntry:
        """
        Salva un file nel FileStore.

        Comportamento per strategia
        ---------------------------
        REFLINK     : reflink nella pool, poi reflink per il link del ricordo
        HARDLINK    : copia nella pool, hard link per il link del ricordo
                      (se il sorgente è sullo stesso device: hard link diretto)
        SYMLINK     : copia nella pool, symlink per il link del ricordo
        COPY_ATOMIC : copia atomica (tmp+rename) ovunque

        Deduplicazione
        --------------
        Se un file con lo stesso SHA-256 è già nella pool,
        non viene mai riscritto — viene solo creato un nuovo link.

        Parametri
        ---------
        memory_id   : ID del ricordo associato
        source_path : file da allegare
        move        : se True, rimuove il sorgente dopo il salvataggio
        """
        src  = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"File non trovato: {source_path}")

        ext = src.suffix.lower()
        if ext not in SUPPORTED_MEDIA:
            raise UnsupportedMediaError(
                f"Estensione '{ext}' non supportata. "
                f"Ammesse: {sorted(SUPPORTED_MEDIA.keys())}"
            )

        media_type = SUPPORTED_MEDIA[ext]
        checksum   = _sha256(src)
        safe_name  = _safe_name(src.name)

        # ── 1. Pool: un file per contenuto unico ──
        pool_path = self._ensure_in_pool(src, checksum, safe_name, ext)

        # ── 2. Link nella cartella del ricordo ────
        link_path = self._link_for_memory(memory_id, pool_path, safe_name)

        # ── 3. Inode del file nella pool ──────────
        inode = os.stat(pool_path).st_ino

        # ── 4. Rimuovi sorgente se move=True ──────
        if move and src.exists():
            try:
                src.unlink()
            except OSError:
                pass

        entry = FileEntry(
            memory_id     = memory_id,
            original_name = src.name,
            pool_path     = str(pool_path.relative_to(self._base)),
            link_path     = str(link_path.relative_to(self._base)),
            media_type    = media_type,
            size_bytes    = pool_path.stat().st_size,
            checksum      = checksum,
            inode         = inode,
            strategy_used = self._caps.strategy.value,
            stored_at     = datetime.now(timezone.utc).isoformat(),
        )

        self._idx_pool.setdefault(checksum, str(pool_path.relative_to(self._base)))
        self._idx_mem.setdefault(memory_id, []).append(entry.to_dict())
        self._save_index()

        return entry

    def store_bytes(
        self,
        memory_id : str,
        data      : bytes,
        filename  : str,
    ) -> FileEntry:
        """
        Salva dati binari direttamente in memoria.
        Utile per upload da API, web form, o stream.
        """
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_MEDIA:
            raise UnsupportedMediaError(f"Estensione '{ext}' non supportata.")

        # Scrivi in un file temporaneo, poi usa store()
        fd, tmp = tempfile.mkstemp(
            suffix=ext,
            dir=self._base / "pool",
            prefix=".tmp_upload_"
        )
        try:
            os.write(fd, data)
            os.close(fd)
            entry = self.store(memory_id, tmp, move=True)
            # Aggiusta il nome originale (store() usa il nome del tmp)
            entry = FileEntry(
                **{**entry.to_dict(), "original_name": filename}
            )
            # Aggiorna indice con il nome corretto
            if memory_id in self._idx_mem:
                self._idx_mem[memory_id][-1]["original_name"] = filename
                self._save_index()
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

        return entry

    # ── LETTURA ──────────────────────────────

    def get_path(self, memory_id: str) -> Path:
        """
        Ritorna il path assoluto del file principale di un ricordo.
        Il path punta al link (hard/sym) nella cartella memories/,
        non al file nella pool.
        """
        entries = self._idx_mem.get(memory_id, [])
        if not entries:
            raise FileNotFoundInStoreError(
                f"Nessun file per memory_id='{memory_id}'"
            )
        return self._base / entries[0]["link_path"]

    def get_pool_path(self, memory_id: str) -> Path:
        """
        Ritorna il path nella pool (il file fisico originale).
        Utile per verificare deduplicazione.
        """
        entries = self._idx_mem.get(memory_id, [])
        if not entries:
            raise FileNotFoundInStoreError(
                f"Nessun file per memory_id='{memory_id}'"
            )
        return self._base / entries[0]["pool_path"]

    def get_bytes(self, memory_id: str) -> bytes:
        """Legge il contenuto binario del file."""
        return self.get_path(memory_id).read_bytes()

    def list_by_memory(self, memory_id: str) -> list[FileEntry]:
        return [FileEntry.from_dict(d) for d in self._idx_mem.get(memory_id, [])]

    def list_by_type(self, media_type: str) -> list[FileEntry]:
        result = []
        for entries in self._idx_mem.values():
            for e in entries:
                if e.get("media_type") == media_type:
                    result.append(FileEntry.from_dict(e))
        return result

    def exists(self, memory_id: str) -> bool:
        return bool(self._idx_mem.get(memory_id))

    # ── STATS ────────────────────────────────

    def info(self) -> dict:
        """Statistiche complete: filesystem, files, dimensioni."""
        total_files = sum(len(v) for v in self._idx_mem.values())
        total_bytes = sum(
            e.get("size_bytes", 0)
            for entries in self._idx_mem.values()
            for e in entries
        )
        pool_count  = sum(1 for _ in (self._base / "pool").rglob("*") if _.is_file())
        pool_bytes  = _dir_size(self._base / "pool")

        by_type: dict[str, int] = {}
        for entries in self._idx_mem.values():
            for e in entries:
                mt = e.get("media_type", "unknown")
                by_type[mt] = by_type.get(mt, 0) + 1

        return {
            "base_dir":          str(self._base.resolve()),
            "filesystem":        self._caps.fs_type.value,
            "strategy":          self._caps.strategy.value,
            "strategy_note":     self._caps.strategy_note,
            "total_entries":     total_files,
            "total_logical_mb":  round(total_bytes / 1024 / 1024, 3),
            "pool_unique_files": pool_count,
            "pool_physical_mb":  round(pool_bytes / 1024 / 1024, 3),
            "dedup_ratio":       round(total_files / pool_count, 2) if pool_count else 1.0,
            "by_type":           by_type,
        }

    def tree(self) -> str:
        """Stampa la struttura ad albero del FileStore."""
        lines = [f"{self._base.name}/  [{self._caps.fs_type.value} / {self._caps.strategy.value}]"]
        pool_n = sum(1 for _ in (self._base / "pool").rglob("*") if _.is_file())
        mem_n  = sum(1 for _ in (self._base / "memories").rglob("*") if _.is_file())
        lines.append(f"  pool/       ({pool_n} file fisici unici)")
        lines.append(f"  memories/   ({mem_n} link)")
        lines.append(f"  {self.INDEX_FILE}")
        return "\n".join(lines)

    # ── ESTRATEGIA ───────────────────────────

    def _ensure_in_pool(
        self, src: Path, checksum: str, safe_name: str, ext: str
    ) -> Path:
        """
        Assicura che il file sia nella pool.
        Se già presente (stesso SHA-256), non riscrive niente.
        Ritorna il path assoluto nella pool.
        """
        if checksum in self._idx_pool:
            pool_rel = self._idx_pool[checksum]
            pool_abs = self._base / pool_rel
            if pool_abs.exists():
                return pool_abs

        # Shard per prime 2 cifre dell'hash (evita cartelle con migliaia di file)
        shard = checksum[:2]
        shard_dir = self._base / "pool" / shard
        shard_dir.mkdir(parents=True, exist_ok=True)
        dest = shard_dir / f"{checksum[:16]}_{safe_name}"

        strategy = self._caps.strategy
        src_dev  = os.stat(src).st_dev
        pool_dev = os.stat(shard_dir).st_dev

        if dest.exists():
            return dest

        if strategy == LinkStrategy.REFLINK:
            _do_reflink(src, dest)

        elif strategy == LinkStrategy.HARDLINK and src_dev == pool_dev:
            # Hard link solo se stesso device
            try:
                os.link(src, dest)
            except OSError:
                _do_copy_atomic(src, dest)

        else:
            # COPY_ATOMIC (o SYMLINK: in pool teniamo sempre una copia fisica)
            _do_copy_atomic(src, dest)

        return dest

    def _link_for_memory(
        self, memory_id: str, pool_path: Path, safe_name: str
    ) -> Path:
        """
        Crea il link (hard/sym/copy) nella cartella memories/<memory_id>/.
        Ritorna il path assoluto del link.
        """
        mem_dir = self._base / "memories" / memory_id[:8] / memory_id
        mem_dir.mkdir(parents=True, exist_ok=True)
        link_dest = mem_dir / safe_name

        if link_dest.exists() or link_dest.is_symlink():
            return link_dest

        strategy = self._caps.strategy
        pool_dev = os.stat(pool_path).st_dev
        mem_dev  = os.stat(mem_dir).st_dev

        if strategy == LinkStrategy.REFLINK:
            _do_reflink(pool_path, link_dest)

        elif strategy == LinkStrategy.HARDLINK and pool_dev == mem_dev:
            try:
                os.link(pool_path, link_dest)
            except OSError:
                _do_copy_atomic(pool_path, link_dest)

        elif strategy == LinkStrategy.SYMLINK:
            try:
                os.symlink(pool_path.resolve(), link_dest)
            except OSError:
                _do_copy_atomic(pool_path, link_dest)

        else:
            _do_copy_atomic(pool_path, link_dest)

        return link_dest

    # ── INDICE ───────────────────────────────

    def _load_index(self) -> None:
        if not self._index_path.exists():
            return
        try:
            data = json.loads(self._index_path.read_text("utf-8"))
            self._idx_pool = data.get("pool", {})
            self._idx_mem  = data.get("memories", {})
        except (json.JSONDecodeError, OSError):
            pass

    def _save_index(self) -> None:
        payload = json.dumps(
            {"pool": self._idx_pool, "memories": self._idx_mem},
            ensure_ascii=False, indent=2,
        )
        tmp = self._index_path.with_suffix(".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(self._index_path)

    def __repr__(self) -> str:
        i = self.info()
        return (
            f"FileStore(base='{self._base.name}'  "
            f"fs={i['filesystem']}  "
            f"strategy={i['strategy']}  "
            f"entries={i['total_entries']}  "
            f"pool={i['pool_unique_files']})"
        )


# ─────────────────────────────────────────────
# OPERAZIONI BASSO LIVELLO
# ─────────────────────────────────────────────

def _do_reflink(src: Path, dst: Path) -> None:
    """ioctl FICLONE (Linux) o clonefile (macOS)."""
    import platform, ctypes
    os_name = platform.system()
    try:
        if os_name == "Linux":
            import fcntl
            with open(src, "rb") as s, open(dst, "w+b") as d:
                fcntl.ioctl(d.fileno(), 0x40049409, s.fileno())
        elif os_name == "Darwin":
            libc = ctypes.CDLL(ctypes.util.find_library("c"))
            libc.clonefile(str(src).encode(), str(dst).encode(), 0)
        else:
            raise OSError("reflink non supportato su questo OS")
    except OSError:
        _do_copy_atomic(src, dst)


def _do_copy_atomic(src: Path, dst: Path) -> None:
    """Copia in un file tmp nella stessa dir, poi rename atomico."""
    parent = dst.parent
    fd, tmp = tempfile.mkstemp(dir=parent, prefix=".tmp_copy_")
    try:
        os.close(fd)
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)  # atomico su POSIX e Windows NT
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_name(name: str) -> str:
    import re
    name = Path(name).name
    name = re.sub(r"[^\w\-.]", "_", name)
    return name[:80]


def _dir_size(path: Path) -> int:
    total = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    total += p.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total
