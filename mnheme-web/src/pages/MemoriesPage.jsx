import { useState } from 'react';
import { FEELINGS, FEELING_LABELS } from '../core/constants';
import { useMemoryDB } from '../hooks/useMemoryDB';
import MemoryList from '../components/MemoryList';
import Search from '../components/Search';
import SectionGuide from '../components/SectionGuide';

export default function MemoriesPage() {
  const { recallAll, recallByFeeling, recall, revision } = useMemoryDB();
  const [filter, setFilter]       = useState({ feeling: '', concept: '', limit: 50, oldestFirst: false });
  const [memories, setMemories]   = useState(null);
  const [tab, setTab]             = useState('browse');

  const handleBrowse = () => {
    let mems;
    if (filter.concept.trim() && filter.feeling) {
      mems = recall(filter.concept.trim(), {
        feeling: filter.feeling, limit: filter.limit, oldestFirst: filter.oldestFirst
      });
    } else if (filter.concept.trim()) {
      mems = recall(filter.concept.trim(), { limit: filter.limit, oldestFirst: filter.oldestFirst });
    } else if (filter.feeling) {
      mems = recallByFeeling(filter.feeling, { limit: filter.limit, oldestFirst: filter.oldestFirst });
    } else {
      mems = recallAll({ limit: filter.limit, oldestFirst: filter.oldestFirst });
    }
    setMemories(mems);
  };

  return (
    <div>
      <div className="view-header">
        <h1>Memories</h1>
        <p className="view-desc">Esplora, filtra e cerca nei ricordi.</p>
      </div>

      <SectionGuide title="Come esplorare i ricordi?">
        <p>
          Questa sezione ti permette di sfogliare e cercare in tutti i tuoi ricordi.
        </p>
        <p>
          <strong>Browse</strong> &mdash; Filtra i ricordi per concetto, sentimento o entrambi.
          Puoi scegliere l'ordine (più recenti o più vecchi prima) e il numero massimo di risultati.
        </p>
        <p>
          <strong>Search</strong> &mdash; Cerca parole specifiche nel contenuto dei ricordi
          usando la ricerca full-text, oppure cerca per tag specifico.
        </p>
        <div className="guide-note">
          Tutti i ricordi sono immutabili: una volta scritti, non possono essere modificati o cancellati.
          Questo riflette il principio di MNHEME &mdash; la memoria si stratifica, non si sovrascrive.
        </div>
      </SectionGuide>

      <div className="tab-bar">
        <button className={`tab-btn ${tab === 'browse' ? 'active' : ''}`} onClick={() => setTab('browse')}>
          Browse
        </button>
        <button className={`tab-btn ${tab === 'search' ? 'active' : ''}`} onClick={() => setTab('search')}>
          Search
        </button>
      </div>

      {tab === 'browse' && (
        <div>
          <div className="filter-bar">
            <div className="filter-group">
              <label>CONCEPT</label>
              <input
                type="text"
                value={filter.concept}
                onChange={e => setFilter(p => ({ ...p, concept: e.target.value }))}
                placeholder="Tutti..."
              />
            </div>
            <div className="filter-group">
              <label>FEELING</label>
              <select
                value={filter.feeling}
                onChange={e => setFilter(p => ({ ...p, feeling: e.target.value }))}
              >
                <option value="">Tutti</option>
                {FEELINGS.map(f => (
                  <option key={f} value={f}>{FEELING_LABELS[f]}</option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label>LIMIT</label>
              <input
                type="number"
                value={filter.limit}
                onChange={e => setFilter(p => ({ ...p, limit: Number(e.target.value) }))}
                min={1} max={500}
                style={{ width: 72 }}
              />
            </div>
            <div className="filter-group">
              <label>ORDER</label>
              <select
                value={filter.oldestFirst ? 'asc' : 'desc'}
                onChange={e => setFilter(p => ({ ...p, oldestFirst: e.target.value === 'asc' }))}
              >
                <option value="desc">Newest first</option>
                <option value="asc">Oldest first</option>
              </select>
            </div>
            <button className="btn-primary" onClick={handleBrowse}>Fetch</button>
          </div>

          {memories !== null && (
            <div>
              <div style={{ marginBottom: 8, fontSize: 11, color: 'var(--muted)' }}>
                {memories.length} risultati
              </div>
              <MemoryList memories={memories} />
            </div>
          )}
        </div>
      )}

      {tab === 'search' && <Search />}
    </div>
  );
}
