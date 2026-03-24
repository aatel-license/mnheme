// mnheme/java/mnheme/StorageEngine.java
// ======================================
// Append-only binary log engine.
// Frame: MAGIC(4B) | SIZE(4B big-endian) | JSON UTF-8 payload
// Deps: Jackson (com.fasterxml.jackson.core)

package mnheme;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.ReentrantLock;

public class StorageEngine {

    private static final byte[] MAGIC = {0x4D, 0x4E, 0x45, (byte) 0xE0};
    private static final int HEADER_SIZE = 8;

    private final Path path;
    private final ReentrantLock lock = new ReentrantLock();
    private final ObjectMapper mapper = new ObjectMapper();

    public StorageEngine(Path path) throws IOException {
        this.path = path;
        if (!Files.exists(path)) {
            Files.createFile(path);
        }
    }

    /**
     * Append a JSON record. Returns byte offset of the written record.
     */
    public long append(Map<String, Object> record) throws IOException {
        byte[] payload = mapper.writeValueAsBytes(record);
        int size = payload.length;

        ByteBuffer frame = ByteBuffer.allocate(HEADER_SIZE + size);
        frame.put(MAGIC);
        frame.order(ByteOrder.BIG_ENDIAN).putInt(size);
        frame.put(payload);
        frame.flip();

        lock.lock();
        try (FileChannel ch = FileChannel.open(
                path, StandardOpenOption.APPEND, StandardOpenOption.WRITE)) {
            long offset = ch.size();
            while (frame.hasRemaining()) ch.write(frame);
            ch.force(true); // fsync
            return offset;
        } finally {
            lock.unlock();
        }
    }

    /** Holds a scanned (offset, record) pair. */
    public record ScanResult(long offset, Map<String, Object> record) {}

    /**
     * Scan all valid records. Truncated/corrupted records are skipped silently.
     */
    @SuppressWarnings("unchecked")
    public List<ScanResult> scan() throws IOException {
        List<ScanResult> results = new ArrayList<>();
        if (!Files.exists(path)) return results;

        try (RandomAccessFile raf = new RandomAccessFile(path.toFile(), "r")) {
            byte[] header = new byte[HEADER_SIZE];
            while (true) {
                long offset = raf.getFilePointer();
                int read = raf.read(header);
                if (read < HEADER_SIZE) break;

                if (!magicMatches(header)) {
                    raf.seek(offset + 1); // resync
                    continue;
                }

                int size = ByteBuffer.wrap(header, 4, 4)
                        .order(ByteOrder.BIG_ENDIAN).getInt();
                byte[] payload = new byte[size];
                if (raf.read(payload) < size) break; // truncated

                try {
                    Map<String, Object> rec = mapper.readValue(payload, Map.class);
                    results.add(new ScanResult(offset, rec));
                } catch (Exception ignored) { /* corrupted JSON */ }
            }
        }
        return results;
    }

    /**
     * Read a single record at a known offset — O(1).
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> readAt(long offset) throws IOException {
        try (RandomAccessFile raf = new RandomAccessFile(path.toFile(), "r")) {
            raf.seek(offset);
            byte[] header = new byte[HEADER_SIZE];
            if (raf.read(header) < HEADER_SIZE) return null;
            if (!magicMatches(header)) return null;

            int size = ByteBuffer.wrap(header, 4, 4)
                    .order(ByteOrder.BIG_ENDIAN).getInt();
            byte[] payload = new byte[size];
            if (raf.read(payload) < size) return null;

            try {
                return mapper.readValue(payload, Map.class);
            } catch (Exception e) {
                return null;
            }
        }
    }

    public long fileSize() throws IOException {
        return Files.size(path);
    }

    private static boolean magicMatches(byte[] header) {
        return header[0] == MAGIC[0] && header[1] == MAGIC[1]
                && header[2] == MAGIC[2] && header[3] == MAGIC[3];
    }
}
