import { useState } from 'react';
import { useBrain } from '../hooks/useBrain';
import { useMemoryDB } from '../hooks/useMemoryDB';

export default function Reflect() {
  const { listConcepts } = useMemoryDB();
  const { reflect, loading, error } = useBrain();
  const [concept, setConcept] = useState('');
  const [result, setResult]   = useState(null);

  const concepts = listConcepts();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!concept.trim() || loading) return;
    try {
      const r = await reflect(concept.trim());
      setResult(r);
    } catch {
      // error from hook
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="form-card">
        <div className="form-row">
          <div className="field">
            <label>CONCETTO DA ANALIZZARE</label>
            <input
              type="text"
              value={concept}
              onChange={e => setConcept(e.target.value)}
              placeholder="Debito, Famiglia, Lavoro..."
              list="concept-list"
            />
            <datalist id="concept-list">
              {concepts.map(c => (
                <option key={c.concept} value={c.concept} />
              ))}
            </datalist>
          </div>
          <div className="field" style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button type="submit" className="btn-primary" disabled={loading || !concept.trim()}>
              {loading ? <><span className="loading" /> Reflecting...</> : '~ Reflect'}
            </button>
          </div>
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
          <div className="response-area visible">
            <div className="response-label">Riflessione su "{result.concept}"</div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{result.reflection}</div>
            {result.arc && (
              <div style={{ marginTop: 12, fontSize: 11, color: 'var(--amber)' }}>
                Arco emotivo: {result.arc}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
