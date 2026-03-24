// mnheme/go/mnheme/index.go
// ==========================
// IndexEngine — all in-RAM, rebuilt from log on cold start.

package mnheme

import (
	"sort"
	"strings"
	"unicode"
)

// cfKey combines concept+feeling as a map key.
type cfKey struct{ concept, feeling string }

// IndexEngine holds all in-memory indexes.
type IndexEngine struct {
	concept  map[string][]uint64
	feeling  map[string][]uint64
	tag      map[string][]uint64
	cf       map[cfKey][]uint64
	timeline []timeEntry // sorted by timestamp
	all      []uint64
	word     map[string][]uint64 // inverted full-text
}

type timeEntry struct {
	timestamp string
	offset    uint64
}

// NewIndexEngine creates an empty IndexEngine.
func NewIndexEngine() *IndexEngine {
	return &IndexEngine{
		concept: make(map[string][]uint64),
		feeling: make(map[string][]uint64),
		tag:     make(map[string][]uint64),
		cf:      make(map[cfKey][]uint64),
		word:    make(map[string][]uint64),
	}
}

// IndexRecord adds a single record to all indexes.
func (idx *IndexEngine) IndexRecord(offset uint64, r map[string]any) {
	concept   := strVal(r, "concept")
	feeling   := strVal(r, "feeling")
	timestamp := strVal(r, "timestamp")

	idx.concept[concept] = append(idx.concept[concept], offset)
	idx.feeling[feeling] = append(idx.feeling[feeling], offset)
	key := cfKey{concept, feeling}
	idx.cf[key] = append(idx.cf[key], offset)
	idx.timeline = append(idx.timeline, timeEntry{timestamp, offset})
	idx.all = append(idx.all, offset)

	if tags, ok := r["tags"].([]any); ok {
		for _, t := range tags {
			if ts, ok := t.(string); ok && ts != "" {
				idx.tag[ts] = append(idx.tag[ts], offset)
			}
		}
	}

	// Inverted full-text
	combined := strVal(r, "content") + " " + concept + " " + strVal(r, "note")
	for tok := range tokenize(combined) {
		idx.word[tok] = append(idx.word[tok], offset)
	}
}

// Rebuild clears and rebuilds all indexes from scan results.
func (idx *IndexEngine) Rebuild(records []ScanResult) int {
	idx.concept  = make(map[string][]uint64)
	idx.feeling  = make(map[string][]uint64)
	idx.tag      = make(map[string][]uint64)
	idx.cf       = make(map[cfKey][]uint64)
	idx.timeline = nil
	idx.all      = nil
	idx.word     = make(map[string][]uint64)

	for _, sr := range records {
		idx.IndexRecord(sr.Offset, sr.Record)
	}
	sort.Slice(idx.timeline, func(i, j int) bool {
		return idx.timeline[i].timestamp < idx.timeline[j].timestamp
	})
	return len(records)
}

// ── Queries ──────────────────────────────────────────────────────

func (idx *IndexEngine) OffsetsByConcept(concept, feeling string, oldestFirst bool) []uint64 {
	var offs []uint64
	if feeling != "" {
		offs = append([]uint64{}, idx.cf[cfKey{concept, feeling}]...)
	} else {
		offs = append([]uint64{}, idx.concept[concept]...)
	}
	if !oldestFirst {
		reverseU64(offs)
	}
	return offs
}

func (idx *IndexEngine) OffsetsByFeeling(feeling string, oldestFirst bool) []uint64 {
	offs := append([]uint64{}, idx.feeling[feeling]...)
	if !oldestFirst {
		reverseU64(offs)
	}
	return offs
}

func (idx *IndexEngine) OffsetsByWord(word string) []uint64 {
	offs := append([]uint64{}, idx.word[strings.ToLower(word)]...)
	reverseU64(offs)
	return offs
}

func (idx *IndexEngine) AllOffsets(oldestFirst bool) []uint64 {
	offs := append([]uint64{}, idx.all...)
	if !oldestFirst {
		reverseU64(offs)
	}
	return offs
}

func (idx *IndexEngine) TimelineOffsets(concept string) []uint64 {
	cset := make(map[uint64]struct{})
	for _, off := range idx.concept[concept] {
		cset[off] = struct{}{}
	}
	var result []uint64
	for _, te := range idx.timeline {
		if _, ok := cset[te.offset]; ok {
			result = append(result, te.offset)
		}
	}
	return result
}

// ── Stats ─────────────────────────────────────────────────────────

func (idx *IndexEngine) AllConcepts() []string {
	concepts := make([]string, 0, len(idx.concept))
	for k := range idx.concept {
		concepts = append(concepts, k)
	}
	sort.Strings(concepts)
	return concepts
}

func (idx *IndexEngine) Count(concept, feeling string) int {
	switch {
	case concept != "" && feeling != "":
		return len(idx.cf[cfKey{concept, feeling}])
	case concept != "":
		return len(idx.concept[concept])
	case feeling != "":
		return len(idx.feeling[feeling])
	default:
		return len(idx.all)
	}
}

func (idx *IndexEngine) FeelingDistribution() map[string]int {
	dist := make(map[string]int, len(idx.feeling))
	for f, offs := range idx.feeling {
		dist[f] = len(offs)
	}
	return dist
}

func (idx *IndexEngine) ConceptFeelingMatrix() map[string]map[string]int {
	matrix := make(map[string]map[string]int)
	for key, offs := range idx.cf {
		if matrix[key.concept] == nil {
			matrix[key.concept] = make(map[string]int)
		}
		matrix[key.concept][key.feeling] = len(offs)
	}
	return matrix
}

// ── Helpers ───────────────────────────────────────────────────────

func strVal(m map[string]any, key string) string {
	if v, ok := m[key]; ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return ""
}

func reverseU64(s []uint64) {
	for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
		s[i], s[j] = s[j], s[i]
	}
}

func tokenize(text string) map[string]struct{} {
	tokens := make(map[string]struct{})
	lower  := strings.ToLower(text)
	var buf strings.Builder
	for _, r := range lower {
		if unicode.IsLetter(r) {
			buf.WriteRune(r)
		} else {
			if buf.Len() >= 3 {
				tokens[buf.String()] = struct{}{}
			}
			buf.Reset()
		}
	}
	if buf.Len() >= 3 {
		tokens[buf.String()] = struct{}{}
	}
	return tokens
}
