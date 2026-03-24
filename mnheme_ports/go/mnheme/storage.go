// mnheme/go/mnheme/storage.go
// ============================
// StorageEngine — append-only binary log
//
// Frame: MAGIC(4B) | SIZE(4B big-endian) | JSON UTF-8 payload
// Every append calls Sync() for durability.

package mnheme

import (
	"encoding/binary"
	"encoding/json"
	"errors"
	"io"
	"os"
	"sync"
)

var magic = [4]byte{0x4D, 0x4E, 0x45, 0xE0}

const headerSize = 8

// StorageEngine manages the append-only binary log file.
type StorageEngine struct {
	path string
	mu   sync.Mutex
}

// NewStorageEngine opens or creates the storage file at path.
func NewStorageEngine(path string) (*StorageEngine, error) {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil {
		return nil, err
	}
	f.Close()
	return &StorageEngine{path: path}, nil
}

// Append serialises record as JSON and writes a framed record to the file.
// Returns the byte offset of the written record.
func (s *StorageEngine) Append(record map[string]any) (uint64, error) {
	payload, err := json.Marshal(record)
	if err != nil {
		return 0, err
	}

	size := uint32(len(payload))
	frame := make([]byte, headerSize+len(payload))
	copy(frame[:4], magic[:])
	binary.BigEndian.PutUint32(frame[4:8], size)
	copy(frame[8:], payload)

	s.mu.Lock()
	defer s.mu.Unlock()

	f, err := os.OpenFile(s.path, os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil {
		return 0, err
	}
	defer f.Close()

	offset, err := f.Seek(0, io.SeekEnd)
	if err != nil {
		return 0, err
	}

	if _, err := f.Write(frame); err != nil {
		return 0, err
	}
	return uint64(offset), f.Sync() // fsync
}

// ScanResult holds a scanned record and its file offset.
type ScanResult struct {
	Offset uint64
	Record map[string]any
}

// Scan reads all valid records sequentially from the beginning.
// Truncated or corrupted records are silently skipped.
func (s *StorageEngine) Scan() ([]ScanResult, error) {
	f, err := os.Open(s.path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, nil
		}
		return nil, err
	}
	defer f.Close()

	var results []ScanResult
	header := make([]byte, headerSize)

	for {
		offset, err := f.Seek(0, io.SeekCurrent)
		if err != nil {
			break
		}

		_, err = io.ReadFull(f, header)
		if err != nil {
			break // EOF or truncated header
		}

		if [4]byte(header[:4]) != magic {
			// resync: skip one byte
			f.Seek(offset+1, io.SeekStart)
			continue
		}

		size := binary.BigEndian.Uint32(header[4:8])
		payload := make([]byte, size)
		if _, err := io.ReadFull(f, payload); err != nil {
			break // truncated payload
		}

		var record map[string]any
		if err := json.Unmarshal(payload, &record); err != nil {
			continue // corrupted JSON, skip
		}
		results = append(results, ScanResult{Offset: uint64(offset), Record: record})
	}

	return results, nil
}

// ReadAt reads a single record at a known byte offset — O(1).
func (s *StorageEngine) ReadAt(offset uint64) (map[string]any, error) {
	f, err := os.Open(s.path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	if _, err := f.Seek(int64(offset), io.SeekStart); err != nil {
		return nil, err
	}

	header := make([]byte, headerSize)
	if _, err := io.ReadFull(f, header); err != nil {
		return nil, err
	}
	if [4]byte(header[:4]) != magic {
		return nil, errors.New("invalid magic at offset")
	}

	size := binary.BigEndian.Uint32(header[4:8])
	payload := make([]byte, size)
	if _, err := io.ReadFull(f, payload); err != nil {
		return nil, err
	}

	var record map[string]any
	if err := json.Unmarshal(payload, &record); err != nil {
		return nil, err
	}
	return record, nil
}

// FileSize returns the current file size in bytes.
func (s *StorageEngine) FileSize() (int64, error) {
	info, err := os.Stat(s.path)
	if err != nil {
		return 0, err
	}
	return info.Size(), nil
}
