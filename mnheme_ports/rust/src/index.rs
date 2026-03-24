// mnheme/rust/src/index.rs
// =========================
// IndexEngine — all in-RAM, rebuilt from log on cold start.
//
// Structures:
//   concept_index : HashMap<String, Vec<u64>>
//   feeling_index : HashMap<String, Vec<u64>>
//   tag_index     : HashMap<String, Vec<u64>>
//   cf_index      : HashMap<(String,String), Vec<u64>>
//   timeline      : Vec<(String, u64)>  -- sorted by timestamp
//   word_index    : HashMap<String, Vec<u64>>  -- inverted full-text

use std::collections::HashMap;
use regex::Regex;
use serde_json::Value;

pub struct IndexEngine {
    concept: HashMap<String, Vec<u64>>,
    feeling: HashMap<String, Vec<u64>>,
    tag:     HashMap<String, Vec<u64>>,
    cf:      HashMap<(String, String), Vec<u64>>,
    timeline: Vec<(String, u64)>,
    all:     Vec<u64>,
    word:    HashMap<String, Vec<u64>>,
}

impl IndexEngine {
    pub fn new() -> Self {
        Self {
            concept: HashMap::new(),
            feeling: HashMap::new(),
            tag:     HashMap::new(),
            cf:      HashMap::new(),
            timeline: Vec::new(),
            all:     Vec::new(),
            word:    HashMap::new(),
        }
    }

    /// Index a single record at `offset`.
    pub fn index_record(&mut self, offset: u64, record: &Value) {
        let concept   = record["concept"].as_str().unwrap_or("").to_string();
        let feeling   = record["feeling"].as_str().unwrap_or("").to_string();
        let tags: Vec<String> = record["tags"]
            .as_array()
            .map(|a| a.iter().filter_map(|v| v.as_str().map(String::from)).collect())
            .unwrap_or_default();
        let timestamp = record["timestamp"].as_str().unwrap_or("").to_string();

        self.concept.entry(concept.clone()).or_default().push(offset);
        self.feeling.entry(feeling.clone()).or_default().push(offset);
        self.cf.entry((concept.clone(), feeling.clone())).or_default().push(offset);
        self.timeline.push((timestamp, offset));
        self.all.push(offset);

        for tag in &tags {
            if !tag.is_empty() {
                self.tag.entry(tag.clone()).or_default().push(offset);
            }
        }

        // Inverted index — tokenize content + concept + note
        let content = record["content"].as_str().unwrap_or("");
        let note    = record["note"].as_str().unwrap_or("");
        let tokens  = tokenize(&format!("{} {} {}", content, concept, note));
        for token in tokens {
            self.word.entry(token).or_default().push(offset);
        }
    }

    /// Rebuild all indexes from an iterator of (offset, record) pairs.
    pub fn rebuild(&mut self, records: Vec<(u64, Value)>) -> usize {
        self.concept.clear();
        self.feeling.clear();
        self.tag.clear();
        self.cf.clear();
        self.timeline.clear();
        self.all.clear();
        self.word.clear();

        let count = records.len();
        for (offset, record) in records {
            self.index_record(offset, &record);
        }
        self.timeline.sort_by(|a, b| a.0.cmp(&b.0));
        count
    }

    // ── QUERIES ──────────────────────────────────────────────────

    pub fn offsets_by_concept(
        &self,
        concept: &str,
        feeling: Option<&str>,
        oldest_first: bool,
    ) -> Vec<u64> {
        let mut offsets = if let Some(f) = feeling {
            self.cf
                .get(&(concept.to_string(), f.to_string()))
                .cloned()
                .unwrap_or_default()
        } else {
            self.concept.get(concept).cloned().unwrap_or_default()
        };
        if !oldest_first {
            offsets.reverse();
        }
        offsets
    }

    pub fn offsets_by_feeling(&self, feeling: &str, oldest_first: bool) -> Vec<u64> {
        let mut offsets = self.feeling.get(feeling).cloned().unwrap_or_default();
        if !oldest_first {
            offsets.reverse();
        }
        offsets
    }

    pub fn offsets_by_word(&self, word: &str) -> Vec<u64> {
        let mut offsets = self.word.get(&word.to_lowercase()).cloned().unwrap_or_default();
        offsets.reverse(); // most recent first
        offsets
    }

    pub fn all_offsets(&self, oldest_first: bool) -> Vec<u64> {
        let mut offs = self.all.clone();
        if !oldest_first {
            offs.reverse();
        }
        offs
    }

    pub fn timeline_offsets(&self, concept: &str) -> Vec<u64> {
        let concept_set: std::collections::HashSet<u64> = self
            .concept
            .get(concept)
            .map(|v| v.iter().copied().collect())
            .unwrap_or_default();
        self.timeline
            .iter()
            .filter(|(_, off)| concept_set.contains(off))
            .map(|(_, off)| *off)
            .collect()
    }

    // ── STATS ─────────────────────────────────────────────────────

    pub fn all_concepts(&self) -> Vec<String> {
        let mut v: Vec<_> = self.concept.keys().cloned().collect();
        v.sort();
        v
    }

    pub fn count(&self, concept: Option<&str>, feeling: Option<&str>) -> usize {
        match (concept, feeling) {
            (Some(c), Some(f)) => self
                .cf
                .get(&(c.to_string(), f.to_string()))
                .map_or(0, |v| v.len()),
            (Some(c), None) => self.concept.get(c).map_or(0, |v| v.len()),
            (None, Some(f)) => self.feeling.get(f).map_or(0, |v| v.len()),
            (None, None) => self.all.len(),
        }
    }

    pub fn feeling_distribution(&self) -> HashMap<String, usize> {
        self.feeling
            .iter()
            .map(|(k, v)| (k.clone(), v.len()))
            .collect()
    }

    pub fn concept_feeling_matrix(&self) -> HashMap<String, HashMap<String, usize>> {
        let mut matrix: HashMap<String, HashMap<String, usize>> = HashMap::new();
        for ((concept, feeling), offsets) in &self.cf {
            matrix
                .entry(concept.clone())
                .or_default()
                .insert(feeling.clone(), offsets.len());
        }
        matrix
    }
}

fn tokenize(text: &str) -> std::collections::HashSet<String> {
    // Match Unicode word chars, min 3 chars
    let re = Regex::new(r"[a-zA-Zàáâäãåæçèéêëìíîïòóôöõùúûüýÿñ]{3,}").unwrap();
    re.find_iter(&text.to_lowercase())
        .map(|m| m.as_str().to_string())
        .collect()
}
