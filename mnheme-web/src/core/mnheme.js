/**
 * MNHEME MemoryDB — The Human Memory Database
 * =============================================
 * Port of mnheme.py. Coordinates StorageEngine + IndexEngine.
 * All data in localStorage. Append-only, immutable.
 */

import { StorageEngine } from './storage.js';
import { IndexEngine, tokenize } from './index-engine.js';
import { FEELINGS, MEDIA_TYPES } from './constants.js';

// ── Checksum helper ──────────────────────────

async function sha256(text) {
  const data = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

// ── Errors ───────────────────────────────────

export class MnhemeError extends Error {
  constructor(message) {
    super(message);
    this.name = 'MnhemeError';
  }
}

export class InvalidFeelingError extends MnhemeError {
  constructor(message) {
    super(message);
    this.name = 'InvalidFeelingError';
  }
}

// ── Memory object ────────────────────────────

export class Memory {
  constructor({ memory_id, concept, feeling, media_type, content, note, tags, timestamp, checksum }) {
    this.memory_id  = memory_id;
    this.concept    = concept;
    this.feeling    = feeling;
    this.media_type = media_type;
    this.content    = content;
    this.note       = note;
    this.tags       = tags;
    this.timestamp  = timestamp;
    this.checksum   = checksum;
    Object.freeze(this);
  }

  toDict() {
    return {
      memory_id:  this.memory_id,
      concept:    this.concept,
      feeling:    this.feeling,
      media_type: this.media_type,
      content:    this.content,
      note:       this.note,
      tags:       [...this.tags],
      timestamp:  this.timestamp,
      checksum:   this.checksum,
    };
  }
}

// ── MemoryDB ─────────────────────────────────

export class MemoryDB {
  constructor() {
    this._storage = new StorageEngine();
    this._index   = new IndexEngine();

    // Try loading persisted index, else rebuild
    const count = this._storage.count();
    if (!this._index.tryLoad(count)) {
      this._index.rebuild(this._storage.scan());
      this._index.flush(this._storage.count());
    }
  }

  // ── WRITE ──────────────────────────────────

  async remember(concept, feeling, content, { mediaType = 'text', note = '', tags = [] } = {}) {
    const feelingVal   = this._validateFeeling(feeling);
    const mediaTypeVal = this._validateMediaType(mediaType);
    const conceptClean = concept.trim();
    const tagsList     = tags.filter(t => t.trim()).map(t => t.trim());

    if (!conceptClean) throw new MnhemeError('Il concetto non puo essere vuoto.');
    if (!content)      throw new MnhemeError('Il contenuto non puo essere vuoto.');

    const memory_id = crypto.randomUUID();
    const timestamp = new Date().toISOString();
    const checksum  = await sha256(content);

    const record = {
      memory_id, concept: conceptClean, feeling: feelingVal,
      media_type: mediaTypeVal, content, note, tags: tagsList,
      timestamp, checksum,
    };

    const idx = this._storage.append(record);
    this._index.indexRecord(idx, record);
    this._index.flush(this._storage.count());

    return new Memory(record);
  }

  // ── READ ───────────────────────────────────

  recall(concept, { feeling = null, limit = null, oldestFirst = false } = {}) {
    const fVal = feeling ? this._validateFeeling(feeling) : null;
    const offsets = this._index.offsetsByConcept(
      concept.trim(), { feeling: fVal, oldestFirst }
    );
    return this._loadOffsets(offsets, limit);
  }

  recallByFeeling(feeling, { limit = null, oldestFirst = false } = {}) {
    const fVal = this._validateFeeling(feeling);
    const offsets = this._index.offsetsByFeeling(fVal, { oldestFirst });
    return this._loadOffsets(offsets, limit);
  }

  recallAll({ limit = null, oldestFirst = false } = {}) {
    const offsets = this._index.allOffsets({ oldestFirst });
    return this._loadOffsets(offsets, limit);
  }

  recallByTag(tag, { limit = 100, oldestFirst = false } = {}) {
    let offsets = this._index.offsetsByTag(tag.trim(), limit);
    if (oldestFirst) offsets = offsets.reverse();
    return this._loadOffsets(offsets, null);
  }

  search(text, { inContent = true, inConcept = true, inNote = true, limit = null } = {}) {
    const needle = text.trim().toLowerCase();
    if (!needle) return [];

    const tokens = tokenize(needle);

    // If all tokens exist in inverted index, use it (O(k))
    if (tokens.size > 0 && [...tokens].every(t => this._index.hasWord(t))) {
      const sets = [...tokens].map(t => new Set(this._index.offsetsByWord(t)));
      let candidateOffsets = [...sets[0]].filter(off => sets.every(s => s.has(off)));
      candidateOffsets.sort((a, b) => b - a);

      if (limit) candidateOffsets = candidateOffsets.slice(0, limit);

      const records = this._storage.readMany(candidateOffsets);
      const results = [];
      for (const r of records) {
        if (!r) continue;
        let match = false;
        if (inContent && (r.content || '').toLowerCase().includes(needle)) match = true;
        if (!match && inConcept && (r.concept || '').toLowerCase().includes(needle)) match = true;
        if (!match && inNote && (r.note || '').toLowerCase().includes(needle)) match = true;
        if (match) results.push(new Memory(r));
      }
      return results;
    }

    // Fallback: linear scan
    const results = [];
    for (const [, record] of this._storage.scan()) {
      let match = false;
      if (inContent && (record.content || '').toLowerCase().includes(needle)) match = true;
      if (inConcept && (record.concept || '').toLowerCase().includes(needle)) match = true;
      if (inNote && (record.note || '').toLowerCase().includes(needle)) match = true;
      if (match) {
        results.push(new Memory(record));
        if (limit && results.length >= limit) break;
      }
    }
    return results.reverse();
  }

  // ── STATS ──────────────────────────────────

  listConcepts() {
    const matrix = this._index.conceptFeelingMatrix();
    const result = [];
    for (const concept of Object.keys(matrix).sort()) {
      const feelings = matrix[concept];
      const total = Object.values(feelings).reduce((a, b) => a + b, 0);
      result.push({ concept, total, feelings });
    }
    return result;
  }

  listFeelings() {
    const matrix = this._index.conceptFeelingMatrix();
    const fToData = {};
    for (const [concept, feelings] of Object.entries(matrix)) {
      for (const [feeling, count] of Object.entries(feelings)) {
        if (!fToData[feeling]) {
          fToData[feeling] = { feeling, total: 0, concepts: [] };
        }
        fToData[feeling].total += count;
        fToData[feeling].concepts.push(concept);
      }
    }
    return Object.values(fToData).sort((a, b) => b.total - a.total);
  }

  conceptTimeline(concept) {
    const offsets = this._index.timelineOffsets(concept.trim());
    if (!offsets.length) return [];
    const records = this._storage.readMany(offsets);
    return records
      .filter(r => r !== null)
      .map(r => ({
        timestamp: r.timestamp,
        feeling:   r.feeling,
        note:      r.note || '',
        tags:      r.tags || [],
      }));
  }

  feelingDistribution() {
    const dist = this._index.feelingDistribution();
    return Object.fromEntries(
      Object.entries(dist).sort(([, a], [, b]) => b - a)
    );
  }

  count({ concept = null, feeling = null } = {}) {
    const fVal = feeling ? this._validateFeeling(feeling) : null;
    return this._index.count({ concept, feeling: fVal });
  }

  // ── EXPORT / IMPORT ────────────────────────

  exportJSON({ concept = null, feeling = null, includeContent = true } = {}) {
    let memories;
    if (concept) {
      memories = this.recall(concept, { feeling });
    } else if (feeling) {
      memories = this.recallByFeeling(feeling);
    } else {
      memories = this.recallAll();
    }

    const data = memories.map(m => {
      const d = m.toDict();
      if (!includeContent) delete d.content;
      return d;
    });

    return {
      exported_at: new Date().toISOString(),
      memories: data,
    };
  }

  async importJSON(data) {
    const entries = data.memories || (Array.isArray(data) ? data : []);

    // Get existing IDs
    const existingIds = new Set();
    for (const [, rec] of this._storage.scan()) {
      existingIds.add(rec.memory_id);
    }

    let imported = 0;
    for (const entry of entries) {
      if (existingIds.has(entry.memory_id)) continue;

      const record = {
        memory_id:  entry.memory_id,
        concept:    entry.concept,
        feeling:    entry.feeling,
        media_type: entry.media_type || 'text',
        content:    entry.content || '',
        note:       entry.note || '',
        tags:       entry.tags || [],
        timestamp:  entry.timestamp,
        checksum:   entry.checksum || '',
      };

      const idx = this._storage.append(record);
      this._index.indexRecord(idx, record);
      existingIds.add(entry.memory_id);
      imported++;
    }

    if (imported > 0) {
      this._index.flush(this._storage.count());
    }

    return imported;
  }

  // ── INFO ───────────────────────────────────

  storageInfo() {
    const size = this._storage.storageSize();
    return {
      storage_type:    'localStorage',
      storage_size_bytes: size,
      storage_size_kb: Math.round(size / 1024 * 100) / 100,
      total_records:   this.count(),
    };
  }

  // ── INTERNAL ───────────────────────────────

  _validateFeeling(feeling) {
    const val = String(feeling).trim().toLowerCase();
    if (!FEELINGS.includes(val)) {
      throw new InvalidFeelingError(
        `Sentimento '${val}' non valido. Ammessi: ${FEELINGS.join(', ')}`
      );
    }
    return val;
  }

  _validateMediaType(mediaType) {
    const val = String(mediaType).trim().toLowerCase();
    if (!MEDIA_TYPES.includes(val)) {
      throw new MnhemeError(
        `Tipo media '${val}' non valido. Ammessi: ${MEDIA_TYPES.join(', ')}`
      );
    }
    return val;
  }

  _loadOffsets(offsets, limit) {
    if (limit) offsets = offsets.slice(0, limit);
    if (!offsets.length) return [];
    const records = this._storage.readMany(offsets);
    return records.filter(r => r !== null).map(r => new Memory(r));
  }
}
