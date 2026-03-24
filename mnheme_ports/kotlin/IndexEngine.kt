// mnheme/kotlin/mnheme/IndexEngine.kt
package mnheme

import org.json.JSONObject

/**
 * In-RAM index engine — rebuilt from log on cold start.
 * Uses only stdlib + org.json (ships with Android).
 */
class IndexEngine {

    private val concept  = mutableMapOf<String, MutableList<Long>>()
    private val feeling  = mutableMapOf<String, MutableList<Long>>()
    private val tag      = mutableMapOf<String, MutableList<Long>>()
    private val cf       = mutableMapOf<Pair<String,String>, MutableList<Long>>()
    private val timeline = mutableListOf<Pair<String, Long>>() // (timestamp, offset) sorted
    private val all      = mutableListOf<Long>()
    private val word     = mutableMapOf<String, MutableList<Long>>() // inverted full-text

    fun indexRecord(offset: Long, r: JSONObject) {
        val c  = r.optString("concept")
        val f  = r.optString("feeling")
        val ts = r.optString("timestamp")

        concept .getOrPut(c) { mutableListOf() }.add(offset)
        feeling .getOrPut(f) { mutableListOf() }.add(offset)
        cf      .getOrPut(c to f) { mutableListOf() }.add(offset)
        timeline.add(ts to offset)
        all     .add(offset)

        val tags = r.optJSONArray("tags")
        if (tags != null) {
            for (i in 0 until tags.length()) {
                val t = tags.optString(i)
                if (t.isNotBlank()) tag.getOrPut(t) { mutableListOf() }.add(offset)
            }
        }

        // Inverted full-text
        val combined = "${r.optString("content")} $c ${r.optString("note")}"
        tokenize(combined).forEach { tok ->
            word.getOrPut(tok) { mutableListOf() }.add(offset)
        }
    }

    fun rebuild(records: List<StorageEngine.ScanResult>): Int {
        concept.clear(); feeling.clear(); tag.clear()
        cf.clear(); timeline.clear(); all.clear(); word.clear()
        records.forEach { indexRecord(it.offset, it.record) }
        timeline.sortBy { it.first }
        return records.size
    }

    // ── Queries ──────────────────────────────────────────────────

    fun offsetsByConcept(c: String, f: String?, oldestFirst: Boolean): List<Long> {
        val offs = if (f != null && f.isNotEmpty())
            cf[c to f]?.toMutableList() ?: mutableListOf()
        else
            concept[c]?.toMutableList() ?: mutableListOf()
        return if (oldestFirst) offs else offs.asReversed()
    }

    fun offsetsByFeeling(f: String, oldestFirst: Boolean): List<Long> {
        val offs = feeling[f]?.toMutableList() ?: mutableListOf()
        return if (oldestFirst) offs else offs.asReversed()
    }

    fun allOffsets(oldestFirst: Boolean): List<Long> {
        val offs = all.toMutableList()
        return if (oldestFirst) offs else offs.asReversed()
    }

    fun timelineOffsets(c: String): List<Long> {
        val cset = concept[c]?.toHashSet() ?: emptySet()
        return timeline.filter { it.second in cset }.map { it.second }
    }

    // ── Stats ─────────────────────────────────────────────────────

    fun allConcepts(): List<String> = concept.keys.sorted()

    fun count(c: String?, f: String?): Int = when {
        c != null && f != null -> cf[c to f]?.size ?: 0
        c != null              -> concept[c]?.size ?: 0
        f != null              -> feeling[f]?.size ?: 0
        else                   -> all.size
    }

    fun feelingDistribution(): Map<String, Int> =
        feeling.mapValues { it.value.size }

    fun conceptFeelingMatrix(): Map<String, Map<String, Int>> {
        val matrix = mutableMapOf<String, MutableMap<String, Int>>()
        cf.forEach { (key, offs) ->
            matrix.getOrPut(key.first) { mutableMapOf() }[key.second] = offs.size
        }
        return matrix
    }

    companion object {
        private val TOKEN_RE = Regex("[a-zA-Zàáâäãåæçèéêëìíîïòóôöõùúûüýÿñ]{3,}")

        fun tokenize(text: String): Set<String> =
            TOKEN_RE.findAll(text.lowercase()).map { it.value }.toHashSet()
    }
}
