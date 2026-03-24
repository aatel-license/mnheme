// mnheme/nodejs/index.js
// =======================
// IndexEngine — in-RAM, rebuilt on cold start.

'use strict';

class IndexEngine {
    constructor() {
        this.concept  = new Map(); // concept → [offset, ...]
        this.feeling  = new Map(); // feeling → [offset, ...]
        this.tag      = new Map(); // tag     → [offset, ...]
        this.cf       = new Map(); // "c\0f"  → [offset, ...]
        this.timeline = [];        // [{ts, offset}] sorted
        this.all      = [];
        this.word     = new Map(); // token   → [offset, ...]
    }

    /** Index a single record. */
    indexRecord(offset, record) {
        const concept   = record.concept   || '';
        const feeling   = record.feeling   || '';
        const timestamp = record.timestamp || '';
        const tags      = Array.isArray(record.tags) ? record.tags : [];

        push(this.concept, concept, offset);
        push(this.feeling, feeling, offset);
        push(this.cf, cfKey(concept, feeling), offset);
        this.timeline.push({ ts: timestamp, offset });
        this.all.push(offset);

        for (const t of tags) {
            if (t) push(this.tag, t, offset);
        }

        // Inverted full-text
        const combined = `${record.content || ''} ${concept} ${record.note || ''}`;
        for (const tok of tokenize(combined)) {
            push(this.word, tok, offset);
        }
    }

    /** Rebuild all indexes from scan results. */
    rebuild(scanResults) {
        this.concept.clear(); this.feeling.clear(); this.tag.clear();
        this.cf.clear(); this.timeline = []; this.all = []; this.word.clear();

        for (const { offset, record } of scanResults) {
            this.indexRecord(offset, record);
        }
        this.timeline.sort((a, b) => a.ts < b.ts ? -1 : a.ts > b.ts ? 1 : 0);
        return scanResults.length;
    }

    // ── Queries ──────────────────────────────────────────────────

    offsetsByConcept(concept, feeling, oldestFirst = false) {
        const key  = feeling ? cfKey(concept, feeling) : null;
        const offs = [...(key ? this.cf.get(key) : this.concept.get(concept)) || []];
        if (!oldestFirst) offs.reverse();
        return offs;
    }

    offsetsByFeeling(feeling, oldestFirst = false) {
        const offs = [...(this.feeling.get(feeling) || [])];
        if (!oldestFirst) offs.reverse();
        return offs;
    }

    allOffsets(oldestFirst = false) {
        const offs = [...this.all];
        if (!oldestFirst) offs.reverse();
        return offs;
    }

    timelineOffsets(concept) {
        const cset = new Set(this.concept.get(concept) || []);
        return this.timeline
            .filter(e => cset.has(e.offset))
            .map(e => e.offset);
    }

    // ── Stats ─────────────────────────────────────────────────────

    allConcepts() { return [...this.concept.keys()].sort(); }

    count(concept, feeling) {
        if (concept && feeling) return (this.cf.get(cfKey(concept, feeling)) || []).length;
        if (concept)            return (this.concept.get(concept) || []).length;
        if (feeling)            return (this.feeling.get(feeling) || []).length;
        return this.all.length;
    }

    feelingDistribution() {
        const dist = {};
        for (const [f, offs] of this.feeling) dist[f] = offs.length;
        return dist;
    }

    conceptFeelingMatrix() {
        const matrix = {};
        for (const [key, offs] of this.cf) {
            const [c, f] = key.split('\0');
            if (!matrix[c]) matrix[c] = {};
            matrix[c][f] = offs.length;
        }
        return matrix;
    }
}

// ── Helpers ───────────────────────────────────────────────────────

function push(map, key, val) {
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(val);
}

function cfKey(c, f) { return `${c}\0${f}`; }

function tokenize(text) {
    const tokens = new Set();
    const re = /[a-zA-Zàáâäãåæçèéêëìíîïòóôöõùúûüýÿñ]{3,}/gu;
    for (const m of text.toLowerCase().matchAll(re)) tokens.add(m[0]);
    return tokens;
}

module.exports = { IndexEngine };
