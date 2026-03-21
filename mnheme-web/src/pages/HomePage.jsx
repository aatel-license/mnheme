import Perceive from '../components/Perceive';
import MemoryList from '../components/MemoryList';
import { useMemoryDB } from '../hooks/useMemoryDB';

export default function HomePage() {
  const { recallAll, revision } = useMemoryDB();
  const recentMemories = recallAll({ limit: 5 });

  return (
    <div>
      <div className="view-header">
        <h1>Perceive</h1>
        <p className="view-desc">
          Scrivi liberamente. Il cervello di MNHEME analizza, cataloga e arricchisce il ricordo.
        </p>
      </div>

      <Perceive />

      {recentMemories.length > 0 && (
        <div style={{ marginTop: 32 }}>
          <div className="section-title">ULTIMI RICORDI</div>
          <MemoryList memories={recentMemories} />
        </div>
      )}
    </div>
  );
}
