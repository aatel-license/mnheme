import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { THEMES, DEFAULT_THEME, THEME_IDS } from '../core/themes.js';

const THEME_KEY = 'mnheme_theme';
const ThemeContext = createContext(null);

function loadThemeId() {
  try {
    const id = localStorage.getItem(THEME_KEY);
    return THEME_IDS.includes(id) ? id : DEFAULT_THEME;
  } catch {
    return DEFAULT_THEME;
  }
}

function applyTheme(themeId) {
  const theme = THEMES[themeId];
  if (!theme) return;
  const root = document.documentElement;
  root.setAttribute('data-theme', themeId);
  for (const [prop, value] of Object.entries(theme.vars)) {
    root.style.setProperty(prop, value);
  }
}

export function ThemeProvider({ children }) {
  const [themeId, setThemeId] = useState(loadThemeId);

  useEffect(() => {
    applyTheme(themeId);
  }, [themeId]);

  const setTheme = useCallback((id) => {
    if (!THEME_IDS.includes(id)) return;
    localStorage.setItem(THEME_KEY, id);
    setThemeId(id);
  }, []);

  const value = { themeId, setTheme, themes: THEMES, themeIds: THEME_IDS };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be inside <ThemeProvider>');
  return ctx;
}
