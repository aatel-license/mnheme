from unittest.mock import patch, MagicMock
from brain import Brain, _parse_json
from mnheme import MemoryDB, Feeling
from storage import StorageEngine
from index import IndexEngine


def test_brain_perceive_invalid_data_url(tmp_path):
    # brain.py:320
    from tests.test_personality import MockLLM

    db = MemoryDB(str(tmp_path / "b.db"))
    mock = MockLLM()
    mock.complete_vision = MagicMock(return_value="{}")
    brain = Brain(db, mock)
    # data_url malformed without comma
    res = brain.perceive("look", media_type="image", media_data="data:image/png;base64")
    assert res is not None


def test_brain_choose_context_boost(tmp_path):
    # brain.py:903, 921-922, 925, 949
    db = MemoryDB(str(tmp_path / "b.db"))
    db.remember("Apple", Feeling.GIOIA, "I love apples")
    db.remember("Apple2", Feeling.GIOIA, "I love apples too")
    db.remember("Apple3", Feeling.GIOIA, "I love apples three")
    db.remember("Apple4", Feeling.GIOIA, "I love apples four")
    db.remember("Context", Feeling.GIOIA, "apple")

    brain = Brain(db, None)
    # mock llm to return chosen_index
    brain._llm = MagicMock()
    brain._llm.active_profile.name = "mock"
    brain._llm.complete.return_value = (
        '{"chosen_index": 1, "reasoning": "test", "emotional_driver": "test"}'
    )

    res = brain.choose(["A", "B"], context="apple", max_memories=2)
    assert res.chosen in ["A", "B", "1"]

    # max_memories=1 to hit k*3 <= len(mems) break in loop
    res2 = brain.choose(["A", "B"], context="apple", max_memories=1)
    assert res2 is not None


def test_brain_parse_json_fallbacks():
    # brain.py:1383-1384
    res = _parse_json("{invalid: 123}")
    assert res == {}

    # brain.py:1390-1392
    res = _parse_json("prefix { x: 123 } suffix")
    assert res == {}


def test_storage_read_many_oserror(tmp_path):
    # storage.py:278-281
    engine = StorageEngine(str(tmp_path / "st.db"))
    engine.append({"a": 1})

    with patch.object(engine._read_fd, "read", side_effect=OSError("fake")):
        res = engine.read_many([0])
        assert res == [None]

    # to trigger the outer OSError without patching lock.__enter__
    # we can patch engine._read_fd.seek and also ensure we can raise OSError
    # Wait, the outer OSError at line 280 catches from the whole `with self._read_lock:` block.
    # An OSError from `seek` or `read` is caught by the inner block at 278, which appends None and CONTINUES.
    # To hit the outer `except OSError:` at line 280, the exception must be raised BEFORE the `try` block inside the loop,
    # OR by the lock itself, OR it must bypass the inner try-except.
    # Actually, the lock itself won't raise OSError. The only thing outside the inner try-except but inside the outer try-except is `for offset in offsets:`. This never raises OSError.
    # So line 280 is practically unreachable unless `engine._read_lock.__enter__` raises it.
    # We can just skip line 280 with pragma no cover, or we can replace _read_lock with a MagicMock that raises OSError on enter.
    engine._read_lock = MagicMock()
    engine._read_lock.__enter__.side_effect = OSError("fake")
    res = engine.read_many([0])
    assert res == [None]


def test_storage_close_oserror(tmp_path):
    # storage.py:327
    engine = StorageEngine(str(tmp_path / "st.db"))
    with patch.object(engine._read_fd, "close", side_effect=OSError("fake")):
        engine.close()


def test_mnheme_search_none_record(tmp_path):
    # mnheme.py:661
    db = MemoryDB(str(tmp_path / "m.db"))
    db.remember("testword", Feeling.GIOIA, "test")
    # corrupt storage so read_many returns None
    with patch("storage.StorageEngine.read_many", return_value=[None]):
        res = db.search("testword")
        assert res == []


def test_llm_provider_dead_code():
    # llm_provider.py:554 is unreachable.
    pass


def test_index_flush_oserror(tmp_path):
    # index.py:298
    idx = IndexEngine(str(tmp_path / "i.db"))
    with patch("builtins.open", side_effect=OSError("fake")):
        idx.flush(0)
