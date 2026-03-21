import { useState } from 'react';
import { useSettings } from '../hooks/useSettings';
import { PROVIDER_PRESETS } from '../core/constants';
import SectionGuide from './SectionGuide';

export default function Settings() {
  const { settings, updateSettings, testConnection, isConfigured } = useSettings();
  const [testing, setTesting]     = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    updateSettings({ [name]: name === 'temperature' || name === 'maxTokens'
      ? Number(value) : value });
  };

  const handlePreset = (e) => {
    const name = e.target.value;
    if (!name) return;
    const preset = PROVIDER_PRESETS[name];
    if (preset) {
      updateSettings({ url: preset.url, model: preset.model || settings.model || '' });
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    const result = await testConnection();
    setTestResult(result);
    setTesting(false);
  };

  return (
    <div>
      <SectionGuide title="Quali provider LLM sono gratuiti?">
        <p>
          MNHEME funziona con qualsiasi provider LLM. Ecco i migliori <strong>gratuiti</strong>,
          divisi per categoria.
        </p>

        <p style={{ marginTop: 12, marginBottom: 4 }}><strong>Gratuiti e locali (nessun limite)</strong></p>
        <div className="guide-provider-grid">
          <div className="guide-provider-card">
            <div className="guide-provider-name">LM Studio</div>
            <div className="guide-provider-detail">GUI desktop, modelli GGUF da HuggingFace. Nessuna API key necessaria. Limite = solo il tuo hardware.</div>
            <div className="guide-provider-tag free">Gratuito</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">Ollama</div>
            <div className="guide-provider-detail">CLI, supporta Llama, Mistral, DeepSeek, Qwen, Gemma e altri. Nessuna API key. Limite = solo il tuo hardware.</div>
            <div className="guide-provider-tag free">Gratuito</div>
          </div>
        </div>

        <p style={{ marginTop: 16, marginBottom: 4 }}><strong>Free tier cloud (non scadono)</strong></p>
        <div className="guide-provider-grid">
          <div className="guide-provider-card">
            <div className="guide-provider-name">Google AI Studio</div>
            <div className="guide-provider-detail">Il free tier più generoso. Gemini 2.5 Pro: 5 RPM, 100 richieste/giorno. Flash: 10 RPM, 250/giorno. Context 1M token.</div>
            <div className="guide-provider-tag free">Gratuito</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">Mistral</div>
            <div className="guide-provider-detail">Piano "Experiment": 1 miliardo di token/mese. Tutti i modelli inclusi, anche Codestral. Solo verifica telefono.</div>
            <div className="guide-provider-tag free">Gratuito</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">Groq</div>
            <div className="guide-provider-detail">~30 RPM. LLaMA 3.3 70B: ~500K token/giorno. Velocità eccezionale: inference hardware dedicato.</div>
            <div className="guide-provider-tag free">Gratuito</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">Cerebras</div>
            <div className="guide-provider-detail">1M token/giorno. Inference ultra-rapida a 2600+ token/sec. Context fino a 64K.</div>
            <div className="guide-provider-tag free">Gratuito</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">OpenRouter</div>
            <div className="guide-provider-detail">~27 modelli gratuiti (ID con suffisso :free). 20 RPM, 50 richieste/giorno sui modelli free.</div>
            <div className="guide-provider-tag free">Gratuito</div>
          </div>
        </div>

        <p style={{ marginTop: 16, marginBottom: 4 }}><strong>Crediti iniziali (si esauriscono)</strong></p>
        <div className="guide-provider-grid">
          <div className="guide-provider-card">
            <div className="guide-provider-name">Together AI</div>
            <div className="guide-provider-detail">Fino a $100 in crediti alla registrazione. Ampia scelta di modelli open-source.</div>
            <div className="guide-provider-tag credits">$100 crediti</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">Anthropic</div>
            <div className="guide-provider-detail">$5 alla registrazione. Claude Haiku, Sonnet, Opus. Studenti: fino a $300.</div>
            <div className="guide-provider-tag credits">$5 crediti</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">SambaNova</div>
            <div className="guide-provider-detail">$5 crediti (~30M token su Llama 8B). Scadenza: 30 giorni.</div>
            <div className="guide-provider-tag credits">$5 / 30gg</div>
          </div>
          <div className="guide-provider-card">
            <div className="guide-provider-name">Fireworks AI</div>
            <div className="guide-provider-detail">$1 in crediti iniziali. Modelli a partire da $0.20/M token.</div>
            <div className="guide-provider-tag credits">$1 crediti</div>
          </div>
        </div>

        <div className="guide-note" style={{ marginTop: 14 }}>
          <strong>Consiglio:</strong> per iniziare senza costi, usa LM Studio o Ollama in locale.
          Come fallback cloud, Google AI Studio e Groq sono le scelte migliori.
          Seleziona un preset dal menu qui sotto per configurare automaticamente l'URL.
        </div>
      </SectionGuide>

      <div className="form-card">
        <div className="field">
          <label>PROVIDER PRESET</label>
          <select onChange={handlePreset} defaultValue="">
            <option value="">-- Scegli un preset --</option>
            {Object.keys(PROVIDER_PRESETS).map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <div className="field">
            <label>ENDPOINT URL <span className="required">*</span></label>
            <input
              type="text" name="url"
              value={settings.url || ''}
              onChange={handleChange}
              placeholder="https://api.openrouter.ai/v1/chat/completions"
            />
          </div>
          <div className="field">
            <label>MODEL <span className="required">*</span></label>
            <input
              type="text" name="model"
              value={settings.model || ''}
              onChange={handleChange}
              placeholder="gpt-4, claude-3-opus, llama-3..."
            />
          </div>
        </div>

        <div className="field">
          <label>API KEY <span className="optional">opzionale per provider locali</span></label>
          <input
            type="password" name="apiKey"
            value={settings.apiKey || ''}
            onChange={handleChange}
            placeholder="sk-..."
            autoComplete="off"
          />
        </div>

        <div className="form-row">
          <div className="field">
            <label>TEMPERATURE</label>
            <input
              type="number" name="temperature"
              value={settings.temperature ?? 0.3}
              onChange={handleChange}
              min="0" max="2" step="0.1"
            />
          </div>
          <div className="field">
            <label>MAX TOKENS</label>
            <input
              type="number" name="maxTokens"
              value={settings.maxTokens ?? 2048}
              onChange={handleChange}
              min="100" max="16384" step="100"
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            className="btn-primary"
            onClick={handleTest}
            disabled={testing || !isConfigured}
          >
            {testing ? <><span className="loading" /> Testing...</> : '@ Test Connection'}
          </button>
        </div>
      </div>

      {testResult && (
        <div className={`response-area visible ${testResult.ok ? '' : 'error'}`}>
          <div className="response-label">
            {testResult.ok ? 'Connessione riuscita' : 'Connessione fallita'}
          </div>
          {testResult.ok
            ? `Il provider ha risposto: "${testResult.reply}"`
            : testResult.error
          }
        </div>
      )}

      <div className="form-card" style={{ marginTop: 20 }}>
        <div className="section-title" style={{ marginBottom: 12 }}>STATO CONFIGURAZIONE</div>
        <div className="storage-row">
          <span className="storage-key">Provider</span>
          <span className="storage-val">
            {settings.url ? (settings.url.includes('anthropic') ? 'Anthropic' : 'OpenAI-compatible') : '—'}
          </span>
        </div>
        <div className="storage-row">
          <span className="storage-key">URL</span>
          <span className="storage-val">{settings.url || '—'}</span>
        </div>
        <div className="storage-row">
          <span className="storage-key">Model</span>
          <span className="storage-val">{settings.model || '—'}</span>
        </div>
        <div className="storage-row">
          <span className="storage-key">API Key</span>
          <span className="storage-val">{settings.apiKey ? '****' + settings.apiKey.slice(-4) : '—'}</span>
        </div>
      </div>
    </div>
  );
}
