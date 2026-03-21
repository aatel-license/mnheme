import { useState } from 'react';
import { useBrain } from '../hooks/useBrain';
import { useMemoryDB } from '../hooks/useMemoryDB';
import MemoryCard from './MemoryCard';

export default function Perceive() {
  const [text, setText] = useState('');
  const { perceive, loading, error } = useBrain();
  const { refresh } = useMemoryDB();
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    try {
      const r = await perceive(text.trim());
      setResult(r);
      refresh();
      setText('');
    } catch {
      // error is in the hook
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="form-card">
        <div className="field">
          <label>COSA STAI VIVENDO?</label>
          <textarea
            rows={4}
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Scrivi liberamente un pensiero, un'emozione, un ricordo..."
            disabled={loading}
          />
          <div className="char-count">{text.length} chars</div>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={loading || !text.trim()}>
            {loading ? <><span className="loading" /> Perceiving...</> : '> Perceive'}
          </button>
        </div>
      </form>

      {error && (
        <div className="response-area visible error">
          <div className="response-label">Errore</div>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <div className="response-label" style={{ marginBottom: 8 }}>Ricordo Creato</div>
          <div className="result-meta">
            <span className="tag-chip">Concetto: {result.concept}</span>
            <span className="tag-chip">Sentimento: {result.feeling}</span>
            {result.tags.map((t, i) => (
              <span key={i} className="tag-chip">#{t}</span>
            ))}
          </div>
          <MemoryCard memory={result.memory} />
        </div>
      )}
    </div>
  );
}
