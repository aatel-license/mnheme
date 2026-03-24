// mnheme/java/mnheme/IndexEngine.java
package mnheme;

import java.util.*;
import java.util.regex.*;
import java.util.stream.*;

/**
 * In-RAM index engine. Rebuilt from log on cold start.
 *
 * concept_index : Map<String, List<Long>>
 * feeling_index : Map<String, List<Long>>
 * cf_index      : Map<"concept\0feeling", List<Long>>
 * word_index    : Map<String, List<Long>>  -- inverted full-text
 */
public class IndexEngine {

    private static final Pattern TOKEN_RE =
        Pattern.compile("[a-zA-Zàáâäãåæçèéêëìíîïòóôöõùúûüýÿñ]{3,}",
                        Pattern.UNICODE_CHARACTER_CLASS);

    private final Map<String, List<Long>> concept    = new HashMap<>();
    private final Map<String, List<Long>> feeling    = new HashMap<>();
    private final Map<String, List<Long>> tag        = new HashMap<>();
    private final Map<String, List<Long>> cf         = new HashMap<>();
    private final List<String[]>          timelineTs = new ArrayList<>();
    private final List<Long>              all        = new ArrayList<>();
    private final Map<String, List<Long>> word       = new HashMap<>();

    public void indexRecord(long offset, Map<String, Object> r) {
        String c  = strVal(r, "concept");
        String f  = strVal(r, "feeling");
        String ts = strVal(r, "timestamp");

        concept.computeIfAbsent(c, k -> new ArrayList<>()).add(offset);
        feeling.computeIfAbsent(f, k -> new ArrayList<>()).add(offset);
        cf.computeIfAbsent(cfKey(c, f), k -> new ArrayList<>()).add(offset);
        timelineTs.add(new String[]{ts, String.valueOf(offset)});
        all.add(offset);

        Object tagsObj = r.get("tags");
        if (tagsObj instanceof List<?> tags) {
            for (Object t : tags) {
                if (t instanceof String s && !s.isBlank())
                    tag.computeIfAbsent(s, k -> new ArrayList<>()).add(offset);
            }
        }

        String combined = strVal(r, "content") + " " + c + " " + strVal(r, "note");
        for (String tok : tokenize(combined))
            word.computeIfAbsent(tok, k -> new ArrayList<>()).add(offset);
    }

    public int rebuild(List<StorageEngine.ScanResult> records) {
        concept.clear(); feeling.clear(); tag.clear();
        cf.clear(); timelineTs.clear(); all.clear(); word.clear();
        for (var sr : records) indexRecord(sr.offset(), sr.record());
        timelineTs.sort(Comparator.comparing(a -> a[0]));
        return records.size();
    }

    public List<Long> offsetsByConcept(String c, String f, boolean oldestFirst) {
        List<Long> offs = new ArrayList<>(
            f != null && !f.isEmpty()
                ? cf.getOrDefault(cfKey(c, f), List.of())
                : concept.getOrDefault(c, List.of()));
        if (!oldestFirst) Collections.reverse(offs);
        return offs;
    }

    public List<Long> offsetsByFeeling(String f, boolean oldestFirst) {
        List<Long> offs = new ArrayList<>(feeling.getOrDefault(f, List.of()));
        if (!oldestFirst) Collections.reverse(offs);
        return offs;
    }

    public List<Long> allOffsets(boolean oldestFirst) {
        List<Long> offs = new ArrayList<>(all);
        if (!oldestFirst) Collections.reverse(offs);
        return offs;
    }

    public List<Long> timelineOffsets(String c) {
        Set<Long> cset = new HashSet<>(concept.getOrDefault(c, List.of()));
        return timelineTs.stream()
            .map(a -> Long.parseLong(a[1]))
            .filter(cset::contains)
            .collect(Collectors.toList());
    }

    public List<String> allConcepts() {
        return concept.keySet().stream().sorted().collect(Collectors.toList());
    }

    public int count(String c, String f) {
        if (c != null && f != null) return cf.getOrDefault(cfKey(c, f), List.of()).size();
        if (c != null)               return concept.getOrDefault(c, List.of()).size();
        if (f != null)               return feeling.getOrDefault(f, List.of()).size();
        return all.size();
    }

    public Map<String, Integer> feelingDistribution() {
        Map<String, Integer> dist = new LinkedHashMap<>();
        feeling.forEach((k, v) -> dist.put(k, v.size()));
        return dist;
    }

    public Map<String, Map<String, Integer>> conceptFeelingMatrix() {
        Map<String, Map<String, Integer>> matrix = new LinkedHashMap<>();
        cf.forEach((key, offsets) -> {
            int idx = key.indexOf('\0');
            String cKey = key.substring(0, idx);
            String fKey = key.substring(idx + 1);
            matrix.computeIfAbsent(cKey, k -> new LinkedHashMap<>()).put(fKey, offsets.size());
        });
        return matrix;
    }

    private static String cfKey(String c, String f) { return c + '\0' + f; }

    private static Set<String> tokenize(String text) {
        Set<String> tokens = new HashSet<>();
        Matcher m = TOKEN_RE.matcher(text.toLowerCase(Locale.ROOT));
        while (m.find()) tokens.add(m.group());
        return tokens;
    }

    private static String strVal(Map<String, Object> m, String key) {
        Object v = m.get(key);
        return v instanceof String s ? s : "";
    }
}
