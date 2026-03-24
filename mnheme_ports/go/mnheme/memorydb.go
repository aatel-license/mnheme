// mnheme/go/mnheme/memorydb.go
// =============================
// MemoryDB — public API
//
// Usage:
//   db, _ := mnheme.Open("mente.mnheme")
//   mem, _ := db.Remember("Debito", "ansia", "Ho firmato il mutuo.", "", nil)
//   memories, _ := db.Recall("Debito", "", 0, false)

package mnheme

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"
)

// Valid feelings
var validFeelings = map[string]struct{}{
	"gioia": {}, "tristezza": {}, "rabbia": {}, "paura": {},
	"nostalgia": {}, "amore": {}, "malinconia": {}, "serenità": {},
	"sorpresa": {}, "ansia": {}, "gratitudine": {}, "vergogna": {},
	"orgoglio": {}, "noia": {}, "curiosità": {},
}

// Memory is an immutable snapshot of a stored memory record.
type Memory struct {
	MemoryID  string   `json:"memory_id"`
	Concept   string   `json:"concept"`
	Feeling   string   `json:"feeling"`
	MediaType string   `json:"media_type"`
	Content   string   `json:"content"`
	Note      string   `json:"note"`
	Tags      []string `json:"tags"`
	Timestamp string   `json:"timestamp"`
	Checksum  string   `json:"checksum"`
}

// MemoryDB is the main database object.
type MemoryDB struct {
	storage *StorageEngine
	index   *IndexEngine
	path    string
}

// Open opens or creates the database at path.
// Cold start: scans the log and rebuilds indexes.
func Open(path string) (*MemoryDB, error) {
	storage, err := NewStorageEngine(path)
	if err != nil {
		return nil, fmt.Errorf("mnheme.Open: %w", err)
	}
	index   := NewIndexEngine()
	records, err := storage.Scan()
	if err != nil {
		return nil, fmt.Errorf("mnheme.Open scan: %w", err)
	}
	index.Rebuild(records)
	return &MemoryDB{storage: storage, index: index, path: path}, nil
}

// ── Write ─────────────────────────────────────────────────────────

// Remember appends a new memory to the database.
func (db *MemoryDB) Remember(
	concept   string,
	feeling   string,
	content   string,
	note      string,
	tags      []string,
	mediaType string,
) (*Memory, error) {
	concept = strings.TrimSpace(concept)
	if concept == "" {
		return nil, fmt.Errorf("concept cannot be empty")
	}
	if content == "" {
		return nil, fmt.Errorf("content cannot be empty")
	}
	if mediaType == "" {
		mediaType = "text"
	}
	if _, ok := validFeelings[feeling]; !ok {
		return nil, fmt.Errorf("invalid feeling: %q", feeling)
	}
	if tags == nil {
		tags = []string{}
	}

	memID     := uuid.NewString()
	timestamp := time.Now().UTC().Format(time.RFC3339Nano)
	checksum  := fmt.Sprintf("%x", sha256.Sum256([]byte(content)))

	record := map[string]any{
		"memory_id":  memID,
		"concept":    concept,
		"feeling":    feeling,
		"media_type": mediaType,
		"content":    content,
		"note":       note,
		"tags":       tags,
		"timestamp":  timestamp,
		"checksum":   checksum,
	}

	offset, err := db.storage.Append(record)
	if err != nil {
		return nil, fmt.Errorf("remember: %w", err)
	}
	db.index.IndexRecord(offset, record)

	return &Memory{
		MemoryID:  memID,
		Concept:   concept,
		Feeling:   feeling,
		MediaType: mediaType,
		Content:   content,
		Note:      note,
		Tags:      tags,
		Timestamp: timestamp,
		Checksum:  checksum,
	}, nil
}

// ── Read ──────────────────────────────────────────────────────────

// Recall returns memories for a concept, optionally filtered by feeling.
// limit=0 means no limit. Pass oldestFirst=true for ascending order.
func (db *MemoryDB) Recall(concept, feeling string, limit int, oldestFirst bool) ([]*Memory, error) {
	offsets := db.index.OffsetsByConcept(concept, feeling, oldestFirst)
	return db.loadOffsets(offsets, limit)
}

// RecallByFeeling returns all memories with the given feeling.
func (db *MemoryDB) RecallByFeeling(feeling string, limit int, oldestFirst bool) ([]*Memory, error) {
	offsets := db.index.OffsetsByFeeling(feeling, oldestFirst)
	return db.loadOffsets(offsets, limit)
}

// RecallAll returns every memory in the database.
func (db *MemoryDB) RecallAll(limit int, oldestFirst bool) ([]*Memory, error) {
	offsets := db.index.AllOffsets(oldestFirst)
	return db.loadOffsets(offsets, limit)
}

// Search performs a full-text scan across content, concept, and note.
func (db *MemoryDB) Search(
	text string,
	inContent, inConcept, inNote bool,
	limit int,
) ([]*Memory, error) {
	needle  := strings.ToLower(text)
	records, err := db.storage.Scan()
	if err != nil {
		return nil, err
	}
	var results []*Memory
	// Iterate in reverse (most recent first)
	for i := len(records) - 1; i >= 0; i-- {
		r := records[i].Record
		matched := false
		if inContent && strings.Contains(strings.ToLower(strVal(r, "content")), needle) {
			matched = true
		}
		if inConcept && strings.Contains(strings.ToLower(strVal(r, "concept")), needle) {
			matched = true
		}
		if inNote && strings.Contains(strings.ToLower(strVal(r, "note")), needle) {
			matched = true
		}
		if matched {
			results = append(results, recordToMemory(r))
			if limit > 0 && len(results) >= limit {
				break
			}
		}
	}
	return results, nil
}

// ── Stats ─────────────────────────────────────────────────────────

// Count returns number of memories, optionally filtered.
// Pass empty strings to skip filters.
func (db *MemoryDB) Count(concept, feeling string) int {
	return db.index.Count(concept, feeling)
}

// FeelingDistribution returns feeling → count map.
func (db *MemoryDB) FeelingDistribution() map[string]int {
	return db.index.FeelingDistribution()
}

// ListConcepts returns all known concepts sorted alphabetically.
func (db *MemoryDB) ListConcepts() []string {
	return db.index.AllConcepts()
}

// ConceptTimeline returns the emotional evolution of a concept over time.
func (db *MemoryDB) ConceptTimeline(concept string) ([]map[string]any, error) {
	offsets := db.index.TimelineOffsets(concept)
	var result []map[string]any
	for _, off := range offsets {
		r, err := db.storage.ReadAt(off)
		if err != nil {
			continue
		}
		result = append(result, map[string]any{
			"timestamp": strVal(r, "timestamp"),
			"feeling":   strVal(r, "feeling"),
			"note":      strVal(r, "note"),
			"tags":      r["tags"],
		})
	}
	return result, nil
}

// ── Export ────────────────────────────────────────────────────────

// ExportJSON serialises all memories to a JSON string.
func (db *MemoryDB) ExportJSON() (string, error) {
	memories, err := db.RecallAll(0, true)
	if err != nil {
		return "", err
	}
	out := map[string]any{
		"exported_at": time.Now().UTC().Format(time.RFC3339),
		"memories":    memories,
	}
	b, err := json.MarshalIndent(out, "", "  ")
	return string(b), err
}

// ── Internal ──────────────────────────────────────────────────────

func (db *MemoryDB) loadOffsets(offsets []uint64, limit int) ([]*Memory, error) {
	if limit > 0 && limit < len(offsets) {
		offsets = offsets[:limit]
	}
	result := make([]*Memory, 0, len(offsets))
	for _, off := range offsets {
		r, err := db.storage.ReadAt(off)
		if err != nil {
			continue
		}
		result = append(result, recordToMemory(r))
	}
	return result, nil
}

func recordToMemory(r map[string]any) *Memory {
	m := &Memory{
		MemoryID:  strVal(r, "memory_id"),
		Concept:   strVal(r, "concept"),
		Feeling:   strVal(r, "feeling"),
		MediaType: strVal(r, "media_type"),
		Content:   strVal(r, "content"),
		Note:      strVal(r, "note"),
		Timestamp: strVal(r, "timestamp"),
		Checksum:  strVal(r, "checksum"),
	}
	if tags, ok := r["tags"].([]any); ok {
		for _, t := range tags {
			if s, ok := t.(string); ok {
				m.Tags = append(m.Tags, s)
			}
		}
	}
	return m
}

// go.mod (module declaration)
// module github.com/aatel-license/mnheme
// go 1.22
// require github.com/google/uuid v1.6.0
