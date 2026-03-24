// mnheme/java/mnheme/Memory.java
package mnheme;

import java.util.List;
import java.util.Map;

/**
 * Immutable snapshot of a memory record.
 * Using Java 16+ record for conciseness.
 */
public record Memory(
        String       memoryId,
        String       concept,
        String       feeling,
        String       mediaType,
        String       content,
        String       note,
        List<String> tags,
        String       timestamp,
        String       checksum
) {
    /** Convert to plain Map for JSON serialisation. */
    public Map<String, Object> toMap() {
        return Map.of(
            "memory_id",  memoryId,
            "concept",    concept,
            "feeling",    feeling,
            "media_type", mediaType,
            "content",    content,
            "note",       note,
            "tags",       tags,
            "timestamp",  timestamp,
            "checksum",   checksum
        );
    }

    @SuppressWarnings("unchecked")
    public static Memory fromMap(Map<String, Object> m) {
        return new Memory(
            (String)  m.getOrDefault("memory_id",  ""),
            (String)  m.getOrDefault("concept",    ""),
            (String)  m.getOrDefault("feeling",    ""),
            (String)  m.getOrDefault("media_type", "text"),
            (String)  m.getOrDefault("content",    ""),
            (String)  m.getOrDefault("note",       ""),
            m.containsKey("tags") ? (List<String>) m.get("tags") : List.of(),
            (String)  m.getOrDefault("timestamp",  ""),
            (String)  m.getOrDefault("checksum",   "")
        );
    }
}
