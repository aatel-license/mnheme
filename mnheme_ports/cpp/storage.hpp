// mnheme/cpp/storage.hpp
// =======================
// StorageEngine — append-only binary log
// Deps: nlohmann/json (header-only)
//
// Frame: MAGIC(4B) | SIZE(4B big-endian) | JSON UTF-8 PAYLOAD

#pragma once
#include <cstdint>
#include <filesystem>
#include <mutex>
#include <optional>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>

namespace mnheme {

using json = nlohmann::json;

static constexpr uint8_t MAGIC[4] = {0x4D, 0x4E, 0x45, 0xE0};
static constexpr size_t  HEADER_SIZE = 8;

class StorageEngine {
public:
    explicit StorageEngine(const std::filesystem::path& path);

    /// Append a JSON record. Returns byte offset of the written record.
    uint64_t append(const json& record);

    /// Scan all valid records. Returns vector of (offset, json).
    std::vector<std::pair<uint64_t, json>> scan() const;

    /// Read a single record at a known offset — O(1).
    std::optional<json> read_at(uint64_t offset) const;

    /// File size in bytes.
    uint64_t file_size() const;

private:
    std::filesystem::path path_;
    mutable std::mutex    mutex_;

    static uint32_t read_be32(const uint8_t* buf);
    static void     write_be32(uint8_t* buf, uint32_t val);
};

} // namespace mnheme
