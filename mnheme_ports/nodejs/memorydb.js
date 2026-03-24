// mnheme/nodejs/memorydb.js
// ==========================
// MemoryDB — public API for MNHEME
//
// Usage:
//   const { MemoryDB, Feeling } = require('./memorydb');
//   const db = await MemoryDB.open('mente.mnheme');
//   const mem = await db.remember('Debito', Feeling.ANSIA, 'Ho firmato il mutuo.');
//   const list = await db.recall('Debito');

'use strict';

const crypto = require('node:crypto');
const { StorageEngine } = require('./storage');
const { IndexEngine   } = require('./index');

// ── Feeling constants ─────────────────────────────────────────────
const Feeling = Object.freeze({
    GIOIA:       'gioia',
    TRISTEZZA:   'tristezza',
    RABBIA:      'rabbia',
    PAURA:       'paura',
    NOSTALGIA:   'nostalgia',
    AMORE:       'amore',
    MALINCONIA:  'malinconia',
    SERENITA:    'serenità',
    SORPRESA:    'sorpresa',
    ANSIA:       'ansia',
    GRATITUDINE: 'gratitudine',
    VERGOGNA:    'vergogna',
    ORGOGLIO:    'orgoglio',
    NOIA:        'noia',
    CURIOSITA:   'curiosità',
});

const VALID_FEELINGS = new Set(Object.values(Feeling));

// ── MemoryDB ──────────────────────────────────────────────────────
class MemoryDB {
    /**
     * @param {StorageEngine} storage
     * @param {IndexEngine}   index
     * @param {string}        dbPath
     */
    constructor(storage, index, dbPath) {
        this._storage = storage;
        this._index   = index;
        this._path    = dbPath;
    }

    /**
     * Open or create the database at `filePath`.
     * Performs cold-start scan and index rebuild.
     * @param {string} filePath
     * @returns {Promise<MemoryDB>}
     */
    static async open(filePath) {
        const storage = new StorageEngine(filePath);
        const index   = new IndexEngine();
        const records = await storage.scan();
        index.rebuild(records);
        return new MemoryDB(storage, index, filePath);
    }

    // ── Write ────────────────────────────────────────────────────

    /**
     * Append a new memory.
     * @param {string}   concept
     * @param {string}   feeling   - use Feeling.* constants
     * @param {string}   content
     * @param {Object}   [opts]
     * @param {string}   [opts.note='']
     * @param {string[]} [opts.tags=[]]
     * @param {string}   [opts.mediaType='text']
     * @returns {Promise<Object>} the stored Memory object
     */
    async remember(concept, feeling, content, opts = {}) {
        const { note = '', tags = [], mediaType = 'text' } = opts;

        concept = concept.trim();
        if (!concept)                     throw new Error('Concept cannot be empty');
        if (!content)                     throw new Error('Content cannot be empty');
        if (!VALID_FEELINGS.has(feeling)) throw new Error(`Invalid feeling: "${feeling}"`);

        const memoryId  = crypto.randomUUID();
        const timestamp = new Date().toISOString();
        const checksum  = crypto.createHash('sha256').update(content, 'utf8').digest('hex');

        const record = {
            memory_id:  memoryId,
            concept,
            feeling,
            media_type: mediaType,
            content,
            note,
            tags:       [...tags],
            timestamp,
            checksum,
        };

        const offset = await this._storage.append(record);
        this._index.indexRecord(offset, record);
        return { ...record };
    }

    // ── Read ─────────────────────────────────────────────────────

    /**
     * Recall memories by concept. Most recent first.
     * @param {string}  concept
     * @param {Object}  [opts]
     * @param {string}  [opts.feeling]
     * @param {number}  [opts.limit=0]    0 = no limit
     * @param {boolean} [opts.oldestFirst=false]
     */
    async recall(concept, opts = {}) {
        const { feeling = null, limit = 0, oldestFirst = false } = opts;
        const offsets = this._index.offsetsByConcept(concept.trim(), feeling, oldestFirst);
        return this._loadOffsets(offsets, limit);
    }

    /**
     * Recall all memories with a given feeling.
     */
    async recallByFeeling(feeling, opts = {}) {
        const { limit = 0, oldestFirst = false } = opts;
        const offsets = this._index.offsetsByFeeling(feeling, oldestFirst);
        return this._loadOffsets(offsets, limit);
    }

    /**
     * Retrieve every memory.
     */
    async recallAll(opts = {}) {
        const { limit = 0, oldestFirst = false } = opts;
        const offsets = this._index.allOffsets(oldestFirst);
        return this._loadOffsets(offsets, limit);
    }

    /**
     * Full-text search across content, concept, note.
     * @param {string}  text
     * @param {Object}  [opts]
     * @param {boolean} [opts.inContent=true]
     * @param {boolean} [opts.inConcept=true]
     * @param {boolean} [opts.inNote=true]
     * @param {number}  [opts.limit=0]
     */
    async search(text, opts = {}) {
        const { inContent = true, inConcept = true, inNote = true, limit = 0 } = opts;
        const needle  = text.toLowerCase();
        const records = await this._storage.scan();
        const results = [];

        for (let i = records.length - 1; i >= 0; i--) {
            const r = records[i].record;
            let matched = false;
            if (inContent && (r.content || '').toLowerCase().includes(needle)) matched = true;
            if (inConcept && (r.concept || '').toLowerCase().includes(needle)) matched = true;
            if (inNote    && (r.note    || '').toLowerCase().includes(needle)) matched = true;
            if (matched) {
                results.push({ ...r });
                if (limit > 0 && results.length >= limit) break;
            }
        }
        return results;
    }

    // ── Stats ────────────────────────────────────────────────────

    /** Count with optional filters. */
    count(concept = null, feeling = null) {
        return this._index.count(concept, feeling);
    }

    /** Returns {feeling: count, ...} map. */
    feelingDistribution() {
        return this._index.feelingDistribution();
    }

    /** Returns sorted array of all concept names. */
    listConcepts() {
        return this._index.allConcepts();
    }

    /** Returns [{timestamp, feeling, note, tags}] for a concept's timeline. */
    async conceptTimeline(concept) {
        const offsets = this._index.timelineOffsets(concept.trim());
        const result  = [];
        for (const off of offsets) {
            const r = await this._storage.readAt(off);
            if (r) result.push({
                timestamp: r.timestamp,
                feeling:   r.feeling,
                note:      r.note   || '',
                tags:      r.tags   || [],
            });
        }
        return result;
    }

    // ── Export ───────────────────────────────────────────────────

    async exportJson() {
        const memories = await this.recallAll({ oldestFirst: true });
        return JSON.stringify({
            exported_at: new Date().toISOString(),
            memories,
        }, null, 2);
    }

    // ── Internal ─────────────────────────────────────────────────

    async _loadOffsets(offsets, limit) {
        const n   = limit > 0 ? Math.min(limit, offsets.length) : offsets.length;
        const out = [];
        for (let i = 0; i < n; i++) {
            const r = await this._storage.readAt(offsets[i]);
            if (r) out.push({ ...r });
        }
        return out;
    }
}

module.exports = { MemoryDB, Feeling };
