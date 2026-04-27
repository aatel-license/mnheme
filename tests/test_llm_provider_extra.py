"""
test_llm_provider_extra.py — Copertura di llm_provider.py per rami non ancora coperti.

Copre: call_provider (HTTP error, URL error, generic error), _extract_text (malformed body),
       _build_anthropic, _build_openai (con/senza api_key), complete_multi, retry logic,
       list_providers, from_profile, ProviderProfile (is_local, is_anthropic, available, repr)
"""
import json
import threading
import time
import urllib.error
from unittest.mock import patch, MagicMock

import pytest
from llm_provider import (
    LLMProvider, ProviderProfile, LLMError, RateLimiter,
    load_env, discover_providers, call_provider,
    _build_anthropic, _build_openai, _extract_text,
)


# ── ProviderProfile ───────────────────────────────────────────────────────────

def test_is_anthropic_true():
    p = ProviderProfile("ant", "https://api.anthropic.com/v1/messages", "claude-3", api_key="k")
    assert p.is_anthropic


def test_is_anthropic_false():
    p = ProviderProfile("lm", "http://localhost:1234/v1/chat/completions", "llama")
    assert not p.is_anthropic


def test_is_local_localhost():
    p = ProviderProfile("lm", "http://localhost:1234", "llama")
    assert p.is_local


def test_is_local_127():
    p = ProviderProfile("lm", "http://127.0.0.1:11434", "llama")
    assert p.is_local


def test_is_local_false():
    p = ProviderProfile("groq", "https://api.groq.com/openai/v1", "llama3")
    assert not p.is_local


def test_available_true():
    p = ProviderProfile("x", "http://url", "model")
    assert p.available


def test_available_false_no_url():
    p = ProviderProfile("x", "", "model")
    assert not p.available


def test_available_false_no_model():
    p = ProviderProfile("x", "http://url", "")
    assert not p.available


def test_provider_profile_repr():
    p = ProviderProfile("mock", "http://mock", "mock-model", api_key="key", rpm=10)
    r = repr(p)
    assert "mock" in r
    assert "mock-model" in r


def test_provider_profile_repr_no_key():
    p = ProviderProfile("mock", "http://localhost", "mock-model")
    r = repr(p)
    # local providers show 'local' or 'no-auth' depending on is_local
    assert "local" in r or "no-auth" in r


# ── _build_anthropic / _build_openai ──────────────────────────────────────────

def test_build_anthropic():
    p = ProviderProfile("ant", "https://api.anthropic.com/v1/messages", "claude-3", api_key="k")
    payload, headers = _build_anthropic(p, "system", "user", 0.5, 1000)
    assert payload["model"] == "claude-3"
    assert "x-api-key" in headers
    assert headers["x-api-key"] == "k"
    assert payload["system"] == "system"


def test_build_openai_with_key():
    p = ProviderProfile("groq", "https://api.groq.com/v1", "llama3", api_key="secret")
    payload, headers = _build_openai(p, "sys", "usr", 0.3, 2048)
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer secret"


def test_build_openai_no_key():
    p = ProviderProfile("lm", "http://localhost:1234", "local-model")
    payload, headers = _build_openai(p, "sys", "usr", 0.3, 2048)
    assert "Authorization" not in headers


# ── _extract_text ─────────────────────────────────────────────────────────────

def test_extract_text_openai_format():
    body = {"choices": [{"message": {"content": "risposta"}}]}
    result = _extract_text(body, False, "groq")
    assert result == "risposta"


def test_extract_text_anthropic_format():
    body = {"content": [{"text": "risposta anthropic"}]}
    result = _extract_text(body, True, "anthropic")
    assert result == "risposta anthropic"


def test_extract_text_malformed_openai():
    with pytest.raises(LLMError):
        _extract_text({}, False, "groq")


def test_extract_text_malformed_anthropic():
    with pytest.raises(LLMError):
        _extract_text({}, True, "anthropic")


# ── call_provider (mock HTTP) ─────────────────────────────────────────────────

def _make_profile(is_anthropic=False):
    url = "https://api.anthropic.com/v1/messages" if is_anthropic else "http://localhost:1234/v1/chat/completions"
    return ProviderProfile("test", url, "test-model", api_key="key" if is_anthropic else "")


def test_call_provider_openai_success():
    body = {"choices": [{"message": {"content": "ok"}}]}
    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(body).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = call_provider(_make_profile(False), "sys", "usr")
    assert result == "ok"


def test_call_provider_anthropic_success():
    body = {"content": [{"text": "anthropic ok"}]}
    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(body).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = call_provider(_make_profile(True), "sys", "usr")
    assert result == "anthropic ok"


def test_call_provider_http_error():
    err = urllib.error.HTTPError("url", 429, "Rate Limit", {}, None)
    err.read = lambda: b"rate limit exceeded"
    with patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(LLMError) as exc:
            call_provider(_make_profile(), "sys", "usr")
    assert exc.value.status_code == 429


def test_call_provider_url_error():
    err = urllib.error.URLError("connection refused")
    with patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(LLMError) as exc:
            call_provider(_make_profile(), "sys", "usr")
    assert "test" in exc.value.provider


def test_call_provider_generic_error():
    with patch("urllib.request.urlopen", side_effect=Exception("boom")):
        with pytest.raises(LLMError):
            call_provider(_make_profile(), "sys", "usr")


def test_call_provider_with_overrides():
    body = {"choices": [{"message": {"content": "ok"}}]}
    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(body).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = call_provider(_make_profile(), "sys", "usr", temperature=0.9, max_tokens=100)
    assert result == "ok"


# ── LLMProvider multi + retry ─────────────────────────────────────────────────

def _make_provider_with_mocks(responses: list, multi=False):
    """Crea un LLMProvider con _complete_single mockato per rispondere in sequenza."""
    p = ProviderProfile("a", "http://a.test", "model-a")
    q = ProviderProfile("b", "http://b.test", "model-b")
    provider = LLMProvider({"a": p, "b": q}, active="a", use_multi=multi, priority=["a", "b"])
    return provider


def test_complete_multi_fallback():
    """Multi-provider: prova 'a' (fallisce) poi 'b' (succede)."""
    p = ProviderProfile("a", "http://a.test", "model-a")
    q = ProviderProfile("b", "http://b.test", "model-b")
    provider = LLMProvider({"a": p, "b": q}, active="a", use_multi=True, priority=["a", "b"])

    def fake_complete_single(name, system, user, temperature, max_tokens):
        if name == "a":
            raise LLMError("a broken", provider="a", status_code=500)
        return "b ok"

    provider._complete_single = fake_complete_single
    result = provider.complete("sys", "usr")
    assert result == "b ok"


def test_complete_multi_all_fail():
    """Multi-provider: tutti falliscono → LLMError aggregato."""
    p = ProviderProfile("a", "http://a.test", "model-a")
    q = ProviderProfile("b", "http://b.test", "model-b")
    provider = LLMProvider({"a": p, "b": q}, active="a", use_multi=True, priority=["a", "b"])

    def fake_complete_single(name, system, user, temperature, max_tokens):
        raise LLMError("broken", provider=name, status_code=500)

    provider._complete_single = fake_complete_single
    with pytest.raises(LLMError, match="Tutti"):
        provider.complete("sys", "usr")


def test_retry_on_transient_errors():
    """_complete_single deve ritentare su 429/5xx."""
    p = ProviderProfile("a", "http://a.test", "model-a")
    provider = LLMProvider({"a": p}, active="a", retry_count=2, retry_backoff=0.01)

    call_count = {"n": 0}

    def fake_call(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise LLMError("rate limit", provider="a", status_code=429)
        return "ok"

    with patch("llm_provider.call_provider", side_effect=fake_call):
        with patch("time.sleep"):
            result = provider.complete("sys", "usr")
    assert result == "ok"
    assert call_count["n"] == 3


def test_retry_non_transient_raises_immediately():
    """Errore non transiente (es 400) non deve essere retentato."""
    p = ProviderProfile("a", "http://a.test", "model-a")
    provider = LLMProvider({"a": p}, active="a", retry_count=2, retry_backoff=0.01)

    call_count = {"n": 0}

    def fake_call(*args, **kwargs):
        call_count["n"] += 1
        raise LLMError("bad request", provider="a", status_code=400)

    with patch("llm_provider.call_provider", side_effect=fake_call):
        with pytest.raises(LLMError):
            provider.complete("sys", "usr")

    assert call_count["n"] == 1  # nessun retry


# ── LLMProvider.use() ─────────────────────────────────────────────────────────

def test_use_valid():
    p = ProviderProfile("a", "http://a", "model-a")
    q = ProviderProfile("b", "http://b", "model-b")
    provider = LLMProvider({"a": p, "b": q}, active="a")
    provider.use("b")
    assert provider.active_profile.name == "b"


def test_use_invalid():
    p = ProviderProfile("a", "http://a", "model-a")
    provider = LLMProvider({"a": p}, active="a")
    with pytest.raises(ValueError):
        provider.use("nonexistent")


# ── LLMProvider.list_providers() ──────────────────────────────────────────────

def test_list_providers(capsys):
    p = ProviderProfile("groq", "https://api.groq.com/v1", "llama3", api_key="k", rpm=30)
    q = ProviderProfile("lm-studio", "http://localhost:1234/v1", "local", rpm=9999)
    provider = LLMProvider({"groq": p, "lm-studio": q}, active="groq")
    provider.list_providers()
    captured = capsys.readouterr()
    assert "groq" in captured.out
    assert "lm-studio" in captured.out
    assert "attivo" in captured.out


# ── LLMProvider.from_profile() ────────────────────────────────────────────────

def test_from_profile():
    p = ProviderProfile("test", "http://test", "model")
    provider = LLMProvider.from_profile(p)
    assert provider.active_profile.name == "test"


# ── LLMProvider properties ────────────────────────────────────────────────────

def test_available_providers():
    p = ProviderProfile("a", "http://a", "model-a")
    q = ProviderProfile("b", "http://b", "model-b")
    provider = LLMProvider({"a": p, "b": q}, active="a")
    avail = provider.available_providers
    assert "a" in avail and "b" in avail


def test_repr():
    p = ProviderProfile("a", "http://a", "model-a", rpm=20)
    provider = LLMProvider({"a": p}, active="a")
    r = repr(provider)
    assert "LLMProvider" in r
    assert "model-a" in r


# ── LLMError ──────────────────────────────────────────────────────────────────

def test_llm_error_attributes():
    err = LLMError("message", provider="groq", status_code=500)
    assert err.provider == "groq"
    assert err.status_code == 500
    assert "message" in str(err)


# ── RateLimiter ───────────────────────────────────────────────────────────────

def test_rate_limiter_no_wait():
    limiter = RateLimiter(rpm=9999)
    start = time.monotonic()
    limiter.wait()
    limiter.wait()
    elapsed = time.monotonic() - start
    # Con RPM altissimo, l'attesa deve essere quasi nulla
    assert elapsed < 1.0


def test_rate_limiter_rpm_property():
    limiter = RateLimiter(rpm=60)
    assert limiter.rpm == 60


def test_rate_limiter_zero_rpm():
    """RPM=0 deve essere normalizzato a 1 (max(1, rpm))."""
    limiter = RateLimiter(rpm=0)
    assert limiter.rpm == 1


# ── load_env ──────────────────────────────────────────────────────────────────

def test_load_env_with_comments(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nFOO=bar\nBAZ=qux\n", encoding="utf-8")
    env = load_env(env_file)
    assert env["FOO"] == "bar"
    assert env["BAZ"] == "qux"


def test_load_env_quoted_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('KEY="quoted value"\nKEY2=\'single\'\n', encoding="utf-8")
    env = load_env(env_file)
    assert env["KEY"] == "quoted value"
    assert env["KEY2"] == "single"


def test_load_env_missing_file(tmp_path):
    env = load_env(tmp_path / "nonexistent.env")
    assert env == {}


def test_load_env_no_equals(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("NOVALID\nFOO=bar\n", encoding="utf-8")
    env = load_env(env_file)
    assert "FOO" in env
    assert "NOVALID" not in env


# ── discover_providers ────────────────────────────────────────────────────────

def test_discover_custom_provider():
    env = {
        "MYAPP_URL": "http://myapp.local/v1",
        "MYAPP_MODEL": "local-model",
        "MYAPP_RPM": "20",
    }
    profiles = discover_providers(env)
    assert "myapp" in profiles
    assert profiles["myapp"].rpm == 20


def test_discover_temperature_override():
    env = {
        "GROQ_URL": "https://api.groq.com/v1",
        "GROQ_MODEL": "llama3",
        "TEMPERATURE": "0.7",
    }
    profiles = discover_providers(env, default_temp=0.3)
    assert profiles["groq"].temperature == 0.7


def test_discover_api_key_aliases():
    """ANTHROPIC_API_KEY deve essere rilevato tramite alias."""
    env = {
        "ANTHROPIC_URL": "https://api.anthropic.com/v1/messages",
        "ANTHROPIC_MODEL": "claude-3",
        "ANTHROPIC_API_KEY": "my-secret-key",
    }
    profiles = discover_providers(env)
    assert "anthropic" in profiles
    assert profiles["anthropic"].api_key == "my-secret-key"


# ── LLMProvider init edge cases ───────────────────────────────────────────────

def test_provider_not_found_raises():
    p = ProviderProfile("a", "http://a", "model-a")
    with pytest.raises(ValueError, match="non trovato"):
        LLMProvider({"a": p}, active="nonexistent")


def test_provider_no_profiles_raises():
    with pytest.raises(ValueError):
        LLMProvider({})


def test_provider_priority_ordering():
    p = ProviderProfile("a", "http://a", "model-a")
    q = ProviderProfile("b", "http://b", "model-b")
    provider = LLMProvider({"a": p, "b": q}, priority=["b", "a"])
    assert provider._active == "b"


# ── from_env ──────────────────────────────────────────────────────────────────

def test_from_env_no_profiles(tmp_path):
    env_file = tmp_path / "empty.env"
    env_file.write_text("# no providers\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Nessun provider"):
        LLMProvider.from_env(env_file)


def test_from_env_with_active_provider(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "GROQ_URL=https://api.groq.com/v1\nGROQ_MODEL=llama3\n"
        "LM_STUDIO_URL=http://localhost:1234/v1\nLM_STUDIO_MODEL=local\n"
        "ACTIVE_PROVIDER=groq\n",
        encoding="utf-8",
    )
    provider = LLMProvider.from_env(env_file)
    assert provider.active_profile.name == "groq"


def test_from_env_multi_provider(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "GROQ_URL=https://api.groq.com/v1\nGROQ_MODEL=llama3\n"
        "USE_MULTI_PROVIDER=true\n",
        encoding="utf-8",
    )
    provider = LLMProvider.from_env(env_file)
    assert provider._use_multi
