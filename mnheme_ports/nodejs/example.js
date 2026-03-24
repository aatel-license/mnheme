// mnheme/nodejs/example.js
'use strict';

const { MemoryDB, Feeling } = require('./memorydb');

(async () => {
    const db = await MemoryDB.open('mente.mnheme');

    const mem = await db.remember('Debito', Feeling.ANSIA,
        'Ho firmato il mutuo oggi. 25 anni.', {
            note: 'Era un mercoledì piovoso.',
            tags: ['casa', 'mutuo', '2024'],
        });
    console.log('Stored:', mem.memory_id);

    const memories = await db.recall('Debito');
    console.log(`Recalled ${memories.length} memories for Debito`);

    console.log('Total:', db.count());
    console.log('Feelings:', db.feelingDistribution());

    const json = await db.exportJson();
    require('fs').writeFileSync('backup.json', json);
    console.log('Exported to backup.json');
})();
