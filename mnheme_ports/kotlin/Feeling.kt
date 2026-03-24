// mnheme/kotlin/mnheme/Feeling.kt
package mnheme

enum class Feeling(val value: String) {
    GIOIA       ("gioia"),
    TRISTEZZA   ("tristezza"),
    RABBIA      ("rabbia"),
    PAURA       ("paura"),
    NOSTALGIA   ("nostalgia"),
    AMORE       ("amore"),
    MALINCONIA  ("malinconia"),
    SERENITA    ("serenità"),
    SORPRESA    ("sorpresa"),
    ANSIA       ("ansia"),
    GRATITUDINE ("gratitudine"),
    VERGOGNA    ("vergogna"),
    ORGOGLIO    ("orgoglio"),
    NOIA        ("noia"),
    CURIOSITA   ("curiosità");

    companion object {
        private val byValue = entries.associateBy { it.value }
        fun fromString(s: String): Feeling =
            byValue[s.lowercase()] ?: throw IllegalArgumentException("Unknown feeling: $s")
        fun isValid(s: String): Boolean = s.lowercase() in byValue
        val validValues: Set<String> get() = byValue.keys
    }
}
