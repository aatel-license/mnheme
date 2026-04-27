import json
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock

import pytest

from brain import Brain, _parse_json
from mnheme import MemoryDB, Feeling
from storage import StorageEngine
from llm_provider import ProviderProfile
from index import IndexEngine

def test_brain_perceive_invalid_data_url(tmp_path):
    # brain.py:320
    db = MemoryDB(str(tmp_path / "b.db"))
    brain = Brain(db, None)
    # data_url malformed without comma
    res = brain.perceive("look", is_media=True, media_data="data:image/png;base64")
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
    
    # max_memories=2, context="apple"
    res = brain._sample_memories(max_memories=2, context="apple")
    assert len(res) <= 2
    
    # to hit line 903: k > len(indices)
    res = brain._sample_memories(max_memories=10)

def test_brain_parse_json_fallbacks():
    # brain.py:1383-1384
    # malformed match.group() inner JSONDecodeError
    # text with { but invalid inside
    res = _parse_json("{invalid: 123}")
    assert res == {}

    # brain.py:1390-1392
    res = _parse_json("prefix { x: 123 } suffix")
    assert res == {}

def test_storage_read_many_oserror(tmp_path):
    # storage.py:278-281
    engine = StorageEngine(str(tmp_path / "st.db"))
    engine.append({"a": 1})
    
    with patch("storage.StorageEngine._read_fd") as m_fd:
        # trigger inner OSError
        m_fd.read.side_effect = OSError("fake")
        res = engine.read_many([0])
        assert res == [None]

    with patch("storage.StorageEngine._read_lock") as m_lock:
        # trigger outer OSError
        m_lock.__enter__.side_effect = OSError("fake")
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
    db.remember("A", Feeling.GIOIA, "test")
    # corrupt storage so read_many returns None
    with patch("storage.StorageEngine.read_many", return_value=[None]):
        res = db.search("a")
        assert res == []

def test_llm_provider_from_dict_keyerror():
    # llm_provider.py:554
    # delete mandatory key 'name' to trigger KeyError
    d = {"provider": "openai", "model": "gpt-4"}
    res = ProviderProfile.from_dict(d)
    assert res is None

def test_index_flush_oserror(tmp_path):
    # index.py:298
    idx = IndexEngine(str(tmp_path / "i.db"))
    with patch("builtins.open", side_effect=OSError("fake")):
        idx.flush()
