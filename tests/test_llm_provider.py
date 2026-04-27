"""
test_llm_provider.py — Test del sistema provider senza rete reale (mock)
"""
import sys, os, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from llm_provider import (
    load_env, discover_providers, LLMProvider,
    ProviderProfile, RateLimiter, call_provider, LLMError
)


MOCK_ENV_CONTENT = """
TEMPERATURE=0.3
USE_MULTI_PROVIDER=false

LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=nvidia/nemotron-3-nano-4b
LM_STUDIO_API_KEY=
LM_STUDIO_RPM=60

GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_test_fake_key
GROQ_RPM=30

ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-test-fake
ANTHROPIC_RPM=5

MISTRAL_URL=https://api.mistral.ai/v1/chat/completions
MISTRAL_MODEL=mistral-large-latest
MISTRAL_API_KEY=fake_mistral_key
MISTRAL_RPM=5

CUSTOM_URL=http://myserver.local:8080/v1/chat/completions
CUSTOM_MODEL=my-finetuned-model
CUSTOM_API_KEY=
CUSTOM_RPM=100
"""


def _write_mock_env():
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(MOCK_ENV_CONTENT)
    return path


# ── load_env / discover_providers ─────────────

def test_load_env():
    path = _write_mock_env()
    try:
        env = load_env(path)
        assert len(env) > 0
        assert "LM_STUDIO_URL" in env
        assert env["GROQ_API_KEY"] == "gsk_test_fake_key"
    finally:
        os.remove(path)


def test_discover_providers():
    path = _write_mock_env()
    try:
        env = load_env(path)
        profiles = discover_providers(env)
        assert len(profiles) >= 5
        assert "lm-studio" in profiles
        assert "groq" in profiles
        assert "anthropic" in profiles
        assert "mistral" in profiles
        assert "custom" in profiles
    finally:
        os.remove(path)


def test_anthropic_detection():
    path = _write_mock_env()
    try:
        env = load_env(path)
        profiles = discover_providers(env)
        ant = profiles.get("anthropic")
        assert ant is not None
        assert ant.is_anthropic is True
        assert ant.is_local is False
    finally:
        os.remove(path)


def test_lm_studio_detection():
    path = _write_mock_env()
    try:
        env = load_env(path)
        profiles = discover_providers(env)
        lm = profiles.get("lm-studio")
        assert lm is not None
        assert lm.is_local is True
        assert lm.is_anthropic is False
    finally:
        os.remove(path)


def test_custom_provider():
    path = _write_mock_env()
    try:
        env = load_env(path)
        profiles = discover_providers(env)
        custom = profiles.get("custom")
        assert custom is not None
        assert custom.url == "http://myserver.local:8080/v1/chat/completions"
        assert custom.model == "my-finetuned-model"
    finally:
        os.remove(path)


# ── LLMProvider ───────────────────────────────

def test_llm_provider_from_env():
    path = _write_mock_env()
    try:
        provider = LLMProvider.from_env(path)
        assert provider is not None
        assert len(provider.available_providers) >= 5
    finally:
        os.remove(path)


def test_switch_provider():
    path = _write_mock_env()
    try:
        provider = LLMProvider.from_env(path)
        provider.use("groq")
        assert provider.active_profile.name == "groq"
        provider.use("lm-studio")
        assert provider.active_profile.name == "lm-studio"
    finally:
        os.remove(path)


def test_force_provider():
    path = _write_mock_env()
    try:
        p2 = LLMProvider.from_env(path, active="anthropic")
        assert p2.active_profile.name == "anthropic"
    finally:
        os.remove(path)


def test_unknown_provider_error():
    path = _write_mock_env()
    try:
        try:
            LLMProvider.from_env(path, active="openai")
            assert False, "Doveva sollevare ValueError"
        except ValueError:
            pass  # OK
    finally:
        os.remove(path)


def test_multi_provider():
    path = _write_mock_env()
    try:
        env = load_env(path)
        env["USE_MULTI_PROVIDER"] = "true"
        profiles = discover_providers(env)
        p_multi = LLMProvider(
            profiles,
            use_multi=True,
            priority=["lm-studio", "groq", "anthropic"],
        )
        assert p_multi._use_multi is True
    finally:
        os.remove(path)


def test_priority():
    path = _write_mock_env()
    try:
        p_prio = LLMProvider.from_env(
            path,
            priority=["lm-studio", "groq", "anthropic", "mistral"]
        )
        assert p_prio._active == "lm-studio"
        assert len(p_prio._priority) >= 4
    finally:
        os.remove(path)


# ── RateLimiter ───────────────────────────────

def test_rate_limiter():
    limiter = RateLimiter(rpm=60)
    times = []
    for _ in range(3):
        t0 = time.perf_counter()
        limiter.wait()
        times.append((time.perf_counter() - t0) * 1000)
    assert len(times) == 3
    # Ogni gap dovrebbe essere circa 1 secondo (60 RPM)
    for t in times:
        assert t < 2000, f"Gap troppo lungo: {t}ms"


def test_rate_limiter_custom_rpm():
    limiter = RateLimiter(rpm=3600)  # 1 al secondo
    assert limiter.rpm == 3600


# ── LLMError ──────────────────────────────────

def test_llm_error():
    try:
        raise LLMError("Test error", provider="mock")
    except LLMError as e:
        assert "Test error" in str(e)
        assert e.provider == "mock"


# ── Mock LLM → Brain integration ─────────────

class MockProvider(LLMProvider):
    """Provider che simula risposte senza rete."""
    def __init__(self):
        profile = ProviderProfile(
            name="mock", url="http://mock", model="mock-llm",
            api_key="", rpm=9999,
        )
        super().__init__({"mock": profile}, active="mock")
        self.calls = []

    def complete(self, system, user, **kw):
        self.calls.append(user[:50])
        import json as _json
        if '"concept"' in user and '"feeling"' in user:
            return _json.dumps({
                "concept":  "Test",
                "feeling":  "curiosità",
                "tags":     ["mock", "test"],
                "enriched": "Testo arricchito dalla percezione cognitiva."
            })
        if '"keywords"' in user:
            return _json.dumps({"keywords": ["test"], "concepts": ["Test"]})
        return "Risposta mock generata correttamente.\n\nCertezza: alta — dati diretti dai ricordi."


def test_brain_perceive():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB(":memory:")
    mock = MockProvider()
    brain = Brain(db, mock)

    r = brain.perceive("Sto testando il sistema MNHEME con provider agnostico.")
    assert r.extracted_concept == "Test"
    assert r.extracted_feeling == "curiosità"


def test_brain_ask():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB(":memory:")
    mock = MockProvider()
    brain = Brain(db, mock)

    db.remember("Famiglia", Feeling.AMORE, "Pranzo della domenica.")
    db.remember("Debito", Feeling.ANSIA, "La banca ha chiamato.")

    ans = brain.ask("Come sto?")
    assert len(ans.memories_used) >= 1


def test_brain_reflect():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB(":memory:")
    mock = MockProvider()
    brain = Brain(db, mock)

    db.remember("Famiglia", Feeling.AMORE, "Pranzo della domenica.")

    ref = brain.reflect("Famiglia")
    assert ref.concept == "Famiglia"


def test_brain_dream():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB(":memory:")
    mock = MockProvider()
    brain = Brain(db, mock)

    db.remember("A", Feeling.AMORE, "Ricordo A")
    db.remember("B", Feeling.ANSIA, "Ricordo B")
    db.remember("C", Feeling.GIOIA, "Ricordo C")

    drm = brain.dream(n_memories=3)
    assert len(drm.memories) >= 2


def test_brain_introspect():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB(":memory:")
    mock = MockProvider()
    brain = Brain(db, mock)

    db.remember("A", Feeling.AMORE, "Ricordo A")
    db.remember("B", Feeling.ANSIA, "Ricordo B")

    intro = brain.introspect()
    assert intro.total_memories >= 2


def test_brain_repr():
    from mnheme import MemoryDB
    from brain import Brain

    mock = MockProvider()
    db = MemoryDB(":memory:")
    brain = Brain(db, mock)
    r = repr(brain)
    assert "Brain(" in r
    assert "db=" in r


def test_brain_language():
    from mnheme import MemoryDB
    from brain import Brain

    mock = MockProvider()
    db = MemoryDB(":memory:")
    brain = Brain(db, mock, language="english")
    assert brain._language == "english"


def test_mock_provider_calls_tracking():
    from mnheme import MemoryDB
    mock = MockProvider()
    db = MemoryDB(":memory:")
    from brain import Brain
    brain = Brain(db, mock)

    brain.perceive("Test 1")
    brain.perceive("Test 2")
    assert len(mock.calls) == 2


def test_provider_list():
    path = _write_mock_env()
    try:
        provider = LLMProvider.from_env(path)
        # list_providers non dovrebbe sollevare
        provider.list_providers()
    finally:
        os.remove(path)
