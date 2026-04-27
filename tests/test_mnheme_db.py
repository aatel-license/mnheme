"""
test_mnheme_db.py — Copertura delle funzionalità di mnheme.py non ancora coperte.
"""
import json
import os
import tempfile
from pathlib import Path

import pytest
from mnheme import (
    MemoryDB, Memory, Feeling, MediaType,
    MnhemeError, InvalidFeelingError, InvalidMediaTypeError,
)


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    path = tmp_path / "test.mnheme"
    d = MemoryDB(str(path))
    yield d
    d.close()


@pytest.fixture
def db_with_data(db):
    db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.")
    db.remember("Famiglia", Feeling.AMORE, "Sorriso di mia figlia.")
    db.remember("Viaggio", Feeling.NOSTALGIA, "Lisbona sotto la pioggia.")
    db.remember("Debito", Feeling.PAURA, "Lettera dalla banca.")
    return db


# ── remember validation ───────────────────────────────────────────────────────

def test_remember_empty_concept(db):
    with pytest.raises(MnhemeError, match="concetto"):
        db.remember("   ", Feeling.ANSIA, "contenuto")


def test_remember_empty_content(db):
    with pytest.raises(MnhemeError, match="contenuto"):
        db.remember("Casa", Feeling.ANSIA, "")


def test_invalid_feeling(db):
    with pytest.raises(InvalidFeelingError):
        db.remember("Casa", "sentimento_inesistente", "contenuto")


def test_invalid_media_type(db):
    with pytest.raises(InvalidMediaTypeError):
        db.remember("Casa", Feeling.ANSIA, "contenuto", media_type="unknown_type")


def test_remember_with_tags(db):
    m = db.remember("Casa", Feeling.GIOIA, "Entrati in casa nuova!", tags=["immobile", "famiglia"])
    assert "immobile" in m.tags
    assert "famiglia" in m.tags


def test_remember_feeling_as_string(db):
    m = db.remember("Casa", "gioia", "Entrati in casa nuova!")
    assert m.feeling == "gioia"


def test_remember_feeling_enum(db):
    m = db.remember("Casa", Feeling.GIOIA, "Entrati!")
    assert m.feeling == "gioia"


def test_remember_media_type_enum(db):
    m = db.remember("Foto", Feeling.GIOIA, "data:image/png;base64,abc", media_type=MediaType.IMAGE)
    assert m.media_type == "image"


# ── remember_many ─────────────────────────────────────────────────────────────

def test_remember_many(db):
    items = [
        {"concept": "A", "feeling": "gioia", "content": "contenuto A"},
        {"concept": "B", "feeling": "ansia", "content": "contenuto B"},
        {"concept": "C", "feeling": "amore", "content": "contenuto C"},
    ]
    memories = db.remember_many(items)
    assert len(memories) == 3
    assert db.count() == 3


def test_remember_many_empty(db):
    assert db.remember_many([]) == []


def test_remember_many_missing_fields(db):
    with pytest.raises(MnhemeError):
        db.remember_many([{"concept": "", "feeling": "gioia", "content": ""}])


def test_remember_many_optional_fields(db):
    items = [
        {
            "concept": "Test",
            "feeling": "gioia",
            "content": "contenuto",
            "media_type": "text",
            "note": "nota",
            "tags": ["a", "b"],
        }
    ]
    mems = db.remember_many(items)
    assert len(mems) == 1
    assert mems[0].note == "nota"
    assert "a" in mems[0].tags


# ── recall ────────────────────────────────────────────────────────────────────

def test_recall_with_feeling(db_with_data):
    mems = db_with_data.recall("Debito", feeling=Feeling.ANSIA)
    assert len(mems) == 1
    assert mems[0].feeling == "ansia"


def test_recall_oldest_first(db_with_data):
    mems_new = db_with_data.recall("Debito")
    mems_old = db_with_data.recall("Debito", oldest_first=True)
    assert mems_new[0].memory_id == mems_old[-1].memory_id


def test_recall_with_limit(db_with_data):
    mems = db_with_data.recall("Debito", limit=1)
    assert len(mems) == 1


def test_recall_nonexistent(db):
    mems = db.recall("XYZ_Inesistente")
    assert mems == []


def test_recall_by_feeling(db_with_data):
    mems = db_with_data.recall_by_feeling(Feeling.ANSIA)
    assert all(m.feeling == "ansia" for m in mems)


def test_recall_by_feeling_oldest(db_with_data):
    mems = db_with_data.recall_by_feeling(Feeling.NOSTALGIA, oldest_first=True)
    assert len(mems) >= 1


def test_recall_all_limit(db_with_data):
    mems = db_with_data.recall_all(limit=2)
    assert len(mems) == 2


def test_recall_all_oldest(db_with_data):
    mems = db_with_data.recall_all(oldest_first=True)
    assert len(mems) == 4


# ── recall_by_tag ─────────────────────────────────────────────────────────────

def test_recall_by_tag(db):
    db.remember("Casa", Feeling.GIOIA, "Casa nuova!", tags=["immobile"])
    db.remember("Lavoro", Feeling.ANSIA, "Riunione!", tags=["ufficio"])
    mems = db.recall_by_tag("immobile")
    assert len(mems) == 1
    assert mems[0].concept == "Casa"


def test_recall_by_tag_oldest_first(db):
    db.remember("A", Feeling.GIOIA, "primo", tags=["test"])
    db.remember("B", Feeling.GIOIA, "secondo", tags=["test"])
    mems = db.recall_by_tag("test", oldest_first=True)
    assert mems[0].concept == "A"


def test_recall_by_tag_limit_none(db):
    for i in range(5):
        db.remember(f"X{i}", Feeling.GIOIA, f"contenuto {i}", tags=["multi"])
    mems = db.recall_by_tag("multi", limit=None)
    assert len(mems) == 5


# ── search ───────────────────────────────────────────────────────────────────

def test_search_in_content(db):
    db.remember("Casa", Feeling.GIOIA, "Ho comprato un mutuo dalla banca")
    results = db.search("mutuo")
    assert len(results) > 0


def test_search_in_concept(db):
    db.remember("Mutuo", Feeling.ANSIA, "contenuto generico")
    results = db.search("mutuo", in_content=False, in_concept=True)
    assert len(results) > 0


def test_search_in_note(db):
    db.remember("X", Feeling.GIOIA, "contenuto", note="questa è una nota speciale")
    results = db.search("nota speciale", in_note=True, in_content=False, in_concept=False)
    assert len(results) > 0


def test_search_empty(db):
    db.remember("X", Feeling.GIOIA, "contenuto")
    results = db.search("")
    assert results == []


def test_search_not_found(db):
    db.remember("X", Feeling.GIOIA, "contenuto del ricordo")
    results = db.search("xyz_impossibile_trovare_123")
    assert results == []


def test_search_fallback_short_token(db):
    """Token corto (<3 chars) → fallback a scansione lineare."""
    db.remember("Casa", Feeling.GIOIA, "io ho la casa")
    results = db.search("io")  # 2 chars → fallback
    # Può trovare o non trovare — l'importante è non crashare
    assert isinstance(results, list)


def test_search_with_limit(db):
    for i in range(10):
        db.remember("Test", Feeling.GIOIA, f"testo test numero {i}")
    results = db.search("testo", limit=3)
    assert len(results) <= 3


# ── count ────────────────────────────────────────────────────────────────────

def test_count_all(db_with_data):
    assert db_with_data.count() == 4


def test_count_by_concept(db_with_data):
    assert db_with_data.count(concept="Debito") == 2


def test_count_by_feeling(db_with_data):
    assert db_with_data.count(feeling=Feeling.ANSIA) == 1


def test_count_by_concept_and_feeling(db_with_data):
    assert db_with_data.count(concept="Debito", feeling="ansia") == 1


# ── stats ────────────────────────────────────────────────────────────────────

def test_list_concepts(db_with_data):
    concepts = db_with_data.list_concepts()
    names = [c["concept"] for c in concepts]
    assert "Debito" in names
    assert "Famiglia" in names


def test_list_feelings(db_with_data):
    feelings = db_with_data.list_feelings()
    feeling_names = [f["feeling"] for f in feelings]
    assert "ansia" in feeling_names


def test_feeling_distribution(db_with_data):
    dist = db_with_data.feeling_distribution()
    assert "ansia" in dist
    assert dist["ansia"] >= 1


def test_concept_timeline(db_with_data):
    timeline = db_with_data.concept_timeline("Debito")
    assert len(timeline) == 2
    assert all("timestamp" in t for t in timeline)
    assert all("feeling" in t for t in timeline)


def test_concept_timeline_empty(db):
    assert db.concept_timeline("Inesistente") == []


def test_storage_info(db_with_data):
    info = db_with_data.storage_info()
    assert "log_size_bytes" in info
    assert info["total_records"] == 4


# ── export / import ───────────────────────────────────────────────────────────

def test_export_json_all(db_with_data, tmp_path):
    path = tmp_path / "export.json"
    payload = db_with_data.export_json(str(path))
    data = json.loads(payload)
    assert len(data["memories"]) == 4
    assert path.exists()


def test_export_json_by_concept(db_with_data):
    payload = db_with_data.export_json(concept="Debito")
    data = json.loads(payload)
    assert all(m["concept"] == "Debito" for m in data["memories"])


def test_export_json_by_feeling(db_with_data):
    payload = db_with_data.export_json(feeling=Feeling.AMORE)
    data = json.loads(payload)
    assert all(m["feeling"] == "amore" for m in data["memories"])


def test_export_json_no_content(db_with_data):
    payload = db_with_data.export_json(include_content=False)
    data = json.loads(payload)
    for m in data["memories"]:
        assert "content" not in m


def test_export_import_roundtrip(db_with_data, tmp_path):
    export_path = tmp_path / "export.json"
    db_with_data.export_json(str(export_path))

    db2 = MemoryDB(str(tmp_path / "db2.mnheme"))
    n = db2.import_json(str(export_path))
    assert n == 4
    assert db2.count() == 4
    db2.close()


def test_import_json_no_duplicates(db_with_data, tmp_path):
    export_path = tmp_path / "export.json"
    db_with_data.export_json(str(export_path))
    # importa due volte — la seconda deve ritornare 0
    n1 = db_with_data.import_json(str(export_path))
    n2 = db_with_data.import_json(str(export_path))
    assert n2 == 0


def test_export_json_no_path(db_with_data):
    """export_json senza path → ritorna solo la stringa JSON."""
    payload = db_with_data.export_json()
    data = json.loads(payload)
    assert "memories" in data


# ── remember_file ─────────────────────────────────────────────────────────────

def test_remember_file(db, tmp_path):
    img = tmp_path / "foto.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)
    mem, fe = db.remember_file("Famiglia", Feeling.AMORE, str(img))
    assert mem.media_type == "image"
    assert fe.media_type == "images"


def test_remember_file_unsupported(db, tmp_path):
    f = tmp_path / "file.xyz"
    f.write_bytes(b"data")
    from filestore import UnsupportedMediaError
    with pytest.raises(UnsupportedMediaError):
        db.remember_file("X", Feeling.GIOIA, str(f))


def test_remember_file_move(db, tmp_path):
    img = tmp_path / "foto.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)
    mem, fe = db.remember_file("Famiglia", Feeling.AMORE, str(img), copy=False)
    assert mem.media_type == "image"


# ── remember_bytes ────────────────────────────────────────────────────────────

def test_remember_bytes_image(db):
    data = b"\xff\xd8\xff" + b"\x00" * 200
    mem, fe = db.remember_bytes("Foto", Feeling.GIOIA, data, "foto.jpg")
    assert mem.media_type == "image"
    assert fe.media_type == "images"


def test_remember_bytes_audio(db):
    data = b"ID3" + b"\x00" * 100
    mem, fe = db.remember_bytes("Musica", Feeling.NOSTALGIA, data, "canzone.mp3")
    assert mem.media_type == "audio"


def test_remember_bytes_unsupported(db):
    from filestore import UnsupportedMediaError
    with pytest.raises(UnsupportedMediaError):
        db.remember_bytes("X", Feeling.GIOIA, b"data", "file.xyz")


# ── files property ────────────────────────────────────────────────────────────

def test_files_property(db):
    from filestore import FileStore
    assert isinstance(db.files, FileStore)


# ── context manager ───────────────────────────────────────────────────────────

def test_context_manager(tmp_path):
    path = tmp_path / "cm.mnheme"
    with MemoryDB(str(path)) as db:
        db.remember("Test", Feeling.GIOIA, "contenuto")
        assert db.count() == 1


# ── repr ──────────────────────────────────────────────────────────────────────

def test_repr(db_with_data):
    r = repr(db_with_data)
    assert "MemoryDB" in r
    assert "records=4" in r


# ── Memory.to_dict / __repr__ ─────────────────────────────────────────────────

def test_memory_to_dict(db):
    m = db.remember("Casa", Feeling.GIOIA, "contenuto", note="nota", tags=["a"])
    d = m.to_dict()
    assert d["concept"] == "Casa"
    assert d["feeling"] == "gioia"
    assert "a" in d["tags"]


def test_memory_repr(db):
    m = db.remember("Casa", Feeling.GIOIA, "X" * 100)
    r = repr(m)
    assert "Memory" in r
    assert "…" in r  # contenuto troncato


def test_memory_repr_short(db):
    m = db.remember("Casa", Feeling.GIOIA, "corto")
    r = repr(m)
    # content is short enough that it won't have a trailing '…' after 'content='
    assert "Memory(" in r
    assert "content='corto'" in r


# ── fsync policies ────────────────────────────────────────────────────────────

def test_db_fsync_never(tmp_path):
    db = MemoryDB(str(tmp_path / "fast.mnheme"), fsync_policy="never")
    db.remember("A", Feeling.GIOIA, "contenuto")
    assert db.count() == 1
    db.close()


def test_db_fsync_batch(tmp_path):
    db = MemoryDB(str(tmp_path / "batch.mnheme"), fsync_policy="batch", fsync_ms=50)
    db.remember("A", Feeling.GIOIA, "contenuto")
    assert db.count() == 1
    db.close()


# ── index reload from disk ────────────────────────────────────────────────────

def test_index_reload(tmp_path):
    """Chiude e riapre il DB: l'indice deve essere ricaricato dal disco."""
    path = str(tmp_path / "reload.mnheme")
    db1 = MemoryDB(path)
    db1.remember("Casa", Feeling.GIOIA, "Ho preso casa.")
    db1.close()

    db2 = MemoryDB(path)
    assert db2.count() == 1
    mems = db2.recall("Casa")
    assert len(mems) == 1
    db2.close()


# ── search: linear scan fallback paths ───────────────────────────────────────

def test_search_linear_scan_in_concept(db):
    """Forza scansione lineare (token 2 chars) e cerca nel concetto."""
    # "io" è 2 chars → non nell'indice invertito → linear scan
    db.remember("IO", Feeling.GIOIA, "qualcosa di neutro")
    results = db.search("io", in_concept=True, in_content=False, in_note=False)
    assert isinstance(results, list)


def test_search_linear_scan_in_note(db):
    """Forza scansione lineare e cerca nella note."""
    db.remember("X", Feeling.GIOIA, "contenuto generico", note="io studio sempre")
    # "io" è 2 chars → linear scan
    results = db.search("io", in_note=True, in_content=False, in_concept=False)
    assert isinstance(results, list)


def test_search_linear_scan_limit_stops_early(db):
    """Linear scan si ferma al raggiungimento del limit."""
    for i in range(20):
        db.remember("X", Feeling.GIOIA, f"io sono numero {i}")
    # "io" → linear scan; limit deve fermare la ricerca
    results = db.search("io", limit=3)
    assert len(results) <= 3


def test_search_index_path_in_concept_only(db):
    """Indice invertito: match only in concept, not in content."""
    db.remember("Debito", Feeling.ANSIA, "Nulla di correlato")
    # "debito" is 6 chars, will be in word index (concept tokenized)
    results = db.search("debito", in_content=False, in_concept=True, in_note=False)
    assert len(results) >= 1

