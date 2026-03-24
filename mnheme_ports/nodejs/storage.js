// mnheme/nodejs/storage.js
// =========================
// StorageEngine — append-only binary log
// Frame: MAGIC(4B) | SIZE(4B big-endian) | JSON UTF-8 payload

'use strict';

const fs = require('node:fs');

const MAGIC       = Buffer.from([0x4D, 0x4E, 0x45, 0xE0]);
const HEADER_SIZE = 8;

class StorageEngine {
    constructor(filePath) {
        this.filePath = filePath;
        if (!fs.existsSync(filePath)) {
            fs.writeFileSync(filePath, Buffer.alloc(0));
        }
    }

    /** Append JSON record. Returns BigInt byte offset. */
    async append(record) {
        const payload = Buffer.from(JSON.stringify(record), 'utf8');
        const frame   = Buffer.allocUnsafe(HEADER_SIZE + payload.length);
        MAGIC.copy(frame, 0);
        frame.writeUInt32BE(payload.length, 4);
        payload.copy(frame, HEADER_SIZE);

        const fd = await fs.promises.open(this.filePath, 'a');
        try {
            const stat   = await fd.stat();
            const offset = BigInt(stat.size);
            await fd.write(frame);
            await fd.sync(); // fsync
            return offset;
        } finally {
            await fd.close();
        }
    }

    /** Scan all valid records → [{offset: BigInt, record: Object}] */
    async scan() {
        const results = [];
        if (!fs.existsSync(this.filePath)) return results;

        const buf = await fs.promises.readFile(this.filePath);
        let pos = 0;

        while (pos < buf.length) {
            const offset = pos;
            if (pos + HEADER_SIZE > buf.length) break;
            if (!buf.subarray(pos, pos + 4).equals(MAGIC)) { pos++; continue; }

            const size = buf.readUInt32BE(pos + 4);
            pos += HEADER_SIZE;
            if (pos + size > buf.length) break;

            try {
                const record = JSON.parse(buf.subarray(pos, pos + size).toString('utf8'));
                results.push({ offset: BigInt(offset), record });
            } catch { /* corrupted, skip */ }
            pos += size;
        }
        return results;
    }

    /** Read single record at known offset — O(1). */
    async readAt(offset) {
        const n  = Number(offset);
        const fd = await fs.promises.open(this.filePath, 'r');
        try {
            const header = Buffer.allocUnsafe(HEADER_SIZE);
            const { bytesRead: hr } = await fd.read(header, 0, HEADER_SIZE, n);
            if (hr < HEADER_SIZE || !header.subarray(0, 4).equals(MAGIC)) return null;

            const size    = header.readUInt32BE(4);
            const payload = Buffer.allocUnsafe(size);
            const { bytesRead: pr } = await fd.read(payload, 0, size, n + HEADER_SIZE);
            if (pr < size) return null;
            try { return JSON.parse(payload.toString('utf8')); } catch { return null; }
        } finally {
            await fd.close();
        }
    }

    async fileSize() {
        return (await fs.promises.stat(this.filePath)).size;
    }
}

module.exports = { StorageEngine };
