"""
examples.py — Test completo di MNHEME
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from mnheme import MemoryDB, Feeling, MediaType
import json

DB_PATH = "/tmp/test_mnheme.mnheme"

# Pulizia
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

db = MemoryDB(DB_PATH)
sep = "─" * 60

print(sep)
print("  MNHEME — Test Engine Personalizzato")
print(sep)

# ── 1. REMEMBER ─────────────────────────────────
print("\n[1] Registrazione ricordi")

memories = [
    ("Debito",   Feeling.ANSIA,       "Ho firmato il mutuo oggi. 25 anni.",         ["casa","mutuo","2024"]),
    ("Debito",   Feeling.PAURA,       "La banca ha mandato una lettera. Arretrati.",["banca","urgente"]),
    ("Debito",   Feeling.SERENITA,    "Ho pagato l'ultimo rate. Finalmente libero.", ["libertà","traguardo"]),
    ("Famiglia", Feeling.AMORE,       "Il sorriso di mia figlia stamattina.",       ["figlia"]),
    ("Famiglia", Feeling.NOSTALGIA,   "Il profumo della cucina della nonna.",        ["nonna","infanzia"]),
    ("Lavoro",   Feeling.ORGOGLIO,    "Il progetto ha ricevuto gli applausi.",       ["progetto"]),
    ("Lavoro",   Feeling.ANSIA,       "Colloquio domani alle 9. Non dormo.",         ["colloquio"]),
    ("Viaggio",  Feeling.GIOIA,       "Il tramonto a Santorini. Indimenticabile.",  ["grecia","vacanza"]),
    ("Viaggio",  Feeling.NOSTALGIA,   "Quel caffè di Lisbona con la pioggia.",       ["portogallo","pioggia"]),
]

for concept, feeling, content, tags in memories:
    m = db.remember(concept, feeling, content, tags=tags)
    print(f"  ✓  [{m.feeling:12}] {m.concept:10} → {m.content[:45]}")

# ── 2. RECALL per CONCETTO ──────────────────────
print(f"\n[2] recall('Debito')")
for m in db.recall("Debito"):
    print(f"  [{m.feeling}] {m.content}")

print(f"\n[2b] recall('Debito', feeling='ansia')")
for m in db.recall("Debito", feeling=Feeling.ANSIA):
    print(f"  [{m.feeling}] {m.content}")

# ── 3. RECALL per SENTIMENTO ────────────────────
print(f"\n[3] recall_by_feeling('nostalgia')")
for m in db.recall_by_feeling(Feeling.NOSTALGIA):
    print(f"  [{m.concept}] {m.content}")

# ── 4. RECALL ALL ───────────────────────────────
print(f"\n[4] recall_all(limit=3)")
for m in db.recall_all(limit=3):
    print(f"  [{m.concept} / {m.feeling}] {m.content[:40]}")

# ── 5. SEARCH ───────────────────────────────────
print(f"\n[5] search('lisbona')")
for m in db.search("lisbona"):
    print(f"  [{m.concept}] {m.content}")

print(f"\n[5b] search('a'  in_concept=True, in_content=False, in_note=False)")
for m in db.search("viaggio", in_content=False, in_concept=True, in_note=False):
    print(f"  [{m.concept}] {m.content[:45]}")

# ── 6. RECALL BY TAG ────────────────────────────
print(f"\n[6] recall_by_tag('infanzia')")
for m in db.recall_by_tag("infanzia"):
    print(f"  {m.content}")

# ── 7. STATISTICHE ──────────────────────────────
print(f"\n[7] Statistiche")
print(f"  Totale ricordi:       {db.count()}")
print(f"  Solo 'Debito':        {db.count(concept='Debito')}")
print(f"  Solo 'ansia':         {db.count(feeling=Feeling.ANSIA)}")
print(f"  'Lavoro' + 'ansia':   {db.count(concept='Lavoro', feeling='ansia')}")

print(f"\n  Concetti:")
for c in db.list_concepts():
    feelings_str = "  ".join(f"{f}×{n}" for f, n in c["feelings"].items())
    print(f"    {c['concept']:12} → {c['total']} ricordi   {feelings_str}")

print(f"\n  Distribuzione sentimenti:")
for feeling, count in db.feeling_distribution().items():
    bar = "█" * count
    print(f"    {feeling:14} {bar} ({count})")

# ── 8. TIMELINE ─────────────────────────────────
print(f"\n[8] concept_timeline('Debito')")
for entry in db.concept_timeline("Debito"):
    print(f"  {entry['timestamp'][:19]}  [{entry['feeling']:10}]  {entry['note'] or entry['tags']}")

# ── 9. STORAGE INFO ─────────────────────────────
print(f"\n[9] storage_info()")
info = db.storage_info()
for k, v in info.items():
    print(f"  {k:20} {v}")

# ── 10. EXPORT / IMPORT ─────────────────────────
print(f"\n[10] Export JSON e re-import")
export_path = "/tmp/backup_debito.json"
db.export_json(export_path, concept="Debito")
with open(export_path) as f:
    exported = json.load(f)
print(f"  Esportati {len(exported['memories'])} ricordi di 'Debito'")

# Creo un nuovo db e reimporto
db2 = MemoryDB("/tmp/test_mnheme2.mnheme")
n = db2.import_json(export_path)
print(f"  Importati {n} ricordi nel nuovo db → totale: {db2.count()}")

# Import duplicato: non deve aggiungere nulla
n2 = db2.import_json(export_path)
print(f"  Re-import duplicati aggiunti: {n2}  (atteso: 0)")

# ── 11. PERSISTENZA ─────────────────────────────
print(f"\n[11] Persistenza: riapro il db da file")
db3 = MemoryDB(DB_PATH)
print(f"  Ricordi ricaricati: {db3.count()}  (atteso: {len(memories)})")
print(f"  Concetti in indice: {db3._index.all_concepts()}")

# ── 12. IMMUTABILITÀ ────────────────────────────
print(f"\n[12] Immutabilità dei Memory")
m0 = db.recall("Debito")[0]
try:
    m0.concept = "Modifica"  # type: ignore
    print("  ✗ Modifica riuscita — ERRORE!")
except Exception as e:
    print(f"  ✓ Modifica bloccata: {type(e).__name__}")

# ── 13. VERIFICA FISICA DEL FILE ────────────────
print(f"\n[13] Verifica formato binario del file")
with open(DB_PATH, "rb") as f:
    raw = f.read(8)
magic = raw[:4]
print(f"  Magic bytes: {magic.hex().upper()}  = {list(magic)}")
print(f"  Dimensione file: {os.path.getsize(DB_PATH)} byte")

print(f"\n{sep}")
print(f"  {db}")
print(f"{sep}")

# Pulizia
os.remove(DB_PATH)
os.remove("/tmp/test_mnheme2.mnheme")
os.remove(export_path)
