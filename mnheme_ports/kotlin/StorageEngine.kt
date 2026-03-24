// mnheme/kotlin/mnheme/StorageEngine.kt
// =======================================
// Append-only binary log engine — Android & JVM compatible.
// Zero external deps: uses only kotlin.stdlib + org.json (Android built-in).
//
// Frame: MAGIC(4B) | SIZE(4B big-endian) | JSON UTF-8 payload
//
// On Android: pass context.filesDir.resolve("mente.mnheme") as path.
// On JVM:     pass java.nio.file.Path or java.io.File.

package mnheme

import org.json.JSONObject
import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock

private val MAGIC       = byteArrayOf(0x4D, 0x4E, 0x45, 0xE0.toByte())
private const val HEADER_SIZE = 8

class StorageEngine(private val file: File) {

    private val lock = ReentrantLock()

    init {
        if (!file.exists()) file.createNewFile()
    }

    /**
     * Append a JSON record. Returns the byte offset of the written frame.
     */
    fun append(record: JSONObject): Long {
        val payload = record.toString().toByteArray(Charsets.UTF_8)
        val size    = payload.size

        val frame = ByteBuffer.allocate(HEADER_SIZE + size).apply {
            order(ByteOrder.BIG_ENDIAN)
            put(MAGIC)
            putInt(size)
            put(payload)
        }.array()

        return lock.withLock {
            file.outputStream().use { os ->
                val offset = file.length()
                os.channel.apply {
                    position(size()) // seek to end
                    write(ByteBuffer.wrap(frame))
                    force(true) // fsync
                }
                offset
            }
        }
    }

    data class ScanResult(val offset: Long, val record: JSONObject)

    /**
     * Scan all valid records. Truncated/corrupted records silently skipped.
     */
    fun scan(): List<ScanResult> {
        val results = mutableListOf<ScanResult>()
        if (!file.exists() || file.length() == 0L) return results

        RandomAccessFile(file, "r").use { raf ->
            val header = ByteArray(HEADER_SIZE)
            while (true) {
                val offset = raf.filePointer
                val read   = raf.read(header)
                if (read < HEADER_SIZE) break

                if (!header.take(4).toByteArray().contentEquals(MAGIC)) {
                    raf.seek(offset + 1) // resync
                    continue
                }

                val size = ByteBuffer.wrap(header, 4, 4)
                    .order(ByteOrder.BIG_ENDIAN).int
                val payload = ByteArray(size)
                if (raf.read(payload) < size) break // truncated

                runCatching { JSONObject(String(payload, Charsets.UTF_8)) }
                    .onSuccess { results.add(ScanResult(offset, it)) }
                // corrupted JSON: skip silently
            }
        }
        return results
    }

    /**
     * Read a single record at a known byte offset — O(1).
     */
    fun readAt(offset: Long): JSONObject? {
        if (!file.exists()) return null
        return runCatching {
            RandomAccessFile(file, "r").use { raf ->
                raf.seek(offset)
                val header = ByteArray(HEADER_SIZE)
                if (raf.read(header) < HEADER_SIZE) return null
                if (!header.take(4).toByteArray().contentEquals(MAGIC)) return null

                val size = ByteBuffer.wrap(header, 4, 4)
                    .order(ByteOrder.BIG_ENDIAN).int
                val payload = ByteArray(size)
                if (raf.read(payload) < size) return null
                JSONObject(String(payload, Charsets.UTF_8))
            }
        }.getOrNull()
    }

    fun fileSize(): Long = if (file.exists()) file.length() else 0L
}
