import { useState } from 'react';
import { useBrain } from '../hooks/useBrain';
import MemoryList from './MemoryList';

export default function Ask() {
  const [question, setQuestion] = useState('');
  const { ask, loading, error } = useBrain();
  const [result, setResult]     = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;
    try {
      const r = await ask(question.trim());
      setResult(r);
    } catch {
      // error from hook
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="form-card">
        <div className="field">
          <label>DOMANDA (RAG)</label>
          <textarea
            rows={3}
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Come mi sento rispetto al denaro? C'è qualcosa di irrisolto con la mia famiglia?"
            disabled={loading}
          />
        </div>
        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={loading || !question.trim()}>
            {loading ? <><span className="loading" /> Thinking...</> : '? Ask'}
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
          <div className="response-area visible">
            <div className="response-label">Risposta</div>
            {result.answer}
            {result.confidence && (
              <div style={{ marginTop: 12, fontSize: 11, color: 'var(--amber)' }}>
                Certezza: {result.confidence}
              </div>
            )}
          </div>
          {result.memoriesUsed.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <div className="response-label" style={{ marginBottom: 8 }}>
                Ricordi utilizzati ({result.memoriesUsed.length})
              </div>
              <MemoryList memories={result.memoriesUsed} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
