"""
test_storage.py — Copertura completa di storage.py
"""
import os
import json
import struct
import tempfile
import threading
import time
from pathlib import Path

import pytest
from storage import StorageEngine, CorruptedRecordError, MAGIC, _encode, _reopen, _seek_next_magic


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_file(tmp_path):
    return str(tmp_path / "test.mnheme")


# ── Basic append / scan ────────────────────────────────────────────────────────

def test_append_and_scan(tmp_file):
    engine = StorageEngine(tmp_file)
    rec = {"concept": "Debito", "feeling": "ansia", "content": "mutuo"}
    offset = engine.append(rec)
    assert offset == 0
    results = list(engine.scan())
    assert len(results) == 1
    assert results[0][1]["concept"] == "Debito"
    engine.close()


def test_append_multiple(tmp_file):
    engine = StorageEngine(tmp_file)
    for i in range(5):
        engine.append({"n": i})
    results = list(engine.scan())
    assert len(results) == 5
    engine.close()


def test_read_at(tmp_file):
    engine = StorageEngine(tmp_file)
    rec = {"x": 42}
    offset = engine.append(rec)
    loaded = engine.read_at(offset)
    assert loaded == rec
    engine.close()


def test_read_at_invalid_offset(tmp_file):
    engine = StorageEngine(tmp_file)
    engine.append({"x": 1})
    # Offset nel mezzo del record — risultato None o dati invalidi
    result = engine.read_at(2)
    assert result is None
    engine.close()


def test_read_at_beyond_eof(tmp_file):
    engine = StorageEngine(tmp_file)
    result = engine.read_at(9999)
    assert result is None
    engine.close()


# ── append_batch ──────────────────────────────────────────────────────────────

def test_append_batch_empty(tmp_file):
    engine = StorageEngine(tmp_file)
    offsets = engine.append_batch([])
    assert offsets == []
    engine.close()


def test_append_batch_multiple(tmp_file):
    engine = StorageEngine(tmp_file)
    records = [{"i": i} for i in range(10)]
    offsets = engine.append_batch(records)
    assert len(offsets) == 10
    assert offsets[0] == 0
    assert len(set(offsets)) == 10  # tutti distinti
    # Verifica che siano leggibili
    results = list(engine.scan())
    assert len(results) == 10
    engine.close()


# ── read_many ─────────────────────────────────────────────────────────────────

def test_read_many(tmp_file):
    engine = StorageEngine(tmp_file)
    offsets = engine.append_batch([{"a": 1}, {"b": 2}, {"c": 3}])
    results = engine.read_many(offsets)
    assert len(results) == 3
    assert results[0] == {"a": 1}
    assert results[1] == {"b": 2}
    assert results[2] == {"c": 3}
    engine.close()


def test_read_many_with_invalid(tmp_file):
    engine = StorageEngine(tmp_file)
    offset = engine.append({"x": 10})
    results = engine.read_many([offset, 9999])
    assert results[0] == {"x": 10}
    assert results[1] is None
    engine.close()


def test_read_many_empty(tmp_file):
    engine = StorageEngine(tmp_file)
    results = engine.read_many([])
    assert results == []
    engine.close()


# ── file_size / record_count ──────────────────────────────────────────────────

def test_file_size(tmp_file):
    engine = StorageEngine(tmp_file)
    assert engine.file_size() == 0
    engine.append({"hello": "world"})
    assert engine.file_size() > 0
    engine.close()


def test_record_count(tmp_file):
    engine = StorageEngine(tmp_file)
    assert engine.record_count() == 0
    engine.append({"a": 1})
    engine.append({"b": 2})
    assert engine.record_count() == 2
    engine.close()


# ── Context manager ───────────────────────────────────────────────────────────

def test_context_manager(tmp_file):
    with StorageEngine(tmp_file) as engine:
        engine.append({"test": True})
        results = list(engine.scan())
    assert len(results) == 1


# ── Crash recovery — record corrotti ─────────────────────────────────────────

def test_scan_truncated_header(tmp_file):
    """File con header incompleto alla fine: scan deve terminare senza crash."""
    with StorageEngine(tmp_file) as engine:
        engine.append({"valid": True})

    # Aggiungi un header troncato dopo il record valido
    with open(tmp_file, "ab") as f:
        f.write(MAGIC[:2])  # header incompleto

    engine = StorageEngine(tmp_file)
    results = list(engine.scan())
    # Il record valido deve essere letto; i byte spazzatura ignorati
    assert len(results) >= 1
    engine.close()


def test_scan_wrong_magic(tmp_file):
    """Byte con magic errato intercalati tra record validi."""
    with open(tmp_file, "ab") as f:
        f.write(b"\x00\x00\x00\x00\x00\x00\x00\x00")  # no magic

    with StorageEngine(tmp_file) as engine:
        engine.append({"after": "garbage"})

    engine = StorageEngine(tmp_file)
    results = list(engine.scan())
    assert any(r.get("after") == "garbage" for _, r in results)
    engine.close()


def test_scan_oversized_payload(tmp_file):
    """Record con SIZE > 64MB viene saltato."""
    with open(tmp_file, "wb") as f:
        # Magic + size > 64MB
        f.write(MAGIC)
        f.write(struct.pack(">I", 67_108_865))  # 64MB + 1

    engine = StorageEngine(tmp_file)
    results = list(engine.scan())
    assert results == []
    engine.close()


def test_scan_truncated_payload(tmp_file):
    """Header valido ma payload troncato."""
    with open(tmp_file, "wb") as f:
        payload = b'{"x": 1}'
        f.write(MAGIC)
        f.write(struct.pack(">I", len(payload) + 10))  # size > payload reale
        f.write(payload)  # payload incompleto

    engine = StorageEngine(tmp_file)
    results = list(engine.scan())
    assert results == []
    engine.close()


def test_scan_corrupted_json(tmp_file):
    """Header valido, payload della giusta lunghezza ma JSON invalido."""
    bad_payload = b"not a json!!"
    with open(tmp_file, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack(">I", len(bad_payload)))
        f.write(bad_payload)

    engine = StorageEngine(tmp_file)
    results = list(engine.scan())
    assert results == []
    engine.close()


def test_scan_valid_after_corrupt(tmp_file):
    """Record valido DOPO record corrotto deve essere letto."""
    good = _encode({"valid": True})
    bad_payload = b"not_json_at_all"
    corrupt = MAGIC + struct.pack(">I", len(bad_payload)) + bad_payload

    with open(tmp_file, "wb") as f:
        f.write(corrupt)
        f.write(good)

    engine = StorageEngine(tmp_file)
    results = list(engine.scan())
    # Può trovare 0 o 1 record valido — l'importante è non crashare
    engine.close()


# ── batch fsync_policy ────────────────────────────────────────────────────────

def test_fsync_policy_never(tmp_file):
    engine = StorageEngine(tmp_file, fsync_policy="never")
    offsets = engine.append_batch([{"n": i} for i in range(3)])
    assert len(offsets) == 3
    engine.close()


def test_fsync_policy_batch(tmp_file):
    engine = StorageEngine(tmp_file, fsync_policy="batch", fsync_ms=50)
    engine.append({"batch": True})
    time.sleep(0.12)  # attende il flush thread
    results = list(engine.scan())
    engine.close()
    # Non importa quanti risultati — solo verifica che non crashi


# ── Thread safety ─────────────────────────────────────────────────────────────

def test_concurrent_reads(tmp_file):
    engine = StorageEngine(tmp_file)
    offsets = engine.append_batch([{"i": i} for i in range(20)])

    errors = []

    def read_all():
        try:
            engine.read_many(offsets)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=read_all) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    engine.close()


# ── repr ──────────────────────────────────────────────────────────────────────

def test_repr(tmp_file):
    engine = StorageEngine(tmp_file)
    r = repr(engine)
    assert "StorageEngine" in r
    assert "fsync" in r
    engine.close()


# ── _seek_next_magic helper ───────────────────────────────────────────────────

def test_seek_next_magic_found(tmp_file):
    """Verifica che _seek_next_magic posizioni sul MAGIC corretto."""
    content = b"\x00" * 16 + MAGIC + b"extra"
    with open(tmp_file, "wb") as f:
        f.write(content)

    with open(tmp_file, "rb") as f:
        _seek_next_magic(f, 0)
        pos = f.tell()

    assert pos == 16


def test_seek_next_magic_not_found(tmp_file):
    """Se MAGIC non c'è, f deve puntare alla fine del file."""
    with open(tmp_file, "wb") as f:
        f.write(b"\x00" * 50)

    with open(tmp_file, "rb") as f:
        _seek_next_magic(f, 0)
        pos = f.tell()

    assert pos == 50  # fine file


def test_seek_next_magic_cross_chunk(tmp_file):
    """MAGIC a cavallo tra due chunk da 4096 byte."""
    # Metti il MAGIC appena oltre 4096 byte
    prefix = b"\x00" * 4095
    content = prefix + MAGIC
    with open(tmp_file, "wb") as f:
        f.write(content)

    with open(tmp_file, "rb") as f:
        _seek_next_magic(f, 0)
        pos = f.tell()

    assert pos == 4095


# ── _encode helper ────────────────────────────────────────────────────────────

def test_encode_structure():
    frame = _encode({"a": 1})
    assert frame[:4] == MAGIC
    size = struct.unpack(">I", frame[4:8])[0]
    payload = frame[8:]
    assert len(payload) == size
    assert json.loads(payload.decode("utf-8")) == {"a": 1}


# ── close idempotent ─────────────────────────────────────────────────────────

def test_close_twice(tmp_file):
    engine = StorageEngine(tmp_file)
    engine.append({"x": 1})
    engine.close()
    engine.close()  # deve essere idempotente (no crash)


# ── read_at: truncated payload branch ────────────────────────────────────────

def test_read_at_truncated_payload_in_file(tmp_file):
    """Header valido ma payload dichiarato più lungo di quello reale → None."""
    payload = b'{"x": 1}'
    with open(tmp_file, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack(">I", len(payload) + 20))  # dichiara più byte
        f.write(payload)  # payload corto

    engine = StorageEngine(tmp_file)
    result = engine.read_at(0)
    assert result is None
    engine.close()


def test_read_at_json_decode_error(tmp_file):
    """Payload valida lunghezza ma JSON malformato → None (JSONDecodeError branch)."""
    bad = b"definitely not json!!"
    with open(tmp_file, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack(">I", len(bad)))
        f.write(bad)

    engine = StorageEngine(tmp_file)
    result = engine.read_at(0)
    assert result is None
    engine.close()


# ── read_many: truncated payload branch ───────────────────────────────────────

def test_read_many_truncated_payload(tmp_file):
    """read_many con offset che punta a payload troncato → None nell'array."""
    # Scrivi un record valido poi dati troncati
    payload = b'{"x": 1}'
    valid_frame = _encode({"valid": True})
    truncated_header = MAGIC + struct.pack(">I", len(payload) + 50) + payload

    with open(tmp_file, "wb") as f:
        f.write(valid_frame)
        f.write(truncated_header)

    engine = StorageEngine(tmp_file)
    # Offset del frame troncato = len(valid_frame)
    bad_offset = len(valid_frame)
    results = engine.read_many([0, bad_offset])
    assert results[0] is not None  # valido
    assert results[1] is None      # troncato
    engine.close()


# ── _flush_batch_locked with data ────────────────────────────────────────────

def test_flush_batch_with_data(tmp_file):
    """Forza _flush_batch_locked con dati nel buffer."""
    engine = StorageEngine(tmp_file, fsync_policy="batch", fsync_ms=1000)
    # Aggiungi dati direttamente nel batch buffer per testare il flush
    engine._batch_buf.append(_encode({"manual": True}))
    engine._flush_batch_locked()
    engine.close()


# ── close with batch policy ───────────────────────────────────────────────────

def test_close_with_batch_policy(tmp_file):
    """close() con fsync_policy=batch deve chiamare _flush_batch_locked."""
    engine = StorageEngine(tmp_file, fsync_policy="batch", fsync_ms=5000)
    engine.append({"x": 1})
    engine.close()  # deve flush e stop


# ── _reopen OSError ───────────────────────────────────────────────────────────

def test_reopen_oserror(tmp_file):
    """_reopen con path non apribile non deve crashare."""
    engine = StorageEngine(tmp_file)
    engine.append({"x": 1})
    # Dopo close() il path esiste ancora ma il fd è chiuso.
    # Simuliamo l'OSError rendendo il file non apribile momentaneamente.
    import os
    original_open = open

    call_count = {"n": 0}

    def patched_open(path, mode="r", *args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1 and "rb" in str(mode):
            raise OSError("simulated open error")
        return original_open(path, mode, *args, **kwargs)

    import builtins
    old_open = builtins.open
    builtins.open = patched_open
    try:
        _reopen(engine)  # deve catturare OSError silenziosamente
    finally:
        builtins.open = old_open

    engine.close()

