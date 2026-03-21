import { useState } from 'react';
import Ask from '../components/Ask';
import Reflect from '../components/Reflect';
import Remember from '../components/Remember';
import { useBrain } from '../hooks/useBrain';

function DreamPanel() {
  const { dream, loading, error } = useBrain();
  const [result, setResult] = useState(null);

  const handleDream = async () => {
    try {
      const r = await dream();
      setResult(r);
    } catch {
      // error from hook
    }
  };

  return (
    <div>
      <div className="form-card">
        <p style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 16 }}>
          Il cervello prende ricordi distanti e cerca connessioni inattese.
          Simula il processo onirico di consolidamento della memoria.
        </p>
        <div className="form-actions">
          <button className="btn-primary" onClick={handleDream} disabled={loading}>
            {loading ? <><span className="loading" /> Dreaming...</> : '~ Dream'}
          </button>
        </div>
      </div>

      {error && (
        <div className="response-area visible error" style={{ marginTop: 12 }}>
          <div className="response-label">Errore</div>
          {error}
        </div>
      )}

      {result && (
        <div className="response-area visible" style={{ marginTop: 12 }}>
          <div className="response-label">Connessioni Oniriche</div>
          <div style={{ whiteSpace: 'pre-wrap' }}>{result.connections}</div>
        </div>
      )}
    </div>
  );
}

export default function BrainPage() {
  const [tab, setTab] = useState('ask');

  return (
    <div>
      <div className="view-header">
        <h1>Brain</h1>
        <p className="view-desc">
          Il cervello cognitivo di MNHEME: interroga, rifletti, ricorda manualmente, sogna.
        </p>
      </div>

      <div className="tab-bar">
        <button className={`tab-btn ${tab === 'ask' ? 'active' : ''}`} onClick={() => setTab('ask')}>
          Ask (RAG)
        </button>
        <button className={`tab-btn ${tab === 'reflect' ? 'active' : ''}`} onClick={() => setTab('reflect')}>
          Reflect
        </button>
        <button className={`tab-btn ${tab === 'remember' ? 'active' : ''}`} onClick={() => setTab('remember')}>
          Remember
        </button>
        <button className={`tab-btn ${tab === 'dream' ? 'active' : ''}`} onClick={() => setTab('dream')}>
          Dream
        </button>
      </div>

      {tab === 'ask'      && <Ask />}
      {tab === 'reflect'  && <Reflect />}
      {tab === 'remember' && <Remember />}
      {tab === 'dream'    && <DreamPanel />}
    </div>
  );
}
