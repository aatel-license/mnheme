import { useState } from 'react';

export default function SectionGuide({ title, children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="section-guide">
      <button
        className="section-guide-toggle"
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
      >
        <span className="section-guide-icon">?</span>
        <span>{open ? 'Nascondi guida' : title || 'Come funziona?'}</span>
        <span className={`section-guide-chevron ${open ? 'open' : ''}`}>&#9662;</span>
      </button>
      {open && (
        <div className="section-guide-body">
          {children}
        </div>
      )}
    </div>
  );
}
