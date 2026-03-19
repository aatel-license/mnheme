"""
test_llm_provider.py
====================
Test del sistema provider senza rete reale — usa un mock .env
"""
import sys, os, time, threading
sys.path.insert(0, os.path.dirname(__file__))

from llm_provider import (
    load_env, discover_providers, LLMProvider,
    ProviderProfile, RateLimiter, call_provider, LLMError
)
from brain import Brain
from mnheme import MemoryDB, Feeling

sep = "═" * 65

# ─────────────────────────────────────────────
# Mock .env in memoria
# ─────────────────────────────────────────────
MOCK_ENV_CONTENT = """
TEMPERATURE=0.3
USE_MULTI_PROVIDER=false

LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=mistral-7b-local
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

# Scrivi il mock .env
mock_env_path = "/tmp/_test_mnheme.env"
with open(mock_env_path, "w") as f:
    f.write(MOCK_ENV_CONTENT)

print(sep)
print("  MNHEME LLMProvider — Test sistema provider")
print(sep)

# ── 1. load_env ─────────────────────────────
print("\n[1] load_env()")
env = load_env(mock_env_path)
print(f"  Variabili caricate: {len(env)}")
for k, v in env.items():
    masked = v[:6] + "..." if len(v) > 6 and "KEY" in k and v else (v or "(vuota)")
    print(f"  {k:<30} = {masked}")

# ── 2. discover_providers ───────────────────
print("\n[2] discover_providers()")
profiles = discover_providers(env)
print(f"  Provider trovati: {len(profiles)}")
for name, p in profiles.items():
    print(f"  {p}")

# ── 3. Anthropic auto-detection ─────────────
print("\n[3] Rilevamento automatico Anthropic")
ant = profiles.get("anthropic")
if ant:
    print(f"  is_anthropic: {ant.is_anthropic}  (atteso: True)")
    print(f"  is_local:     {ant.is_local}       (atteso: False)")

lm = profiles.get("lm-studio")
if lm:
    print(f"  lm-studio is_anthropic: {lm.is_anthropic}  (atteso: False)")
    print(f"  lm-studio is_local:     {lm.is_local}       (atteso: True)")

# ── 4. LLMProvider.from_env ─────────────────
print("\n[4] LLMProvider.from_env()")
provider = LLMProvider.from_env(mock_env_path)
print(f"  {provider}")
print(f"  Provider attivo: {provider._active}")
print(f"  Disponibili: {provider.available_providers}")

print("\n  Lista completa:")
provider.list_providers()

# ── 5. Cambio provider a runtime ────────────
print("\n[5] Cambio provider a runtime")
provider.use("groq")
print(f"  Attivo ora: {provider.active_profile.name}")
provider.use("lm-studio")
print(f"  Attivo ora: {provider.active_profile.name}")

# ── 6. Forzare provider specifico ───────────
print("\n[6] LLMProvider.from_env(active='anthropic')")
p2 = LLMProvider.from_env(mock_env_path, active="anthropic")
print(f"  Attivo: {p2.active_profile.name}")
print(f"  Modello: {p2.active_profile.model}")

# ── 7. Provider sconosciuto → errore chiaro ─
print("\n[7] Provider inesistente → ValueError")
try:
    LLMProvider.from_env(mock_env_path, active="openai")
except ValueError as e:
    print(f"  ✓ Errore corretto: {str(e)[:80]}")

# ── 8. RateLimiter ──────────────────────────
print("\n[8] RateLimiter (60 RPM = 1 req/sec)")
limiter = RateLimiter(rpm=60)
times = []
for _ in range(3):
    t0 = time.perf_counter()
    limiter.wait()
    times.append((time.perf_counter() - t0) * 1000)
print(f"  Gap tra chiamate: {[f'{t:.1f}ms' for t in times]}")
print(f"  RPM configurato: {limiter.rpm}")

# ── 9. Multi-provider ───────────────────────
print("\n[9] Multi-provider fallback")
env_multi = dict(env)
env_multi["USE_MULTI_PROVIDER"] = "true"
profiles_multi = discover_providers(env_multi)
p_multi = LLMProvider(
    profiles_multi,
    use_multi = True,
    priority  = ["lm-studio", "groq", "anthropic"],
)
print(f"  multi={p_multi._use_multi}")
print(f"  priority={p_multi._priority[:5]}")
print(f"  {p_multi}")

# ── 10. Priority personalizzata ─────────────
print("\n[10] Priority personalizzata")
p_prio = LLMProvider.from_env(
    mock_env_path,
    priority = ["groq", "anthropic", "lm-studio", "mistral"]
)
print(f"  Provider attivo (primo in priority): {p_prio._active}")
print(f"  Priority: {p_prio._priority}")

# ── 11. Mock LLM → Brain ────────────────────
print(f"\n{sep}")
print("  [11] Integrazione Brain con Mock Provider")
print(sep)

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
        # perceive
        if '"concept"' in user and '"feeling"' in user:
            return _json.dumps({
                "concept":  "Test",
                "feeling":  "curiosità",
                "tags":     ["mock", "test"],
                "enriched": "Testo arricchito dalla percezione cognitiva."
            })
        # keyword
        if '"keywords"' in user:
            return _json.dumps({"keywords": ["test"], "concepts": ["Test"]})
        return "Risposta mock generata correttamente.\n\nCertezza: alta — dati diretti dai ricordi."

db    = MemoryDB(":memory:")
mock  = MockProvider()
brain = Brain(db, mock)

# perceive
r = brain.perceive("Sto testando il sistema MNHEME con provider agnostico.")
print(f"\n  perceive() → concept={r.extracted_concept}  feeling={r.extracted_feeling}")

db.remember("Famiglia", Feeling.AMORE, "Pranzo della domenica.")
db.remember("Debito",   Feeling.ANSIA, "La banca ha chiamato.")

# ask
ans = brain.ask("Come sto?")
print(f"  ask()     → ricordi usati: {len(ans.memories_used)}  provider: {ans.provider_used}")

# reflect
ref = brain.reflect("Famiglia")
print(f"  reflect() → arc='{ref.arc or '(nessuno)'}'")

# dream
drm = brain.dream(n_memories=3)
print(f"  dream()   → {len(drm.memories)} memorie  provider: {drm.provider_used}")

# introspect
intro = brain.introspect()
print(f"  introspect() → {intro.total_memories} memorie  dominanti: {intro.dominant_concepts}")

print(f"\n  Chiamate LLM totali: {len(mock.calls)}")
print(f"  {brain}")

# Cleanup
os.remove(mock_env_path)

print(f"\n{sep}")
print("  Tutti i test passati.")
print(sep)
