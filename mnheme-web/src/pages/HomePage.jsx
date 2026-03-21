import Perceive from '../components/Perceive';
import MemoryList from '../components/MemoryList';
import SectionGuide from '../components/SectionGuide';
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

      <SectionGuide title="Come funziona Perceive?">
        <p>
          <strong>Perceive</strong> trasforma i tuoi pensieri grezzi in ricordi strutturati.
          È l'unica funzione che <em>scrive</em> nel tuo diario.
        </p>
        <ol className="guide-steps">
          <li>Scrivi liberamente quello che stai vivendo, pensando o provando</li>
          <li>L'intelligenza artificiale analizza il testo ed estrae un <strong>concetto chiave</strong> (es. "Famiglia", "Lavoro"), un <strong>sentimento</strong> e dei <strong>tag</strong> tematici</li>
          <li>Il testo viene riscritto con maggiore profondità psicologica</li>
          <li>Il ricordo viene salvato in modo permanente e immutabile &mdash; non potrà mai essere modificato o cancellato</li>
        </ol>
        <div className="guide-note">
          I 15 sentimenti riconosciuti sono: gioia, tristezza, rabbia, paura, nostalgia, amore, malinconia, serenità, sorpresa, ansia, gratitudine, vergogna, orgoglio, noia, curiosità.
        </div>
      </SectionGuide>

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
