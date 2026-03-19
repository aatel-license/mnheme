"""
integration_test.py
===================
Test di integrazione completo per MNHEME.
Da eseguire localmente: python integration_test.py

Copre:
  - MemoryDB: write, read, search, stats, export/import
  - StorageEngine: persistenza fisica, crash recovery
  - IndexEngine: rebuild da log
  - FsProbe: detection filesystem
  - FileStore: store bytes, store file, get, dedup
  - LLMProvider: discovery .env, rate limiter, multi-provider
  - Brain: perceive, ask, reflect, dream, introspect, summarize (mock LLM)
  - API REST: endpoints principali (se fastapi installato)
  - Start scripts: verifica esistenza e sintassi
"""

import sys
import os
import json
import shutil
import tempfile
import time
import pathlib
import threading
import traceback

# Aggiungi la directory del progetto al path
PROJECT_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

PASS  = "\033[0;32m  PASS\033[0m"
FAIL  = "\033[0;31m  FAIL\033[0m"
SKIP  = "\033[0;33m  SKIP\033[0m"
SEP   = "─" * 70
BOLD  = "\033[1m"
NC    = "\033[0m"

results = {"pass": 0, "fail": 0, "skip": 0}


def section(name):
    print(f"\n{SEP}\n{BOLD}  {name}{NC}\n{SEP}")


def test(name, fn):
    try:
        fn()
        print(f"{PASS}  {name}")
        results["pass"] += 1
    except Exception as e:
        print(f"{FAIL}  {name}")
        print(f"         {type(e).__name__}: {e}")
        if "--verbose" in sys.argv:
            traceback.print_exc()
        results["fail"] += 1


def skip(name, reason=""):
    print(f"{SKIP}  {name}  ({reason})")
    results["skip"] += 1


# Temp dir per tutti i test di file
TMP = pathlib.Path(tempfile.mkdtemp(prefix="mnheme_itest_"))


def cleanup():
    shutil.rmtree(TMP, ignore_errors=True)


# ─────────────────────────────────────────────
# 1. MEMORYDB
# ─────────────────────────────────────────────

section("1 · MemoryDB — core")

from mnheme import MemoryDB, Feeling, MediaType, Memory

DB_PATH = TMP / "test.mnheme"


def t_remember():
    db = MemoryDB(DB_PATH)
    m = db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.", tags=["casa"])
    assert m.concept == "Debito"
    assert m.feeling == "ansia"
    assert m.memory_id and len(m.memory_id) == 36
    assert m.checksum  # SHA-256 presente


def t_immutability():
    db = MemoryDB(DB_PATH)
    m = db.remember("Test", Feeling.CURIOSITA, "contenuto")
    try:
        m.concept = "Modifica"
        raise AssertionError("Doveva sollevare FrozenInstanceError")
    except Exception as e:
        assert "frozen" in type(e).__name__.lower() or "FrozenInstance" in type(e).__name__


def t_recall_concept():
    db = MemoryDB(DB_PATH)
    mems = db.recall("Debito")
    assert len(mems) >= 1
    assert all(m.concept == "Debito" for m in mems)


def t_recall_feeling():
    db = MemoryDB(DB_PATH)
    mems = db.recall_by_feeling(Feeling.ANSIA)
    assert len(mems) >= 1
    assert all(m.feeling == "ansia" for m in mems)


def t_recall_filter():
    db = MemoryDB(DB_PATH)
    mems = db.recall("Debito", feeling=Feeling.ANSIA)
    assert all(m.concept == "Debito" and m.feeling == "ansia" for m in mems)


def t_recall_limit():
    db = MemoryDB(DB_PATH)
    mems = db.recall_all(limit=2)
    assert len(mems) <= 2


def t_recall_oldest_first():
    db = MemoryDB(DB_PATH)
    mems = db.recall("Debito", oldest_first=True)
    if len(mems) > 1:
        assert mems[0].timestamp <= mems[-1].timestamp


def t_recall_by_tag():
    db = MemoryDB(DB_PATH)
    mems = db.recall_by_tag("casa")
    assert len(mems) >= 1


def t_search():
    db = MemoryDB(DB_PATH)
    results = db.search("mutuo")
    assert len(results) >= 1
    # search con limit
    limited = db.search("a", limit=2)
    assert len(limited) <= 2


def t_count():
    db = MemoryDB(DB_PATH)
    total = db.count()
    by_c  = db.count(concept="Debito")
    by_f  = db.count(feeling=Feeling.ANSIA)
    assert total >= by_c >= 0
    assert total >= by_f >= 0


def t_list_concepts():
    db = MemoryDB(DB_PATH)
    concepts = db.list_concepts()
    assert isinstance(concepts, list)
    assert any(c["concept"] == "Debito" for c in concepts)
    for c in concepts:
        assert "concept" in c and "total" in c and "feelings" in c


def t_list_feelings():
    db = MemoryDB(DB_PATH)
    feelings = db.list_feelings()
    assert isinstance(feelings, list)
    assert len(feelings) > 0


def t_concept_timeline():
    db = MemoryDB(DB_PATH)
    timeline = db.concept_timeline("Debito")
    assert isinstance(timeline, list)
    for entry in timeline:
        assert "timestamp" in entry and "feeling" in entry


def t_feeling_distribution():
    db = MemoryDB(DB_PATH)
    dist = db.feeling_distribution()
    assert isinstance(dist, dict)
    assert "ansia" in dist


def t_all_feelings_valid():
    db = MemoryDB(DB_PATH)
    for f in Feeling:
        m = db.remember("TestFeelings", f, f"test {f.value}")
        assert m.feeling == f.value


def t_all_mediatypes():
    db = MemoryDB(DB_PATH)
    for mt in MediaType:
        m = db.remember("TestMedia", Feeling.CURIOSITA, f"test {mt.value}",
                         media_type=mt)
        assert m.media_type == mt.value


def t_invalid_feeling():
    db = MemoryDB(DB_PATH)
    try:
        db.remember("Test", "sentimento_inesistente_xyz", "contenuto")
        raise AssertionError("Doveva sollevare un errore")
    except Exception as e:
        assert "sentimento_inesistente_xyz" in str(e).lower() or "valido" in str(e).lower() or "invalid" in str(e).lower()


def t_export_import():
    db = MemoryDB(DB_PATH)
    export_path = TMP / "export_test.json"
    json_str = db.export_json(str(export_path), concept="Debito")
    parsed = json.loads(json_str)
    assert "memories" in parsed and "exported_at" in parsed
    assert len(parsed["memories"]) >= 1
    # Import in nuovo db
    db2 = MemoryDB(TMP / "import_test.mnheme")
    n = db2.import_json(str(export_path))
    assert n >= 1
    # Re-import: non duplica
    n2 = db2.import_json(str(export_path))
    assert n2 == 0


test("remember() crea un Memory corretto",          t_remember)
test("Memory è frozen=True (immutabile)",            t_immutability)
test("recall(concept) filtra correttamente",         t_recall_concept)
test("recall_by_feeling() filtra correttamente",     t_recall_feeling)
test("recall(concept, feeling=...) combo",           t_recall_filter)
test("recall_all(limit=N) rispetta il limite",       t_recall_limit)
test("recall(oldest_first=True) ordine ascendente",  t_recall_oldest_first)
test("recall_by_tag() trova per tag",                t_recall_by_tag)
test("search() full-text + limit",                   t_search)
test("count() totale / per concept / per feeling",   t_count)
test("list_concepts() struttura corretta",           t_list_concepts)
test("list_feelings() non vuoto",                    t_list_feelings)
test("concept_timeline() struttura corretta",        t_concept_timeline)
test("feeling_distribution() dizionario",            t_feeling_distribution)
test("tutti i 15 Feeling validi",                    t_all_feelings_valid)
test("tutti i 5 MediaType validi",                   t_all_mediatypes)
test("feeling non valido → errore chiaro",           t_invalid_feeling)
test("export_json + import_json + dedup",            t_export_import)

# ─────────────────────────────────────────────
# 2. STORAGE ENGINE
# ─────────────────────────────────────────────

section("2 · StorageEngine — file fisico")

from storage import StorageEngine, MAGIC
import struct


def t_magic_bytes():
    p = TMP / "magic_test.mnheme"
    s = StorageEngine(p)
    s.append({"test": "hello"})
    raw = p.read_bytes()
    assert raw[:4] == MAGIC, f"Magic errato: {raw[:4].hex()}"


def t_append_and_scan():
    p = TMP / "scan_test.mnheme"
    s = StorageEngine(p)
    s.append({"id": 1, "value": "alpha"})
    s.append({"id": 2, "value": "beta"})
    records = list(s.scan())
    assert len(records) == 2
    assert records[0][1]["value"] == "alpha"
    assert records[1][1]["value"] == "beta"


def t_read_at():
    p = TMP / "read_at_test.mnheme"
    s = StorageEngine(p)
    off1 = s.append({"x": 1})
    off2 = s.append({"x": 2})
    r1 = s.read_at(off1)
    r2 = s.read_at(off2)
    assert r1["x"] == 1
    assert r2["x"] == 2


def t_persistence_reload():
    p = TMP / "persist_test.mnheme"
    s1 = StorageEngine(p)
    s1.append({"msg": "persistito"})
    s2 = StorageEngine(p)                    # nuova istanza, stesso file
    records = list(s2.scan())
    assert len(records) == 1
    assert records[0][1]["msg"] == "persistito"


def t_truncated_record_skipped():
    p = TMP / "truncated_test.mnheme"
    s = StorageEngine(p)
    s.append({"good": True})
    # Scrivi un frame corrotto in fondo
    with open(p, "ab") as f:
        f.write(MAGIC + struct.pack(">I", 9999))   # size dichiarato >> bytes disponibili
    s2 = StorageEngine(p)
    records = list(s2.scan())
    assert len(records) == 1  # il record troncato è stato saltato


def t_file_size():
    p = TMP / "size_test.mnheme"
    s = StorageEngine(p)
    before = s.file_size()
    s.append({"payload": "x" * 100})
    after = s.file_size()
    assert after > before


test("MAGIC bytes corretti nel file",             t_magic_bytes)
test("append + scan restituisce i record",        t_append_and_scan)
test("read_at(offset) accesso diretto",           t_read_at)
test("persistenza su disco e reload",             t_persistence_reload)
test("record troncato saltato silenziosamente",   t_truncated_record_skipped)
test("file_size() cresce dopo append",            t_file_size)

# ─────────────────────────────────────────────
# 3. INDEX ENGINE
# ─────────────────────────────────────────────

section("3 · IndexEngine — indici RAM")

from index import IndexEngine


def t_index_rebuild():
    p = TMP / "idx_rebuild.mnheme"
    db = MemoryDB(p)
    db.remember("A", Feeling.GIOIA,    "contenuto A", tags=["x"])
    db.remember("B", Feeling.TRISTEZZA,"contenuto B", tags=["y"])
    db.remember("A", Feeling.ANSIA,    "contenuto A2",tags=["x"])
    # Riapri: rebuild automatico
    db2 = MemoryDB(p)
    assert db2.count() == 3
    assert db2.count(concept="A") == 2
    assert db2.count(concept="B") == 1


def t_index_concept_feeling():
    p = TMP / "idx_cf.mnheme"
    db = MemoryDB(p)
    db.remember("X", Feeling.AMORE,    "amore")
    db.remember("X", Feeling.AMORE,    "amore 2")
    db.remember("X", Feeling.PAURA,    "paura")
    assert db.count(concept="X", feeling=Feeling.AMORE) == 2
    assert db.count(concept="X", feeling=Feeling.PAURA) == 1


def t_index_tags():
    p = TMP / "idx_tags.mnheme"
    db = MemoryDB(p)
    db.remember("T", Feeling.CURIOSITA, "c1", tags=["alpha", "beta"])
    db.remember("T", Feeling.CURIOSITA, "c2", tags=["beta", "gamma"])
    by_alpha = db.recall_by_tag("alpha")
    by_beta  = db.recall_by_tag("beta")
    assert len(by_alpha) == 1
    assert len(by_beta)  == 2


def t_index_timeline_order():
    p = TMP / "idx_timeline.mnheme"
    db = MemoryDB(p)
    db.remember("Z", Feeling.NOSTALGIA, "primo")
    time.sleep(0.01)
    db.remember("Z", Feeling.GIOIA,     "secondo")
    tl = db.concept_timeline("Z")
    assert tl[0]["feeling"] == "nostalgia"
    assert tl[1]["feeling"] == "gioia"


test("rebuild indici da log esistente",           t_index_rebuild)
test("count(concept, feeling) combo",              t_index_concept_feeling)
test("indice tag funzionante",                     t_index_tags)
test("timeline in ordine cronologico",             t_index_timeline_order)

# ─────────────────────────────────────────────
# 4. FSPROBE
# ─────────────────────────────────────────────

section("4 · FsProbe — rilevamento filesystem")

from fsprobe import FsProbe, LinkStrategy, FsType


def t_probe_runs():
    probe = FsProbe(TMP)
    caps  = probe.detect()
    assert caps.os_name in ("Linux", "Windows", "Darwin")
    assert isinstance(caps.can_hardlink, bool)
    assert isinstance(caps.can_symlink,  bool)
    assert isinstance(caps.can_reflink,  bool)
    assert caps.strategy in LinkStrategy


def t_probe_cached():
    probe = FsProbe(TMP)
    caps1 = probe.detect()
    t0    = time.perf_counter()
    caps2 = probe.detect()
    elapsed = (time.perf_counter() - t0) * 1000
    assert caps2 is caps1         # stesso oggetto (cache)
    assert elapsed < 5            # sotto 5ms


def t_probe_strategy_chosen():
    probe = FsProbe(TMP)
    caps  = probe.detect()
    # Deve aver scelto una strategia
    assert caps.strategy_note != ""
    assert caps.strategy != None


def t_probe_inode_bits():
    probe = FsProbe(TMP)
    caps  = probe.detect()
    assert caps.inode_bits in (32, 64)


test("probe() completa senza errori",             t_probe_runs)
test("probe() usa la cache alla seconda chiamata", t_probe_cached)
test("strategia scelta + note popolate",           t_probe_strategy_chosen)
test("inode_bits è 32 o 64",                       t_probe_inode_bits)

# ─────────────────────────────────────────────
# 5. FILESTORE
# ─────────────────────────────────────────────

section("5 · FileStore — storage file fisici")

from filestore import FileStore, FileEntry, UnsupportedMediaError


def t_store_bytes():
    fs = FileStore(TMP / "fs1")
    data = b"\xFF\xD8\xFF" + b"IMG" * 200
    entry = fs.store_bytes("mem-001", data, "foto.jpg")
    assert entry.memory_id == "mem-001"
    assert entry.original_name == "foto.jpg"
    assert entry.media_type == "images"
    assert entry.size_bytes  > 0
    assert entry.checksum   and len(entry.checksum) == 64


def t_store_file():
    fs = FileStore(TMP / "fs2")
    tmp_file = TMP / "test_upload.jpg"
    tmp_file.write_bytes(b"\xFF\xD8\xFF" + b"X" * 500)
    entry = fs.store("mem-002", tmp_file, move=False)
    assert tmp_file.exists()   # copy, not move
    assert entry.memory_id == "mem-002"
    # Test move=True
    tmp_file2 = TMP / "test_move.mp4"
    tmp_file2.write_bytes(b"\x00\x00\x00\x18ftyp" + b"V" * 300)
    fs.store("mem-003", tmp_file2, move=True)
    assert not tmp_file2.exists()  # file spostato


def t_get_bytes():
    fs = FileStore(TMP / "fs3")
    original = b"\xFF\xD8\xFF" + b"GETTEST" * 100
    fs.store_bytes("mem-get", original, "get.jpg")
    recovered = fs.get_bytes("mem-get")
    assert recovered == original


def t_deduplication():
    fs   = FileStore(TMP / "fs4")
    data = b"\xFF\xD8\xFF" + b"SAME" * 300
    e1   = fs.store_bytes("mem-dup-1", data, "copia1.jpg")
    e2   = fs.store_bytes("mem-dup-2", data, "copia2.jpg")
    # Stesso checksum
    assert e1.checksum == e2.checksum
    # Stesso pool_path
    assert e1.pool_path == e2.pool_path
    # Stesso inode (se hardlink supportato)
    if e1.strategy_used == "hardlink":
        p1 = (TMP / "fs4" / e1.link_path)
        p2 = (TMP / "fs4" / e2.link_path)
        if p1.exists() and p2.exists():
            assert os.stat(p1).st_ino == os.stat(p2).st_ino


def t_unsupported_extension():
    fs = FileStore(TMP / "fs5")
    try:
        fs.store_bytes("mem-x", b"data", "file.exe")
        raise AssertionError("Doveva sollevare UnsupportedMediaError")
    except UnsupportedMediaError:
        pass


def t_list_by_type():
    fs = FileStore(TMP / "fs6")
    fs.store_bytes("m1", b"\xFF\xD8\xFF" + b"A"*100, "a.jpg")
    fs.store_bytes("m2", b"\xFF\xD8\xFF" + b"B"*100, "b.png")
    fs.store_bytes("m3", b"\x00\x00\x00\x18ftyp"   + b"C"*100, "c.mp4")
    images = fs.list_by_type("images")
    videos = fs.list_by_type("videos")
    assert len(images) == 2
    assert len(videos) == 1


def t_filestore_info():
    fs   = FileStore(TMP / "fs7")
    fs.store_bytes("m1", b"\xFF\xD8\xFF" + b"I"*200, "i.jpg")
    info = fs.info()
    assert info["total_entries"] == 1
    assert info["pool_unique_files"] == 1
    assert info["by_type"]["images"] == 1


test("store_bytes() crea FileEntry corretto",      t_store_bytes)
test("store(path, copy/move)",                     t_store_file)
test("get_bytes() recupera esattamente i dati",   t_get_bytes)
test("deduplicazione SHA-256 + inode",            t_deduplication)
test("estensione non supportata → errore",        t_unsupported_extension)
test("list_by_type() raggruppa correttamente",    t_list_by_type)
test("info() conta entries e pool",               t_filestore_info)

# ─────────────────────────────────────────────
# 6. MEMORYDB + FILESTORE integrazione
# ─────────────────────────────────────────────

section("6 · MemoryDB + FileStore — integrazione media")


def t_remember_bytes():
    db  = MemoryDB(TMP / "db_media.mnheme", files_dir=TMP / "db_media_files")
    raw = b"\xFF\xD8\xFF" + b"M" * 400
    mem, fe = db.remember_bytes("Vacanza", Feeling.GIOIA, raw, "spiaggia.jpg")
    assert mem.concept    == "Vacanza"
    assert mem.media_type == "image"
    assert fe.memory_id   == mem.memory_id
    path = db.files.get_path(mem.memory_id)
    assert path.exists()


def t_remember_file():
    db  = MemoryDB(TMP / "db_file.mnheme", files_dir=TMP / "db_file_files")
    src = TMP / "upload.jpg"
    src.write_bytes(b"\xFF\xD8\xFF" + b"F" * 300)
    mem, fe = db.remember_file("Foto", Feeling.NOSTALGIA, src, note="Scatto")
    assert db.files.exists(mem.memory_id)
    assert src.exists()   # copy di default


test("remember_bytes() + FileStore",              t_remember_bytes)
test("remember_file() + FileStore",               t_remember_file)

# ─────────────────────────────────────────────
# 7. LLM PROVIDER
# ─────────────────────────────────────────────

section("7 · LLMProvider — discovery e rate limiting")

from llm_provider import (
    load_env, discover_providers, LLMProvider,
    ProviderProfile, RateLimiter, LLMError
)


def t_load_env():
    env_file = TMP / "test.env"
    env_file.write_text(
        "TEMPERATURE=0.5\n"
        "GROQ_URL=https://api.groq.com/openai/v1/chat/completions\n"
        "GROQ_MODEL=llama-3\n"
        "GROQ_API_KEY=fake-key\n"
        "GROQ_RPM=30\n"
        "# commento ignorato\n"
        "EMPTY_VAL=\n"
    )
    env = load_env(env_file)
    assert env["TEMPERATURE"]  == "0.5"
    assert env["GROQ_URL"]     == "https://api.groq.com/openai/v1/chat/completions"
    assert env["GROQ_MODEL"]   == "llama-3"
    assert env["GROQ_API_KEY"] == "fake-key"
    assert env["GROQ_RPM"]     == "30"
    assert "EMPTY_VAL" in env


def t_discover_providers():
    env = {
        "TEMPERATURE":  "0.3",
        "GROQ_URL":     "https://api.groq.com/openai/v1/chat/completions",
        "GROQ_MODEL":   "llama-3",
        "GROQ_API_KEY": "gsk_fake",
        "GROQ_RPM":     "30",
        "ANTHROPIC_URL":    "https://api.anthropic.com/v1/messages",
        "ANTHROPIC_MODEL":  "claude-opus-4-5",
        "ANTHROPIC_API_KEY":"sk-ant-fake",
        "ANTHROPIC_RPM":    "5",
        "LM_STUDIO_URL":  "http://localhost:1234/v1/chat/completions",
        "LM_STUDIO_MODEL":"local-model",
        "LM_STUDIO_RPM":  "60",
        # Provider senza model → ignorato
        "EMPTY_URL":   "http://example.com",
    }
    profiles = discover_providers(env)
    assert "groq"      in profiles
    assert "anthropic" in profiles
    assert "lm-studio" in profiles
    assert "empty"     not in profiles
    assert profiles["anthropic"].is_anthropic  == True
    assert profiles["lm-studio"].is_anthropic  == False
    assert profiles["lm-studio"].is_local      == True
    assert profiles["groq"].rpm                == 30
    assert profiles["anthropic"].temperature   == 0.3


def t_provider_active():
    env = {
        "GROQ_URL":    "https://api.groq.com/openai/v1/chat/completions",
        "GROQ_MODEL":  "llama-3",
        "GROQ_API_KEY":"gsk_fake",
        "GROQ_RPM":    "30",
    }
    profiles = discover_providers(env)
    p = LLMProvider(profiles, active="groq")
    assert p._active == "groq"
    assert p.active_profile.name == "groq"


def t_provider_unknown_active():
    env = {
        "GROQ_URL":   "https://api.groq.com/openai/v1/chat/completions",
        "GROQ_MODEL": "llama-3",
    }
    profiles = discover_providers(env)
    try:
        LLMProvider(profiles, active="openai_inesistente")
        raise AssertionError("Doveva sollevare ValueError")
    except ValueError as e:
        assert "openai_inesistente" in str(e)


def t_provider_use():
    env = {
        "GROQ_URL":    "https://api.groq.com/openai/v1/chat/completions",
        "GROQ_MODEL":  "llama-3",
        "MISTRAL_URL":   "https://api.mistral.ai/v1/chat/completions",
        "MISTRAL_MODEL": "mistral-large",
    }
    profiles = discover_providers(env)
    p = LLMProvider(profiles)
    p.use("mistral")
    assert p._active == "mistral"


def t_rate_limiter():
    limiter = RateLimiter(rpm=120)   # 0.5s tra le richieste
    t0 = time.perf_counter()
    limiter.wait()
    limiter.wait()
    elapsed = (time.perf_counter() - t0) * 1000
    # Prima chiamata: ~0ms, seconda: ~500ms
    assert elapsed >= 400, f"Rate limiter troppo veloce: {elapsed:.0f}ms"


def t_rate_limiter_threadsafe():
    limiter = RateLimiter(rpm=600)   # 0.1s tra le richieste
    times   = []
    def worker():
        limiter.wait()
        times.append(time.monotonic())
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    # Ogni thread deve aver aspettato
    times.sort()
    gaps = [times[i+1] - times[i] for i in range(len(times)-1)]
    assert all(g >= 0.08 for g in gaps), f"Rate limiter non thread-safe: {gaps}"


test("load_env() parser completo",                t_load_env)
test("discover_providers() da dict env",          t_discover_providers)
test("LLMProvider(active=...) funziona",          t_provider_active)
test("active sconosciuto → ValueError chiaro",    t_provider_unknown_active)
test("provider.use() cambia provider attivo",     t_provider_use)
test("RateLimiter rispetta il RPM",               t_rate_limiter)
test("RateLimiter è thread-safe",                 t_rate_limiter_threadsafe)

# ─────────────────────────────────────────────
# 8. BRAIN (mock LLM)
# ─────────────────────────────────────────────

section("8 · Brain — operazioni cognitive (mock LLM)")

from brain import Brain, PerceptionResult, AskResult, ReflectionResult, DreamResult, IntrospectionResult


class MockProvider(LLMProvider):
    """LLM finto per test senza rete."""
    def __init__(self):
        p = ProviderProfile(name="mock", url="http://mock", model="mock", api_key="", rpm=9999)
        super().__init__({"mock": p}, active="mock")
        self.calls = []

    def complete(self, system, user, **kw):
        self.calls.append(user[:60])
        import json as _j, re as _re
        # perceive
        if '"concept"' in user and '"feeling"' in user and '"enriched"' in user:
            kw_lower = user.lower()
            concept = "Debito" if "banca" in kw_lower or "mutuo" in kw_lower else \
                      "Famiglia" if "figlia" in kw_lower or "fratello" in kw_lower else "Memoria"
            feeling = "paura" if "tremore" in kw_lower or "busta" in kw_lower else \
                      "gioia" if "sorriso" in kw_lower else "curiosità"
            return _j.dumps({"concept": concept, "feeling": feeling,
                             "tags": ["mock","test"], "enriched": "Testo arricchito mock."})
        # keyword extraction per ask
        if '"keywords"' in user and '"concepts"' in user:
            return _j.dumps({"keywords": ["test"], "concepts": ["Debito"]})
        # tutto il resto (ask answer, reflect, dream, introspect, summarize)
        return "Risposta mock.\n\nCertezza: alta — mock\n\nArco: da mock a mock"


def make_brain():
    db   = MemoryDB(TMP / f"brain_{id(object())}.mnheme")
    mock = MockProvider()
    # Carica qualche ricordo di base
    db.remember("Debito",   Feeling.ANSIA,     "Ho firmato il mutuo.")
    db.remember("Famiglia", Feeling.AMORE,     "Sorriso di mia figlia.")
    db.remember("Viaggio",  Feeling.NOSTALGIA, "Lisbona con la pioggia.")
    return Brain(db, mock), db, mock


def t_perceive():
    brain, db, mock = make_brain()
    r = brain.perceive("Ho aperto la busta dalla banca. Tremore alle mani.")
    assert isinstance(r, PerceptionResult)
    assert r.extracted_concept in [f.value for f in Feeling] or len(r.extracted_concept) > 0
    assert r.memory.memory_id and r.memory.concept
    assert db.count() == 4   # 3 base + 1 nuovo


def t_perceive_override():
    brain, db, _ = make_brain()
    r = brain.perceive("qualsiasi cosa", concept="Override", feeling="gioia")
    assert r.extracted_concept == "Override"
    assert r.extracted_feeling == "gioia"


def t_ask():
    brain, db, mock = make_brain()
    ans = brain.ask("Come mi sento rispetto al denaro?")
    assert isinstance(ans, AskResult)
    assert ans.question  != ""
    assert ans.answer    != ""
    assert isinstance(ans.memories_used, list)
    assert ans.provider_used == "mock"


def t_reflect():
    brain, db, mock = make_brain()
    ref = brain.reflect("Debito")
    assert isinstance(ref, ReflectionResult)
    assert ref.concept   == "Debito"
    assert len(ref.memories) >= 1


def t_reflect_missing_concept():
    brain, db, mock = make_brain()
    try:
        brain.reflect("ConcettoInesistente_XYZ")
        raise AssertionError("Doveva sollevare ValueError")
    except ValueError:
        pass


def t_dream():
    brain, db, mock = make_brain()
    dream = brain.dream(n_memories=3)
    assert isinstance(dream, DreamResult)
    assert dream.connections != ""
    assert len(dream.memories) <= 3


def t_dream_too_few():
    db   = MemoryDB(TMP / "brain_dream_empty.mnheme")
    mock = MockProvider()
    br   = Brain(db, mock)
    db.remember("Solo", Feeling.NOIA, "unico ricordo")
    try:
        br.dream()
        raise AssertionError("Doveva sollevare ValueError")
    except ValueError:
        pass


def t_introspect():
    brain, db, mock = make_brain()
    intro = brain.introspect()
    assert isinstance(intro, IntrospectionResult)
    assert intro.total_memories >= 3
    assert isinstance(intro.dominant_concepts, list)
    assert isinstance(intro.emotional_map, dict)


def t_introspect_empty():
    db   = MemoryDB(TMP / "brain_empty.mnheme")
    mock = MockProvider()
    br   = Brain(db, mock)
    try:
        br.introspect()
        raise AssertionError("Doveva sollevare ValueError")
    except ValueError:
        pass


def t_summarize():
    brain, db, mock = make_brain()
    mems = db.recall_all()
    text = brain.summarize(mems, style="narrativo")
    assert isinstance(text, str) and len(text) > 0
    # Empty list
    empty = brain.summarize([], style="poetico")
    assert "nessun" in empty.lower()


def t_llm_call_count():
    brain, db, mock = make_brain()
    before = len(mock.calls)
    brain.perceive("test 1")
    brain.perceive("test 2")
    brain.ask("domanda?")
    after = len(mock.calls)
    # perceive fa 1 call, ask fa 2 (keyword + answer)
    assert after - before == 4


test("perceive() → PerceptionResult",             t_perceive)
test("perceive() con override concept/feeling",   t_perceive_override)
test("ask() → AskResult con memories_used",       t_ask)
test("reflect() → ReflectionResult",             t_reflect)
test("reflect() su concetto inesistente → errore", t_reflect_missing_concept)
test("dream() → DreamResult",                    t_dream)
test("dream() con <2 ricordi → errore",           t_dream_too_few)
test("introspect() → IntrospectionResult",        t_introspect)
test("introspect() su db vuoto → errore",         t_introspect_empty)
test("summarize() testo e lista vuota",           t_summarize)
test("conteggio chiamate LLM corretto",           t_llm_call_count)

# ─────────────────────────────────────────────
# 9. API REST (opzionale)
# ─────────────────────────────────────────────

section("9 · API REST — FastAPI (opzionale)")

try:
    import fastapi
    import httpx
    HAS_API_DEPS = True
except ImportError:
    HAS_API_DEPS = False

if not HAS_API_DEPS:
    skip("Endpoints POST /memories",  "fastapi o httpx non installati")
    skip("Endpoints GET /concepts",   "fastapi o httpx non installati")
    skip("Endpoints GET /search",     "fastapi o httpx non installati")
    skip("Endpoints GET /stats",      "fastapi o httpx non installati")
else:
    from fastapi.testclient import TestClient
    import mnheme_api

    # Usa un DB temporaneo per i test API
    mnheme_api.db = MemoryDB(TMP / "api_test.mnheme")
    client = TestClient(mnheme_api.app)

    def t_api_post_memory():
        r = client.post("/memories", json={
            "concept": "API Test", "feeling": "curiosità",
            "content": "Test via API", "tags": ["api"]
        })
        assert r.status_code == 201
        data = r.json()
        assert data["concept"]   == "API Test"
        assert data["feeling"]   == "curiosità"
        assert data["memory_id"] != ""

    def t_api_get_memories():
        r = client.get("/memories")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def t_api_get_memories_filter():
        r = client.get("/memories?feeling=curiosità&limit=5")
        assert r.status_code == 200
        data = r.json()
        assert all(m["feeling"] == "curiosità" for m in data)

    def t_api_get_concepts():
        r = client.get("/concepts")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def t_api_get_concept_memories():
        r = client.get("/concepts/API Test")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def t_api_search():
        r = client.get("/memories/search?q=API")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def t_api_stats():
        r = client.get("/stats")
        assert r.status_code == 200
        data = r.json()
        assert "total_memories" in data
        assert data["total_memories"] >= 1

    def t_api_timeline():
        r = client.get("/concepts/API Test/timeline")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def t_api_export():
        r = client.get("/export?concept=API Test")
        assert r.status_code == 200

    test("POST /memories crea ricordo",           t_api_post_memory)
    test("GET  /memories lista",                  t_api_get_memories)
    test("GET  /memories?feeling= filtro",        t_api_get_memories_filter)
    test("GET  /concepts lista",                  t_api_get_concepts)
    test("GET  /concepts/{concept} ricordi",      t_api_get_concept_memories)
    test("GET  /memories/search?q= cerca",        t_api_search)
    test("GET  /stats statistiche",               t_api_stats)
    test("GET  /concepts/{concept}/timeline",     t_api_timeline)
    test("GET  /export JSON",                     t_api_export)

# ─────────────────────────────────────────────
# 10. START SCRIPTS
# ─────────────────────────────────────────────

section("10 · Start scripts — esistenza e sintassi")


def t_start_sh_exists():
    p = PROJECT_DIR / "start.sh"
    assert p.exists(), "start.sh non trovato"
    assert p.stat().st_size > 1000


def t_start_bat_exists():
    p = PROJECT_DIR / "start.bat"
    assert p.exists(), "start.bat non trovato"
    assert p.stat().st_size > 1000


def t_start_sh_syntax():
    import subprocess
    p = PROJECT_DIR / "start.sh"
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True)
    assert r.returncode == 0, f"Errore sintassi bash: {r.stderr.decode()}"


def t_env_example_exists():
    p = PROJECT_DIR / ".env.example"
    assert p.exists(), ".env.example non trovato"
    content = p.read_text()
    assert "GROQ_URL"       in content
    assert "ANTHROPIC_URL"  in content
    assert "LM_STUDIO_URL"  in content
    assert "TEMPERATURE"    in content


test("start.sh esiste e non è vuoto",             t_start_sh_exists)
test("start.bat esiste e non è vuoto",            t_start_bat_exists)
test("start.sh sintassi bash valida",             t_start_sh_syntax)
test(".env.example ha tutti i provider",          t_env_example_exists)

# ─────────────────────────────────────────────
# RIEPILOGO
# ─────────────────────────────────────────────

print(f"\n{'═'*70}")
print(f"\033[1m  RISULTATI\033[0m")
print(f"{'═'*70}")
total = results["pass"] + results["fail"] + results["skip"]
print(f"\n  Totale:  {total}")
print(f"  \033[0;32mPass:    {results['pass']}\033[0m")
if results["fail"]:
    print(f"  \033[0;31mFail:    {results['fail']}\033[0m")
if results["skip"]:
    print(f"  \033[0;33mSkip:    {results['skip']}\033[0m")

print()
cleanup()

if results["fail"] > 0:
    print(f"  \033[0;31mAlcuni test falliti. Aggiungi --verbose per dettagli.\033[0m\n")
    sys.exit(1)
else:
    print(f"  \033[0;32mTutti i test superati.\033[0m\n")
