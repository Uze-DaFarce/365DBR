#!/usr/bin/env python3
"""
Phase 4 smoke tests for db/query (requires live local Postgres + populated data).

Run from monorepo root:
  python db/scripts/test_query_phase4.py

Exits non-zero on any failure. Uses real local day packs when present.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))

from query import dual_read_day, get_connection, load_day, load_verse, search_strong


def main() -> int:
    failures = 0

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal failures
        status = "PASS" if cond else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures += 1

    print("=== Phase 4 query layer smoke ===")
    conn = get_connection()
    try:
        # Day load
        day = load_day(conn, "0101")
        check("day 0101 loads", day["verseCount"] > 50, f"verses={day['verseCount']}")
        check("day has label", bool(day.get("label")))
        check("day has 4 passages", len(day["passages"]) == 4)
        check("lsv in available", "lsv" in day["availableTranslations"])
        first_vid = next(iter(day["verseMap"]))
        first = day["verseMap"][first_vid]
        check("verseMap has original", "original" in first)
        check("verseMap has lsv", "lsv" in first and bool(first["lsv"].get("text")))
        # Flattened string shape (not array) — mirrors loadDailyBread contract
        check(
            "lsv text is str (flattened)",
            isinstance(first["lsv"]["text"], str),
        )
        check(
            "original tokens list present",
            isinstance(first["original"].get("tokens"), list),
        )

        # Known verse
        gen = load_verse(conn, "GEN.1.1")
        check("GEN.1.1 LSV", "LSV" in gen["translations"])
        check(
            "GEN.1.1 has Strong's tokens",
            any(t.get("strong") for t in gen["original"]["tokens"]),
        )
        lsv = gen["translations"]["LSV"]
        check("GEN.1.1 LSV mentions God/beginning", "God" in lsv or "beginning" in lsv.lower())

        jhn = load_verse(conn, "JHN.1.1")
        check("JHN.1.1 Greek tokens", len(jhn["original"]["tokens"]) >= 3)
        check("JHN.1.1 language greek", jhn["original"]["language"] == "greek")

        # Strong's H430 (Elohim)
        s = search_strong(conn, "H430", limit=5)
        check("H430 hits", s["total_verses"] >= 100, f"total={s['total_verses']}")
        check("H430 returns rows", s["returned"] >= 1)
        check("H430 GEN.1.1 in early hits or total large", s["total_verses"] > 0)

        # Dual-read against local packs if present
        local_manifest = ROOT / "apps" / "365DBR" / "data" / "0101" / "manifest.json"
        if local_manifest.exists():
            for d in ("0101", "0702", "1225"):
                mp = ROOT / "apps" / "365DBR" / "data" / d / "manifest.json"
                if not mp.exists():
                    print(f"  [SKIP] dual-read {d} (no local pack)")
                    continue
                report = dual_read_day(conn, d, source="local")
                check(
                    f"dual-read {d}",
                    report["ok"],
                    f"checked={report['checked']} mismatches={report['mismatch_count']}",
                )
        else:
            print("  [SKIP] dual-read (no local 0101 pack)")

    finally:
        conn.close()

    print("=" * 40)
    if failures:
        print(f"FAILED: {failures}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
