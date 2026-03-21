/**
 * Shared MemoryDB singleton.
 * Ensures all hooks use the same instance.
 */
import { MemoryDB } from './mnheme.js';

let _instance = null;

export function getDB() {
  if (!_instance) _instance = new MemoryDB();
  return _instance;
}
