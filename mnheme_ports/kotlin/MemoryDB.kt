// mnheme/kotlin/mnheme/MemoryDB.kt
// ==================================
// MemoryDB — public API, Android & JVM compatible.
//
// Android usage (e.g. in a ViewModel with viewModelScope):
//   val db = MemoryDB(context.filesDir.resolve("mente.mnheme"))
//   val mem = withContext(Dispatchers.IO) {
//       db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.")
//   }
//
// JVM usage:
//   val db = MemoryDB(File("mente.mnheme"))
//   val mem = db.remember("Debito", Feeling.ANSIA, "Ho firmato il mutuo.")
//
// Dependencies (build.gradle.kts):
//   // Already on Android; for JVM add:
//   implementation("org.json:json:20240303")
//   // For coroutine helpers:
//   implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")

package mnheme

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.security.MessageDigest
import java.time.Instant
import java.util.UUID

class MemoryDB(file: File) : AutoCloseable {

    private val storage = StorageEngine(file)
    private val index   = IndexEngine()
    private val dbPath  = file.absolutePath

    init {
        // Cold start: rebuild indexes from log
        val records = storage.scan()
        index.rebuild(records)
    }

    // ── Write ─────────────────────────────────────────────────────

    /**
     * Append a new memory. Thread-safe.
     *
     * @param concept   conceptual key (e.g. "Casa", "Lavoro")
     * @param feeling   use [Feeling] enum
     * @param content   free-text content
     * @param note      optional annotation
     * @param tags      optional labels
     * @param mediaType "text" | "image" | "video" | "audio" | "doc"
     */
    fun remember(
        concept:   String,
        feeling:   Feeling,
        content:   String,
        note:      String       = "",
        tags:      List<String> = emptyList(),
        mediaType: String       = "text",
    ): Memory {
        val c = concept.trim()
        require(c.isNotEmpty()) { "Concept cannot be empty" }
        require(content.isNotEmpty()) { "Content cannot be empty" }

        val memoryId  = UUID.randomUUID().toString()
        val timestamp = Instant.now().toString()
        val checksum  = sha256(content)
        val cleanTags = tags.map { it.trim() }.filter { it.isNotEmpty() }

        val record = JSONObject().apply {
            put("memory_id",  memoryId)
            put("concept",    c)
            put("feeling",    feeling.value)
            put("media_type", mediaType)
            put("content",    content)
            put("note",       note)
            put("tags",       JSONArray(cleanTags))
            put("timestamp",  timestamp)
            put("checksum",   checksum)
        }

        val offset = storage.append(record)
        index.indexRecord(offset, record)

        return Memory(
            memoryId  = memoryId,
            concept   = c,
            feeling   = feeling.value,
            mediaType = mediaType,
            content   = content,
            note      = note,
            tags      = cleanTags,
            timestamp = timestamp,
            checksum  = checksum,
        )
    }

    // ── Read ──────────────────────────────────────────────────────

    /**
     * Recall memories by concept. Most recent first by default.
     */
    fun recall(
        concept:     String,
        feeling:     Feeling?    = null,
        limit:       Int         = 0,
        oldestFirst: Boolean     = false,
    ): List<Memory> {
        val offsets = index.offsetsByConcept(concept.trim(), feeling?.value, oldestFirst)
        return loadOffsets(offsets, limit)
    }

    /** Recall all memories tagged with a feeling. */
    fun recallByFeeling(
        feeling:     Feeling,
        limit:       Int     = 0,
        oldestFirst: Boolean = false,
    ): List<Memory> {
        val offsets = index.offsetsByFeeling(feeling.value, oldestFirst)
        return loadOffsets(offsets, limit)
    }

    /** Retrieve every memory. */
    fun recallAll(limit: Int = 0, oldestFirst: Boolean = false): List<Memory> {
        val offsets = index.allOffsets(oldestFirst)
        return loadOffsets(offsets, limit)
    }

    /**
     * Full-text search across content, concept, note.
     */
    fun search(
        text:      String,
        inContent: Boolean = true,
        inConcept: Boolean = true,
        inNote:    Boolean = true,
        limit:     Int     = 0,
    ): List<Memory> {
        val needle  = text.lowercase()
        val records = storage.scan()
        val results = mutableListOf<Memory>()

        for (i in records.indices.reversed()) {
            val r = records[i].record
            var matched = false
            if (inContent && r.optString("content").lowercase().contains(needle)) matched = true
            if (inConcept && r.optString("concept").lowercase().contains(needle)) matched = true
            if (inNote    && r.optString("note")   .lowercase().contains(needle)) matched = true
            if (matched) {
                results.add(Memory.fromJson(r))
                if (limit > 0 && results.size >= limit) break
            }
        }
        return results
    }

    // ── Stats ─────────────────────────────────────────────────────

    /** Count with optional filters. */
    fun count(concept: String? = null, feeling: Feeling? = null): Int =
        index.count(concept, feeling?.value)

    /** Returns feeling → count map. */
    fun feelingDistribution(): Map<String, Int> = index.feelingDistribution()

    /** Returns sorted list of all concept names. */
    fun listConcepts(): List<String> = index.allConcepts()

    /** Returns the emotional timeline of a concept. */
    fun conceptTimeline(concept: String): List<Map<String, Any?>> {
        val offsets = index.timelineOffsets(concept.trim())
        return offsets.mapNotNull { off ->
            val r = storage.readAt(off) ?: return@mapNotNull null
            mapOf(
                "timestamp" to r.optString("timestamp"),
                "feeling"   to r.optString("feeling"),
                "note"      to r.optString("note"),
                "tags"      to r.optJSONArray("tags"),
            )
        }
    }

    // ── Export ────────────────────────────────────────────────────

    fun exportJson(): String {
        val memories  = recallAll(oldestFirst = true).map { it.toJson() }
        val arr       = JSONArray(memories)
        return JSONObject().apply {
            put("exported_at", Instant.now().toString())
            put("memories",    arr)
        }.toString(2)
    }

    // ── Android ViewModel extension ───────────────────────────────

    /**
     * Storage info — useful for UI display in Android.
     */
    fun storageInfo(): Map<String, Any> = mapOf(
        "log_path"       to dbPath,
        "log_size_bytes" to storage.fileSize(),
        "total_records"  to count(),
    )

    // ── Internal ──────────────────────────────────────────────────

    private fun loadOffsets(offsets: List<Long>, limit: Int): List<Memory> {
        val n = if (limit > 0) minOf(limit, offsets.size) else offsets.size
        return (0 until n).mapNotNull { i ->
            storage.readAt(offsets[i])?.let { Memory.fromJson(it) }
        }
    }

    private fun sha256(input: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val hash   = digest.digest(input.toByteArray(Charsets.UTF_8))
        return hash.joinToString("") { "%02x".format(it) }
    }

    override fun close() { /* no persistent connection */ }
}
