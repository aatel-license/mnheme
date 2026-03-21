/**
 * MNHEME StorageEngine — localStorage-backed
 * ============================================
 * Port of storage.py. Stores JSON array in localStorage.
 * Append-only semantics: records are never modified or deleted.
 */

const STORAGE_KEY = 'mnheme_records';

export class StorageEngine {
  constructor() {
    this._records = this._load();
  }

  /** Append a record. Returns the index (offset equivalent). */
  append(record) {
    const idx = this._records.length;
    this._records.push(record);
    this._persist();
    return idx;
  }

  /** Append multiple records at once. Returns array of indices. */
  appendBatch(records) {
    const indices = [];
    for (const record of records) {
      indices.push(this._records.length);
      this._records.push(record);
    }
    this._persist();
    return indices;
  }

  /** Read a single record by index. */
  readAt(index) {
    if (index < 0 || index >= this._records.length) return null;
    return this._records[index];
  }

  /** Read multiple records by indices. */
  readMany(indices) {
    return indices.map(i => this.readAt(i));
  }

  /** Iterate all records as [index, record] pairs. */
  *scan() {
    for (let i = 0; i < this._records.length; i++) {
      yield [i, this._records[i]];
    }
  }

  /** Total number of records. */
  count() {
    return this._records.length;
  }

  /** Clear all records (for import/reset). */
  clear() {
    this._records = [];
    this._persist();
  }

  /** Estimated storage size in bytes. */
  storageSize() {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? new Blob([raw]).size : 0;
  }

  /** Persist to localStorage. */
  _persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this._records));
    } catch (e) {
      console.error('MNHEME StorageEngine: failed to persist', e);
    }
  }

  /** Load from localStorage. */
  _load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }
}
