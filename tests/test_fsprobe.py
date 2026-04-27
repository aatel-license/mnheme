"""
test_fsprobe.py — Test FsProbe + FileStore
"""
import sys, os, shutil, tempfile, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from fsprobe import FsProbe, FsType, LinkStrategy
from filestore import FileStore, UnsupportedMediaError
from mnheme import MemoryDB, Feeling


# ── FsProbe tests ─────────────────────────────

def test_probe_detect():
    probe = FsProbe("/tmp")
    caps = probe.detect()
    assert caps is not None
    d = caps.to_dict()
    assert isinstance(d, dict)


def test_probe_cache():
    import time
    probe = FsProbe("/tmp")
    t0 = time.perf_counter()
    caps2 = probe.detect()
    ms = (time.perf_counter() - t0) * 1000
    assert ms < 50, f"Cache troppo lenta: {ms}ms"


def test_probe_capabilities():
    probe = FsProbe("/tmp")
    caps = probe.detect()
    assert hasattr(caps, "can_hardlink")
    assert hasattr(caps, "can_reflink")
    assert hasattr(caps, "can_symlink")
    assert hasattr(caps, "is_remote")
    assert hasattr(caps, "is_readonly")
    assert hasattr(caps, "is_case_sensitive")
    assert hasattr(caps, "inode_bits")
    assert hasattr(caps, "strategy")


def test_probe_strategy():
    probe = FsProbe("/tmp")
    caps = probe.detect()
    assert isinstance(caps.strategy, LinkStrategy)
    assert len(caps.strategy_note) > 0


# ── FileStore tests ───────────────────────────

@pytest.fixture
def fstore(tmp_path):
    """Crea un FileStore temporaneo."""
    base = str(tmp_path / "fstore")
    os.makedirs(base, exist_ok=True)
    return FileStore(base)


def test_fstore_create(fstore):
    assert fstore is not None
    assert hasattr(fstore, "caps")
    assert hasattr(fstore, "_base")


def test_fstore_store_image(tmp_path):
    base = str(tmp_path / "fstore")
    os.makedirs(base, exist_ok=True)
    fs = FileStore(base)

    fd, tmp_file = tempfile.mkstemp(suffix=".jpg")
    os.write(fd, b"\xFF\xD8\xFF" + b"IMG" * 500)
    os.close(fd)

    entry = fs.store("mem-001", tmp_file)
    assert entry is not None
    assert entry.pool_path is not None
    assert entry.link_path is not None


def test_fstore_store_video(tmp_path):
    base = str(tmp_path / "fstore")
    os.makedirs(base, exist_ok=True)
    fs = FileStore(base)

    fd, tmp_file = tempfile.mkstemp(suffix=".mp4")
    os.write(fd, b"\x00\x00\x00\x18ftyp" + b"VID" * 300)
    os.close(fd)

    entry = fs.store("mem-002", tmp_file)
    assert entry is not None


def test_fstore_store_audio(tmp_path):
    base = str(tmp_path / "fstore")
    os.makedirs(base, exist_ok=True)
    fs = FileStore(base)

    fd, tmp_file = tempfile.mkstemp(suffix=".mp3")
    os.write(fd, b"ID3" + b"AUD" * 200)
    os.close(fd)

    entry = fs.store("mem-003", tmp_file)
    assert entry is not None


def test_fstore_store_doc(tmp_path):
    base = str(tmp_path / "fstore")
    os.makedirs(base, exist_ok=True)
    fs = FileStore(base)

    fd, tmp_file = tempfile.mkstemp(suffix=".pdf")
    os.write(fd, b"%PDF-1.4" + b"DOC" * 100)
    os.close(fd)

    entry = fs.store("mem-004", tmp_file)
    assert entry is not None


def test_fstore_dedup(tmp_path):
    """Due file con stesso contenuto → stesso pool."""
    base = str(tmp_path / "fstore")
    os.makedirs(base, exist_ok=True)
    fs = FileStore(base)

    data = b"\xFF\xD8\xFF" + b"IMG" * 500
    fd1, tmp1 = tempfile.mkstemp(suffix=".jpg")
    os.write(fd1, data); os.close(fd1)
    fd2, tmp2 = tempfile.mkstemp(suffix=".jpg")
    os.write(fd2, data); os.close(fd2)

    e1 = fs.store("mem-005", tmp1)
    e2 = fs.store("mem-006", tmp2)

    assert e1.checksum == e2.checksum
    assert e1.pool_path == e2.pool_path


def test_fstore_get_path(fstore):
    fd, tmp_file = tempfile.mkstemp(suffix=".jpg")
    os.write(fd, b"\xFF\xD8\xFF" + b"X" * 100)
    os.close(fd)

    fstore.store("mem-007", tmp_file)
    path = fstore.get_path("mem-007")
    assert path is not None


def test_fstore_get_bytes(fstore):
    fd, tmp_file = tempfile.mkstemp(suffix=".jpg")
    os.write(fd, b"\xFF\xD8\xFF" + b"X" * 100)
    os.close(fd)

    fstore.store("mem-008", tmp_file)
    data = fstore.get_bytes("mem-008")
    assert len(data) > 0


def test_fstore_list_by_type(fstore):
    fd, tmp_file = tempfile.mkstemp(suffix=".jpg")
    os.write(fd, b"\xFF\xD8\xFF" + b"X" * 100)
    os.close(fd)

    fstore.store("mem-009", tmp_file)
    items = fstore.list_by_type("images")
    assert len(items) >= 1


def test_fstore_info(fstore):
    info = fstore.info()
    assert isinstance(info, dict)


def test_fstore_tree(fstore):
    tree = fstore.tree()
    assert isinstance(tree, str)


# ── MemoryDB + FileStore integration ──────────

@pytest.fixture
def db_with_files(tmp_path):
    """Crea un MemoryDB con file storage."""
    db_path = str(tmp_path / "test.mnheme")
    files_dir = str(tmp_path / "files")
    return MemoryDB(db_path, files_dir=files_dir)


def test_db_file_integration(db_with_files):
    fd, tmp_img = tempfile.mkstemp(suffix=".jpg")
    os.write(fd, b"\xFF\xD8\xFF" + b"X" * 800)
    os.close(fd)

    mem, fe = db_with_files.remember_file(
        "Famiglia", Feeling.AMORE, tmp_img,
        note="Test integrazione", tags=["test"]
    )
    assert mem is not None
    assert fe is not None


def test_db_detects_fs_type(db_with_files):
    assert hasattr(db_with_files.files, "caps")
    # FsType non ha LOCAL/REMOTE — usa i valori reali del filesystem rilevato
    fs_type_val = db_with_files.files.caps.fs_type.value
    assert isinstance(fs_type_val, str) and len(fs_type_val) > 0


# ── UnsupportedMediaError ─────────────────────

def test_unsupported_media_error():
    try:
        raise UnsupportedMediaError("formato", "tipo")
    except UnsupportedMediaError as e:
        assert "formato" in str(e) or "tipo" in str(e)


# ── FsProbe edge cases ───────────────────────

def test_probe_nonexistent_dir(tmp_path):
    """Usa un path temporaneo non esistente invece di /nonexistent (root protected)."""
    target = str(tmp_path / "does_not_exist_xyz123")
    probe = FsProbe(target)
    caps = probe.detect()
    assert caps is not None  # dovrebbe gestire il caso con fallback


def test_probe_root():
    probe = FsProbe("/")
    caps = probe.detect()
    assert caps is not None
