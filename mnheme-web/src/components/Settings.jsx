import { useState } from 'react';
import { useSettings } from '../hooks/useSettings';
import { PROVIDER_PRESETS } from '../core/constants';

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
