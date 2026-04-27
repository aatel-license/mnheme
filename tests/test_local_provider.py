"""
test_local_provider.py — Test LLMProvider con LM Studio locale (mock)
"""
import sys, os, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from llm_provider import load_env, discover_providers, LLMProvider, ProviderProfile


class MockLLM(LLMProvider):
    """Mock provider che simula risposte senza rete."""
    def __init__(self):
        p = ProviderProfile(name="mock", url="http://mock", model="mock-llm", api_key="", rpm=9999)
        super().__init__({"mock": p}, active="mock")

    def complete(self, system, user, **kw):
        import json as _j
        if '"concept"' in user and '"feeling"' in user:
            return _j.dumps({
                "concept": "Test",
                "feeling": "curiosità",
                "tags": ["mock", "test"],
                "enriched": "Testo arricchito dalla percezione cognitiva."
            })
        if '"keywords"' in user:
            return _j.dumps({"keywords": ["test"], "concepts": ["Test"]})
        return "Risposta mock generata correttamente.\n\nCertezza: alta — dati diretti dai ricordi."


def test_load_env():
    env_content = """
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
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        env = load_env(path)
        assert len(env) > 0
        assert "LM_STUDIO_URL" in env
        assert env["GROQ_API_KEY"] == "gsk_test_fake_key"
    finally:
        os.remove(path)


def test_discover_providers():
    env_content = """
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=nvidia/nemotron-3-nano-4b

GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_test_fake_key
GROQ_RPM=30

ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-test-fake
ANTHROPIC_RPM=5
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        env = load_env(path)
        profiles = discover_providers(env)
        assert len(profiles) >= 3
        assert "lm-studio" in profiles
        assert "groq" in profiles
        assert "anthropic" in profiles
    finally:
        os.remove(path)


def test_anthropic_detection():
    env_content = """
ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-test-fake
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

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
    env_content = """
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=nvidia/nemotron-3-nano-4b
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        env = load_env(path)
        profiles = discover_providers(env)
        lm = profiles.get("lm-studio")
        assert lm is not None
        assert lm.is_local is True
        assert lm.is_anthropic is False
    finally:
        os.remove(path)


def test_llm_provider_from_env():
    env_content = """
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=nvidia/nemotron-3-nano-4b

GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_test_fake_key
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        provider = LLMProvider.from_env(path)
        assert provider is not None
        assert len(provider.available_providers) >= 2
    finally:
        os.remove(path)


def test_switch_provider():
    env_content = """
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=nvidia/nemotron-3-nano-4b

GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_test_fake_key
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        provider = LLMProvider.from_env(path)
        provider.use("groq")
        assert provider.active_profile.name == "groq"
        provider.use("lm-studio")
        assert provider.active_profile.name == "lm-studio"
    finally:
        os.remove(path)


def test_force_provider():
    env_content = """
ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-test-fake
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        p2 = LLMProvider.from_env(path, active="anthropic")
        assert p2.active_profile.name == "anthropic"
    finally:
        os.remove(path)


def test_unknown_provider_error():
    env_content = """
ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-test-fake
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        try:
            LLMProvider.from_env(path, active="openai")
            assert False, "Doveva sollevare ValueError"
        except ValueError:
            pass  # OK
    finally:
        os.remove(path)


def test_multi_provider():
    env_content = """
USE_MULTI_PROVIDER=true
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=nvidia/nemotron-3-nano-4b
GROQ_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_API_KEY=gsk_test_fake_key
ANTHROPIC_URL=https://api.anthropic.com/v1/messages
ANTHROPIC_MODEL=claude-opus-4-5
ANTHROPIC_API_KEY=sk-ant-test-fake
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        env = load_env(path)
        profiles = discover_providers(env)
        p_multi = LLMProvider(
            profiles,
            use_multi=True,
            priority=["lm-studio", "groq", "anthropic"],
        )
        assert p_multi._use_multi is True
    finally:
        os.remove(path)


def test_custom_provider():
    env_content = """
CUSTOM_URL=http://myserver.local:8080/v1/chat/completions
CUSTOM_MODEL=my-finetuned-model
CUSTOM_API_KEY=custom_key_123
"""
    path = "/tmp/_test_mnheme.env"
    with open(path, "w") as f:
        f.write(env_content)

    try:
        env = load_env(path)
        profiles = discover_providers(env)
        assert "custom" in profiles
        custom = profiles["custom"]
        assert custom.url == "http://myserver.local:8080/v1/chat/completions"
        assert custom.model == "my-finetuned-model"
    finally:
        os.remove(path)


def test_llm_error():
    from llm_provider import LLMError

    mock = MockLLM()
    try:
        raise LLMError("Test error", provider="mock")
    except LLMError as e:
        assert "Test error" in str(e)
        assert e.provider == "mock"


def test_brain_integration():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB("/tmp/_mnheme_test_" + str(os.getpid()) + ".mnheme")
    mock = MockLLM()
    brain = Brain(db, mock)

    # Inseriamo ricordi prima di usare i metodi che li richiedono
    db.remember("Test", Feeling.CURIOSITA, "Sto testando il sistema MNHEME con provider agnostico.")
    db.remember("Famiglia", Feeling.AMORE, "Pranzo della domenica.")
    db.remember("Debito", Feeling.ANSIA, "La banca ha chiamato.")

    ans = brain.ask("Come sto?")
    assert len(ans.answer) > 0
    assert len(ans.memories_used) >= 1

    ref = brain.reflect("Famiglia")
    assert ref.concept == "Famiglia"

    drm = brain.dream(n_memories=3)
    assert len(drm.memories) >= 2

    intro = brain.introspect()
    assert intro.total_memories >= 2


def test_brain_summarize():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB("/tmp/_mnheme_test_sum_" + str(os.getpid()) + ".mnheme")
    mock = MockLLM()
    brain = Brain(db, mock)

    result = brain.summarize([])
    assert "Nessun ricordo" in result


def test_brain_reflect_no_memories():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB("/tmp/_mnheme_test_reflect_" + str(os.getpid()) + ".mnheme")
    mock = MockLLM()
    brain = Brain(db, mock)

    try:
        brain.reflect("NonEsiste")
        assert False, "Doveva sollevare ValueError"
    except ValueError as e:
        assert "Nessun ricordo" in str(e)


def test_brain_dream_too_few_memories():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB("/tmp/_mnheme_test_dream_" + str(os.getpid()) + ".mnheme")
    mock = MockLLM()
    brain = Brain(db, mock)

    # Con 0 ricordi dream() solleva ValueError
    try:
        brain.dream()
        assert False, "Doveva sollevare ValueError"
    except ValueError as e:
        assert "2 ricordi" in str(e)


def test_brain_introspect_empty_db():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB("/tmp/_mnheme_test_introspect_" + str(os.getpid()) + ".mnheme")
    mock = MockLLM()
    brain = Brain(db, mock)

    # Con 0 ricordi introspect() solleva ValueError
    try:
        brain.introspect()
        assert False, "Doveva sollevare ValueError"
    except ValueError as e:
        assert "vuoto" in str(e).lower() or "Database vuoto" in str(e)


def test_brain_repr():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB("/tmp/_mnheme_test_repr_" + str(os.getpid()) + ".mnheme")
    mock = MockLLM()
    brain = Brain(db, mock)
    r = repr(brain)
    assert "Brain(" in r
    assert "db=" in r
    assert "llm=" in r


def test_brain_language():
    from mnheme import MemoryDB, Feeling
    from brain import Brain

    db = MemoryDB("/tmp/_mnheme_test_lang_" + str(os.getpid()) + ".mnheme")
    mock = MockLLM()
    brain = Brain(db, mock, language="english")
    assert brain._language == "english"
