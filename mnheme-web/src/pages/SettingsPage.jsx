import Settings from '../components/Settings';
import ExportImport from '../components/ExportImport';
import ThemeSelector from '../components/ThemeSelector';
import { useState } from 'react';

export default function SettingsPage() {
  const [tab, setTab] = useState('appearance');

  return (
    <div>
      <div className="view-header">
        <h1>Settings</h1>
        <p className="view-desc">Personalise your journal and configure integrations.</p>
      </div>

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
