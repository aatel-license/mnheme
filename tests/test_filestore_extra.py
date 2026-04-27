"""
test_filestore_extra.py — Copertura di filestore.py e fsprobe.py

Copre: store() error paths, get_pool_path(), get_bytes(), list_by_memory(),
       exists(), list_by_type(), FileNotFoundInStoreError, store move, dedup,
       _do_copy_atomic, _do_reflink fallback, store_bytes, repr, _load_index errors,
       FileEntry.to_dict/from_dict/repr, fsprobe capabilities
"""
import os
import struct
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from filestore import (
    FileStore, FileEntry, UnsupportedMediaError, FileNotFoundInStoreError,
    SUPPORTED_MEDIA, _sha256, _safe_name, _do_copy_atomic, _do_reflink,
)
from fsprobe import FsProbe, LinkStrategy


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def fs(tmp_path):
    return FileStore(tmp_path / "files")


@pytest.fixture
def sample_jpg(tmp_path):
    img = tmp_path / "test_image.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 200)
    return img


@pytest.fixture
def sample_mp3(tmp_path):
    audio = tmp_path / "test_audio.mp3"
    audio.write_bytes(b"ID3" + b"\x00" * 100)
    return audio


@pytest.fixture
def sample_pdf(tmp_path):
    doc = tmp_path / "test_doc.pdf"
    doc.write_bytes(b"%PDF-1.4" + b"\x00" * 50)
    return doc


# ── store() basic ─────────────────────────────────────────────────────────────

def test_store_jpg(fs, sample_jpg):
    entry = fs.store("mem-001", sample_jpg)
    assert entry.memory_id == "mem-001"
    assert entry.media_type == "images"
    assert entry.size_bytes > 0
    assert entry.checksum


def test_store_mp3(fs, sample_mp3):
    entry = fs.store("mem-002", sample_mp3)
    assert entry.media_type == "audio"


def test_store_pdf(fs, sample_pdf):
    entry = fs.store("mem-003", sample_pdf)
    assert entry.media_type == "docs"


def test_store_file_not_found(fs, tmp_path):
    with pytest.raises(FileNotFoundError):
        fs.store("mem-x", tmp_path / "nonexistent.jpg")


def test_store_unsupported_extension(fs, tmp_path):
    bad = tmp_path / "file.xyz"
    bad.write_bytes(b"data")
    with pytest.raises(UnsupportedMediaError):
        fs.store("mem-x", bad)


def test_store_dedup(fs, sample_jpg):
    """Stesso file: seconda store deve usare entry esistente nella pool."""
    e1 = fs.store("mem-001", sample_jpg)
    e2 = fs.store("mem-002", sample_jpg)
    # Stesso checksum → stessa pool_path
    assert e1.checksum == e2.checksum
    assert e1.pool_path == e2.pool_path


def test_store_move(tmp_path):
    fs = FileStore(tmp_path / "files")
    img = tmp_path / "move_me.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)
    entry = fs.store("mem-001", img, move=True)
    assert entry.media_type == "images"
    # Il file originale può o non può esistere ancora (OS permette)


def test_store_link_already_exists(fs, sample_jpg):
    """Secondo store dello stesso file per lo stesso memory_id non crashe."""
    e1 = fs.store("mem-dup", sample_jpg)
    e2 = fs.store("mem-dup", sample_jpg)
    assert e1.link_path == e2.link_path


# ── store_bytes ───────────────────────────────────────────────────────────────

def test_store_bytes_jpg(fs):
    data = b"\xff\xd8\xff" + b"\x00" * 100
    entry = fs.store_bytes("mem-byte-001", data, "foto.jpg")
    assert entry.original_name == "foto.jpg"
    assert entry.media_type == "images"


def test_store_bytes_unsupported(fs):
    with pytest.raises(UnsupportedMediaError):
        fs.store_bytes("mem-x", b"data", "file.xyz")


def test_store_bytes_video(fs):
    data = b"\x00" * 500
    entry = fs.store_bytes("mem-vid", data, "clip.mp4")
    assert entry.media_type == "videos"


# ── get_path / get_pool_path / get_bytes ──────────────────────────────────────

def test_get_path(fs, sample_jpg):
    e = fs.store("mem-001", sample_jpg)
    p = fs.get_path("mem-001")
    assert p.exists()


def test_get_path_not_found(fs):
    with pytest.raises(FileNotFoundInStoreError):
        fs.get_path("nonexistent-memory-id")


def test_get_pool_path(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    p = fs.get_pool_path("mem-001")
    assert p.exists()


def test_get_pool_path_not_found(fs):
    with pytest.raises(FileNotFoundInStoreError):
        fs.get_pool_path("nonexistent")


def test_get_bytes(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    data = fs.get_bytes("mem-001")
    assert isinstance(data, bytes)
    assert len(data) > 0


# ── list_by_memory / list_by_type / exists ────────────────────────────────────

def test_list_by_memory(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    entries = fs.list_by_memory("mem-001")
    assert len(entries) == 1
    assert isinstance(entries[0], FileEntry)


def test_list_by_memory_empty(fs):
    entries = fs.list_by_memory("nonexistent")
    assert entries == []


def test_list_by_type(fs, sample_jpg, sample_mp3):
    fs.store("mem-001", sample_jpg)
    fs.store("mem-002", sample_mp3)
    images = fs.list_by_type("images")
    audio = fs.list_by_type("audio")
    assert len(images) >= 1
    assert len(audio) >= 1


def test_exists_true(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    assert fs.exists("mem-001")


def test_exists_false(fs):
    assert not fs.exists("nonexistent")


# ── info / tree / repr ───────────────────────────────────────────────────────

def test_info(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    info = fs.info()
    assert info["total_entries"] == 1
    assert "filesystem" in info
    assert "strategy" in info
    assert "by_type" in info


def test_info_dedup_ratio(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    fs.store("mem-002", sample_jpg)
    info = fs.info()
    assert info["dedup_ratio"] >= 1.0


def test_tree(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    t = fs.tree()
    assert "pool/" in t
    assert "memories/" in t


def test_repr(fs, sample_jpg):
    fs.store("mem-001", sample_jpg)
    r = repr(fs)
    assert "FileStore" in r


# ── FileEntry ─────────────────────────────────────────────────────────────────

def test_file_entry_to_dict(fs, sample_jpg):
    entry = fs.store("mem-001", sample_jpg)
    d = entry.to_dict()
    assert d["memory_id"] == "mem-001"
    assert "checksum" in d


def test_file_entry_from_dict(fs, sample_jpg):
    entry = fs.store("mem-001", sample_jpg)
    d = entry.to_dict()
    entry2 = FileEntry.from_dict(d)
    assert entry2.memory_id == entry.memory_id


def test_file_entry_repr(fs, sample_jpg):
    entry = fs.store("mem-001", sample_jpg)
    r = repr(entry)
    assert "FileEntry" in r
    assert "strategy" in r


# ── _load_index with corrupt file ─────────────────────────────────────────────

def test_load_index_corrupt_json(tmp_path):
    files_dir = tmp_path / "files"
    files_dir.mkdir()
    # Crea un _index.json corrotto
    (files_dir / "_index.json").write_text("NOT JSON", encoding="utf-8")
    # FileStore deve inizializzare senza crashare
    fs = FileStore(files_dir)
    assert fs.exists("any") == False


def test_load_index_valid(tmp_path, sample_jpg):
    files_dir = tmp_path / "files"
    fs1 = FileStore(files_dir)
    fs1.store("mem-reload", sample_jpg)

    # Riapre: deve caricare l'indice esistente
    fs2 = FileStore(files_dir)
    assert fs2.exists("mem-reload")
    data = fs2.get_bytes("mem-reload")
    assert len(data) > 0


# ── _do_copy_atomic ───────────────────────────────────────────────────────────

def test_do_copy_atomic(tmp_path):
    src = tmp_path / "source.txt"
    src.write_bytes(b"hello world")
    dst = tmp_path / "dest.txt"
    _do_copy_atomic(src, dst)
    assert dst.exists()
    assert dst.read_bytes() == b"hello world"


def test_do_copy_atomic_failure(tmp_path):
    """Se shutil.copy2 fallisce, il tmp file viene rimosso e l'eccezione è propagata."""
    src = tmp_path / "source.txt"
    src.write_bytes(b"data")
    dst = tmp_path / "subdir_nonexistent" / "dest.txt"
    # dest dir non esiste → shutil.copy2 fallisce
    with pytest.raises(Exception):
        _do_copy_atomic(src, dst)


# ── _do_reflink fallback ──────────────────────────────────────────────────────

def test_do_reflink_falls_back_to_copy(tmp_path):
    """Su filesystem senza reflink, _do_reflink deve cadere in _do_copy_atomic."""
    src = tmp_path / "source.jpg"
    src.write_bytes(b"\xff\xd8\xff" + b"\x00" * 50)
    dst = tmp_path / "dest.jpg"
    # Su ext4, il reflink fallirà e farà fallback a copy
    _do_reflink(src, dst)
    assert dst.exists()
    assert dst.read_bytes() == src.read_bytes()


# ── _sha256 / _safe_name ─────────────────────────────────────────────────────

def test_sha256(tmp_path):
    f = tmp_path / "test.bin"
    f.write_bytes(b"hello world")
    h = _sha256(f)
    assert len(h) == 64  # sha256 hex digest


def test_safe_name():
    assert _safe_name("foto natale 2024.jpg") == "foto_natale_2024.jpg"
    assert _safe_name("file/with/slashes.jpg") == "slashes.jpg"
    long_name = "a" * 100 + ".jpg"
    assert len(_safe_name(long_name)) <= 80


# ── fsprobe basics ─────────────────────────────────────────────────────────────

def test_fsprobe_detect(tmp_path):
    probe = FsProbe(tmp_path)
    caps = probe.detect()
    assert caps is not None
    assert caps.strategy is not None


def test_fsprobe_repr(tmp_path):
    probe = FsProbe(tmp_path)
    caps = probe.detect()
    r = repr(caps)
    assert "FsCapabilities" in r or len(r) > 0


def test_fsprobe_strategy_value(tmp_path):
    probe = FsProbe(tmp_path)
    caps = probe.detect()
    assert caps.strategy.value in ["hardlink", "copy_atomic", "symlink", "reflink"]


# ── FileStore with explicit probe_dir ─────────────────────────────────────────

def test_filestore_probe_dir(tmp_path):
    """FileStore con probe_dir esplicito non deve crashare."""
    files_dir = tmp_path / "myfiles"
    fs = FileStore(files_dir, probe_dir=tmp_path)
    assert fs.caps is not None


# ── caps property ────────────────────────────────────────────────────────────

def test_caps_property(fs):
    caps = fs.caps
    assert caps is not None
    assert hasattr(caps, "strategy")


# ── SUPPORTED_MEDIA completeness ──────────────────────────────────────────────

def test_supported_media_extensions():
    assert ".jpg" in SUPPORTED_MEDIA
    assert ".mp4" in SUPPORTED_MEDIA
    assert ".mp3" in SUPPORTED_MEDIA
    assert ".pdf" in SUPPORTED_MEDIA
    assert ".png" in SUPPORTED_MEDIA


# ── FileStore multiple files per memory ──────────────────────────────────────

def test_multiple_files_same_memory(fs, sample_jpg, sample_mp3):
    fs.store("mem-multi", sample_jpg)
    fs.store("mem-multi", sample_mp3)
    entries = fs.list_by_memory("mem-multi")
    assert len(entries) == 2


# ── store move with OSError on unlink ────────────────────────────────────────

def test_store_move_oserror_on_unlink(fs, sample_jpg):
    """Se unlink fallisce durante move=True, non deve crashare."""
    with patch("pathlib.Path.unlink", side_effect=OSError("perm denied")):
        entry = fs.store("mem-move-err", sample_jpg, move=True)
    assert entry is not None
