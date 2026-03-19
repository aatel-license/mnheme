"""
test_fsprobe.py — Test FsProbe + FileStore
"""
import sys, os, shutil, tempfile
sys.path.insert(0, os.path.dirname(__file__))

from fsprobe import FsProbe, FsType, LinkStrategy
from filestore import FileStore, UnsupportedMediaError
from mnheme import MemoryDB, Feeling

sep = "─" * 65

print(sep)
print("  FsProbe — rilevamento filesystem")
print(sep)

# ── 1. Probe sul filesystem corrente ────────────
print("\n[1] Probe directory /tmp")
probe = FsProbe("/tmp")
caps  = probe.detect()
print(f"\n  {caps}")
print()
for k, v in caps.to_dict().items():
    print(f"  {k:<22} {v}")

# ── 2. Probe idempotente (cache) ─────────────────
print(f"\n[2] Probe cache (deve essere istantaneo)")
import time
t0 = time.perf_counter()
caps2 = probe.detect()
ms = (time.perf_counter() - t0) * 1000
print(f"  Seconda chiamata: {ms:.3f}ms  (cache: {caps2 is caps})")

# ── 3. Capabilities live ─────────────────────────
print(f"\n[3] Capabilities rilevate live")
print(f"  can_hardlink:      {caps.can_hardlink}")
print(f"  can_reflink:       {caps.can_reflink}")
print(f"  can_symlink:       {caps.can_symlink}")
print(f"  is_remote:         {caps.is_remote}")
print(f"  is_readonly:       {caps.is_readonly}")
print(f"  is_case_sensitive: {caps.is_case_sensitive}")
print(f"  inode_bits:        {caps.inode_bits}")
print(f"  strategy:          {caps.strategy.value}")
print(f"  strategy_note:     {caps.strategy_note}")

# ── 4. FileStore con FS detection ────────────────
print(f"\n{sep}")
print("  FileStore — storage adattivo")
print(sep)

BASE = "/tmp/_test_fstore"
if os.path.exists(BASE): shutil.rmtree(BASE)

fs = FileStore(BASE)
print(f"\n[4] FileStore creato")
print(f"  {fs}")
print(f"  Filesystem: {fs.caps.fs_type.value}")
print(f"  Strategia:  {fs.caps.strategy.value}  ({fs.caps.strategy_note})")

# ── 5. Salvataggio file ──────────────────────────
print(f"\n[5] Salvataggio file")

# Crea file di test
tmp_files = {}
for name, data in [
    ("foto_natale.jpg",      b"\xFF\xD8\xFF" + b"IMG" * 500),
    ("video_vacanza.mp4",    b"\x00\x00\x00\x18ftyp" + b"VID" * 300),
    ("nota_vocale.mp3",      b"ID3" + b"AUD" * 200),
    ("documento.pdf",        b"%PDF-1.4" + b"DOC" * 100),
    ("foto_natale_copia.jpg", b"\xFF\xD8\xFF" + b"IMG" * 500),  # DUPLICATO!
]:
    fd, path = tempfile.mkstemp(suffix=os.path.splitext(name)[1])
    os.write(fd, data); os.close(fd)
    tmp_files[name] = path

mem_ids = ["mem-001", "mem-002", "mem-003", "mem-004", "mem-005"]

entries = []
for mem_id, (name, tmp_path) in zip(mem_ids, tmp_files.items()):
    entry = fs.store(mem_id, tmp_path)
    entries.append(entry)
    print(f"  [{mem_id}] {name}")
    print(f"     pool:     {entry.pool_path}")
    print(f"     link:     {entry.link_path}")
    print(f"     inode:    {entry.inode}")
    print(f"     strategy: {entry.strategy_used}")

# Pulizia tmp
for p in tmp_files.values():
    if os.path.exists(p): os.unlink(p)

# ── 6. Verifica inode (dedup) ────────────────────
print(f"\n[6] Verifica inode — deduplicazione")
e1 = entries[0]   # foto_natale.jpg
e5 = entries[4]   # foto_natale_copia.jpg (stesso contenuto)

pool1 = BASE + "/" + e1.pool_path
pool5 = BASE + "/" + e5.pool_path
link1 = BASE + "/" + e1.link_path
link5 = BASE + "/" + e5.link_path

print(f"  foto_natale.jpg      checksum: {e1.checksum[:16]}...")
print(f"  foto_natale_copia    checksum: {e5.checksum[:16]}...")
print(f"  Stesso checksum:     {e1.checksum == e5.checksum}")
print(f"  Stesso pool_path:    {e1.pool_path == e5.pool_path}")

if os.path.exists(pool1) and os.path.exists(pool5):
    ino1 = os.stat(pool1).st_ino
    ino5 = os.stat(pool5).st_ino
    print(f"  inode pool1: {ino1}")
    print(f"  inode pool5: {ino5}")
    print(f"  Pool stesso file fisico: {ino1 == ino5}")

if caps.can_hardlink:
    inoL1 = os.stat(link1).st_ino
    inoL5 = os.stat(link5).st_ino
    inoP1 = os.stat(pool1).st_ino
    print(f"\n  nlink conteggio inode pool1: {os.stat(pool1).st_nlink}")
    print(f"  link1 inode: {inoL1}  ==  pool inode: {inoP1}  -> {inoL1 == inoP1}")

elif caps.can_symlink:
    print(f"\n  link1 è symlink: {os.path.islink(link1)}")
    print(f"  link1 -> {os.readlink(link1)}")

# ── 7. Lettura ───────────────────────────────────
print(f"\n[7] Lettura file")
path  = fs.get_path("mem-001")
data  = fs.get_bytes("mem-001")
print(f"  Path: {path}")
print(f"  Esiste: {path.exists()}")
print(f"  Bytes: {len(data)}")

# ── 8. List by type ──────────────────────────────
print(f"\n[8] Lista per tipo")
for t in ("images", "videos", "audio", "docs"):
    items = fs.list_by_type(t)
    print(f"  {t:8}: {len(items)} file")

# ── 9. Info e tree ───────────────────────────────
print(f"\n[9] Info FileStore")
info = fs.info()
for k, v in info.items():
    print(f"  {k:<24} {v}")

print(f"\n[10] Tree")
print(fs.tree())

# ── 11. Struttura fisica su disco ───────────────
print(f"\n[11] Struttura fisica")
for root, dirs, files in os.walk(BASE):
    level  = root.replace(BASE, "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    for f in files:
        fpath = os.path.join(root, f)
        ino   = os.stat(fpath).st_ino
        nlink = os.stat(fpath).st_nlink
        size  = os.path.getsize(fpath)
        link_marker = " -> " + os.readlink(fpath) if os.path.islink(fpath) else ""
        print(f"{indent}  {f}  ({size}B  ino={ino}  nlink={nlink}){link_marker}")

# ── 12. Integrazione MemoryDB ────────────────────
print(f"\n{sep}")
print("  Integrazione MemoryDB + FileStore")
print(sep)

DB_PATH   = "/tmp/_test_mnheme_fs.mnheme"
FILES_DIR = "/tmp/_test_mnheme_fs_files"
for p in [DB_PATH, FILES_DIR]:
    if os.path.exists(p): shutil.rmtree(p, ignore_errors=True)
    try: os.remove(p)
    except: pass

db = MemoryDB(DB_PATH, files_dir=FILES_DIR)
print(f"\n  Filesystem rilevato: {db.files.caps.fs_type.value}")
print(f"  Strategia usata:     {db.files.caps.strategy.value}")

fd, tmp_img = tempfile.mkstemp(suffix=".jpg")
os.write(fd, b"\xFF\xD8\xFF" + b"X" * 800); os.close(fd)

mem, fe = db.remember_file("Famiglia", Feeling.AMORE, tmp_img,
                            note="Test integrazione", tags=["test"])
print(f"\n  Memory: {mem}")
print(f"  FileEntry: {fe}")
print(f"  Path: {db.files.get_path(mem.memory_id)}")
os.unlink(tmp_img)

print(f"\n{sep}")
print(f"  Probe summary: {caps}")
print(sep)

# Cleanup
shutil.rmtree(BASE, ignore_errors=True)
shutil.rmtree(FILES_DIR, ignore_errors=True)
if os.path.exists(DB_PATH): os.remove(DB_PATH)
