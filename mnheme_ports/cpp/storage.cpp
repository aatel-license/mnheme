// mnheme/cpp/storage.cpp
#include "storage.hpp"
#include <cstring>
#include <fstream>
#include <stdexcept>

#ifdef _WIN32
  #include <windows.h>
  #include <io.h>
#else
  #include <unistd.h>
#endif

namespace mnheme {

StorageEngine::StorageEngine(const std::filesystem::path& path)
    : path_(path)
{
    // Create if not exists
    if (!std::filesystem::exists(path_)) {
        std::ofstream f(path_, std::ios::binary);
        if (!f) throw std::runtime_error("Cannot create storage file: " + path_.string());
    }
}

uint32_t StorageEngine::read_be32(const uint8_t* buf) {
    return (static_cast<uint32_t>(buf[0]) << 24) |
           (static_cast<uint32_t>(buf[1]) << 16) |
           (static_cast<uint32_t>(buf[2]) << 8)  |
           (static_cast<uint32_t>(buf[3]));
}

void StorageEngine::write_be32(uint8_t* buf, uint32_t val) {
    buf[0] = (val >> 24) & 0xFF;
    buf[1] = (val >> 16) & 0xFF;
    buf[2] = (val >>  8) & 0xFF;
    buf[3] = (val      ) & 0xFF;
}

uint64_t StorageEngine::append(const json& record) {
    std::string payload = record.dump();
    uint32_t size = static_cast<uint32_t>(payload.size());

    std::vector<uint8_t> frame;
    frame.reserve(HEADER_SIZE + size);
    frame.insert(frame.end(), MAGIC, MAGIC + 4);
    uint8_t size_buf[4];
    write_be32(size_buf, size);
    frame.insert(frame.end(), size_buf, size_buf + 4);
    frame.insert(frame.end(), payload.begin(), payload.end());

    std::lock_guard<std::mutex> lock(mutex_);

    std::ofstream f(path_, std::ios::binary | std::ios::app);
    if (!f) throw std::runtime_error("Cannot open storage file for writing");

    uint64_t offset = static_cast<uint64_t>(f.tellp());
    f.write(reinterpret_cast<const char*>(frame.data()), frame.size());
    f.flush();

#ifdef _WIN32
    HANDLE h = reinterpret_cast<HANDLE>(_get_osfhandle(_fileno(
        reinterpret_cast<FILE*>(f.rdbuf()))));
    FlushFileBuffers(h);
#else
    // fsync via fd
    int fd = open(path_.c_str(), O_RDONLY);
    if (fd != -1) { fsync(fd); close(fd); }
#endif

    return offset;
}

std::vector<std::pair<uint64_t, json>> StorageEngine::scan() const {
    std::vector<std::pair<uint64_t, json>> results;

    std::ifstream f(path_, std::ios::binary);
    if (!f) return results;

    while (true) {
        uint64_t offset = static_cast<uint64_t>(f.tellg());
        uint8_t header[HEADER_SIZE];
        if (!f.read(reinterpret_cast<char*>(header), HEADER_SIZE)) break;

        if (std::memcmp(header, MAGIC, 4) != 0) {
            // Resync: seek back and skip one byte
            f.seekg(static_cast<std::streamoff>(offset + 1));
            continue;
        }

        uint32_t size = read_be32(header + 4);
        std::string payload(size, '\0');
        if (!f.read(payload.data(), size)) break; // truncated

        try {
            results.emplace_back(offset, json::parse(payload));
        } catch (...) {
            // corrupted JSON — skip silently
        }
    }

    return results;
}

std::optional<json> StorageEngine::read_at(uint64_t offset) const {
    std::ifstream f(path_, std::ios::binary);
    if (!f) return std::nullopt;

    f.seekg(static_cast<std::streamoff>(offset));
    uint8_t header[HEADER_SIZE];
    if (!f.read(reinterpret_cast<char*>(header), HEADER_SIZE)) return std::nullopt;
    if (std::memcmp(header, MAGIC, 4) != 0) return std::nullopt;

    uint32_t size = read_be32(header + 4);
    std::string payload(size, '\0');
    if (!f.read(payload.data(), size)) return std::nullopt;

    try {
        return json::parse(payload);
    } catch (...) {
        return std::nullopt;
    }
}

uint64_t StorageEngine::file_size() const {
    return std::filesystem::file_size(path_);
}

} // namespace mnheme
