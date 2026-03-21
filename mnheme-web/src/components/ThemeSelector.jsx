import { useTheme } from '../hooks/useTheme';

/** Small swatches showing 4 representative colors from each theme. */
function Swatches({ vars }) {
  const colors = [vars['--bg'], vars['--accent'], vars['--text'], vars['--sidebar-bg']];
  return (
    <div className="theme-swatches">
      {colors.map((c, i) => (
        <span key={i} className="theme-swatch" style={{ background: c }} />
      ))}
    </div>
  );
}

export default function ThemeSelector() {
  const { themeId, setTheme, themes, themeIds } = useTheme();

  return (
    <div>
      <div className="form-card">
        <div className="section-title" style={{ marginBottom: 16 }}>Appearance</div>
        <p style={{ fontSize: 14, color: 'var(--muted)', marginBottom: 20, lineHeight: 1.6 }}>
          Choose a visual theme for your journal. The selected theme is saved
          automatically and applied on every visit.
        </p>

        <div className="theme-grid">
          {themeIds.map(id => {
            const t = themes[id];
            const isActive = id === themeId;
            return (
              <div
                key={id}
                className={`theme-card${isActive ? ' active' : ''}`}
                onClick={() => setTheme(id)}
                role="button"
                tabIndex={0}
                onKeyDown={e => e.key === 'Enter' && setTheme(id)}
                aria-pressed={isActive}
              >
                {isActive && <span className="theme-check" aria-hidden="true">&#10003;</span>}
                <div className="theme-card-name">{t.name}</div>
                <div className="theme-card-desc">{t.description}</div>
                <Swatches vars={t.vars} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
