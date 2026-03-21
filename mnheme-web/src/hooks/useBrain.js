import { useState, useCallback, useRef } from 'react';
import { Brain } from '../core/brain.js';
import { getDB } from '../core/singleton.js';

export function useBrain() {
  const dbRef = useRef(getDB());
  const brainRef = useRef(new Brain(dbRef.current));

  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [result, setResult]   = useState(null);

  const run = useCallback(async (fn) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await fn();
      setResult(r);
      return r;
    } catch (e) {
      setError(e.message || String(e));
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const perceive = useCallback(
    (text, opts) => run(() => brainRef.current.perceive(text, opts)),
    [run]
  );

  const ask = useCallback(
    (question, opts) => run(() => brainRef.current.ask(question, opts)),
    [run]
  );

  const reflect = useCallback(
    (concept) => run(() => brainRef.current.reflect(concept)),
    [run]
  );

  const dream = useCallback(
    (n) => run(() => brainRef.current.dream(n)),
    [run]
  );

  return { perceive, ask, reflect, dream, loading, error, result };
}
