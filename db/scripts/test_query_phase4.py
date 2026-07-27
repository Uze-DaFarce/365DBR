#!/usr/bin/env python3
"""
Phase 4 smoke tests — thin wrapper.

Prefer the real-world suite:
  python db/scripts/test_query_stress_phase4.py

This file keeps a short smoke path that still avoids only GEN.1.1/0101 toys:
uses mid-year / alignment days when packs exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))

from query import dual_read_day, get_connection, load_day, load_verse, search_strong

# Prefer non-toy days
SMOKE_DAYS = ("0823", "0228", "0615", "1015", "0331")
SMOKE_VERSES = ("PSA.31.18", "ACT.8.37", "ROM.16.24", "EXO.20.3")


def main() -> int:
    failures = 0

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal failures
        status = "PASS" if cond else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures += 1

    print("=== Phase 4 query smoke (non-toy days) ===")
    print("  For large coverage: python db/scripts/test_query_stress_phase4.py")
    conn = get_connection()
    try:
        loaded = None
        for d in SMOKE_DAYS:
            try:
                loaded = load_day(conn, d)
                check(
                    f"load_day {d}",
                    loaded["verseCount"] > 20,
                    f"verses={loaded['verseCount']}",
                )
                break
            except Exception:
                continue
        if loaded is None:
            check("load_day any smoke day", False, f"tried {SMOKE_DAYS}")
        else:
            vid = next(iter(loaded["verseMap"]))
            ent = loaded["verseMap"][vid]
            check("flattened lsv str", isinstance((ent.get("lsv") or {}).get("text"), str))

        for vid in SMOKE_VERSES:
            try:
                v = load_verse(conn, vid)
                check(
                    f"verse {vid}",
                    bool(v.get("translations") or v.get("original", {}).get("tokens")),
                    f"trans={list((v.get('translations') or {}).keys())}",
                )
            except KeyError:
                print(f"  [SKIP] {vid} not in DB")

        s = search_strong(conn, "H3068", limit=5)  # YHWH — not only H430
        check("strong H3068", s["total_verses"] >= 1, f"total={s['total_verses']}")

        for d in SMOKE_DAYS:
            mp = ROOT / "apps" / "365DBR" / "data" / d / "manifest.json"
            if not mp.exists():
                continue
            r = dual_read_day(conn, d, source="local")
            check(
                f"dual-read {d}",
                r["ok"],
                f"checked={r['checked']} mm={r['mismatch_count']}",
            )
            break
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
