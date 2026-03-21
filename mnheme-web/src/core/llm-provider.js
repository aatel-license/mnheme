/**
 * MNHEME LLM Provider — simplified browser-side
 * ================================================
 * Port of llm_provider.py. Uses fetch() for HTTP calls.
 * Supports OpenAI-compatible and Anthropic formats.
 */

const SETTINGS_KEY = 'mnheme_settings';

export class LLMError extends Error {
  constructor(message, { provider = '', statusCode = 0 } = {}) {
    super(message);
    this.name = 'LLMError';
    this.provider = provider;
    this.statusCode = statusCode;
  }
}

export class LLMProvider {
  constructor({ url, model, apiKey = '', temperature = 0.3, maxTokens = 2048 }) {
    this.url         = url;
    this.model       = model;
    this.apiKey      = apiKey;
    this.temperature = temperature;
    this.maxTokens   = maxTokens;
    this.isAnthropic = url.toLowerCase().includes('anthropic.com');
    this.name        = this.isAnthropic ? 'anthropic' : 'openai-compat';
  }

  /** Create from localStorage settings. */
  static fromSettings() {
    try {
      const raw = localStorage.getItem(SETTINGS_KEY);
      if (!raw) return null;
      const settings = JSON.parse(raw);
      if (!settings.url || !settings.model) return null;
      return new LLMProvider({
        url:         settings.url,
        model:       settings.model,
        apiKey:      settings.apiKey || '',
        temperature: settings.temperature ?? 0.3,
        maxTokens:   settings.maxTokens ?? 2048,
      });
    } catch {
      return null;
    }
  }

  /** Complete a system+user prompt. Returns the response text. */
  async complete(system, user) {
    let payload, headers;

    if (this.isAnthropic) {
      payload = {
        model:       this.model,
        max_tokens:  this.maxTokens,
        temperature: this.temperature,
        system:      system,
        messages:    [{ role: 'user', content: user }],
      };
      headers = {
        'Content-Type':      'application/json',
        'x-api-key':         this.apiKey,
        'anthropic-version': '2023-06-01',
      };
    } else {
      payload = {
        model:       this.model,
        max_tokens:  this.maxTokens,
        temperature: this.temperature,
        messages: [
          { role: 'system', content: system },
          { role: 'user',   content: user },
        ],
      };
      headers = {
        'Content-Type': 'application/json',
      };
      if (this.apiKey) {
        headers['Authorization'] = `Bearer ${this.apiKey}`;
      }
    }

    let res;
    try {
      res = await fetch(this.url, {
        method:  'POST',
        headers,
        body:    JSON.stringify(payload),
      });
    } catch (e) {
      throw new LLMError(
        `Connessione fallita a ${this.url}: ${e.message}`,
        { provider: this.name }
      );
    }

    if (!res.ok) {
      const errText = await res.text().catch(() => '');
      throw new LLMError(
        `HTTP ${res.status} da ${this.name}: ${errText.slice(0, 300)}`,
        { provider: this.name, statusCode: res.status }
      );
    }

    const body = await res.json();

    try {
      if (this.isAnthropic) {
        return body.content[0].text;
      } else {
        return body.choices[0].message.content;
      }
    } catch (e) {
      throw new LLMError(
        `Risposta malformata da ${this.name}: ${JSON.stringify(body).slice(0, 200)}`,
        { provider: this.name }
      );
    }
  }

  /** Quick connection test. Returns { ok: true } or { ok: false, error: string }. */
  async testConnection() {
    try {
      const reply = await this.complete(
        'You are a test assistant.',
        'Reply with just the word OK.'
      );
      return { ok: true, reply: reply.trim() };
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }
}
