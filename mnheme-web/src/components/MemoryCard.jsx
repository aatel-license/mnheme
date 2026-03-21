import { FEELING_LABELS, FEELING_COLORS } from '../core/constants';

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function MemoryCard({ memory, style }) {
  const feelingColor = FEELING_COLORS[memory.feeling] || '#4ade80';

  return (
    <div className="memory-card" style={style}>
      <div className="memory-card-header">
        <span className="memory-concept">{memory.concept}</span>
        <span
          className="memory-feeling"
          style={{ borderColor: feelingColor, color: feelingColor }}
        >
          {FEELING_LABELS[memory.feeling] || memory.feeling}
        </span>
        <span className="memory-mediatype">
          {(memory.media_type || 'text').toUpperCase()}
        </span>
        <span className="memory-ts">{formatDate(memory.timestamp)}</span>
      </div>
      <div className="memory-content">{memory.content}</div>
      {memory.note && (
        <div className="memory-note">{memory.note}</div>
      )}
      {memory.tags && memory.tags.length > 0 && (
        <div className="memory-tags">
          {memory.tags.map((tag, i) => (
            <span key={i} className="memory-tag">{tag}</span>
          ))}
        </div>
      )}
      <div className="memory-id">{memory.memory_id}</div>
    </div>
  );
}
