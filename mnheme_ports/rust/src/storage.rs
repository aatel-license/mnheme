// mnheme/rust/src/storage.rs
// ============================
// StorageEngine — append-only binary log
//
// Frame layout:
//   MAGIC (4B) | SIZE (4B big-endian) | PAYLOAD (SIZE B, UTF-8 JSON)
//
// Every append is atomic (single write + fsync).
// Truncated records at crash are silently skipped on scan.

use std::fs::{File, OpenOptions};
use std::io::{self, BufReader, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use serde_json::Value;

/// 4-byte magic: M N E 0xE0
pub const MAGIC: [u8; 4] = [0x4D, 0x4E, 0x45, 0xE0];
pub const HEADER_SIZE: usize = 8; // 4 magic + 4 size

pub struct StorageEngine {
    path: PathBuf,
    lock: Mutex<()>,
}

impl StorageEngine {
    /// Open or create the storage file at `path`.
    pub fn new(path: impl AsRef<Path>) -> io::Result<Self> {
        let path = path.as_ref().to_path_buf();
        // Create if not exists
        OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path)?;
        Ok(Self {
            path,
            lock: Mutex::new(()),
        })
    }

    /// Append a JSON record. Returns the byte offset where it was written.
    pub fn append(&self, record: &Value) -> io::Result<u64> {
        let payload = serde_json::to_vec(record)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
        let size = payload.len() as u32;
        let mut frame = Vec::with_capacity(HEADER_SIZE + payload.len());
        frame.extend_from_slice(&MAGIC);
        frame.extend_from_slice(&size.to_be_bytes());
        frame.extend_from_slice(&payload);

        let _guard = self.lock.lock().unwrap();
        let mut f = OpenOptions::new().append(true).open(&self.path)?;
        let offset = f.seek(SeekFrom::End(0))?;
        f.write_all(&frame)?;
        f.flush()?;
        f.sync_all()?; // fsync
        Ok(offset)
    }

    /// Scan all valid records. Returns iterator of (offset, Value).
    pub fn scan(&self) -> io::Result<Vec<(u64, Value)>> {
        let f = File::open(&self.path)?;
        let mut reader = BufReader::new(f);
        let mut results = Vec::new();

        loop {
            let offset = reader.seek(SeekFrom::Current(0))?;
            let mut header = [0u8; HEADER_SIZE];
            match reader.read_exact(&mut header) {
                Ok(_) => {}
                Err(e) if e.kind() == io::ErrorKind::UnexpectedEof => break,
                Err(e) => return Err(e),
            }

            if header[..4] != MAGIC {
                // Seek back and skip one byte to resync
                reader.seek(SeekFrom::Start(offset + 1))?;
                continue;
            }

            let size = u32::from_be_bytes([header[4], header[5], header[6], header[7]]) as usize;
            let mut payload = vec![0u8; size];
            match reader.read_exact(&mut payload) {
                Ok(_) => {}
                Err(_) => break, // truncated payload
            }

            if let Ok(record) = serde_json::from_slice::<Value>(&payload) {
                results.push((offset, record));
            }
            // corrupted JSON: silently skip
        }

        Ok(results)
    }

    /// Read a single record at a known byte offset — O(1).
    pub fn read_at(&self, offset: u64) -> io::Result<Option<Value>> {
        let mut f = File::open(&self.path)?;
        f.seek(SeekFrom::Start(offset))?;

        let mut header = [0u8; HEADER_SIZE];
        if f.read_exact(&mut header).is_err() {
            return Ok(None);
        }
        if header[..4] != MAGIC {
            return Ok(None);
        }
        let size = u32::from_be_bytes([header[4], header[5], header[6], header[7]]) as usize;
        let mut payload = vec![0u8; size];
        if f.read_exact(&mut payload).is_err() {
            return Ok(None);
        }
        Ok(serde_json::from_slice(&payload).ok())
    }

    /// File size in bytes.
    pub fn file_size(&self) -> io::Result<u64> {
        Ok(std::fs::metadata(&self.path)?.len())
    }
}
