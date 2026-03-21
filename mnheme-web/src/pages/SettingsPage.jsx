import Settings from '../components/Settings';
import ExportImport from '../components/ExportImport';
import ThemeSelector from '../components/ThemeSelector';
import SectionGuide from '../components/SectionGuide';
import { useState } from 'react';

export default function SettingsPage() {
  const [tab, setTab] = useState('appearance');

  return (
    <div>
      <div className="view-header">
        <h1>Settings</h1>
        <p className="view-desc">Personalizza il tuo diario e configura le integrazioni.</p>
      </div>

      <SectionGuide title="Guida alle impostazioni">
        <p>
          <strong>Appearance</strong> &mdash; Scegli il tema visivo del tuo diario tra 5 stili diversi.
          La scelta viene salvata automaticamente.
        </p>
        <p>
          <strong>LLM Provider</strong> &mdash; Configura il modello di intelligenza artificiale
          che alimenta Perceive, Ask, Reflect e Dream. Puoi usare provider locali gratuiti
          (LM Studio, Ollama) o servizi cloud. Seleziona un preset oppure inserisci manualmente
          URL, modello e chiave API.
        </p>
        <p>
          <strong>Export / Import</strong> &mdash; Esporta tutti i tuoi ricordi come file JSON
          per backup o migrazione. Puoi reimportarli in qualsiasi momento; i duplicati vengono
          ignorati automaticamente.
        </p>
        <div className="guide-note">
          Senza un LLM configurato, potrai comunque usare Remember (salvataggio manuale),
          Browse, Search e Stats. Le funzioni cognitive (Perceive, Ask, Reflect, Dream)
          richiedono un provider LLM attivo.
        </div>
      </SectionGuide>

      <div className="tab-bar">
        <button className={`tab-btn ${tab === 'appearance' ? 'active' : ''}`} onClick={() => setTab('appearance')}>
          Appearance
        </button>
        <button className={`tab-btn ${tab === 'provider' ? 'active' : ''}`} onClick={() => setTab('provider')}>
          LLM Provider
        </button>
        <button className={`tab-btn ${tab === 'data' ? 'active' : ''}`} onClick={() => setTab('data')}>
          Export / Import
        </button>
      </div>

      {tab === 'appearance' && <ThemeSelector />}
      {tab === 'provider'   && <Settings />}
      {tab === 'data'       && <ExportImport />}
    </div>
  );
}
