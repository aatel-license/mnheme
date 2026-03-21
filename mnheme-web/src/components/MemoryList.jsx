import MemoryCard from './MemoryCard';

export default function MemoryList({ memories, emptyMessage = 'Nessun ricordo trovato.' }) {
  if (!memories || memories.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">*</div>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="memories-grid">
      {memories.map((m, i) => (
        <MemoryCard
          key={m.memory_id}
          memory={m}
          style={{ animationDelay: `${i * 30}ms` }}
        />
      ))}
    </div>
  );
}
