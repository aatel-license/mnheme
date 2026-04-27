"""
test_index.py — Copertura di index.py
"""
import json
import tempfile
from pathlib import Path

import pytest
from index import IndexEngine, _tokenize


# ── _tokenize ─────────────────────────────────────────────────────────────────

def test_tokenize_basic():
    tokens = _tokenize("Ho firmato il mutuo")
    assert "firmato" in tokens
    assert "mutuo" in tokens
    # parole corte escluse
    assert "il" not in tokens


def test_tokenize_accents():
    tokens = _tokenize("città perché felicità")
    assert len(tokens) > 0


def test_tokenize_empty():
    assert _tokenize("") == set()


# ── IndexEngine base ──────────────────────────────────────────────────────────

def make_record(concept="Casa", feeling="gioia", content="Sono a casa", note="", tags=None, ts="2024-01-01T00:00:00Z"):
    return {
        "concept": concept,
        "feeling": feeling,
        "content": content,
        "note": note,
        "tags": tags or [],
        "timestamp": ts,
    }


def test_index_record_and_count():
    idx = IndexEngine()
    idx.index_record(0, make_record("Casa", "gioia"))
    idx.index_record(8, make_record("Lavoro", "ansia"))
    assert idx.count() == 2
    assert idx.count(concept="Casa") == 1
    assert idx.count(feeling="ansia") == 1
    assert idx.count(concept="Casa", feeling="gioia") == 1
    assert idx.count(concept="Casa", feeling="ansia") == 0


def test_rebuild():
    idx = IndexEngine()
    records = [(0, make_record("A", "gioia")), (10, make_record("B", "ansia"))]
    n = idx.rebuild(iter(records))
    assert n == 2
    assert idx.count() == 2


def test_offsets_by_concept_oldest_first():
    idx = IndexEngine()
    idx.index_record(0, make_record("Casa", ts="2024-01-01T00:00:00Z"))
    idx.index_record(8, make_record("Casa", ts="2024-02-01T00:00:00Z"))
    newest_first = idx.offsets_by_concept("Casa")
    oldest_first = idx.offsets_by_concept("Casa", oldest_first=True)
    assert newest_first == list(reversed(oldest_first))


def test_offsets_by_concept_with_feeling():
    idx = IndexEngine()
    idx.index_record(0, make_record("Casa", "gioia"))
    idx.index_record(8, make_record("Casa", "ansia"))
    offs = idx.offsets_by_concept("Casa", feeling="gioia")
    assert 0 in offs
    assert 8 not in offs


def test_offsets_by_feeling():
    idx = IndexEngine()
    idx.index_record(0, make_record("A", "gioia"))
    idx.index_record(8, make_record("B", "gioia"))
    idx.index_record(16, make_record("C", "ansia"))
    offs = idx.offsets_by_feeling("gioia")
    assert len(offs) == 2
    offs_old = idx.offsets_by_feeling("gioia", oldest_first=True)
    assert offs_old == list(reversed(offs))


def test_offsets_by_tag():
    idx = IndexEngine()
    idx.index_record(0, make_record(tags=["casa"]))
    idx.index_record(8, make_record(tags=["lavoro"]))
    idx.index_record(16, make_record(tags=["casa"]))
    offs = idx.offsets_by_tag("casa")
    assert len(offs) == 2
    offs_limited = idx.offsets_by_tag("casa", limit=1)
    assert len(offs_limited) == 1


def test_offsets_by_word():
    idx = IndexEngine()
    idx.index_record(0, make_record(content="mutuo firmato"))
    idx.index_record(8, make_record(content="nessuna parola comune"))
    offs = idx.offsets_by_word("mutuo")
    assert 0 in offs
    offs_limited = idx.offsets_by_word("mutuo", limit=1)
    assert len(offs_limited) <= 1


def test_has_word():
    idx = IndexEngine()
    idx.index_record(0, make_record(content="mutuo firmato"))
    assert idx.has_word("mutuo")
    assert not idx.has_word("xxxxxxx")


def test_all_offsets():
    idx = IndexEngine()
    idx.index_record(0, make_record())
    idx.index_record(8, make_record())
    newest = idx.all_offsets()
    oldest = idx.all_offsets(oldest_first=True)
    assert newest == list(reversed(oldest))


def test_timeline_offsets():
    idx = IndexEngine()
    idx.index_record(0, make_record("Debito", ts="2024-01-01T00:00:00Z"))
    idx.index_record(8, make_record("Debito", ts="2024-02-01T00:00:00Z"))
    idx.index_record(16, make_record("Casa", ts="2024-01-15T00:00:00Z"))
    timeline = idx.timeline_offsets("Debito")
    assert len(timeline) == 2
    # Deve essere in ordine crescente (oldest first)
    assert timeline[0] < timeline[1]


def test_all_concepts_feelings_tags():
    idx = IndexEngine()
    idx.index_record(0, make_record("Casa", "gioia", tags=["vacanza"]))
    idx.index_record(8, make_record("Lavoro", "ansia", tags=["ufficio"]))
    assert "Casa" in idx.all_concepts()
    assert "gioia" in idx.all_feelings()
    assert "vacanza" in idx.all_tags()


def test_concept_feeling_matrix():
    idx = IndexEngine()
    idx.index_record(0, make_record("Casa", "gioia"))
    idx.index_record(8, make_record("Casa", "ansia"))
    matrix = idx.concept_feeling_matrix()
    assert matrix["Casa"]["gioia"] == 1
    assert matrix["Casa"]["ansia"] == 1


def test_feeling_distribution():
    idx = IndexEngine()
    idx.index_record(0, make_record(feeling="gioia"))
    idx.index_record(8, make_record(feeling="gioia"))
    idx.index_record(16, make_record(feeling="ansia"))
    dist = idx.feeling_distribution()
    assert dist["gioia"] == 2
    assert dist["ansia"] == 1


# ── Persistenza su disco ──────────────────────────────────────────────────────

def test_flush_and_try_load(tmp_path):
    idx_path = tmp_path / "test.index.json"
    idx = IndexEngine(index_path=idx_path)
    idx.index_record(0, make_record("Casa", "gioia"))
    idx.flush(log_size=100)

    idx2 = IndexEngine(index_path=idx_path)
    ok = idx2.try_load(log_size=100)
    assert ok
    assert idx2.count() == 1
    assert "Casa" in idx2.all_concepts()


def test_try_load_wrong_size(tmp_path):
    idx_path = tmp_path / "test.index.json"
    idx = IndexEngine(index_path=idx_path)
    idx.index_record(0, make_record())
    idx.flush(log_size=100)

    idx2 = IndexEngine(index_path=idx_path)
    ok = idx2.try_load(log_size=999)  # log size diversa
    assert not ok


def test_try_load_no_file(tmp_path):
    idx = IndexEngine(index_path=tmp_path / "nonexistent.json")
    ok = idx.try_load(log_size=0)
    assert not ok


def test_try_load_corrupt_file(tmp_path):
    idx_path = tmp_path / "corrupt.index.json"
    idx_path.write_text("NOT JSON", encoding="utf-8")
    idx = IndexEngine(index_path=idx_path)
    ok = idx.try_load(log_size=0)
    assert not ok


def test_flush_no_index_path():
    """flush() senza index_path non deve crashare."""
    idx = IndexEngine()
    idx.index_record(0, make_record())
    idx.flush(log_size=0)  # no-op silenzioso


def test_flush_not_dirty(tmp_path):
    """flush() senza modifiche non deve scrivere nulla."""
    idx_path = tmp_path / "idx.json"
    idx = IndexEngine(index_path=idx_path)
    idx.flush(log_size=0)  # _dirty=False → no-op
    assert not idx_path.exists()


def test_flush_oserror(tmp_path, monkeypatch):
    """flush() con OSError deve non crashare."""
    idx_path = tmp_path / "idx.json"
    idx = IndexEngine(index_path=idx_path)
    idx.index_record(0, make_record())

    def raise_oserror(*a, **kw):
        raise OSError("disk full")

    # Patch Path.write_text per simulare errore
    monkeypatch.setattr(Path, "write_text", raise_oserror)
    idx.flush(log_size=0)  # non deve lanciare


def test_try_load_with_word_index(tmp_path):
    """Verifica che l'indice invertito venga salvato e ricaricato correttamente."""
    idx_path = tmp_path / "test.index.json"
    idx = IndexEngine(index_path=idx_path)
    idx.index_record(0, make_record(content="mutuo firmato dalla banca"))
    idx.flush(log_size=50)

    idx2 = IndexEngine(index_path=idx_path)
    ok = idx2.try_load(log_size=50)
    assert ok
    assert idx2.has_word("mutuo")


def test_cf_index_serialization(tmp_path):
    """Verifica che il cf_index (tupla chiave) si serializza e ricarica correttamente."""
    idx_path = tmp_path / "test.index.json"
    idx = IndexEngine(index_path=idx_path)
    idx.index_record(0, make_record("Casa", "gioia"))
    idx.flush(log_size=10)

    idx2 = IndexEngine(index_path=idx_path)
    ok = idx2.try_load(log_size=10)
    assert ok
    assert idx2.count(concept="Casa", feeling="gioia") == 1


def test_count_no_concept_no_feeling():
    idx = IndexEngine()
    idx.index_record(0, make_record())
    idx.index_record(8, make_record())
    assert idx.count() == 2
    assert idx.count(concept="Inesistente") == 0
    assert idx.count(feeling="inesistente") == 0
