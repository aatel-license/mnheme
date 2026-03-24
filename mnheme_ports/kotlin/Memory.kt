// mnheme/kotlin/mnheme/Memory.kt
package mnheme

import org.json.JSONArray
import org.json.JSONObject

/**
 * Immutable snapshot of a stored memory.
 * data class gives free equals/hashCode/copy/toString.
 */
data class Memory(
    val memoryId:  String,
    val concept:   String,
    val feeling:   String,
    val mediaType: String,
    val content:   String,
    val note:      String,
    val tags:      List<String>,
    val timestamp: String,
    val checksum:  String,
) {
    fun toJson(): JSONObject = JSONObject().apply {
        put("memory_id",  memoryId)
        put("concept",    concept)
        put("feeling",    feeling)
        put("media_type", mediaType)
        put("content",    content)
        put("note",       note)
        put("tags",       JSONArray(tags))
        put("timestamp",  timestamp)
        put("checksum",   checksum)
    }

    companion object {
        fun fromJson(j: JSONObject): Memory {
            val tagsArr = j.optJSONArray("tags")
            val tags = if (tagsArr != null) {
                (0 until tagsArr.length()).map { tagsArr.optString(it) }
            } else emptyList()

            return Memory(
                memoryId  = j.optString("memory_id"),
                concept   = j.optString("concept"),
                feeling   = j.optString("feeling"),
                mediaType = j.optString("media_type", "text"),
                content   = j.optString("content"),
                note      = j.optString("note"),
                tags      = tags,
                timestamp = j.optString("timestamp"),
                checksum  = j.optString("checksum"),
            )
        }
    }
}
