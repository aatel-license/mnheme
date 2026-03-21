import { useState } from 'react';
import { FEELINGS, FEELING_LABELS } from '../core/constants';
import { useMemoryDB } from '../hooks/useMemoryDB';
import MemoryCard from './MemoryCard';

export default function Remember() {
  const { remember, refresh } = useMemoryDB();
  const [form, setForm] = useState({
    concept: '', feeling: '', content: '', note: '', tags: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [result, setResult]   = useState(null);

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.concept.trim() || !form.feeling || !form.content.trim()) {
      setError('Concept, feeling e content sono obbligatori.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const tags = form.tags.split(',').map(t => t.trim()).filter(Boolean);
      const mem = await remember(form.concept, form.feeling, form.content, {
        note: form.note, tags,
      });
      setResult(mem);
      setForm({ concept: '', feeling: '', content: '', note: '', tags: '' });
      refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setForm({ concept: '', feeling: '', content: '', note: '', tags: '' });
    setError(null);
    setResult(null);
  };

  const tagList = form.tags.split(',').map(t => t.trim()).filter(Boolean);

  return (
    <div>
      <form onSubmit={handleSubmit} className="form-card">
        <div className="form-row">
          <div className="field">
            <label>CONCEPT <span className="required">*</span></label>
            <input
              type="text" name="concept"
              value={form.concept} onChange={handleChange}
              placeholder="Debito, Famiglia, Lavoro..."
              autoComplete="off"
            />
          </div>
          <div className="field">
            <label>FEELING <span className="required">*</span></label>
            <select name="feeling" value={form.feeling} onChange={handleChange}>
              <option value="">-- select --</option>
              {FEELINGS.map(f => (
                <option key={f} value={f}>{FEELING_LABELS[f]} ({f})</option>
              ))}
            </select>
          </div>
        </div>

        <div className="field">
          <label>CONTENT <span className="required">*</span></label>
          <textarea
            name="content" rows={4}
            value={form.content} onChange={handleChange}
            placeholder="Scrivi il ricordo..."
          />
          <div className="char-count">{form.content.length} chars</div>
        </div>

        <div className="form-row">
          <div className="field">
            <label>NOTE <span className="optional">opzionale</span></label>
            <input
              type="text" name="note"
              value={form.note} onChange={handleChange}
              placeholder="Contesto, annotazioni..."
            />
          </div>
          <div className="field">
            <label>TAGS <span className="optional">separati da virgola</span></label>
            <input
              type="text" name="tags"
              value={form.tags} onChange={handleChange}
              placeholder="casa, 2024, urgente..."
            />
            {tagList.length > 0 && (
              <div className="tag-preview">
                {tagList.map((t, i) => (
                  <span key={i} className="tag-chip">{t}</span>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <><span className="loading" /> Saving...</> : '* Remember'}
          </button>
          <button type="button" className="btn-ghost" onClick={handleClear}>Clear</button>
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
          <div className="response-label" style={{ marginBottom: 8 }}>Ricordo Salvato</div>
          <MemoryCard memory={result} />
        </div>
      )}
    </div>
  );
}
