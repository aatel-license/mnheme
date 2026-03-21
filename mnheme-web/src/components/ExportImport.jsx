import { useState, useRef } from 'react';
import { useMemoryDB } from '../hooks/useMemoryDB';

export default function ExportImport() {
  const { exportJSON, importJSON, refresh } = useMemoryDB();
  const fileRef = useRef(null);
  const [status, setStatus]   = useState(null);
  const [loading, setLoading] = useState(false);

  const handleExport = () => {
    const data = exportJSON();
    const count = data.memories.length;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `mnheme_export_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setStatus({ type: 'success', msg: `Esportati ${count} ricordi.` });
  };

  const handleImport = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setStatus(null);

    try {
      const text = await file.text();
      const data = JSON.parse(text);
      const count = await importJSON(data);
      refresh();
      setStatus({ type: 'success', msg: `Importati ${count} nuovi ricordi.` });
    } catch (err) {
      setStatus({ type: 'error', msg: `Errore importazione: ${err.message}` });
    } finally {
      setLoading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  return (
    <div>
      <div className="form-card">
        <div className="section-title" style={{ marginBottom: 16 }}>ESPORTA</div>
        <p style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 16 }}>
          Scarica tutti i ricordi come file JSON. Utile per backup o migrazione.
        </p>
        <div className="form-actions">
          <button className="btn-primary" onClick={handleExport}>
            Export JSON
          </button>
        </div>
      </div>

      <div className="form-card" style={{ marginTop: 20 }}>
        <div className="section-title" style={{ marginBottom: 16 }}>IMPORTA</div>
        <p style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 16 }}>
          Importa ricordi da un file JSON esportato. I duplicati (stesso memory_id) vengono ignorati.
        </p>
        <div className="field">
          <label>FILE JSON</label>
          <input
            type="file"
            accept=".json"
            ref={fileRef}
            onChange={handleImport}
            disabled={loading}
            style={{ padding: 8 }}
          />
        </div>
        {loading && (
          <div style={{ fontSize: 12, color: 'var(--amber)' }}>
            <span className="loading" /> Importazione in corso...
          </div>
        )}
      </div>

      {status && (
        <div className={`response-area visible ${status.type === 'error' ? 'error' : ''}`}
             style={{ marginTop: 16 }}>
          <div className="response-label">
            {status.type === 'success' ? 'Completato' : 'Errore'}
          </div>
          {status.msg}
        </div>
      )}
    </div>
  );
}
