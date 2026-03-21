"""
mnheme/llm_provider.py
======================
Provider LLM completamente agnostico, guidato da .env.

Zero dipendenze esterne — solo stdlib Python.

Funzionalità
------------
  - Carica tutti i provider dal file .env per convenzione di naming
  - Supporta sia l'API nativa Anthropic che qualsiasi endpoint OpenAI-compatibile
    (LM Studio, Ollama, SambaNova, Groq, Mistral, OpenRouter, Google AI Studio, ...)
  - Rate limiting per provider (token bucket, RPM configurabile)
  - Multi-provider con fallback automatico in cascata
  - Retry con backoff esponenziale su errori transitori
  - Selezione del provider attivo a runtime o via env

Convenzione .env
----------------
Ogni provider è definito da un blocco di variabili con prefisso comune:

    <NOME>_URL        endpoint HTTP
    <NOME>_MODEL      nome del modello
    <NOME>_API_KEY    chiave API (opzionale per istanze locali)
    <NOME>_RPM        richieste al minuto (default: 10)

Variabili globali:
    USE_MULTI_PROVIDER=true     abilita fallback a cascata
    TEMPERATURE=0.3             temperatura default per tutti i provider

Provider speciali riconosciuti automaticamente:
    - Se l'URL contiene "anthropic.com" → usa il formato nativo Anthropic
    - Tutti gli altri → formato OpenAI-compatibile
"""

from __future__ import annotations

import json
import os
import re
import time
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# ENV PARSER
# ─────────────────────────────────────────────

def load_env(path: str | Path = ".env") -> dict[str, str]:
    """
    Carica un file .env in un dizionario.
    Supporta commenti (#), stringhe con virgolette, e variabili multiriga.
    Non sovrascrive variabili già presenti nell'ambiente di sistema.
    """
    env: dict[str, str] = {}
    p = Path(path)
    if not p.exists():
        return env

    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # Sistema: variabile di ambiente ha precedenza
        env[key] = os.environ.get(key, val)

    return env


# ─────────────────────────────────────────────
# RATE LIMITER — token bucket per provider
# ─────────────────────────────────────────────

class RateLimiter:
    """
    Token bucket per rispettare il limite RPM di ogni provider.
    Thread-safe.
    """

    def __init__(self, rpm: int) -> None:
        self._rpm      = max(1, rpm)
        self._interval = 60.0 / self._rpm   # secondi tra le richieste
        self._lock     = threading.Lock()
        self._last     = 0.0

    def wait(self) -> None:
        """Blocca finché non è sicuro fare la prossima richiesta."""
        with self._lock:
            now   = time.monotonic()
            delta = now - self._last
            if delta < self._interval:
                time.sleep(self._interval - delta)
            self._last = time.monotonic()

    @property
    def rpm(self) -> int:
        return self._rpm


# ─────────────────────────────────────────────
# PROVIDER PROFILE
# ─────────────────────────────────────────────

@dataclass
class ProviderProfile:
    """
    Configurazione di un singolo provider LLM.
    Costruito automaticamente dal file .env.
    """
    name        : str
    url         : str
    model       : str
    api_key     : str = ""
    rpm         : int = 10
    temperature : float = 0.3
    max_tokens  : int = 2048
    timeout     : int = 60

    # Rilevato automaticamente dall'URL
    is_anthropic: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.is_anthropic = "anthropic.com" in self.url.lower()

    @property
    def is_local(self) -> bool:
        return "localhost" in self.url or "127.0.0.1" in self.url

    @property
    def available(self) -> bool:
        """True se il provider ha URL e model configurati."""
        return bool(self.url and self.model)

    def __repr__(self) -> str:
        auth = "no-auth" if not self.api_key else "auth"
        return (
            f"ProviderProfile(name='{self.name}'  "
            f"model='{self.model}'  "
            f"rpm={self.rpm}  "
            f"{'anthropic' if self.is_anthropic else 'openai-compat'}  "
            f"{'local' if self.is_local else auth})"
        )


# ─────────────────────────────────────────────
# ENV → PROVIDER PROFILES
# ─────────────────────────────────────────────

# Provider noti con il loro prefisso .env
_KNOWN_PREFIXES = [
    "LM_STUDIO", "LOCAL_LLM", "ANTHROPIC", "SAMBANOVA", "OPENROUTER",
    "GOOGLE_AI_STUDIO", "GROQ", "MISTRAL", "CODESTRAL", "CEREBRAS",
    "NVIDIA_NIM", "HF", "GITHUB", "COHERE", "VERCEL", "CLOUDFLARE",
    "VERTEX_AI", "FIREWORKS", "NEBIUS", "HYPERBOLIC", "TOGETHER",
    "NOVITA", "UPSTAGE", "SCALEWAY", "ALIYUN", "BASETEN", "AI21",
    "NLP_CLOUD", "MODAL", "INFERENCE_NET",
]

# Alias per le chiavi API (alcuni provider usano nomi diversi)
_KEY_ALIASES = {
    "LM_STUDIO":      ["LLM_STUDIO_KEY", "LM_STUDIO_KEY", "LM_STUDIO_API_KEY"],
    "ANTHROPIC":      ["ANTHROPIC_API_KEY"],
    "GOOGLE_AI_STUDIO": ["GOOGLE_AI_STUDIO_API_KEY"],
}


def discover_providers(
    env          : dict[str, str],
    *,
    default_temp : float = 0.3,
    default_max_tokens: int = 2048,
    default_timeout: int = 60,
) -> dict[str, ProviderProfile]:
    """
    Costruisce il dizionario dei provider disponibili leggendo il .env.

    Logica di discovery
    -------------------
    1. Cerca i prefissi noti (_KNOWN_PREFIXES)
    2. Scopre automaticamente prefissi sconosciuti con pattern *_URL/*_MODEL
    3. Per ogni prefisso crea un ProviderProfile se URL e MODEL sono presenti

    Ritorna
    -------
    dict name → ProviderProfile, solo per provider con URL e MODEL definiti.
    """
    global_temp = float(env.get("TEMPERATURE", default_temp))

    # Raccoglie tutti i prefissi presenti nell'env (noti + auto-discovery)
    discovered: set[str] = set(_KNOWN_PREFIXES)
    for key in env:
        if key.endswith("_URL") and not key.startswith("#"):
            prefix = key[:-4]  # rimuovi _URL
            discovered.add(prefix)

    profiles: dict[str, ProviderProfile] = {}

    for prefix in sorted(discovered):
        url   = env.get(f"{prefix}_URL",   "").strip()
        model = env.get(f"{prefix}_MODEL", "").strip()

        if not url or not model:
            continue

        # Cerca la API key con tutti gli alias possibili
        api_key = ""
        for alias_key in _KEY_ALIASES.get(prefix, [f"{prefix}_API_KEY", f"{prefix}_KEY"]):
            api_key = env.get(alias_key, "").strip()
            if api_key:
                break

        rpm     = int(env.get(f"{prefix}_RPM", "10") or "10")
        name    = prefix.lower().replace("_", "-")

        profiles[name] = ProviderProfile(
            name        = name,
            url         = url,
            model       = model,
            api_key     = api_key,
            rpm         = rpm,
            temperature = global_temp,
            max_tokens  = default_max_tokens,
            timeout     = default_timeout,
        )

    return profiles


# ─────────────────────────────────────────────
# LLM CLIENT — chiamata HTTP singola
# ─────────────────────────────────────────────

class LLMError(Exception):
    """Errore nella chiamata al provider LLM."""
    def __init__(self, message: str, provider: str = "", status_code: int = 0):
        super().__init__(message)
        self.provider    = provider
        self.status_code = status_code


def call_provider(
    profile     : ProviderProfile,
    system      : str,
    user        : str,
    *,
    temperature : Optional[float] = None,
    max_tokens  : Optional[int]   = None,
) -> str:
    """
    Esegue una singola chiamata HTTP al provider.
    Gestisce sia il formato Anthropic che OpenAI-compatibile.

    Parametri
    ---------
    profile     : configurazione del provider
    system      : prompt di sistema
    user        : messaggio utente
    temperature : sovrascrive il valore del profilo
    max_tokens  : sovrascrive il valore del profilo

    Ritorna
    -------
    Testo della risposta del modello.
    """
    temp   = temperature if temperature is not None else profile.temperature
    tokens = max_tokens  if max_tokens  is not None else profile.max_tokens

    if profile.is_anthropic:
        payload, headers = _build_anthropic(profile, system, user, temp, tokens)
    else:
        payload, headers = _build_openai(profile, system, user, temp, tokens)

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req  = urllib.request.Request(
        profile.url, data=data, headers=headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=profile.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise LLMError(
            f"HTTP {e.code} da {profile.name}: {err_body[:300]}",
            provider    = profile.name,
            status_code = e.code,
        ) from e
    except urllib.error.URLError as e:
        raise LLMError(
            f"Connessione fallita a {profile.name} ({profile.url}): {e.reason}",
            provider = profile.name,
        ) from e
    except Exception as e:
        raise LLMError(str(e), provider=profile.name) from e

    return _extract_text(body, profile.is_anthropic, profile.name)


def _build_anthropic(
    p: ProviderProfile, system: str, user: str, temp: float, tokens: int
) -> tuple[dict, dict]:
    payload = {
        "model":      p.model,
        "max_tokens": tokens,
        "temperature": temp,
        "system":     system,
        "messages":   [{"role": "user", "content": user}],
    }
    headers = {
        "Content-Type":      "application/json",
        "User-Agent":        "Mozilla/5.0 (compatible; MNHEME/1.0)",
        "x-api-key":         p.api_key,
        "anthropic-version": "2023-06-01",
    }
    return payload, headers


def _build_openai(
    p: ProviderProfile, system: str, user: str, temp: float, tokens: int
) -> tuple[dict, dict]:
    payload = {
        "model":       p.model,
        "max_tokens":  tokens,
        "temperature": temp,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent":   "Mozilla/5.0 (compatible; MNHEME/1.0)",
    }
    # Bearer token solo se presente (istanze locali non ne hanno bisogno)
    if p.api_key:
        headers["Authorization"] = f"Bearer {p.api_key}"
    return payload, headers


def _extract_text(body: dict, is_anthropic: bool, provider_name: str) -> str:
    """Estrae il testo dalla risposta indipendentemente dal formato."""
    try:
        if is_anthropic:
            return body["content"][0]["text"]
        else:
            return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise LLMError(
            f"Risposta malformata da {provider_name}: {str(body)[:200]}",
            provider = provider_name,
        ) from e


# ─────────────────────────────────────────────
# LLM PROVIDER — multi-provider con fallback
# ─────────────────────────────────────────────

class LLMProvider:
    """
    Provider LLM agnostico, completamente guidato dal file .env.

    Utilizzo base
    -------------
    >>> provider = LLMProvider.from_env(".env")
    >>> response = provider.complete("Sei un assistente.", "Dimmi qualcosa.")

    Selezione provider specifico
    ----------------------------
    >>> provider = LLMProvider.from_env(".env", active="groq")
    >>> provider = LLMProvider.from_env(".env", active="lm-studio")

    Multi-provider con fallback
    ---------------------------
    Se USE_MULTI_PROVIDER=true nel .env, il provider prova in cascata
    tutti i provider disponibili nell'ordine di priorità configurato.

    Parametri
    ---------
    profiles      : dizionario name → ProviderProfile
    active        : nome del provider da usare (None = primo disponibile)
    use_multi     : se True, attiva il fallback a cascata
    priority      : ordine di priorità dei provider nel fallback
    retry_count   : tentativi per provider su errori transitori (429, 503)
    retry_backoff : moltiplicatore del backoff esponenziale (secondi)
    """

    def __init__(
        self,
        profiles      : dict[str, ProviderProfile],
        *,
        active        : Optional[str] = None,
        use_multi     : bool = False,
        priority      : Optional[list[str]] = None,
        retry_count   : int = 2,
        retry_backoff : float = 1.0,
    ) -> None:
        self._profiles      = profiles
        self._use_multi     = use_multi
        self._retry_count   = retry_count
        self._retry_backoff = retry_backoff
        self._rate_limiters : dict[str, RateLimiter] = {
            name: RateLimiter(p.rpm) for name, p in profiles.items()
        }

        # Ordine di priorità per il fallback
        self._priority = priority or list(profiles.keys())

        # Provider attivo
        if active:
            if active not in profiles:
                raise ValueError(
                    f"Provider '{active}' non trovato nel .env. "
                    f"Disponibili: {list(profiles.keys())}"
                )
            self._active = active
        else:
            # Primo disponibile nell'ordine di priorità
            available = [n for n in self._priority if n in profiles]
            if not available:
                raise ValueError("Nessun provider configurato nel .env.")
            self._active = available[0]

    # ── FACTORY ──────────────────────────────

    @classmethod
    def from_env(
        cls,
        env_path      : str | Path = ".env",
        *,
        active        : Optional[str] = None,
        priority      : Optional[list[str]] = None,
        retry_count   : int = 2,
        retry_backoff : float = 1.0,
    ) -> "LLMProvider":
        """
        Costruisce il provider leggendo il file .env.

        Parametri
        ---------
        env_path  : path al file .env (default: ".env" nella working directory)
        active    : forza un provider specifico (es. "groq", "lm-studio")
        priority  : ordine di priorità per il multi-provider fallback

        Esempio
        -------
        >>> provider = LLMProvider.from_env(".env")
        >>> provider = LLMProvider.from_env(".env", active="ollama")
        >>> provider = LLMProvider.from_env(".env", priority=["groq","lm-studio","anthropic"])
        """
        env      = load_env(env_path)
        profiles = discover_providers(env)

        if not profiles:
            raise ValueError(
                f"Nessun provider trovato in '{env_path}'. "
                "Verifica che almeno un blocco <NOME>_URL + <NOME>_MODEL sia compilato."
            )

        use_multi = env.get("USE_MULTI_PROVIDER", "false").lower() == "true"

        # Legge ACTIVE_PROVIDER dal .env se non passato esplicitamente come parametro
        resolved_active = active or env.get("ACTIVE_PROVIDER") or None

        return cls(
            profiles      = profiles,
            active        = resolved_active,
            use_multi     = use_multi,
            priority      = priority,
            retry_count   = retry_count,
            retry_backoff = retry_backoff,
        )

    @classmethod
    def from_profile(cls, profile: ProviderProfile) -> "LLMProvider":
        """Crea un provider da un singolo ProviderProfile (utile per test)."""
        return cls({profile.name: profile}, active=profile.name)

    # ── COMPLETE ─────────────────────────────

    def complete(
        self,
        system      : str,
        user        : str,
        *,
        temperature : Optional[float] = None,
        max_tokens  : Optional[int]   = None,
    ) -> str:
        """
        Invia una richiesta al provider attivo.
        In modalità multi-provider, prova in cascata fino al primo successo.

        Parametri
        ---------
        system      : prompt di sistema
        user        : messaggio utente
        temperature : sovrascrive il valore del profilo
        max_tokens  : sovrascrive il valore del profilo

        Ritorna
        -------
        Testo della risposta del modello.

        Esempio
        -------
        >>> resp = provider.complete("Sei un assistente.", "Come stai?")
        """
        if self._use_multi:
            return self._complete_multi(system, user, temperature, max_tokens)
        else:
            return self._complete_single(
                self._active, system, user, temperature, max_tokens
            )

    def _complete_single(
        self,
        name        : str,
        system      : str,
        user        : str,
        temperature : Optional[float],
        max_tokens  : Optional[int],
    ) -> str:
        """Chiamata a un singolo provider con retry su errori transitori."""
        profile = self._profiles[name]
        limiter = self._rate_limiters[name]

        last_error: Optional[LLMError] = None
        for attempt in range(self._retry_count + 1):
            limiter.wait()
            try:
                return call_provider(
                    profile, system, user,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except LLMError as e:
                last_error = e
                # Retry solo su 429 (rate limit) e 5xx (errori server)
                if e.status_code in (429, 500, 502, 503, 504) and attempt < self._retry_count:
                    wait = self._retry_backoff * (2 ** attempt)
                    time.sleep(wait)
                    continue
                raise

        raise last_error  # type: ignore

    def _complete_multi(
        self,
        system      : str,
        user        : str,
        temperature : Optional[float],
        max_tokens  : Optional[int],
    ) -> str:
        """Fallback a cascata: prova i provider nell'ordine di priorità."""
        errors: list[str] = []

        # Prima prova il provider attivo, poi gli altri in priorità
        order = [self._active] + [
            n for n in self._priority
            if n != self._active and n in self._profiles
        ]

        for name in order:
            try:
                return self._complete_single(
                    name, system, user, temperature, max_tokens
                )
            except LLMError as e:
                errors.append(f"{name}: {e}")
                continue

        raise LLMError(
            f"Tutti i provider hanno fallito:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    # ── GESTIONE PROVIDER ────────────────────

    def use(self, name: str) -> "LLMProvider":
        """
        Cambia il provider attivo a runtime. Ritorna self per chaining.

        Esempio
        -------
        >>> provider.use("groq").complete(system, user)
        """
        if name not in self._profiles:
            raise ValueError(
                f"Provider '{name}' non trovato. "
                f"Disponibili: {self.available_providers}"
            )
        self._active = name
        return self

    @property
    def active_profile(self) -> ProviderProfile:
        """Profilo del provider attualmente attivo."""
        return self._profiles[self._active]

    @property
    def available_providers(self) -> list[str]:
        """Lista dei provider disponibili (URL + MODEL configurati)."""
        return list(self._profiles.keys())

    def list_providers(self) -> None:
        """Stampa tutti i provider disponibili con le loro configurazioni."""
        print(f"Provider disponibili ({len(self._profiles)}):")
        print(f"  {'NOME':<22} {'MODELLO':<35} {'RPM':>5}  {'TIPO':<16}  STATUS")
        print(f"  {'─'*22} {'─'*35} {'─'*5}  {'─'*16}  {'─'*6}")
        for name, p in self._profiles.items():
            tipo     = "anthropic" if p.is_anthropic else "openai-compat"
            auth     = "no-key" if not p.api_key else "key-set"
            active   = " ← attivo" if name == self._active else ""
            local    = " [local]" if p.is_local else ""
            print(
                f"  {name:<22} {p.model:<35} {p.rpm:>5}  {tipo:<16}  "
                f"{auth}{local}{active}"
            )

    # ── INFO ─────────────────────────────────

    def __repr__(self) -> str:
        p = self.active_profile
        return (
            f"LLMProvider(active='{self._active}'  "
            f"model='{p.model}'  "
            f"rpm={p.rpm}  "
            f"multi={self._use_multi}  "
            f"providers={len(self._profiles)})"
        )