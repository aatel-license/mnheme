// mnheme/cpp/mnheme.hpp
// ======================
// MemoryDB — public API
// IndexEngine — in-RAM indexes

#pragma once
#include "storage.hpp"
#include <chrono>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>
#include <regex>

namespace mnheme {

// ─── IndexEngine ───────────────────────────────────────────────
class IndexEngine {
public:
    IndexEngine() = default;

    void index_record(uint64_t offset, const json& record);
    size_t rebuild(const std::vector<std::pair<uint64_t, json>>& records);

    std::vector<uint64_t> offsets_by_concept(
        const std::string& concept,
        const std::string* feeling   = nullptr,
        bool oldest_first            = false) const;

    std::vector<uint64_t> offsets_by_feeling(
        const std::string& feeling,
        bool oldest_first = false) const;

    std::vector<uint64_t> offsets_by_word(const std::string& word) const;
    std::vector<uint64_t> all_offsets(bool oldest_first = false) const;
    std::vector<uint64_t> timeline_offsets(const std::string& concept) const;

    std::vector<std::string> all_concepts() const;
    size_t count(
        const std::string* concept = nullptr,
        const std::string* feeling = nullptr) const;

    std::map<std::string, size_t> feeling_distribution() const;
    std::map<std::string, std::map<std::string, size_t>> concept_feeling_matrix() const;

private:
    using CFKey = std::pair<std::string, std::string>;

    std::unordered_map<std::string, std::vector<uint64_t>> concept_;
    std::unordered_map<std::string, std::vector<uint64_t>> feeling_;
    std::unordered_map<std::string, std::vector<uint64_t>> tag_;
    std::map<CFKey, std::vector<uint64_t>>                 cf_;
    std::vector<std::pair<std::string, uint64_t>>          timeline_;
    std::vector<uint64_t>                                  all_;
    std::unordered_map<std::string, std::vector<uint64_t>> word_;

    static std::set<std::string> tokenize(const std::string& text);
    static std::string to_lower(std::string s);
};

// ─── Memory struct ─────────────────────────────────────────────
struct Memory {
    std::string              memory_id;
    std::string              concept;
    std::string              feeling;
    std::string              media_type;
    std::string              content;
    std::string              note;
    std::vector<std::string> tags;
    std::string              timestamp;
    std::string              checksum;

    json to_json() const;
    static Memory from_json(const json& j);
};

// ─── MemoryDB ──────────────────────────────────────────────────
class MemoryDB {
public:
    explicit MemoryDB(const std::filesystem::path& path);

    // Write
    Memory remember(
        const std::string&              concept,
        const std::string&              feeling,
        const std::string&              content,
        const std::string&              note       = "",
        const std::vector<std::string>& tags       = {},
        const std::string&              media_type = "text");

    // Read
    std::vector<Memory> recall(
        const std::string&  concept,
        const std::string*  feeling      = nullptr,
        std::optional<size_t> limit      = std::nullopt,
        bool                oldest_first = false) const;

    std::vector<Memory> recall_by_feeling(
        const std::string&    feeling,
        std::optional<size_t> limit      = std::nullopt,
        bool                  oldest_first = false) const;

    std::vector<Memory> recall_all(
        std::optional<size_t> limit      = std::nullopt,
        bool                  oldest_first = false) const;

    std::vector<Memory> search(
        const std::string&    text,
        bool                  in_content = true,
        bool                  in_concept = true,
        bool                  in_note    = true,
        std::optional<size_t> limit      = std::nullopt) const;

    // Stats
    size_t count(
        const std::string* concept = nullptr,
        const std::string* feeling = nullptr) const;

    std::map<std::string, size_t> feeling_distribution() const;
    std::vector<std::string>      list_concepts() const;
    std::vector<json>             concept_timeline(const std::string& concept) const;

    // Export
    std::string export_json() const;

private:
    StorageEngine storage_;
    IndexEngine   index_;
    std::string   path_;

    std::vector<Memory> load_offsets(
        const std::vector<uint64_t>& offsets,
        std::optional<size_t>        limit) const;

    static Memory record_to_memory(const json& r);
    static std::string sha256hex(const std::string& input);
    static std::string iso_timestamp();
    static std::string new_uuid();
};

} // namespace mnheme
