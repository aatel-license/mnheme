import { useState } from 'react';
import { FEELING_LABELS, FEELING_COLORS } from '../core/constants';
import { useMemoryDB } from '../hooks/useMemoryDB';

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function Timeline() {
  const { conceptTimeline, listConcepts } = useMemoryDB();
  const [concept, setConcept]   = useState('');
  const [entries, setEntries]   = useState(null);

  const concepts = listConcepts();

  const loadTimeline = (e) => {
    e?.preventDefault();
    if (!concept.trim()) return;
    const data = conceptTimeline(concept.trim());
    setEntries(data);
  };

  return (
    <div>
      <form onSubmit={loadTimeline} className="filter-bar">
        <div className="filter-group" style={{ flex: 1 }}>
          <label>CONCEPT</label>
          <input
            type="text"
            value={concept}
            onChange={e => setConcept(e.target.value)}
            placeholder="Debito, Famiglia, Lavoro..."
            list="tl-concept-list"
          />
          <datalist id="tl-concept-list">
            {concepts.map(c => (
              <option key={c.concept} value={c.concept} />
            ))}
          </datalist>
        </div>
        <button type="submit" className="btn-primary">Load timeline</button>
      </form>

      {entries !== null && entries.length === 0 && (
        <div className="empty-state">Nessun dato per "{concept}"</div>
      )}

      {entries && entries.length > 0 && (
        <div>
          <div style={{ marginBottom: 14, fontSize: 11, color: 'var(--muted)', letterSpacing: '0.1em' }}>
            {entries.length} entries for <span style={{ color: 'var(--accent)' }}>{concept}</span>
          </div>
          <div className="timeline-track">
            {entries.map((entry, i) => {
              const color = FEELING_COLORS[entry.feeling] || 'var(--accent)';
              return (
                <div className="timeline-entry" key={i} style={{ animationDelay: `${i * 40}ms` }}>
                  <div className="timeline-dot" style={{ borderColor: color, background: color }} />
                  <div className="timeline-card">
                    <div className="timeline-meta">
                      <span
                        className="memory-feeling"
                        style={{ borderColor: color, color }}
                      >
                        {FEELING_LABELS[entry.feeling] || entry.feeling}
                      </span>
                      <span className="timeline-ts">{formatDate(entry.timestamp)}</span>
                    </div>
                    {entry.note && (
                      <div className="timeline-note">{entry.note}</div>
                    )}
                    {entry.tags.length > 0 && (
                      <div className="timeline-tags">
                        {entry.tags.map((t, j) => (
                          <span key={j} className="memory-tag">{t}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
