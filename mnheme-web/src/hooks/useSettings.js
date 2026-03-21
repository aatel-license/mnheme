import { useState, useCallback } from 'react';
import { LLMProvider } from '../core/llm-provider.js';

const SETTINGS_KEY = 'mnheme_settings';

function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function useSettings() {
  const [settings, setSettingsState] = useState(loadSettings);

  const updateSettings = useCallback((updates) => {
    setSettingsState(prev => {
      const next = { ...prev, ...updates };
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  const testConnection = useCallback(async () => {
    const current = loadSettings();
    if (!current.url || !current.model) {
      return { ok: false, error: 'URL e modello sono obbligatori.' };
    }
    const provider = new LLMProvider({
      url:         current.url,
      model:       current.model,
      apiKey:      current.apiKey || '',
      temperature: current.temperature ?? 0.3,
      maxTokens:   current.maxTokens ?? 2048,
    });
    return provider.testConnection();
  }, []);

  const isConfigured = Boolean(settings.url && settings.model);

  return { settings, updateSettings, testConnection, isConfigured };
}
