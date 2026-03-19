"""
mnheme_benchmark.py
==================
Suite di benchmark completa per MNHEME.

Esegui con:
    python mnheme_benchmark.py
    python mnheme_benchmark.py --records 2000
    python mnheme_benchmark.py --records 5000 --output report.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from mnheme import MemoryDB, Feeling, MediaType

CONCEPTS = [
    "Debito", "Famiglia", "Lavoro", "Amore", "Salute",
    "Amicizia", "Viaggio", "Casa", "Denaro", "Paura",
    "Successo", "Fallimento", "Infanzia", "Futuro", "Perdita",
]
FEELINGS = list(Feeling)
CONTENTS = [
    "Ho firmato il contratto. Non so se e stata la scelta giusta.",
    "Il sorriso di mia figlia stamattina mi ha fermato il respiro.",
    "Una lettera dalla banca. Il solito pensiero fisso.",
    "Quel profumo di pane domenicale dalla cucina della nonna.",
    "Non riuscivo a smettere di pensarci durante la riunione.",
    "Per un momento ho dimenticato tutto. Solo il vento e il mare.",
    "Mi ha chiamato e non sapevo cosa dire. Ho riattaccato.",
    "Il treno era vuoto alle sei di mattina. Ho pianto senza motivo.",
    "Hanno detto di si. Ancora non ci credo.",
    "Tre anni fa avrei fatto diversamente. Forse.",
    "Il dottore ha parlato a lungo. Non ricordo quasi nulla.",
    "Era la prima volta che tornavo in quella strada.",
    "Abbiamo riso cosi tanto che faceva male.",
    "Ho trovato una vecchia foto. Non ricordavo di averla.",
    "Stamattina ho deciso. Non so ancora come farlo.",
]
ALL_TAGS = [["importante"],["casa","2024"],["urgente"],["infanzia"],
            ["lavoro","stress"],["famiglia"],["viaggio","estate"],
            ["soldi"],["salute"],[],["amici","risate"],["passato"]]
NOTES = ["Era un martedi piovoso.","Ricordo l'odore nell'aria.","",
         "Non dimentichero mai.","Stavo ascoltando musica.","",
         "Avevo appena mangiato.","Era buio fuori.","",
         "Mi sentivo stranamente calmo."]


def rand_record() -> dict:
    return {
        "concept": random.choice(CONCEPTS),
        "feeling": random.choice(FEELINGS),
        "content": random.choice(CONTENTS),
        "tags":    random.choice(ALL_TAGS),
        "note":    random.choice(NOTES),
    }


@dataclass
class BenchResult:
    name       : str
    n          : int
    total_sec  : float
    min_ms     : float
    max_ms     : float
    mean_ms    : float
    median_ms  : float
    p95_ms     : float
    p99_ms     : float
    throughput : float

    def row(self) -> str:
        return (
            f"  {self.name:<46}"
            f"  n={self.n:<5}"
            f"  mean={self.mean_ms:>8.3f}ms"
            f"  p95={self.p95_ms:>8.3f}ms"
            f"  p99={self.p99_ms:>8.3f}ms"
            f"  {self.throughput:>10,.0f} ops/s"
        )


def measure(name: str, fn, n: int, warmup: int = 0) -> BenchResult:
    for _ in range(warmup):
        fn()
    samples = []
    t_start = time.perf_counter()
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000)
    total = time.perf_counter() - t_start
    samples.sort()
    return BenchResult(
        name       = name,
        n          = n,
        total_sec  = total,
        min_ms     = samples[0],
        max_ms     = samples[-1],
        mean_ms    = statistics.mean(samples),
        median_ms  = statistics.median(samples),
        p95_ms     = samples[int(len(samples) * 0.95)],
        p99_ms     = samples[int(len(samples) * 0.99)],
        throughput = n / total,
    )


def timeit_avg(fn, n: int) -> float:
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - t0) / n * 1000


def header(title: str) -> None:
    print(f"\n{'─'*95}")
    print(f"  {title}")
    print(f"{'─'*95}")


class MnhemeBenchmark:

    def __init__(self, db_path: str, n_records: int) -> None:
        self.db_path   = db_path
        self.n_records = n_records
        self.results   : list[BenchResult] = []
        self.meta      : dict = {}

    def run(self) -> dict:
        W = 95
        print(f"\n{'='*W}")
        print(f"  MNHEME  --  BENCHMARK SUITE")
        print(f"  dataset={self.n_records:,} record   file={self.db_path}")
        print(f"{'='*W}")

        self._write()
        self._write_no_fsync()
        self._read()
        self._search()
        self._cold_start()
        self._scalability()
        self._file_info()
        self._summary()

        return {"config": {"n_records": self.n_records, "db_path": self.db_path},
                "meta": self.meta,
                "results": [asdict(r) for r in self.results]}

    # ── 1. SCRITTURA con fsync ───────────────

    def _write(self) -> None:
        header("1. SCRITTURA  --  append + fsync (durabilita garantita)")
        db = MemoryDB(self.db_path)

        r = measure(
            "remember() singolo (con fsync)",
            lambda: db.remember(**rand_record()),
            n=300,
        )
        self.results.append(r)
        print(r.row())

        remaining = max(0, self.n_records - 300)
        if remaining:
            t0 = time.perf_counter()
            for _ in range(remaining):
                db.remember(**rand_record())
            e = time.perf_counter() - t0
            print(f"\n  bulk fill {remaining:,} record aggiuntivi"
                  f"  -->  {remaining/e:,.0f} ops/s  ({e:.1f}s totali)")

        self.meta["total_records"] = db.count()
        print(f"\n  Dataset pronto: {db.count():,} record")

    # ── 2. SCRITTURA senza fsync ─────────────

    def _write_no_fsync(self) -> None:
        header("2. SCRITTURA  --  append senza fsync (velocita pura I/O)")
        tmp = self.db_path + ".nofsync"
        if os.path.exists(tmp):
            os.remove(tmp)

        import storage as _sm
        import struct as _st

        class FastStorage(_sm.StorageEngine):
            def append(self, record):
                payload = json.dumps(record, ensure_ascii=False).encode("utf-8")
                header_bytes = _sm.MAGIC + _st.pack(">I", len(payload))
                with self._lock:
                    with open(self._path, "ab") as f:
                        offset = f.tell()
                        f.write(header_bytes + payload)
                    return offset

        class FastDB(MemoryDB):
            def __init__(self, path):
                from index import IndexEngine
                self._storage = FastStorage(path)
                self._index   = IndexEngine()
                self._index.rebuild(self._storage.scan())
                self._path    = str(path)

        db_fast = FastDB(tmp)
        r = measure(
            "remember() singolo (senza fsync)",
            lambda: db_fast.remember(**rand_record()),
            n=1000,
        )
        self.results.append(r)
        print(r.row())

        ratio = self.results[0].mean_ms / r.mean_ms
        print(f"\n  fsync aggiunge ~{ratio:.1f}x latenza in piu"
              f"  (sicurezza: ogni write e durabile su crash)")
        os.remove(tmp)

    # ── 3. LETTURA ────────────────────────────

    def _read(self) -> None:
        header("3. LETTURA  --  indici RAM + read_at() selettivo")

        db       = MemoryDB(self.db_path)
        concepts = [c["concept"] for c in db.list_concepts()]
        feelings = list(db.feeling_distribution().keys())
        concept  = random.choice(concepts)
        feeling  = random.choice(feelings)
        n_total  = db.count()
        avg_per  = n_total // max(len(concepts), 1)

        cases = [
            ("recall(concept, limit=10)",            lambda: db.recall(concept, limit=10),           500, 10),
            ("recall(concept, limit=50)",             lambda: db.recall(concept, limit=50),           300, 5),
            (f"recall(concept) -- tutti (~{avg_per})", lambda: db.recall(concept),                    50,  2),
            ("recall(concept, feeling=feeling)",      lambda: db.recall(concept, feeling=feeling),    500, 10),
            (f"recall_by_feeling (limit=20)",         lambda: db.recall_by_feeling(feeling,limit=20), 500, 10),
            (f"recall_all() -- tutti ({n_total:,})",  lambda: db.recall_all(),                        20,  1),
            ("recall_all(limit=10)",                  lambda: db.recall_all(limit=10),                500, 10),
            ("recall_by_tag('importante')",           lambda: db.recall_by_tag("importante"),         500, 10),
            ("count()  --  pura RAM O(1)",            lambda: db.count(),                            5000, 50),
            ("count(concept=X)  --  pura RAM O(1)",   lambda: db.count(concept=concept),             5000, 50),
            ("list_concepts()",                       lambda: db.list_concepts(),                    1000, 20),
            ("list_feelings()",                       lambda: db.list_feelings(),                    1000, 20),
            ("feeling_distribution()",               lambda: db.feeling_distribution(),              2000, 30),
            ("concept_timeline(concept)",             lambda: db.concept_timeline(concept),           200,  5),
        ]

        for name, fn, n, wu in cases:
            r = measure(name, fn, n=n, warmup=wu)
            self.results.append(r)
            print(r.row())

    # ── 4. RICERCA FULL-TEXT ─────────────────

    def _search(self) -> None:
        header("4. RICERCA FULL-TEXT  --  scansione lineare O(n)")

        db = MemoryDB(self.db_path)
        n  = db.count()
        print(f"  (ogni chiamata scansiona tutti i {n:,} record del file)\n")

        cases = [
            ("search('sorriso')  -- match raro",    lambda: db.search("sorriso"),     15),
            ("search('a')        -- match comune",  lambda: db.search("a"),            8),
            ("search('zzz_miss') -- nessun match",  lambda: db.search("zzz_miss"),    15),
            ("search('a', limit=5)",                lambda: db.search("a", limit=5),  50),
        ]
        for name, fn, iters in cases:
            r = measure(name, fn, n=iters, warmup=1)
            self.results.append(r)
            rps = n / (r.mean_ms / 1000)
            print(r.row())
            print(f"  {'':48}  --> scansione: {rps:,.0f} record/s")

    # ── 5. COLD START ─────────────────────────

    def _cold_start(self) -> None:
        header("5. COLD START  --  ricostruzione indici al boot")

        n = MemoryDB(self.db_path).count()
        r = measure(
            f"MemoryDB(path)  --  indicizza {n:,} record",
            lambda: MemoryDB(self.db_path),
            n=8, warmup=1,
        )
        self.results.append(r)
        print(r.row())

        rps = n / (r.mean_ms / 1000)
        print(f"\n  Rebuild rate:              {rps:,.0f} record indicizzati/sec")
        print(f"  Stima cold start a  10k:   ~{10_000/rps*1000:.0f} ms")
        print(f"  Stima cold start a 100k:   ~{100_000/rps*1000:.0f} ms")
        print(f"  Stima cold start a   1M:   ~{1_000_000/rps:.1f} s")
        self.meta["rebuild_rps"] = round(rps)

    # ── 6. SCALABILITA ────────────────────────

    def _scalability(self) -> None:
        header("6. SCALABILITA  --  latenza al variare del dataset")

        points = sorted(set([100, 500, 1_000, 2_000] +
                             [p for p in [5_000, 10_000] if p <= self.n_records] +
                             [self.n_records]))

        print(f"  {'Records':>8}  {'cold_ms':>10}  {'recall_lim10':>13}  "
              f"{'recall_all_ms':>14}  {'search_ms':>10}  {'file_KB':>8}")
        print(f"  {'─'*8}  {'─'*10}  {'─'*13}  {'─'*14}  {'─'*10}  {'─'*8}")

        rows = []
        for n in points:
            tmp = f"/tmp/_mnheme_scale_{n}.mnheme"
            if os.path.exists(tmp): os.remove(tmp)

            db = MemoryDB(tmp)
            for _ in range(n):
                db.remember(**rand_record())

            t0 = time.perf_counter()
            db2 = MemoryDB(tmp)
            cold_ms = (time.perf_counter() - t0) * 1000

            concepts = [c["concept"] for c in db2.list_concepts()]
            concept  = random.choice(concepts)

            rl10  = timeit_avg(lambda: db2.recall(concept, limit=10), 100)
            ra    = timeit_avg(lambda: db2.recall_all(), max(3, min(20, 500//n*10+5)))
            iters = max(3, min(15, 1500 // max(n, 1)))
            sr    = timeit_avg(lambda: db2.search("sorriso"), iters)
            fkb   = os.path.getsize(tmp) / 1024

            print(f"  {n:>8,}  {cold_ms:>10.1f}  {rl10:>13.3f}  {ra:>14.2f}  {sr:>10.2f}  {fkb:>8.1f}")
            rows.append({"n": n, "cold_ms": round(cold_ms, 2),
                         "recall_limit10_ms": round(rl10, 3),
                         "recall_all_ms": round(ra, 2),
                         "search_ms": round(sr, 2), "file_kb": round(fkb, 1)})
            os.remove(tmp)

        self.meta["scale"] = rows

    # ── 7. FILE INFO ──────────────────────────

    def _file_info(self) -> None:
        header("7. FILE FISICO  --  dimensioni e proiezioni")

        db    = MemoryDB(self.db_path)
        info  = db.storage_info()
        n     = info["total_records"]
        sb    = info["size_bytes"]
        avg_b = sb / n if n else 0

        rows = [
            ("Percorso file",                 info["path"]),
            ("Record totali",                 f"{n:,}"),
            ("Dimensione totale",             f"{sb:,} B  ({sb/1024:.2f} KB  /  {sb/1024/1024:.3f} MB)"),
            ("Byte medi per record",          f"{avg_b:.1f} B"),
            ("Overhead frame (magic+size)",   "8 B per record"),
            ("Stima a    10k record",         f"~{avg_b*10_000/1024:.0f} KB"),
            ("Stima a   100k record",         f"~{avg_b*100_000/1024/1024:.1f} MB"),
            ("Stima a     1M record",         f"~{avg_b*1_000_000/1024/1024:.0f} MB"),
            ("Stima a    10M record",         f"~{avg_b*10_000_000/1024/1024/1024:.2f} GB"),
        ]
        for k, v in rows:
            print(f"  {k:<35}  {v}")

        self.meta["file"] = {
            "size_bytes": sb,
            "avg_bytes_per_record": round(avg_b, 1),
            "est_10k_kb":  round(avg_b*10_000/1024, 0),
            "est_100k_mb": round(avg_b*100_000/1024/1024, 1),
            "est_1M_mb":   round(avg_b*1_000_000/1024/1024, 0),
            "est_10M_gb":  round(avg_b*10_000_000/1024/1024/1024, 2),
        }

    # ── SUMMARY ──────────────────────────────

    def _summary(self) -> None:
        W = 95
        print(f"\n{'='*W}")
        print("  RIEPILOGO  --  throughput per categoria")
        print(f"{'='*W}")

        cats = {
            "SCRITTURA":   lambda r: "remember" in r.name,
            "LETTURA":     lambda r: any(x in r.name for x in
                                         ["recall","count","list","distribution","timeline"]),
            "RICERCA":     lambda r: "search" in r.name.lower(),
            "COLD START":  lambda r: "MemoryDB" in r.name,
        }

        for cat, pred in cats.items():
            group = [r for r in self.results if pred(r)]
            if not group:
                continue
            print(f"\n  -- {cat}")
            best_tp = max(r.throughput for r in group)
            for r in group:
                bar = ">" * min(35, max(1, int(r.throughput / best_tp * 35)))
                print(f"    {r.name:<48} {r.mean_ms:>8.3f} ms/op  "
                      f"{r.throughput:>10,.0f} ops/s  {bar}")

        print(f"\n{'='*W}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="MNHEME Benchmark Suite")
    parser.add_argument("--records", type=int, default=2000)
    parser.add_argument("--output",  type=str, default=None)
    parser.add_argument("--db",      type=str, default="/tmp/_mnheme_bench.mnheme")
    args = parser.parse_args()

    if os.path.exists(args.db):
        os.remove(args.db)

    suite  = MnhemeBenchmark(db_path=args.db, n_records=args.records)
    report = suite.run()

    if os.path.exists(args.db):
        os.remove(args.db)

    if args.output:
        Path(args.output).write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Report salvato in: {args.output}")


if __name__ == "__main__":
    main()
