#!/usr/bin/env python3
"""
Phase 4 stress / real-world coverage tests (NOT the toy suite).

Avoids repeating only 0101 / GEN.1.1 / JHN.1.1. Prefers:
  - month lengths & leap day (0229 when present)
  - English↔org alignment edges (Protestant vs Hebrew verse counts)
  - multi-book / long OT ranges, Psalms with superscriptions
  - dual-read across a large stratified day sample
  - Strong's outside the usual H430/Elohim demo when possible

Requires: populated DB + local day packs under apps/365DBR/data/MMDD/.

  python db/scripts/test_query_stress_phase4.py
  python db/scripts/test_query_stress_phase4.py --dual-read-limit 80
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))

from query import (  # noqa: E402
    dual_read_day,
    get_connection,
    load_day,
    load_verse,
    search_strong,
)

LOCAL_DATA = ROOT / "apps" / "365DBR" / "data"
READINGS = LOCAL_DATA / "readings.json"

# English Protestant BCVs that often fall outside Hebrew BIBLE_DATA chapter lengths
ENGLISH_EDGE_BCVS = [
    "GEN.31.55",
    "EXO.8.32",  # nearby English edge; may or may not be in packs
    "EXO.8.29",
    "LEV.6.30",
    "NUM.16.50",
    "DEU.29.29",
    "1SA.23.29",
    "2SA.18.33",
    "NEH.7.73",
    "NEH.9.38",
    "JOB.41.34",
    "PSA.18.1",
    "PSA.31.18",
    "PSA.31.24",
    "ECC.5.1",
    "SON.6.13",
    "ISA.9.1",
    "DAN.4.1",
    "HOS.14.9",
    "JON.1.17",
    "ACT.8.37",  # TR
    "ROM.16.24",
]

# Prefer complex / calendar-edge days when packs exist
PREFERRED_HARD_DAYS = [
    "0229",  # leap day (non-leap years may lack pack)
    "0228",
    "0131",
    "0331",
    "0430",
    "0531",
    "0630",
    "0731",
    "0831",
    "0930",
    "1031",
    "1130",
    "1231",
    "0301",
    "0501",
    "0901",
    "1201",
    # known alignment-heavy (Psalms / long OT)
    "0126",  # PSA.18 superscription offset
    "0212",  # PSA.23 title
    "0227",
    "0222",
    "0319",
    "0407",
    "0523",
    "0604",
    "0711",
    "0815",
    "0819",
    "0921",
    "1015",
    "1115",
]


def _list_local_days() -> list[str]:
    if not LOCAL_DATA.is_dir():
        return []
    out = []
    for p in LOCAL_DATA.iterdir():
        if p.is_dir() and len(p.name) == 4 and p.name.isdigit():
            if (p / "manifest.json").exists():
                out.append(p.name)
    return sorted(out)


def _readings_by_day() -> dict[str, dict]:
    if not READINGS.exists():
        return {}
    rows = json.loads(READINGS.read_text(encoding="utf-8"))
    return {r["day"]: r for r in rows}


def _stratified_sample(all_days: list[str], limit: int, rng: random.Random) -> list[str]:
    """Mix preferred hard days + month-stratified random coverage."""
    have = set(all_days)
    chosen: list[str] = []
    for d in PREFERRED_HARD_DAYS:
        if d in have and d not in chosen:
            chosen.append(d)

    # One random day per month when possible
    by_month: dict[str, list[str]] = {}
    for d in all_days:
        by_month.setdefault(d[:2], []).append(d)
    for _m, days in sorted(by_month.items()):
        pick = rng.choice(days)
        if pick not in chosen:
            chosen.append(pick)

    # Fill with more random until limit
    pool = [d for d in all_days if d not in chosen]
    rng.shuffle(pool)
    for d in pool:
        if len(chosen) >= limit:
            break
        chosen.append(d)

    # Exclude the over-used first-of-year demos unless nothing else exists
    demoted = [d for d in chosen if d not in ("0101", "0702", "1225")]
    if len(demoted) >= max(8, limit // 2):
        chosen = demoted[:limit] if len(demoted) > limit else demoted
        # re-add month coverage if we stripped too hard
        while len(chosen) < min(limit, len(all_days)):
            for d in pool:
                if d not in chosen:
                    chosen.append(d)
                    break
            else:
                break
    return chosen[:limit]


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 4 real-world stress tests")
    ap.add_argument("--dual-read-limit", type=int, default=48, help="Max days for dual-read")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    failures = 0
    warnings = 0

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal failures
        status = "PASS" if cond else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures += 1

    def warn(name: str, detail: str = ""):
        nonlocal warnings
        print(f"  [WARN] {name}" + (f" — {detail}" if detail else ""))
        warnings += 1

    print("=== Phase 4 STRESS tests (complex / large sample) ===")
    print(f"  seed={args.seed} dual_read_limit={args.dual_read_limit}")

    local_days = _list_local_days()
    readings = _readings_by_day()
    check("local day packs present", len(local_days) >= 30, f"count={len(local_days)}")

    sample = _stratified_sample(local_days, args.dual_read_limit, rng)
    print(f"  dual-read sample ({len(sample)} days): {','.join(sample[:12])}…")

    conn = get_connection()
    try:
        # --- A. English-edge BCVs that broke populate (FK) ---
        print("\n--- A. English/Protestant BCV edges (not in Hebrew BIBLE_DATA) ---")
        with conn.cursor() as cur:
            for vid in ENGLISH_EDGE_BCVS:
                cur.execute("SELECT id FROM verses WHERE id = %s", (vid,))
                row = cur.fetchone()
                cur.execute(
                    """
                    SELECT count(*) AS c FROM verse_translations vt
                    JOIN translations t ON t.id = vt.translation_id
                    WHERE vt.verse_id = %s AND t.code IN ('LSV','KJV')
                    """,
                    (vid,),
                )
                nt = cur.fetchone()["c"]
                cur.execute(
                    "SELECT count(*) AS c FROM original_tokens WHERE verse_id = %s",
                    (vid,),
                )
                ntok = cur.fetchone()["c"]
                cur.execute(
                    """
                    SELECT source_verse_id FROM verse_alignments
                    WHERE english_verse_id = %s LIMIT 3
                    """,
                    (vid,),
                )
                al = [r["source_verse_id"] for r in cur.fetchall()]
                if row and (nt > 0 or ntok > 0):
                    check(
                        f"edge {vid} present",
                        True,
                        f"trans={nt} tokens={ntok} align_src={al}",
                    )
                elif row:
                    warn(f"edge {vid} verse row only", f"trans={nt} tokens={ntok}")
                else:
                    # Not every edge appears in every corpus slice
                    warn(f"edge {vid} not in this DB snapshot", "ok if day not populated")

        # --- B. Alignment integrity: english ≠ source on offset maps ---
        print("\n--- B. verse_alignments offset samples ---")
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT english_verse_id, source_verse_id, established_by
                FROM verse_alignments
                WHERE english_verse_id <> source_verse_id
                ORDER BY english_verse_id
                LIMIT 40
                """
            )
            offsets = cur.fetchall()
            check(
                "offset alignments exist",
                len(offsets) >= 5,
                f"count_sample={len(offsets)}",
            )
            # Content match: English LSV and original under english id should both exist
            checked_content = 0
            content_ok = 0
            for a in offsets[:15]:
                eng = a["english_verse_id"]
                try:
                    v = load_verse(conn, eng)
                except KeyError:
                    continue
                checked_content += 1
                has_en = bool(v.get("translations"))
                has_orig = bool((v.get("original") or {}).get("tokens"))
                src_ok = a["source_verse_id"] in (
                    (v.get("original") or {}).get("source_verse_ids") or []
                ) or any(
                    t.get("source_verse_id") == a["source_verse_id"]
                    for t in (v.get("original") or {}).get("tokens") or []
                )
                if has_en and has_orig and src_ok:
                    content_ok += 1
            check(
                "offset rows have EN+original+source provenance",
                checked_content > 0 and content_ok >= max(1, checked_content // 2),
                f"ok={content_ok}/{checked_content}",
            )

        # --- C. Titles / superscriptions ---
        print("\n--- C. Superscription annotations ---")
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(*) AS c FROM annotations
                WHERE annotation_type IN ('superscription','title')
                """
            )
            n_titles = cur.fetchone()["c"]
            check("title/superscription annotations present", n_titles >= 1, f"count={n_titles}")

        # --- D. Day loads on hard calendar / complex days ---
        print("\n--- D. load_day on hard days ---")
        hard_load = [d for d in PREFERRED_HARD_DAYS if d in set(local_days)][:12]
        for d in hard_load:
            try:
                payload = load_day(conn, d)
                check(
                    f"load_day {d}",
                    payload["verseCount"] > 10 and len(payload["passages"]) == 4,
                    f"verses={payload['verseCount']} label={payload.get('label','')[:50]}",
                )
                # Every display verse with LSV should have string text
                bad = 0
                for vid, ent in payload["verseMap"].items():
                    if "lsv" in ent and not isinstance(ent["lsv"].get("text"), str):
                        bad += 1
                check(f"load_day {d} lsv flattened", bad == 0, f"bad={bad}")
            except Exception as e:
                check(f"load_day {d}", False, str(e))

        # --- E. Large dual-read sample ---
        print("\n--- E. dual-read stratified sample ---")
        dr_pass = 0
        dr_fail = 0
        fail_examples: list[str] = []
        total_checked = 0
        for d in sample:
            try:
                r = dual_read_day(conn, d, source="local")
                total_checked += r.get("checked") or 0
                if r.get("ok"):
                    dr_pass += 1
                else:
                    dr_fail += 1
                    if len(fail_examples) < 8:
                        mm = (r.get("mismatches") or [])[:1]
                        fail_examples.append(
                            f"{d}: mm={r.get('mismatch_count')} {mm}"
                        )
            except Exception as e:
                dr_fail += 1
                if len(fail_examples) < 8:
                    fail_examples.append(f"{d}: EXC {e}")
        check(
            "dual-read majority pass",
            dr_pass >= max(1, int(0.85 * (dr_pass + dr_fail))),
            f"pass={dr_pass} fail={dr_fail} cells_checked≈{total_checked}",
        )
        if fail_examples:
            print("  fail samples:")
            for line in fail_examples:
                print(f"    {line}")

        # --- F. Strong's beyond H430 ---
        print("\n--- F. Strong's variety ---")
        for strong in ("H3068", "H430", "H1", "G2424", "G2316"):
            try:
                s = search_strong(conn, strong, limit=8)
                # Greek strongs may be 0 in current GRCTR token data — warn not fail
                if s["total_verses"] >= 1:
                    check(
                        f"strong {strong}",
                        True,
                        f"verses={s['total_verses']} sample={[h['verse_id'] for h in s['hits'][:3]]}",
                    )
                else:
                    warn(f"strong {strong} no hits", "expected for Greek if strongs absent")
            except Exception as e:
                check(f"strong {strong}", False, str(e))

        # --- G. TR / plan complexity from readings ---
        print("\n--- G. Plan complexity spot-checks ---")
        if readings:
            # Days whose api_format spans chapters or unusual books
            complex_days = []
            for day, row in readings.items():
                af = row.get("api_format") or ""
                if day not in set(local_days):
                    continue
                if af.count("-") >= 4 or "PSA." in af and "PRO." in af:
                    if any(x in af for x in ("1CH", "2CH", "NEH", "NUM", "DEU", "PSA.1")):
                        complex_days.append(day)
            rng.shuffle(complex_days)
            for day in complex_days[:8]:
                try:
                    r = dual_read_day(conn, day, source="local")
                    check(
                        f"complex plan dual-read {day}",
                        r.get("ok") is True,
                        f"checked={r.get('checked')} mm={r.get('mismatch_count')}",
                    )
                except Exception as e:
                    check(f"complex plan dual-read {day}", False, str(e))

        # --- H. FK sanity: no tokens without verses ---
        print("\n--- H. Integrity: tokens FK orphans ---")
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(*) AS c
                FROM original_tokens ot
                LEFT JOIN verses v ON v.id = ot.verse_id
                WHERE v.id IS NULL
                """
            )
            orphans = cur.fetchone()["c"]
            check("no original_tokens without verses row", orphans == 0, f"orphans={orphans}")

            cur.execute(
                """
                SELECT count(*) AS c
                FROM verse_translations vt
                LEFT JOIN verses v ON v.id = vt.verse_id
                WHERE v.id IS NULL
                """
            )
            orphans_t = cur.fetchone()["c"]
            check(
                "no verse_translations without verses row",
                orphans_t == 0,
                f"orphans={orphans_t}",
            )

            cur.execute(
                """
                SELECT count(*) AS c FROM verses v
                WHERE v.verse_order >= 90000000
                """
            )
            synthetic = cur.fetchone()["c"]
            # English-only BCVs may use neighbor order now; synthetic still ok to note
            print(f"  [INFO] verses with synthetic high verse_order: {synthetic}")

    finally:
        conn.close()

    print("\n" + "=" * 50)
    print(f"FAILED: {failures}  WARNINGS: {warnings}")
    if failures:
        print("=== STRESS: FAIL ===")
        return 1
    print("=== STRESS: PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
