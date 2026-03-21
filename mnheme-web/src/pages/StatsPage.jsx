import Stats from '../components/Stats';
import Timeline from '../components/Timeline';
import { useState } from 'react';

export default function StatsPage() {
  const [tab, setTab] = useState('stats');

  return (
    <div>
      <div className="view-header">
        <h1>Stats & Timeline</h1>
        <p className="view-desc">Statistiche del database e timeline emotiva.</p>
      </div>

      <div className="tab-bar">
        <button className={`tab-btn ${tab === 'stats' ? 'active' : ''}`} onClick={() => setTab('stats')}>
          Dashboard
        </button>
        <button className={`tab-btn ${tab === 'timeline' ? 'active' : ''}`} onClick={() => setTab('timeline')}>
          Timeline
        </button>
      </div>

      {tab === 'stats'    && <Stats />}
      {tab === 'timeline' && <Timeline />}
    </div>
  );
}
