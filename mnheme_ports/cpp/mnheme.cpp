// mnheme/cpp/mnheme.cpp
#include "mnheme.hpp"
#include <algorithm>
#include <cassert>
#include <iomanip>
#include <random>
#include <set>
#include <sstream>

// ── Tiny SHA-256 via OpenSSL or manual ──────────────────────────
// For production use: link with -lcrypto (OpenSSL)
#ifdef _WIN32
  #include <wincrypt.h>
#else
  #include <openssl/sha.h>
#endif

namespace mnheme {

// ─── IndexEngine ────────────────────────────────────────────────

std::string IndexEngine::to_lower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

std::set<std::string> IndexEngine::tokenize(const std::string& text) {
    std::set<std::string> tokens;
    std::string lower = to_lower(text);
    std::string token;
    for (char c : lower) {
        if (std::isalpha(static_cast<unsigned char>(c))) {
            token += c;
        } else {
            if (token.size() >= 3) tokens.insert(token);
            token.clear();
        }
    }
    if (token.size() >= 3) tokens.insert(token);
    return tokens;
}

void IndexEngine::index_record(uint64_t offset, const json& r) {
    std::string concept   = r.value("concept", "");
    std::string feeling   = r.value("feeling", "");
    std::string timestamp = r.value("timestamp", "");

    concept_[concept].push_back(offset);
    feeling_[feeling].push_back(offset);
    cf_[{concept, feeling}].push_back(offset);
    timeline_.push_back({timestamp, offset});
    all_.push_back(offset);

    if (r.contains("tags") && r["tags"].is_array()) {
        for (const auto& tag : r["tags"]) {
            std::string t = tag.get<std::string>();
            if (!t.empty()) tag_[t].push_back(offset);
        }
    }

    // Inverted full-text index
    std::string combined =
        r.value("content", "") + " " +
        r.value("concept", "") + " " +
        r.value("note",    "");
    for (const auto& tok : tokenize(combined)) {
        word_[tok].push_back(offset);
    }
}

size_t IndexEngine::rebuild(const std::vector<std::pair<uint64_t, json>>& records) {
    concept_.clear(); feeling_.clear(); tag_.clear();
    cf_.clear(); timeline_.clear(); all_.clear(); word_.clear();

    for (const auto& [offset, record] : records) {
        index_record(offset, record);
    }
    std::sort(timeline_.begin(), timeline_.end(),
              [](const auto& a, const auto& b){ return a.first < b.first; });
    return records.size();
}

std::vector<uint64_t> IndexEngine::offsets_by_concept(
    const std::string& concept,
    const std::string* feeling,
    bool oldest_first) const
{
    std::vector<uint64_t> offs;
    if (feeling) {
        auto it = cf_.find({concept, *feeling});
        if (it != cf_.end()) offs = it->second;
    } else {
        auto it = concept_.find(concept);
        if (it != concept_.end()) offs = it->second;
    }
    if (!oldest_first) std::reverse(offs.begin(), offs.end());
    return offs;
}

std::vector<uint64_t> IndexEngine::offsets_by_feeling(
    const std::string& feeling, bool oldest_first) const
{
    std::vector<uint64_t> offs;
    auto it = feeling_.find(feeling);
    if (it != feeling_.end()) offs = it->second;
    if (!oldest_first) std::reverse(offs.begin(), offs.end());
    return offs;
}

std::vector<uint64_t> IndexEngine::offsets_by_word(const std::string& word) const {
    std::string w = to_lower(word);
    auto it = word_.find(w);
    if (it == word_.end()) return {};
    auto offs = it->second;
    std::reverse(offs.begin(), offs.end());
    return offs;
}

std::vector<uint64_t> IndexEngine::all_offsets(bool oldest_first) const {
    auto offs = all_;
    if (!oldest_first) std::reverse(offs.begin(), offs.end());
    return offs;
}

std::vector<uint64_t> IndexEngine::timeline_offsets(const std::string& concept) const {
    std::set<uint64_t> cset;
    auto it = concept_.find(concept);
    if (it != concept_.end())
        cset.insert(it->second.begin(), it->second.end());
    std::vector<uint64_t> result;
    for (const auto& [ts, off] : timeline_)
        if (cset.count(off)) result.push_back(off);
    return result;
}

std::vector<std::string> IndexEngine::all_concepts() const {
    std::vector<std::string> v;
    for (const auto& [k, _] : concept_) v.push_back(k);
    std::sort(v.begin(), v.end());
    return v;
}

size_t IndexEngine::count(const std::string* concept, const std::string* feeling) const {
    if (concept && feeling) {
        auto it = cf_.find({*concept, *feeling});
        return it == cf_.end() ? 0 : it->second.size();
    }
    if (concept) {
        auto it = concept_.find(*concept);
        return it == concept_.end() ? 0 : it->second.size();
    }
    if (feeling) {
        auto it = feeling_.find(*feeling);
        return it == feeling_.end() ? 0 : it->second.size();
    }
    return all_.size();
}

std::map<std::string, size_t> IndexEngine::feeling_distribution() const {
    std::map<std::string, size_t> result;
    for (const auto& [k, v] : feeling_) result[k] = v.size();
    return result;
}

std::map<std::string, std::map<std::string, size_t>>
IndexEngine::concept_feeling_matrix() const {
    std::map<std::string, std::map<std::string, size_t>> matrix;
    for (const auto& [key, v] : cf_)
        matrix[key.first][key.second] = v.size();
    return matrix;
}

// ─── Memory ──────────────────────────────────────────────────────

json Memory::to_json() const {
    return {
        {"memory_id",  memory_id},
        {"concept",    concept},
        {"feeling",    feeling},
        {"media_type", media_type},
        {"content",    content},
        {"note",       note},
        {"tags",       tags},
        {"timestamp",  timestamp},
        {"checksum",   checksum},
    };
}

Memory Memory::from_json(const json& j) {
    Memory m;
    m.memory_id  = j.value("memory_id",  "");
    m.concept    = j.value("concept",    "");
    m.feeling    = j.value("feeling",    "");
    m.media_type = j.value("media_type", "text");
    m.content    = j.value("content",    "");
    m.note       = j.value("note",       "");
    m.timestamp  = j.value("timestamp",  "");
    m.checksum   = j.value("checksum",   "");
    if (j.contains("tags") && j["tags"].is_array())
        m.tags = j["tags"].get<std::vector<std::string>>();
    return m;
}

// ─── MemoryDB ────────────────────────────────────────────────────

MemoryDB::MemoryDB(const std::filesystem::path& path)
    : storage_(path), path_(path.string())
{
    auto records = storage_.scan();
    index_.rebuild(records);
}

std::string MemoryDB::iso_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto t   = std::chrono::system_clock::to_time_t(now);
    std::ostringstream oss;
    oss << std::put_time(std::gmtime(&t), "%FT%TZ");
    return oss.str();
}

std::string MemoryDB::new_uuid() {
    static std::random_device rd;
    static std::mt19937_64 gen(rd());
    std::uniform_int_distribution<uint64_t> dist;
    uint64_t a = dist(gen), b = dist(gen);
    // UUID v4
    a = (a & 0xFFFFFFFFFFFF0FFFULL) | 0x0000000000004000ULL;
    b = (b & 0x3FFFFFFFFFFFFFFFULL) | 0x8000000000000000ULL;
    std::ostringstream oss;
    oss << std::hex << std::setfill('0')
        << std::setw(8) << (a >> 32)        << '-'
        << std::setw(4) << ((a >> 16)&0xFFFF) << '-'
        << std::setw(4) << (a & 0xFFFF)     << '-'
        << std::setw(4) << (b >> 48)        << '-'
        << std::setw(12)<< (b & 0xFFFFFFFFFFFFULL);
    return oss.str();
}

std::string MemoryDB::sha256hex(const std::string& input) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(input.c_str()),
           input.size(), hash);
    std::ostringstream oss;
    for (auto byte : hash)
        oss << std::hex << std::setw(2) << std::setfill('0') << (int)byte;
    return oss.str();
}

Memory MemoryDB::remember(
    const std::string& concept,
    const std::string& feeling,
    const std::string& content,
    const std::string& note,
    const std::vector<std::string>& tags,
    const std::string& media_type)
{
    if (concept.empty()) throw std::invalid_argument("Concept cannot be empty");
    if (content.empty()) throw std::invalid_argument("Content cannot be empty");

    Memory m;
    m.memory_id  = new_uuid();
    m.concept    = concept;
    m.feeling    = feeling;
    m.media_type = media_type;
    m.content    = content;
    m.note       = note;
    m.tags       = tags;
    m.timestamp  = iso_timestamp();
    m.checksum   = sha256hex(content);

    json record = m.to_json();
    uint64_t offset = storage_.append(record);
    index_.index_record(offset, record);
    return m;
}

std::vector<Memory> MemoryDB::recall(
    const std::string& concept,
    const std::string* feeling,
    std::optional<size_t> limit,
    bool oldest_first) const
{
    auto offsets = index_.offsets_by_concept(concept, feeling, oldest_first);
    return load_offsets(offsets, limit);
}

std::vector<Memory> MemoryDB::recall_by_feeling(
    const std::string& feeling,
    std::optional<size_t> limit,
    bool oldest_first) const
{
    auto offsets = index_.offsets_by_feeling(feeling, oldest_first);
    return load_offsets(offsets, limit);
}

std::vector<Memory> MemoryDB::recall_all(
    std::optional<size_t> limit, bool oldest_first) const
{
    auto offsets = index_.all_offsets(oldest_first);
    return load_offsets(offsets, limit);
}

std::vector<Memory> MemoryDB::search(
    const std::string& text,
    bool in_content, bool in_concept, bool in_note,
    std::optional<size_t> limit) const
{
    std::string needle = IndexEngine::to_lower(const_cast<std::string&>(text));
    auto records = storage_.scan();
    std::vector<Memory> results;

    for (auto it = records.rbegin(); it != records.rend(); ++it) {
        const auto& r = it->second;
        bool matched = false;
        auto contains = [&](const std::string& field) {
            std::string val = r.value(field, "");
            std::transform(val.begin(), val.end(), val.begin(), ::tolower);
            return val.find(needle) != std::string::npos;
        };
        if (in_content && contains("content")) matched = true;
        if (in_concept && contains("concept")) matched = true;
        if (in_note    && contains("note"))    matched = true;
        if (matched) {
            results.push_back(record_to_memory(r));
            if (limit && results.size() >= *limit) break;
        }
    }
    return results;
}

size_t MemoryDB::count(const std::string* concept, const std::string* feeling) const {
    return index_.count(concept, feeling);
}

std::map<std::string, size_t> MemoryDB::feeling_distribution() const {
    return index_.feeling_distribution();
}

std::vector<std::string> MemoryDB::list_concepts() const {
    return index_.all_concepts();
}

std::vector<json> MemoryDB::concept_timeline(const std::string& concept) const {
    auto offsets = index_.timeline_offsets(concept);
    std::vector<json> result;
    for (auto offset : offsets) {
        auto r = storage_.read_at(offset);
        if (r) result.push_back({
            {"timestamp", r->value("timestamp", "")},
            {"feeling",   r->value("feeling",   "")},
            {"note",      r->value("note",       "")},
            {"tags",      r->value("tags",       json::array())},
        });
    }
    return result;
}

std::string MemoryDB::export_json() const {
    auto memories = recall_all();
    json arr = json::array();
    for (const auto& m : memories) arr.push_back(m.to_json());
    json out = {{"exported_at", iso_timestamp()}, {"memories", arr}};
    return out.dump(2);
}

std::vector<Memory> MemoryDB::load_offsets(
    const std::vector<uint64_t>& offsets,
    std::optional<size_t> limit) const
{
    std::vector<Memory> result;
    size_t n = limit ? std::min(*limit, offsets.size()) : offsets.size();
    result.reserve(n);
    for (size_t i = 0; i < n; ++i) {
        auto r = storage_.read_at(offsets[i]);
        if (r) result.push_back(record_to_memory(*r));
    }
    return result;
}

Memory MemoryDB::record_to_memory(const json& r) {
    return Memory::from_json(r);
}

} // namespace mnheme

// ─── CMakeLists.txt (minimal) ────────────────────────────────────
// cmake_minimum_required(VERSION 3.20)
// project(mnheme CXX)
// set(CMAKE_CXX_STANDARD 20)
// find_package(OpenSSL REQUIRED)
// find_package(nlohmann_json REQUIRED)
// add_executable(mnheme main.cpp storage.cpp mnheme.cpp)
// target_link_libraries(mnheme PRIVATE OpenSSL::SSL nlohmann_json::nlohmann_json)
