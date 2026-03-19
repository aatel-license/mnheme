"""
mnheme/mnheme.py
==============
MNHEME — Database dei Ricordi Umani
====================================

Architettura interna
--------------------

  ┌──────────────────────────────────────────────────┐
  │                   MemoryDB                        │
  │  (API pubblica: remember / recall / search ...)   │
  └──────────┬────────────────────────────────────────┘
             │
    ┌────────┴──────────────────────┐
    │                               │
  ┌─▼────────────┐      ┌──────────▼──────┐      ┌────────────────┐
  │ StorageEngine│      │  IndexEngine    │      │  FileStore     │
  │  (.mnheme log │      │  (RAM)          │      │  (file fisici) │
  │  append-only)│      │                 │      │  img/video/... │
  └──────────────┘      └─────────────────┘      └────────────────┘

- StorageEngine  : log binario append-only dei metadati.
- IndexEngine    : indici in RAM per lookup O(1).
- FileStore      : salva i file fisici (immagini, video, audio) su disco.
- MemoryDB       : coordina tutto, unica API pubblica.
- Nessun record/file viene mai modificato o cancellato.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from storage import StorageEngine
from index import IndexEngine
from filestore import FileStore, FileEntry, UnsupportedMediaError


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class Feeling(str, Enum):
    GIOIA       = "gioia"
    TRISTEZZA   = "tristezza"
    RABBIA      = "rabbia"
    PAURA       = "paura"
    NOSTALGIA   = "nostalgia"
    AMORE       = "amore"
    MALINCONIA  = "malinconia"
    SERENITA    = "serenità"
    SORPRESA    = "sorpresa"
    ANSIA       = "ansia"
    GRATITUDINE = "gratitudine"
    VERGOGNA    = "vergogna"
    ORGOGLIO    = "orgoglio"
    NOIA        = "noia"
    CURIOSITA   = "curiosità"


class MediaType(str, Enum):
    TEXT  = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOC   = "doc"


# ─────────────────────────────────────────────
# DATA MODEL
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class Memory:
    """
    Rappresentazione immutabile di un ricordo.
    frozen=True: nessun campo può essere modificato dopo la creazione.
    """
    memory_id  : str
    concept    : str
    feeling    : str
    media_type : str
    content    : str
    note       : str
    tags       : tuple[str, ...]
    timestamp  : str
    checksum   : str

    def to_dict(self) -> dict:
        return {
            "memory_id":  self.memory_id,
            "concept":    self.concept,
            "feeling":    self.feeling,
            "media_type": self.media_type,
            "content":    self.content,
            "note":       self.note,
            "tags":       list(self.tags),
            "timestamp":  self.timestamp,
            "checksum":   self.checksum,
        }

    def __repr__(self) -> str:
        preview = self.content[:45] + "…" if len(self.content) > 45 else self.content
        return (
            f"Memory(id={self.memory_id[:8]}… "
            f"concept='{self.concept}' "
            f"feeling='{self.feeling}' "
            f"content='{preview}')"
        )


# ─────────────────────────────────────────────
# EXCEPTIONS
# ─────────────────────────────────────────────

class MnhemeError(Exception):
    """Errore base."""

class InvalidFeelingError(MnhemeError):
    pass

class InvalidMediaTypeError(MnhemeError):
    pass


# ─────────────────────────────────────────────
# MEMORY DATABASE
# ─────────────────────────────────────────────

class MemoryDB:
    """
    MNHEME — il database dei ricordi.

    Utilizzo
    --------
    >>> db = MemoryDB("mente.mnheme")
    >>> db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo oggi.")
    >>> ricordi = db.recall("Debito")

    Il database è append-only: i ricordi non si sovrascrivono mai.
    Tutto è scritto su file binario personalizzato — zero SQLite, zero dipendenze.

    Parametri
    ---------
    path : path al file di storage (default: "mnheme.mnheme")
    """

    def __init__(
        self,
        path       : Union[str, Path] = "mnheme.mnheme",
        *,
        files_dir  : Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Parametri
        ---------
        path      : path al file di log binario (default: "mnheme.mnheme")
        files_dir : directory dove salvare i file multimediali
                    (default: <stesso nome del log senza estensione>_files/)
                    Es: "mente.mnheme" -> "mente_files/"
        """
        self._storage = StorageEngine(path)
        self._index   = IndexEngine()
        n = self._index.rebuild(self._storage.scan())
        self._path    = str(path)
        self._loaded  = n

        # FileStore: cartella accanto al file .mnheme
        if files_dir is None:
            base     = Path(path)
            files_dir = base.parent / (base.stem + "_files")
        self._files = FileStore(files_dir)

    # ── WRITE ────────────────────────────────

    def remember(
        self,
        concept    : str,
        feeling    : Union[Feeling, str],
        content    : str,
        *,
        media_type : Union[MediaType, str] = MediaType.TEXT,
        note       : str = "",
        tags       : list[str] = None,
    ) -> Memory:
        """
        Registra un nuovo ricordo nel database.
        Operazione append-only: non sovrascrive mai nulla.

        Parametri
        ---------
        concept    : chiave concettuale (es. "Casa", "Amore", "Lavoro")
        feeling    : sentimento nel momento del ricordo
        content    : testo libero / path a file / stringa base64
        media_type : TEXT | IMAGE | VIDEO
        note       : annotazione opzionale
        tags       : etichette aggiuntive per la ricerca

        Ritorna
        -------
        Memory : il ricordo creato, immutabile

        Esempio
        -------
        >>> db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.")
        >>> db.remember("Famiglia", Feeling.AMORE, "/foto/natale.jpg",
        ...             media_type=MediaType.IMAGE, note="Tutti insieme")
        """
        feeling_val    = self._validate_feeling(feeling)
        media_type_val = self._validate_media_type(media_type)
        concept_clean  = concept.strip()
        tags_list      = [t.strip() for t in (tags or []) if t.strip()]

        if not concept_clean:
            raise MnhemeError("Il concetto non può essere vuoto.")
        if not content:
            raise MnhemeError("Il contenuto non può essere vuoto.")

        memory_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        checksum  = hashlib.sha256(content.encode("utf-8")).hexdigest()

        record = {
            "memory_id":  memory_id,
            "concept":    concept_clean,
            "feeling":    feeling_val,
            "media_type": media_type_val,
            "content":    content,
            "note":       note,
            "tags":       tags_list,
            "timestamp":  timestamp,
            "checksum":   checksum,
        }

        # 1. Scrivi sul file (append)
        offset = self._storage.append(record)
        # 2. Aggiorna gli indici in RAM
        self._index.index_record(offset, record)

        return Memory(
            memory_id  = memory_id,
            concept    = concept_clean,
            feeling    = feeling_val,
            media_type = media_type_val,
            content    = content,
            note       = note,
            tags       = tuple(tags_list),
            timestamp  = timestamp,
            checksum   = checksum,
        )

    def remember_file(
        self,
        concept     : str,
        feeling     : Union[Feeling, str],
        source_path : Union[str, Path],
        *,
        note        : str = "",
        tags        : list[str] = None,
        copy        : bool = True,
    ) -> tuple["Memory", "FileEntry"]:
        """
        Registra un ricordo allegando un file fisico (immagine, video, audio, doc).

        Il tipo di media viene rilevato automaticamente dall'estensione.
        Il file viene copiato (o spostato) nella directory gestita dal FileStore.

        Parametri
        ---------
        concept     : chiave concettuale
        feeling     : sentimento associato
        source_path : path al file da allegare
        note        : nota opzionale
        tags        : etichette aggiuntive
        copy        : True → copia il file originale (default)
                      False → sposta il file (distrugge l'originale)

        Ritorna
        -------
        (Memory, FileEntry) — il ricordo e i metadati del file salvato

        Esempio
        -------
        >>> mem, fe = db.remember_file(
        ...     "Famiglia", Feeling.AMORE,
        ...     "/foto/natale2024.jpg",
        ...     note="Tutti insieme al pranzo"
        ... )
        >>> print(fe.stored_path)
        images/2024/03/a3f9bc12_natale2024.jpg
        >>> print(db.files.get_path(mem.memory_id))
        /home/user/mente_files/images/2024/03/a3f9bc12_natale2024.jpg
        """
        src   = Path(source_path)
        # Determina media_type dall'estensione
        from filestore import SUPPORTED_MEDIA
        ext   = src.suffix.lower()
        mtype_str = SUPPORTED_MEDIA.get(ext)
        if mtype_str is None:
            raise UnsupportedMediaError(
                f"Estensione '{ext}' non supportata. "
                f"Supportate: {sorted(SUPPORTED_MEDIA.keys())}"
            )
        media_type_map = {
            "images": MediaType.IMAGE,
            "videos": MediaType.VIDEO,
            "audio":  MediaType.AUDIO,
            "docs":   MediaType.DOC,
        }
        media_type = media_type_map.get(mtype_str, MediaType.TEXT)

        # Registra il ricordo con content = nome originale del file
        memory = self.remember(
            concept    = concept,
            feeling    = feeling,
            content    = src.name,
            media_type = media_type,
            note       = note,
            tags       = tags,
        )

        # Salva il file fisico
        file_entry = self._files.store(memory.memory_id, src, move=not copy)

        return memory, file_entry

    def remember_bytes(
        self,
        concept    : str,
        feeling    : Union[Feeling, str],
        data       : bytes,
        filename   : str,
        *,
        note       : str = "",
        tags       : list[str] = None,
    ) -> tuple["Memory", "FileEntry"]:
        """
        Registra un ricordo allegando dati binari direttamente in memoria.
        Utile per upload da API, web form, o stream.

        Parametri
        ---------
        data     : contenuto binario del file
        filename : nome da dare al file salvato (con estensione)

        Ritorna
        -------
        (Memory, FileEntry)

        Esempio
        -------
        >>> with open("foto.jpg", "rb") as f:
        ...     raw = f.read()
        >>> mem, fe = db.remember_bytes("Viaggio", Feeling.GIOIA, raw, "santorini.jpg")
        """
        from filestore import SUPPORTED_MEDIA
        ext = Path(filename).suffix.lower()
        mtype_str = SUPPORTED_MEDIA.get(ext)
        if mtype_str is None:
            raise UnsupportedMediaError(f"Estensione '{ext}' non supportata.")

        media_type_map = {"images": MediaType.IMAGE, "videos": MediaType.VIDEO,
                          "audio": MediaType.AUDIO, "docs": MediaType.DOC}
        media_type = media_type_map.get(mtype_str, MediaType.TEXT)

        memory = self.remember(
            concept    = concept,
            feeling    = feeling,
            content    = filename,
            media_type = media_type,
            note       = note,
            tags       = tags,
        )
        file_entry = self._files.store_bytes(memory.memory_id, data, filename)
        return memory, file_entry

    # ── FILE ACCESS ──────────────────────────

    @property
    def files(self) -> "FileStore":
        """
        Accesso diretto al FileStore per operazioni avanzate sui file.

        Esempio
        -------
        >>> db.files.info()
        >>> db.files.get_path(memory_id)
        >>> db.files.list_by_type("images")
        >>> db.files.tree()
        """
        return self._files

    # ── READ ─────────────────────────────────

    def recall(
        self,
        concept      : str,
        *,
        feeling      : Optional[Union[Feeling, str]] = None,
        limit        : Optional[int] = None,
        oldest_first : bool = False,
    ) -> list[Memory]:
        """
        Richiama i ricordi di un concetto.

        Parametri
        ---------
        concept      : chiave concettuale da richiamare
        feeling      : filtra per sentimento (opzionale)
        limit        : numero massimo di risultati
        oldest_first : ordine cronologico (default: più recenti prima)

        Esempio
        -------
        >>> db.recall("Debito")
        >>> db.recall("Debito", feeling=Feeling.ANSIA, limit=5)
        """
        f_val = self._validate_feeling(feeling) if feeling else None
        offsets = self._index.offsets_by_concept(
            concept.strip(), feeling=f_val, oldest_first=oldest_first
        )
        return self._load_offsets(offsets, limit)

    def recall_by_feeling(
        self,
        feeling      : Union[Feeling, str],
        *,
        limit        : Optional[int] = None,
        oldest_first : bool = False,
    ) -> list[Memory]:
        """
        Richiama tutti i ricordi associati a un sentimento.

        Esempio
        -------
        >>> db.recall_by_feeling(Feeling.NOSTALGIA)
        >>> db.recall_by_feeling("amore", limit=10)
        """
        f_val   = self._validate_feeling(feeling)
        offsets = self._index.offsets_by_feeling(f_val, oldest_first=oldest_first)
        return self._load_offsets(offsets, limit)

    def recall_all(
        self,
        *,
        limit        : Optional[int] = None,
        oldest_first : bool = False,
    ) -> list[Memory]:
        """
        Restituisce tutti i ricordi.

        Esempio
        -------
        >>> db.recall_all()
        >>> db.recall_all(limit=20, oldest_first=True)
        """
        offsets = self._index.all_offsets(oldest_first=oldest_first)
        return self._load_offsets(offsets, limit)

    def recall_by_tag(
        self,
        tag   : str,
        *,
        limit : Optional[int] = None,
    ) -> list[Memory]:
        """
        Richiama i ricordi che contengono un tag.

        Esempio
        -------
        >>> db.recall_by_tag("casa")
        """
        offsets = self._index.offsets_by_tag(tag.strip())
        return self._load_offsets(offsets, limit)

    def search(
        self,
        text         : str,
        *,
        in_content   : bool = True,
        in_concept   : bool = True,
        in_note      : bool = True,
        limit        : Optional[int] = None,
    ) -> list[Memory]:
        """
        Ricerca full-text: scansiona tutti i ricordi.
        (Operazione lineare — su dataset grandi usa indici specifici)

        Parametri
        ---------
        text       : testo da cercare (case-insensitive)
        in_content : cerca nel contenuto
        in_concept : cerca nel concetto
        in_note    : cerca nelle note

        Esempio
        -------
        >>> db.search("mutuo")
        >>> db.search("natale", in_concept=False)
        """
        needle  = text.lower()
        results = []

        for _, record in self._storage.scan():
            match = False
            if in_content and needle in record.get("content", "").lower():
                match = True
            if in_concept and needle in record.get("concept", "").lower():
                match = True
            if in_note and needle in record.get("note", "").lower():
                match = True
            if match:
                results.append(self._record_to_memory(record))
                if limit and len(results) >= limit:
                    break

        return list(reversed(results))  # più recenti prima

    # ── STATS ────────────────────────────────

    def list_concepts(self) -> list[dict]:
        """
        Tutti i concetti con statistiche aggregate.

        Ritorna
        -------
        Lista di dict: { concept, total, feelings: {feeling: count} }

        Esempio
        -------
        >>> db.list_concepts()
        [{'concept': 'Debito', 'total': 3, 'feelings': {'ansia': 2}}, ...]
        """
        matrix = self._index.concept_feeling_matrix()
        result = []
        for concept, feelings in sorted(matrix.items()):
            result.append({
                "concept":  concept,
                "total":    sum(feelings.values()),
                "feelings": feelings,
            })
        return result

    def list_feelings(self) -> list[dict]:
        """
        Tutti i sentimenti con conteggio e concetti associati.

        Ritorna
        -------
        Lista di dict: { feeling, total, concepts: [...] }

        Esempio
        -------
        >>> db.list_feelings()
        [{'feeling': 'ansia', 'total': 5, 'concepts': ['Debito', 'Lavoro']}, ...]
        """
        matrix    = self._index.concept_feeling_matrix()
        f_to_data : dict[str, dict] = {}

        for concept, feelings in matrix.items():
            for feeling, count in feelings.items():
                if feeling not in f_to_data:
                    f_to_data[feeling] = {"feeling": feeling, "total": 0, "concepts": []}
                f_to_data[feeling]["total"]    += count
                f_to_data[feeling]["concepts"].append(concept)

        return sorted(f_to_data.values(), key=lambda x: x["total"], reverse=True)

    def concept_timeline(self, concept: str) -> list[dict]:
        """
        Cronologia emotiva di un concetto (solo metadati, no content).

        Esempio
        -------
        >>> db.concept_timeline("Debito")
        [{'timestamp': '...', 'feeling': 'ansia', 'note': '...', 'tags': [...]}, ...]
        """
        offsets = self._index.timeline_offsets(concept.strip())
        result  = []
        for offset in offsets:
            r = self._storage.read_at(offset)
            if r:
                result.append({
                    "timestamp": r["timestamp"],
                    "feeling":   r["feeling"],
                    "note":      r.get("note", ""),
                    "tags":      r.get("tags", []),
                })
        return result

    def feeling_distribution(self) -> dict[str, int]:
        """
        Mappa sentimento → numero totale di ricordi.

        Esempio
        -------
        >>> db.feeling_distribution()
        {'ansia': 8, 'amore': 5, 'nostalgia': 3}
        """
        dist = self._index.feeling_distribution()
        return dict(sorted(dist.items(), key=lambda x: x[1], reverse=True))

    def count(
        self,
        *,
        concept : Optional[str] = None,
        feeling : Optional[Union[Feeling, str]] = None,
    ) -> int:
        """
        Conta i ricordi con filtri opzionali.

        Esempio
        -------
        >>> db.count()
        >>> db.count(concept="Debito")
        >>> db.count(feeling=Feeling.ANSIA)
        >>> db.count(concept="Debito", feeling="ansia")
        """
        f_val = self._validate_feeling(feeling) if feeling else None
        return self._index.count(concept=concept, feeling=f_val)

    # ── EXPORT / IMPORT ──────────────────────

    def export_json(
        self,
        path            : Optional[Union[str, Path]] = None,
        *,
        concept         : Optional[str] = None,
        feeling         : Optional[Union[Feeling, str]] = None,
        include_content : bool = True,
    ) -> str:
        """
        Esporta ricordi in formato JSON.

        Parametri
        ---------
        path            : se fornito, scrive su file
        concept         : filtra per concetto
        feeling         : filtra per sentimento
        include_content : se False, omette il campo content

        Esempio
        -------
        >>> db.export_json("backup.json")
        >>> db.export_json(concept="Debito")
        """
        if concept:
            memories = self.recall(concept, feeling=feeling)
        elif feeling:
            memories = self.recall_by_feeling(feeling)
        else:
            memories = self.recall_all()

        data = []
        for m in memories:
            d = m.to_dict()
            if not include_content:
                d.pop("content", None)
            data.append(d)

        payload = json.dumps(
            {"exported_at": datetime.now(timezone.utc).isoformat(), "memories": data},
            ensure_ascii=False, indent=2,
        )

        if path:
            Path(path).write_text(payload, encoding="utf-8")

        return payload

    def import_json(self, path: Union[str, Path]) -> int:
        """
        Importa ricordi da un file JSON esportato con export_json().
        Non duplica ricordi già presenti (controlla memory_id).

        Ritorna il numero di ricordi importati.

        Esempio
        -------
        >>> db.import_json("backup.json")
        12
        """
        raw     = Path(path).read_text(encoding="utf-8")
        data    = json.loads(raw)
        entries = data.get("memories", data) if isinstance(data, dict) else data

        # Recupera memory_id già presenti
        existing_ids = {
            rec.get("memory_id") for _, rec in self._storage.scan()
        }

        imported = 0
        for entry in entries:
            if entry.get("memory_id") in existing_ids:
                continue

            record = {
                "memory_id":  entry["memory_id"],
                "concept":    entry["concept"],
                "feeling":    entry["feeling"],
                "media_type": entry.get("media_type", "text"),
                "content":    entry.get("content", ""),
                "note":       entry.get("note", ""),
                "tags":       entry.get("tags", []),
                "timestamp":  entry["timestamp"],
                "checksum":   entry.get("checksum", ""),
            }
            offset = self._storage.append(record)
            self._index.index_record(offset, record)
            existing_ids.add(entry["memory_id"])
            imported += 1

        return imported

    # ── INFO ─────────────────────────────────

    def storage_info(self) -> dict:
        """
        Informazioni sul file fisico di storage e sui file allegati.
        """
        size = self._storage.file_size()
        return {
            "log_path":      self._path,
            "log_size_bytes": size,
            "log_size_kb":   round(size / 1024, 2),
            "total_records": self.count(),
            "files":         self._files.info(),
        }

    # ── INTERNAL ─────────────────────────────

    def _validate_feeling(self, feeling: Union[Feeling, str]) -> str:
        val   = feeling.value if isinstance(feeling, Feeling) else str(feeling).strip().lower()
        valid = {f.value for f in Feeling}
        if val not in valid:
            raise InvalidFeelingError(
                f"Sentimento '{val}' non valido. Ammessi: {sorted(valid)}"
            )
        return val

    def _validate_media_type(self, media_type: Union[MediaType, str]) -> str:
        val   = media_type.value if isinstance(media_type, MediaType) else str(media_type).strip().lower()
        valid = {m.value for m in MediaType}
        if val not in valid:
            raise InvalidMediaTypeError(
                f"Tipo media '{val}' non valido. Ammessi: {sorted(valid)}"
            )
        return val

    def _load_offsets(self, offsets: list[int], limit: Optional[int]) -> list[Memory]:
        """Carica i Memory dal file dato una lista di offset."""
        if limit:
            offsets = offsets[:limit]
        result = []
        for offset in offsets:
            record = self._storage.read_at(offset)
            if record:
                result.append(self._record_to_memory(record))
        return result

    def _record_to_memory(self, record: dict) -> Memory:
        return Memory(
            memory_id  = record["memory_id"],
            concept    = record["concept"],
            feeling    = record["feeling"],
            media_type = record.get("media_type", "text"),
            content    = record.get("content", ""),
            note       = record.get("note", ""),
            tags       = tuple(record.get("tags", [])),
            timestamp  = record["timestamp"],
            checksum   = record.get("checksum", ""),
        )

    def close(self) -> None:
        """Nessuna connessione da chiudere — il file viene aperto/chiuso ad ogni operazione."""
        pass

    def __enter__(self) -> "MemoryDB":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def __repr__(self) -> str:
        info       = self.storage_info()
        files_info = info.get("files", {})
        n_files    = files_info.get("total_entries", files_info.get("total_files", 0))
        return (
            f"MemoryDB(path='{self._path}', "
            f"records={info['total_records']}, "
            f"log={info['log_size_kb']}KB, "
            f"files={n_files})"
        )
