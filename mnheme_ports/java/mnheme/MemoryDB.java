// mnheme/java/mnheme/MemoryDB.java
// ==================================
// MemoryDB — public API for MNHEME
//
// Usage:
//   var db = new MemoryDB(Path.of("mente.mnheme"));
//   var mem = db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.");
//   var list = db.recall("Debito");
//
// Build (Maven):
//   <dependency>
//     <groupId>com.fasterxml.jackson.core</groupId>
//     <artifactId>jackson-databind</artifactId>
//     <version>2.17.0</version>
//   </dependency>
//   <dependency>
//     <groupId>com.github.f4b6a3</groupId>
//     <artifactId>uuid-creator</artifactId>
//     <version>5.3.3</version>
//   </dependency>

package mnheme;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;

public class MemoryDB implements AutoCloseable {

    private final StorageEngine storage;
    private final IndexEngine   index;
    private final String        dbPath;
    private final ObjectMapper  mapper = new ObjectMapper();

    /**
     * Open or create the database at path.
     * Cold start: scans the log and rebuilds all indexes.
     */
    public MemoryDB(Path path) throws IOException {
        this.dbPath  = path.toString();
        this.storage = new StorageEngine(path);
        this.index   = new IndexEngine();
        var records  = storage.scan();
        index.rebuild(records);
    }

    // ── Write ──────────────────────────────────────────────────

    /**
     * Append a new memory. Throws if concept/content is empty or feeling invalid.
     */
    public Memory remember(
            String       concept,
            Feeling      feeling,
            String       content,
            String       note,
            List<String> tags,
            String       mediaType
    ) throws IOException {
        concept   = concept.strip();
        if (concept.isEmpty()) throw new IllegalArgumentException("Concept cannot be empty");
        if (content.isEmpty()) throw new IllegalArgumentException("Content cannot be empty");
        if (note      == null) note      = "";
        if (tags      == null) tags      = List.of();
        if (mediaType == null) mediaType = "text";

        String memoryId  = UUID.randomUUID().toString();
        String timestamp = Instant.now().toString();
        String checksum  = sha256(content);

        Map<String, Object> record = new LinkedHashMap<>();
        record.put("memory_id",  memoryId);
        record.put("concept",    concept);
        record.put("feeling",    feeling.getValue());
        record.put("media_type", mediaType);
        record.put("content",    content);
        record.put("note",       note);
        record.put("tags",       tags);
        record.put("timestamp",  timestamp);
        record.put("checksum",   checksum);

        long offset = storage.append(record);
        index.indexRecord(offset, record);

        return new Memory(memoryId, concept, feeling.getValue(), mediaType,
                          content, note, List.copyOf(tags), timestamp, checksum);
    }

    /** Convenience: remember with defaults (no note, no tags). */
    public Memory remember(String concept, Feeling feeling, String content) throws IOException {
        return remember(concept, feeling, content, "", null, "text");
    }

    // ── Read ───────────────────────────────────────────────────

    /** Recall memories by concept. Most recent first. */
    public List<Memory> recall(String concept) throws IOException {
        return recall(concept, null, -1, false);
    }

    public List<Memory> recall(
            String  concept,
            Feeling feeling,
            int     limit,
            boolean oldestFirst
    ) throws IOException {
        String fVal = feeling != null ? feeling.getValue() : null;
        var offsets = index.offsetsByConcept(concept.strip(), fVal, oldestFirst);
        return loadOffsets(offsets, limit);
    }

    public List<Memory> recallByFeeling(Feeling feeling) throws IOException {
        return recallByFeeling(feeling, -1, false);
    }

    public List<Memory> recallByFeeling(
            Feeling feeling, int limit, boolean oldestFirst
    ) throws IOException {
        var offsets = index.offsetsByFeeling(feeling.getValue(), oldestFirst);
        return loadOffsets(offsets, limit);
    }

    public List<Memory> recallAll() throws IOException {
        return recallAll(-1, false);
    }

    public List<Memory> recallAll(int limit, boolean oldestFirst) throws IOException {
        var offsets = index.allOffsets(oldestFirst);
        return loadOffsets(offsets, limit);
    }

    /**
     * Full-text search across content, concept, note.
     */
    public List<Memory> search(String text) throws IOException {
        return search(text, true, true, true, -1);
    }

    public List<Memory> search(
            String  text,
            boolean inContent, boolean inConcept, boolean inNote,
            int     limit
    ) throws IOException {
        String needle  = text.toLowerCase(Locale.ROOT);
        var    records = storage.scan();
        Collections.reverse(records); // most recent first
        List<Memory> results = new ArrayList<>();

        for (var sr : records) {
            var r = sr.record();
            boolean matched = false;
            if (inContent && strVal(r,"content").toLowerCase().contains(needle)) matched = true;
            if (inConcept && strVal(r,"concept").toLowerCase().contains(needle)) matched = true;
            if (inNote    && strVal(r,"note"   ).toLowerCase().contains(needle)) matched = true;
            if (matched) {
                results.add(Memory.fromMap(r));
                if (limit > 0 && results.size() >= limit) break;
            }
        }
        return results;
    }

    // ── Stats ──────────────────────────────────────────────────

    public int count() { return index.count(null, null); }

    public int count(String concept, Feeling feeling) {
        return index.count(concept, feeling != null ? feeling.getValue() : null);
    }

    public Map<String, Integer> feelingDistribution() {
        return index.feelingDistribution();
    }

    public List<String> listConcepts() {
        return index.allConcepts();
    }

    public List<Map<String, Object>> conceptTimeline(String concept) throws IOException {
        var offsets = index.timelineOffsets(concept.strip());
        List<Map<String, Object>> result = new ArrayList<>();
        for (long off : offsets) {
            var r = storage.readAt(off);
            if (r == null) continue;
            result.add(Map.of(
                "timestamp", strVal(r, "timestamp"),
                "feeling",   strVal(r, "feeling"),
                "note",      strVal(r, "note"),
                "tags",      r.getOrDefault("tags", List.of())
            ));
        }
        return result;
    }

    // ── Export ─────────────────────────────────────────────────

    public String exportJson() throws IOException {
        var memories = recallAll(- 1, true).stream()
                .map(Memory::toMap)
                .collect(Collectors.toList());
        var out = Map.of(
            "exported_at", Instant.now().toString(),
            "memories",    memories
        );
        return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(out);
    }

    // ── Internal ───────────────────────────────────────────────

    private List<Memory> loadOffsets(List<Long> offsets, int limit) throws IOException {
        int n = (limit > 0) ? Math.min(limit, offsets.size()) : offsets.size();
        List<Memory> result = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            var r = storage.readAt(offsets.get(i));
            if (r != null) result.add(Memory.fromMap(r));
        }
        return result;
    }

    private static String strVal(Map<String, Object> m, String key) {
        Object v = m.get(key);
        return v instanceof String s ? s : "";
    }

    private static String sha256(String input) {
        try {
            var digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            var sb = new StringBuilder();
            for (byte b : hash) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public void close() { /* no persistent connection to close */ }
}
