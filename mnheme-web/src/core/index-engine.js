/**
 * MNHEME IndexEngine — in-memory indices with localStorage persistence
 * =====================================================================
 * Port of index.py. Maintains 6 indices for O(1) lookup:
 *   concept, feeling, tag, cf (concept+feeling), timeline, word (inverted full-text)
 */

const INDEX_KEY = 'mnheme_index';
const MIN_TOKEN_LEN = 3;
const TOKEN_RE = /[a-zA-ZàáâäãåæçèéêëìíîïòóôöõùúûüýÿñÀÁÂÄÃÅÆÇÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝÑ]{3,}/g;

/** Extract unique lowercase tokens from text. */
export function tokenize(text) {
  const matches = text.match(TOKEN_RE);
  if (!matches) return new Set();
  return new Set(matches.map(m => m.toLowerCase()));
}

export class IndexEngine {
  constructor() {
    this._concept  = {};  // { concept: [idx, ...] }
    this._feeling  = {};  // { feeling: [idx, ...] }
    this._tag      = {};  // { tag: [idx, ...] }
    this._cf       = {};  // { "concept\0feeling": [idx, ...] }
    this._timeline = [];  // [ [timestamp, idx], ... ]
    this._all      = [];  // [ idx, ... ]
    this._word     = {};  // { word: [idx, ...] } — inverted full-text
    this._dirty    = false;
  }

  /** Index a single record at given index. */
  indexRecord(idx, record) {
    const concept   = record.concept || '';
    const feeling   = record.feeling || '';
    const tags      = record.tags || [];
    const timestamp = record.timestamp || '';

    (this._concept[concept]  ||= []).push(idx);
    (this._feeling[feeling]  ||= []).push(idx);

    const cfKey = concept + '\0' + feeling;
    (this._cf[cfKey] ||= []).push(idx);

    this._timeline.push([timestamp, idx]);
    this._all.push(idx);

    for (const tag of tags) {
      if (tag) (this._tag[tag] ||= []).push(idx);
    }

    // Inverted index: tokenize content + concept + note
    const tokens = new Set([
      ...tokenize(record.content || ''),
      ...tokenize(record.concept || ''),
      ...tokenize(record.note || ''),
    ]);
    for (const token of tokens) {
      (this._word[token] ||= []).push(idx);
    }

    this._dirty = true;
  }

  /** Rebuild all indices from an iterable of [idx, record] pairs. */
  rebuild(scanIter) {
    this._concept  = {};
    this._feeling  = {};
    this._tag      = {};
    this._cf       = {};
    this._timeline = [];
    this._all      = [];
    this._word     = {};

    let count = 0;
    for (const [idx, record] of scanIter) {
      this.indexRecord(idx, record);
      count++;
    }
    this._timeline.sort((a, b) => a[0].localeCompare(b[0]));
    this._dirty = true;
    return count;
  }

  // ── QUERY ──────────────────────────────────

  offsetsByConcept(concept, { feeling = null, oldestFirst = false } = {}) {
    let offsets;
    if (feeling) {
      offsets = [...(this._cf[concept + '\0' + feeling] || [])];
    } else {
      offsets = [...(this._concept[concept] || [])];
    }
    return oldestFirst ? offsets : offsets.reverse();
  }

  offsetsByFeeling(feeling, { oldestFirst = false } = {}) {
    const offsets = [...(this._feeling[feeling] || [])];
    return oldestFirst ? offsets : offsets.reverse();
  }

  offsetsByTag(tag, limit = null) {
    const offsets = [...(this._tag[tag] || [])].reverse();
    return limit ? offsets.slice(0, limit) : offsets;
  }

  offsetsByWord(word, limit = null) {
    const offsets = [...(this._word[word.toLowerCase()] || [])].reverse();
    return limit ? offsets.slice(0, limit) : offsets;
  }

  hasWord(word) {
    return word.toLowerCase() in this._word;
  }

  allOffsets({ oldestFirst = false } = {}) {
    return oldestFirst ? [...this._all] : [...this._all].reverse();
  }

  timelineOffsets(concept) {
    const conceptSet = new Set(this._concept[concept] || []);
    return this._timeline.filter(([, off]) => conceptSet.has(off)).map(([, off]) => off);
  }

  // ── STATS ──────────────────────────────────

  allConcepts() {
    return Object.keys(this._concept).sort();
  }

  allFeelings() {
    return Object.keys(this._feeling).sort();
  }

  allTags() {
    return Object.keys(this._tag).sort();
  }

  count({ concept = null, feeling = null } = {}) {
    if (concept && feeling) {
      return (this._cf[concept + '\0' + feeling] || []).length;
    }
    if (concept) return (this._concept[concept] || []).length;
    if (feeling) return (this._feeling[feeling] || []).length;
    return this._all.length;
  }

  conceptFeelingMatrix() {
    const matrix = {};
    for (const [key, offsets] of Object.entries(this._cf)) {
      const [concept, feeling] = key.split('\0');
      if (!matrix[concept]) matrix[concept] = {};
      matrix[concept][feeling] = offsets.length;
    }
    return matrix;
  }

  feelingDistribution() {
    const dist = {};
    for (const [feeling, offsets] of Object.entries(this._feeling)) {
      dist[feeling] = offsets.length;
    }
    return dist;
  }

  // ── PERSISTENCE ────────────────────────────

  tryLoad(recordCount) {
    try {
      const raw = localStorage.getItem(INDEX_KEY);
      if (!raw) return false;
      const data = JSON.parse(raw);
      if (data.record_count !== recordCount) return false;

      this._concept  = data.concept  || {};
      this._feeling  = data.feeling  || {};
      this._tag      = data.tag      || {};
      this._word     = data.word     || {};
      this._all      = data.all      || [];
      this._timeline = (data.timeline || []).map(x => [x[0], x[1]]);
      this._cf       = data.cf       || {};
      this._dirty    = false;
      return true;
    } catch {
      return false;
    }
  }

  flush(recordCount) {
    if (!this._dirty) return;
    try {
      const payload = JSON.stringify({
        record_count: recordCount,
        concept:  this._concept,
        feeling:  this._feeling,
        tag:      this._tag,
        word:     this._word,
        cf:       this._cf,
        all:      this._all,
        timeline: this._timeline,
      });
      localStorage.setItem(INDEX_KEY, payload);
      this._dirty = false;
    } catch (e) {
      console.error('MNHEME IndexEngine: failed to flush', e);
    }
  }
}
