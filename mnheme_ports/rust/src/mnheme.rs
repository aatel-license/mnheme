// mnheme/rust/src/mnheme.rs
// ==========================
// MemoryDB — public API for the MNHEME memory database.
//
// Usage:
//   let mut db = MemoryDB::open("mente.mnheme")?;
//   let mem = db.remember("Debito", Feeling::Ansia, "Ho firmato il mutuo.")?;
//   let memories = db.recall("Debito", None, None, false)?;

use std::io;
use std::path::Path;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use uuid::Uuid;

use crate::storage::StorageEngine;
use crate::index::IndexEngine;

// ─── Feeling enum ─────────────────────────────────────────────
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Feeling {
    Gioia,
    Tristezza,
    Rabbia,
    Paura,
    Nostalgia,
    Amore,
    Malinconia,
    #[serde(rename = "serenità")]
    Serenita,
    Sorpresa,
    Ansia,
    Gratitudine,
    Vergogna,
    Orgoglio,
    Noia,
    #[serde(rename = "curiosità")]
    Curiosita,
}

impl Feeling {
    pub fn as_str(&self) -> &str {
        match self {
            Feeling::Gioia      => "gioia",
            Feeling::Tristezza  => "tristezza",
            Feeling::Rabbia     => "rabbia",
            Feeling::Paura      => "paura",
            Feeling::Nostalgia  => "nostalgia",
            Feeling::Amore      => "amore",
            Feeling::Malinconia => "malinconia",
            Feeling::Serenita   => "serenità",
            Feeling::Sorpresa   => "sorpresa",
            Feeling::Ansia      => "ansia",
            Feeling::Gratitudine=> "gratitudine",
            Feeling::Vergogna   => "vergogna",
            Feeling::Orgoglio   => "orgoglio",
            Feeling::Noia       => "noia",
            Feeling::Curiosita  => "curiosità",
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "gioia"       => Some(Feeling::Gioia),
            "tristezza"   => Some(Feeling::Tristezza),
            "rabbia"      => Some(Feeling::Rabbia),
            "paura"       => Some(Feeling::Paura),
            "nostalgia"   => Some(Feeling::Nostalgia),
            "amore"       => Some(Feeling::Amore),
            "malinconia"  => Some(Feeling::Malinconia),
            "serenità"    => Some(Feeling::Serenita),
            "sorpresa"    => Some(Feeling::Sorpresa),
            "ansia"       => Some(Feeling::Ansia),
            "gratitudine" => Some(Feeling::Gratitudine),
            "vergogna"    => Some(Feeling::Vergogna),
            "orgoglio"    => Some(Feeling::Orgoglio),
            "noia"        => Some(Feeling::Noia),
            "curiosità"   => Some(Feeling::Curiosita),
            _             => None,
        }
    }
}

// ─── Memory struct ────────────────────────────────────────────
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Memory {
    pub memory_id:  String,
    pub concept:    String,
    pub feeling:    String,
    pub media_type: String,
    pub content:    String,
    pub note:       String,
    pub tags:       Vec<String>,
    pub timestamp:  String,
    pub checksum:   String,
}

// ─── Errors ───────────────────────────────────────────────────
#[derive(Debug)]
pub enum MnhemeError {
    Io(io::Error),
    InvalidFeeling(String),
    EmptyConcept,
    EmptyContent,
}

impl From<io::Error> for MnhemeError {
    fn from(e: io::Error) -> Self {
        MnhemeError::Io(e)
    }
}

impl std::fmt::Display for MnhemeError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            MnhemeError::Io(e)              => write!(f, "IO error: {}", e),
            MnhemeError::InvalidFeeling(s)  => write!(f, "Invalid feeling: {}", s),
            MnhemeError::EmptyConcept       => write!(f, "Concept cannot be empty"),
            MnhemeError::EmptyContent       => write!(f, "Content cannot be empty"),
        }
    }
}

// ─── MemoryDB ─────────────────────────────────────────────────
pub struct MemoryDB {
    storage: StorageEngine,
    index:   IndexEngine,
    path:    String,
}

impl MemoryDB {
    /// Open or create the database at `path`.
    /// Cold start: scans the log and rebuilds indexes.
    pub fn open(path: impl AsRef<Path>) -> Result<Self, MnhemeError> {
        let path_str = path.as_ref().to_string_lossy().to_string();
        let storage  = StorageEngine::new(path.as_ref())?;
        let mut index = IndexEngine::new();
        let records   = storage.scan()?;
        index.rebuild(records);
        Ok(Self { storage, index, path: path_str })
    }

    // ── WRITE ──────────────────────────────────────────────────

    /// Append a new memory. Returns the immutable Memory struct.
    pub fn remember(
        &mut self,
        concept:    &str,
        feeling:    Feeling,
        content:    &str,
        note:       Option<&str>,
        tags:       Option<Vec<String>>,
        media_type: Option<&str>,
    ) -> Result<Memory, MnhemeError> {
        let concept = concept.trim();
        if concept.is_empty() {
            return Err(MnhemeError::EmptyConcept);
        }
        if content.is_empty() {
            return Err(MnhemeError::EmptyContent);
        }

        let memory_id  = Uuid::new_v4().to_string();
        let timestamp  = Utc::now().to_rfc3339();
        let checksum   = format!("{:x}", Sha256::digest(content.as_bytes()));
        let tags_list  = tags.unwrap_or_default();
        let note_str   = note.unwrap_or("");
        let mtype      = media_type.unwrap_or("text");

        let record = json!({
            "memory_id":  memory_id,
            "concept":    concept,
            "feeling":    feeling.as_str(),
            "media_type": mtype,
            "content":    content,
            "note":       note_str,
            "tags":       tags_list,
            "timestamp":  timestamp,
            "checksum":   checksum,
        });

        let offset = self.storage.append(&record)?;
        self.index.index_record(offset, &record);

        Ok(Memory {
            memory_id,
            concept:    concept.to_string(),
            feeling:    feeling.as_str().to_string(),
            media_type: mtype.to_string(),
            content:    content.to_string(),
            note:       note_str.to_string(),
            tags:       tags_list,
            timestamp,
            checksum,
        })
    }

    // ── READ ───────────────────────────────────────────────────

    /// Recall memories by concept, optionally filtered by feeling.
    pub fn recall(
        &self,
        concept:      &str,
        feeling:      Option<&str>,
        limit:        Option<usize>,
        oldest_first: bool,
    ) -> Result<Vec<Memory>, MnhemeError> {
        let offsets = self.index.offsets_by_concept(concept.trim(), feeling, oldest_first);
        self.load_offsets(&offsets, limit)
    }

    /// Recall all memories tagged with a feeling.
    pub fn recall_by_feeling(
        &self,
        feeling:      &str,
        limit:        Option<usize>,
        oldest_first: bool,
    ) -> Result<Vec<Memory>, MnhemeError> {
        let offsets = self.index.offsets_by_feeling(feeling, oldest_first);
        self.load_offsets(&offsets, limit)
    }

    /// Retrieve every memory.
    pub fn recall_all(
        &self,
        limit:        Option<usize>,
        oldest_first: bool,
    ) -> Result<Vec<Memory>, MnhemeError> {
        let offsets = self.index.all_offsets(oldest_first);
        self.load_offsets(&offsets, limit)
    }

    /// Full-text search across content, concept, note.
    pub fn search(
        &self,
        text:       &str,
        in_content: bool,
        in_concept: bool,
        in_note:    bool,
        limit:      Option<usize>,
    ) -> Result<Vec<Memory>, MnhemeError> {
        let needle = text.to_lowercase();
        let mut results = Vec::new();
        let records = self.storage.scan()?;
        for (_, record) in records.iter().rev() {
            let mut matched = false;
            if in_content && record["content"].as_str().unwrap_or("").to_lowercase().contains(&needle) {
                matched = true;
            }
            if in_concept && record["concept"].as_str().unwrap_or("").to_lowercase().contains(&needle) {
                matched = true;
            }
            if in_note && record["note"].as_str().unwrap_or("").to_lowercase().contains(&needle) {
                matched = true;
            }
            if matched {
                results.push(Self::record_to_memory(record));
                if let Some(lim) = limit {
                    if results.len() >= lim {
                        break;
                    }
                }
            }
        }
        Ok(results)
    }

    // ── STATS ──────────────────────────────────────────────────

    pub fn count(&self, concept: Option<&str>, feeling: Option<&str>) -> usize {
        self.index.count(concept, feeling)
    }

    pub fn feeling_distribution(&self) -> std::collections::HashMap<String, usize> {
        let mut dist = self.index.feeling_distribution();
        dist
    }

    pub fn list_concepts(&self) -> Vec<String> {
        self.index.all_concepts()
    }

    pub fn concept_timeline(&self, concept: &str) -> Result<Vec<Value>, MnhemeError> {
        let offsets = self.index.timeline_offsets(concept.trim());
        let mut result = Vec::new();
        for offset in offsets {
            if let Some(r) = self.storage.read_at(offset)? {
                result.push(json!({
                    "timestamp": r["timestamp"],
                    "feeling":   r["feeling"],
                    "note":      r["note"],
                    "tags":      r["tags"],
                }));
            }
        }
        Ok(result)
    }

    // ── EXPORT ────────────────────────────────────────────────

    pub fn export_json(&self) -> Result<String, MnhemeError> {
        let memories = self.recall_all(None, true)?;
        let export = json!({
            "exported_at": Utc::now().to_rfc3339(),
            "memories": memories,
        });
        Ok(serde_json::to_string_pretty(&export)
            .map_err(|e| io::Error::new(io::ErrorKind::Other, e))?)
    }

    // ── INTERNAL ──────────────────────────────────────────────

    fn load_offsets(&self, offsets: &[u64], limit: Option<usize>) -> Result<Vec<Memory>, MnhemeError> {
        let iter: Box<dyn Iterator<Item = &u64>> = if let Some(lim) = limit {
            Box::new(offsets.iter().take(lim))
        } else {
            Box::new(offsets.iter())
        };
        let mut result = Vec::new();
        for &offset in iter {
            if let Some(record) = self.storage.read_at(offset)? {
                result.push(Self::record_to_memory(&record));
            }
        }
        Ok(result)
    }

    fn record_to_memory(r: &Value) -> Memory {
        Memory {
            memory_id:  r["memory_id"].as_str().unwrap_or("").to_string(),
            concept:    r["concept"].as_str().unwrap_or("").to_string(),
            feeling:    r["feeling"].as_str().unwrap_or("").to_string(),
            media_type: r["media_type"].as_str().unwrap_or("text").to_string(),
            content:    r["content"].as_str().unwrap_or("").to_string(),
            note:       r["note"].as_str().unwrap_or("").to_string(),
            tags:       r["tags"]
                .as_array()
                .map(|a| a.iter().filter_map(|v| v.as_str().map(String::from)).collect())
                .unwrap_or_default(),
            timestamp:  r["timestamp"].as_str().unwrap_or("").to_string(),
            checksum:   r["checksum"].as_str().unwrap_or("").to_string(),
        }
    }
}

// ─── Cargo.toml ───────────────────────────────────────────────
// [package]
// name    = "mnheme"
// version = "0.1.0"
// edition = "2021"
//
// [dependencies]
// serde       = { version = "1", features = ["derive"] }
// serde_json  = "1"
// chrono      = { version = "0.4", features = ["serde"] }
// uuid        = { version = "1", features = ["v4"] }
// sha2        = "0.10"
// regex       = "1"
