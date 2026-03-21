import Stats from '../components/Stats';
import Timeline from '../components/Timeline';
import SectionGuide from '../components/SectionGuide';
import { useState } from 'react';

export default function StatsPage() {
  const [tab, setTab] = useState('stats');

  return (
    <div>
      <div className="view-header">
        <h1>Stats & Timeline</h1>
        <p className="view-desc">Statistiche del database e timeline emotiva.</p>
      </div>

      <SectionGuide title="Cosa trovo qui?">
        <p>
          <strong>Dashboard</strong> &mdash; Una panoramica del tuo diario: quanti ricordi hai,
          quanti concetti e sentimenti diversi hai esplorato, e quanto spazio occupa il database.
          Include la distribuzione emotiva (quali emozioni prevalgono) e la mappa dei concetti.
        </p>
        <p>
          <strong>Timeline</strong> &mdash; Scegli un concetto e visualizza come le tue emozioni
          a riguardo si sono evolute nel tempo, in ordine cronologico. Ogni punto della timeline
          mostra il sentimento, la data e le note associate.
        </p>
        <div className="guide-note">
          La timeline è particolarmente utile prima di usare Reflect: ti dà un colpo d'occhio
          visivo sull'evoluzione emotiva, mentre Reflect ne fa un'analisi profonda con l'IA.
        </div>
      </SectionGuide>

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
