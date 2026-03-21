import { useState, useCallback, useRef } from 'react';
import { getDB } from '../core/singleton.js';

export function useMemoryDB() {
  const dbRef = useRef(getDB());
  const db = dbRef.current;

  const [revision, setRevision] = useState(0);
  const bump = useCallback(() => setRevision(r => r + 1), []);

  const remember = useCallback(async (concept, feeling, content, opts) => {
    const mem = await db.remember(concept, feeling, content, opts);
    bump();
    return mem;
  }, [db, bump]);

  const recall = useCallback((...args) => db.recall(...args), [db]);
  const recallAll = useCallback((opts) => db.recallAll(opts), [db]);
  const recallByFeeling = useCallback((f, opts) => db.recallByFeeling(f, opts), [db]);
  const recallByTag = useCallback((t, opts) => db.recallByTag(t, opts), [db]);
  const search = useCallback((q, opts) => db.search(q, opts), [db]);
  const importJSON = useCallback(async (data) => {
    const count = await db.importJSON(data);
    bump();
    return count;
  }, [db, bump]);

  return {
    db,
    revision,
    remember,
    recall,
    recallAll,
    recallByFeeling,
    recallByTag,
    search,
    importJSON,
    refresh: bump,
    count:              (opts) => db.count(opts),
    listConcepts:       () => db.listConcepts(),
    listFeelings:       () => db.listFeelings(),
    feelingDistribution:() => db.feelingDistribution(),
    conceptTimeline:    (c) => db.conceptTimeline(c),
    storageInfo:        () => db.storageInfo(),
    exportJSON:         (opts) => db.exportJSON(opts),
  };
}
