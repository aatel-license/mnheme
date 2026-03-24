// mnheme/java/mnheme/Feeling.java
package mnheme;

public enum Feeling {
    GIOIA("gioia"), TRISTEZZA("tristezza"), RABBIA("rabbia"), PAURA("paura"),
    NOSTALGIA("nostalgia"), AMORE("amore"), MALINCONIA("malinconia"),
    SERENITA("serenità"), SORPRESA("sorpresa"), ANSIA("ansia"),
    GRATITUDINE("gratitudine"), VERGOGNA("vergogna"), ORGOGLIO("orgoglio"),
    NOIA("noia"), CURIOSITA("curiosità");

    private final String value;

    Feeling(String value) { this.value = value; }

    public String getValue() { return value; }

    public static Feeling fromString(String s) {
        for (Feeling f : values()) {
            if (f.value.equalsIgnoreCase(s)) return f;
        }
        throw new IllegalArgumentException("Unknown feeling: " + s);
    }

    public static boolean isValid(String s) {
        for (Feeling f : values())
            if (f.value.equalsIgnoreCase(s)) return true;
        return false;
    }
}
