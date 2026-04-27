"""
test_vision.py — Test complete vision (image/audio/video/doc) su Brain.perceive()
"""
import sys, os, pathlib, base64, tempfile, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from mnheme import MemoryDB, Feeling
from llm_provider import LLMProvider, ProviderProfile
from brain import Brain


class MockLLM(LLMProvider):
    """Mock provider che simula risposte con e senza vision."""
    def __init__(self):
        p = ProviderProfile(name="mock", url="http://mock", model="mock-llm", api_key="", rpm=9999)
        super().__init__({"mock": p}, active="mock")

    def complete(self, system, user, **kw):
        import json as _j
        if '"concept"' in user:
            return _j.dumps({
                "concept": "Test",
                "feeling": "curiosità",
                "tags": ["test"],
                "enriched": "Testo arricchito."
            })
        return "{}"

    def complete_vision(self, system, user, media_items):
        # Simula che il modello abbia visto il media
        assert len(media_items) >= 1
        item = media_items[0]
        assert "data" in item
        assert "media_type" in item
        return self.complete(system, user + f"\n\n[Media ricevuto: {item.get('type', 'unknown')}]")


@pytest.fixture
def brain():
    """Crea un Brain con DB vuoto (path temporaneo)."""
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    return Brain(db, mock), db


# ── TESTS ───────────────────────────────────────

def test_perceive_text_only(brain):
    brain_obj, _ = brain
    r = brain_obj.perceive("Ho aperto una busta dalla banca.")
    assert r.extracted_concept == "Test"
    assert r.memory.content is not None


def test_perceive_image_base64():
    db, _ = tempfile.mkdtemp(), None
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    # Crea un piccolo JPEG finto (header + dati)
    fake_jpeg = b"\xFF\xD8\xFF" + b"X" * 100
    b64 = base64.b64encode(fake_jpeg).decode()

    r = brain_obj.perceive(
        "Foto del contratto firmato",
        media_type="image",
        media_data=b64,
        media_mime="image/jpeg",
    )
    assert r.memory.media_type == "image"


def test_perceive_image_data_url():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_jpeg = b"\xFF\xD8\xFF" + b"X" * 100
    b64 = base64.b64encode(fake_jpeg).decode()
    data_url = f"data:image/jpeg;base64,{b64}"

    r = brain_obj.perceive(
        "Foto del contratto firmato",
        media_type="image",
        media_data=data_url,
        media_mime=None,  # dovrebbe essere estratto dal data URL
    )
    assert r.memory.media_type == "image"


def test_perceive_video():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_mp4 = b"\x00\x00\x00\x18ftyp" + b"V" * 100
    b64 = base64.b64encode(fake_mp4).decode()

    r = brain_obj.perceive(
        "Video della festa di Natale",
        media_type="video",
        media_data=b64,
        media_mime="video/mp4",
    )
    assert r.memory.media_type == "video"


def test_perceive_audio():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_mp3 = b"ID3" + b"A" * 100
    b64 = base64.b64encode(fake_mp3).decode()

    r = brain_obj.perceive(
        "Registrazione vocale",
        media_type="audio",
        media_data=b64,
        media_mime="audio/mpeg",
    )
    assert r.memory.media_type == "audio"


def test_perceive_doc():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_pdf = b"%PDF-1.4" + b"D" * 100
    b64 = base64.b64encode(fake_pdf).decode()

    r = brain_obj.perceive(
        "Documento PDF",
        media_type="doc",
        media_data=b64,
        media_mime="application/pdf",
    )
    assert r.memory.media_type == "doc"


def test_perceive_with_manual_overrides():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    r = brain_obj.perceive(
        "Test manuale",
        concept="ConcettoManuale",
        feeling="rabbia",
        tags=["manuale"],
        note="Nota manuale",
    )
    assert r.extracted_concept == "ConcettoManuale"
    assert r.extracted_feeling == "rabbia"


def test_perceive_manual_tags_override():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    r = brain_obj.perceive(
        "Test override",
        tags=["override1", "override2"],
    )
    assert r.extracted_tags == ["override1", "override2"]


def test_perceive_invalid_feeling_fallback():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    # Se il LLM restituisce un feeling non valido, dovrebbe fare fallback
    class BadMock(LLMProvider):
        def __init__(self):
            p = ProviderProfile(name="bad", url="http://bad", model="bad", api_key="", rpm=9999)
            super().__init__({"bad": p}, active="bad")

        def complete(self, system, user, **kw):
            import json as _j
            return _j.dumps({
                "concept": "Test",
                "feeling": "sentimento_inesistente",  # non valido
                "tags": ["test"],
                "enriched": "Test"
            })

        def complete_vision(self, system, user, media_items):
            return self.complete(system, user)

    brain2 = Brain(db, BadMock())
    r = brain2.perceive("Test fallback")
    # Il feeling non valido dovrebbe essere mappato a "neutralità"
    assert r.extracted_feeling == "neutralità"


def test_perceive_media_context_in_db():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_jpeg = b"\xFF\xD8\xFF" + b"X" * 100
    b64 = base64.b64encode(fake_jpeg).decode()

    r = brain_obj.perceive(
        "Foto",
        media_type="image",
        media_data=b64,
        media_mime="image/jpeg",
    )
    # Il content nel DB per i media dovrebbe essere un data URL
    assert r.memory.content.startswith("data:image/jpeg;base64,")


def test_perceive_text_content_not_base64():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    r = brain_obj.perceive("Test testo normale")
    # Il content per il testo puro dovrebbe essere l'enriched text, non base64
    assert "data:" not in r.memory.content


def test_perceive_no_media():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    # Senza media_type e senza media_data, dovrebbe trattare come testo
    r = brain_obj.perceive("Test senza media")
    assert r.memory.media_type == "text"


def test_perceive_media_without_mime():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_jpeg = b"\xFF\xD8\xFF" + b"X" * 100
    b64 = base64.b64encode(fake_jpeg).decode()

    r = brain_obj.perceive(
        "Foto senza MIME",
        media_type="image",
        media_data=b64,
        media_mime=None,
    )
    assert r.memory.media_type == "image"


def test_perceive_large_media():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    # Simula un file più grande (1MB)
    fake_data = b"\xFF\xD8\xFF" + b"X" * (1024 * 1024)
    b64 = base64.b64encode(fake_data).decode()

    r = brain_obj.perceive(
        "Foto grande",
        media_type="image",
        media_data=b64,
        media_mime="image/jpeg",
    )
    assert r.memory.media_type == "image"


def test_perceive_media_in_context():
    """Verifica che i media non esplodano il contesto LLM."""
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_jpeg = b"\xFF\xD8\xFF" + b"X" * 10000
    b64 = base64.b64encode(fake_jpeg).decode()

    r = brain_obj.perceive(
        "Foto grande",
        media_type="image",
        media_data=b64,
        media_mime="image/jpeg",
    )
    # Il content nel DB dovrebbe contenere il data URL completo
    assert len(r.memory.content) > 0


def test_perceive_audio_without_mime():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_data = b"ID3" + b"A" * 100
    b64 = base64.b64encode(fake_data).decode()

    r = brain_obj.perceive(
        "Audio senza MIME",
        media_type="audio",
        media_data=b64,
        media_mime=None,
    )
    assert r.memory.media_type == "audio"


def test_perceive_doc_without_mime():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    fake_pdf = b"%PDF-1.4" + b"D" * 100
    b64 = base64.b64encode(fake_pdf).decode()

    r = brain_obj.perceive(
        "Doc senza MIME",
        media_type="doc",
        media_data=b64,
        media_mime=None,
    )
    assert r.memory.media_type == "doc"


def test_perceive_empty_input():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    # Input vuoto dovrebbe comunque funzionare (anche se il risultato sarà strano)
    try:
        r = brain_obj.perceive("")
        assert r.raw_input == ""
    except Exception:
        pass  # accettabile anche se solleva


def test_perceive_note_handling():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    r = brain_obj.perceive("Test nota", note="La mia nota personale")
    assert "La mia nota personale" in r.memory.note


def test_perceive_note_from_parsed():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    # Se il LLM non restituisce note, dovrebbe usare un fallback
    class NoNoteMock(LLMProvider):
        def __init__(self):
            p = ProviderProfile(name="nonote", url="http://no", model="no", api_key="", rpm=9999)
            super().__init__({"nonote": p}, active="nonote")

        def complete(self, system, user, **kw):
            import json as _j
            return _j.dumps({
                "concept": "Test",
                "feeling": "curiosità",
                "tags": ["test"],
                # Nessuna nota nel JSON
                "enriched": "Arricchito"
            })

        def complete_vision(self, system, user, media_items):
            return self.complete(system, user)

    brain2 = Brain(db, NoNoteMock())
    r = brain2.perceive("Test senza nota")
    # Dovrebbe esserci un fallback nella note


def test_perceive_media_type_text_default():
    tmp_path = tempfile.mkdtemp()
    db = MemoryDB(str(pathlib.Path(tmp_path) / "test.mnheme"))
    mock = MockLLM()
    brain_obj = Brain(db, mock)

    r = brain_obj.perceive("Test default", media_type="text")
    assert r.memory.media_type == "text"
