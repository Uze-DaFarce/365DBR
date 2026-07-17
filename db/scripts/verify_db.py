#!/usr/bin/env python3
"""
365DBR Phase 3: Full-database validation, integrity & reconciliation.

Checks (fail hard on mismatch):
1. Schema seeds still present (66 books, LSV/KJV)
2. Book-level verse counts vs bible_common.BIBLE_DATA
3. Daily plan coverage (365 days, 4 passages each)
4. Translation coverage (LSV/KJV rows)
5. Original tokens: Hebrew Strong's density; Greek surface present
6. TR integrity samples (e.g. ROM.16.25-27, MAT.17.21, JHN.5.4, ACT.8.37)
7. Sample day load query performance baseline
8. S.I.-style smoke queries (day pack, Strong's, range)

Usage (monorepo root):
  python db/scripts/verify_db.py
  python db/scripts/verify_db.py --json-spot-days "0101,0702,1225"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))
sys.path.insert(0, str(ROOT / "db"))

import bible_common  # noqa: E402
from etl.parse_passage import parse_passage_payload  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / "db" / ".env")
except ImportError:
    pass

LOCAL_DATA = ROOT / "apps" / "365DBR" / "data"

# Verses that must exist under TR/GRCTR (were often absent in critical Greek)
TR_MUST_EXIST = [
    "MAT.17.21",
    "MAT.18.11",
    "JHN.5.4",
    "ACT.8.37",
    "ROM.16.24",
    "ROM.16.25",
    "ROM.16.26",
    "ROM.16.27",
]

# Should NOT exist as verse ids under TR numbering
TR_MUST_NOT_EXIST = [
    "ROM.14.24",
    "ROM.14.25",
    "ROM.14.26",
]


def get_connection():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        user = os.getenv("POSTGRES_USER", "365dbr_dev")
        pw = os.getenv("POSTGRES_PASSWORD", "dev_password_change_me")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "mt_sinai_365dbr")
        dsn = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
    return psycopg.connect(dsn, row_factory=dict_row)


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


class Report:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.failures: list[str] = []

    def check(self, name: str, cond: bool, detail: str = ""):
        status = "PASS" if cond else "FAIL"
        msg = f"  [{status}] {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        if cond:
            self.passed += 1
        else:
            self.failed += 1
            self.failures.append(f"{name}: {detail}" if detail else name)

    def warn(self, name: str, detail: str = ""):
        print(f"  [WARN] {name}" + (f" — {detail}" if detail else ""))
        self.warnings += 1


def expected_verse_count(book: str) -> int:
    return sum(bible_common.BIBLE_DATA[book])


def section_1_seeds(cur, r: Report):
    print("\n=== 1. Seeds & translations ===")
    cur.execute("SELECT count(*) AS c FROM books")
    n = cur.fetchone()["c"]
    r.check("66 books", n == 66, f"count={n}")

    cur.execute("SELECT code, is_primary FROM translations ORDER BY code")
    rows = {row["code"]: row for row in cur.fetchall()}
    r.check("LSV present", "LSV" in rows)
    r.check("KJV present", "KJV" in rows)
    r.check("LSV is primary", rows.get("LSV", {}).get("is_primary") is True)


def section_2_book_counts(cur, r: Report):
    print("\n=== 2. Book-level verse counts vs BIBLE_DATA ===")
    cur.execute("SELECT id, book_code FROM verses")
    db_by_book: dict[str, set[str]] = {}
    for row in cur.fetchall():
        db_by_book.setdefault(row["book_code"], set()).add(row["id"])

    missing_all: list[str] = []
    extra_all: list[str] = []
    for book in bible_common.ALL_BOOKS:
        exp: set[str] = set()
        for ci, n in enumerate(bible_common.BIBLE_DATA[book], start=1):
            for v in range(1, n + 1):
                exp.add(f"{book}.{ci}.{v}")
        db_ids = db_by_book.get(book, set())
        missing_all.extend(sorted(exp - db_ids))
        extra_all.extend(sorted(db_ids - exp))

    r.check(
        "No invalid verse ids beyond BIBLE_DATA",
        len(extra_all) == 0,
        f"extras={extra_all[:10]}" if extra_all else "OK",
    )
    r.check(
        "Full canonical coverage (every BIBLE_DATA verse in DB)",
        len(missing_all) == 0,
        (
            f"missing {len(missing_all)}: {missing_all[:12]}"
            + ("..." if len(missing_all) > 12 else "")
            if missing_all
            else "OK"
        ),
    )
    if missing_all:
        print(
            "      Remediation: ensure readings.json ranges cover these verses, "
            "re-fetch day packs, re-run populate_day for those days."
        )

    total_exp = sum(expected_verse_count(b) for b in bible_common.ALL_BOOKS)
    cur.execute("SELECT count(*) AS c FROM verses")
    total_got = cur.fetchone()["c"]
    r.check(
        f"Total verses ({total_got} == {total_exp})",
        total_got == total_exp,
    )

    # Spot ROM TR shape
    cur.execute(
        "SELECT chapter, count(*) AS c FROM verses WHERE book_code = 'ROM' GROUP BY chapter ORDER BY chapter"
    )
    rom = {row["chapter"]: row["c"] for row in cur.fetchall()}
    r.check("ROM ch14 has 23 verses", rom.get(14) == 23, f"got {rom.get(14)}")
    r.check("ROM ch16 has 27 verses", rom.get(16) == 27, f"got {rom.get(16)}")

    cur.execute(
        "SELECT chapter, count(*) AS c FROM verses WHERE book_code = 'ACT' GROUP BY chapter ORDER BY chapter"
    )
    act = {row["chapter"]: row["c"] for row in cur.fetchall()}
    r.check("ACT ch8 has 40 verses (TR incl. 8:37)", act.get(8) == 40, f"got {act.get(8)}")

def section_3_daily_plan(cur, r: Report):
    print("\n=== 3. Daily reading plan ===")
    cur.execute("SELECT count(*) AS c FROM daily_readings")
    days = cur.fetchone()["c"]
    r.check("365 daily_readings", days == 365, f"got {days}")

    cur.execute(
        """
        SELECT day, count(*) AS c
        FROM daily_passages
        GROUP BY day
        HAVING count(*) <> 4
        """
    )
    bad = cur.fetchall()
    r.check("Every day has exactly 4 passages", len(bad) == 0, f"{len(bad)} days wrong")

    cur.execute("SELECT count(*) AS c FROM daily_passages")
    pc = cur.fetchone()["c"]
    r.check("1460 daily_passages (365*4)", pc == 1460, f"got {pc}")


def section_4_translations(cur, r: Report):
    print("\n=== 4. Translation coverage ===")
    cur.execute(
        """
        SELECT t.code, count(*) AS c
        FROM verse_translations vt
        JOIN translations t ON t.id = vt.translation_id
        GROUP BY t.code
        ORDER BY t.code
        """
    )
    by_code = {row["code"]: row["c"] for row in cur.fetchall()}
    r.check("LSV has translation rows", by_code.get("LSV", 0) > 30000, f"LSV={by_code.get('LSV', 0)}")
    r.check("KJV has translation rows", by_code.get("KJV", 0) > 30000, f"KJV={by_code.get('KJV', 0)}")
    # Day plan covers the year; not every BIBLE_DATA verse may appear if plan skips none...
    # Full plan should cover essentially all verses once. Allow small tolerance only if needed.
    cur.execute("SELECT count(*) AS c FROM verses")
    n_verses = cur.fetchone()["c"]
    lsv = by_code.get("LSV", 0)
    # Expect high coverage: at least 95% of verses have LSV from the 365-day packs
    r.check(
        "LSV covers ≥95% of verse rows",
        lsv >= int(n_verses * 0.95),
        f"LSV={lsv} verses={n_verses}",
    )


def section_5_tokens(cur, r: Report):
    print("\n=== 5. Original tokens (Hebrew / Greek) ===")
    cur.execute(
        """
        SELECT language, count(*) AS c,
               count(strong_number) AS with_strong
        FROM original_tokens
        GROUP BY language
        ORDER BY language
        """
    )
    by_lang = {row["language"]: row for row in cur.fetchall()}
    heb = by_lang.get("hebrew")
    grk = by_lang.get("greek")
    r.check("Hebrew tokens present", heb is not None and heb["c"] > 100_000, f"{heb}")
    r.check("Greek tokens present", grk is not None and grk["c"] > 50_000, f"{grk}")
    if heb:
        ratio = heb["with_strong"] / heb["c"] if heb["c"] else 0
        r.check(
            "Hebrew Strong's density ≥ 90%",
            ratio >= 0.90,
            f"{heb['with_strong']}/{heb['c']} = {ratio:.1%}",
        )
    if grk:
        # GRCTR surface tokens: strongs usually null
        r.check("Greek tokens have surface text rows", grk["c"] > 0)


def section_6_tr_samples(cur, r: Report):
    print("\n=== 6. TR integrity samples ===")
    for vid in TR_MUST_EXIST:
        cur.execute("SELECT 1 FROM verses WHERE id = %s", (vid,))
        exists = cur.fetchone() is not None
        r.check(f"verse exists: {vid}", exists)

        cur.execute(
            """
            SELECT count(*) AS c FROM original_tokens
            WHERE verse_id = %s AND language = 'greek'
            """,
            (vid,),
        )
        tc = cur.fetchone()["c"]
        r.check(f"greek tokens for {vid}", tc > 0, f"tokens={tc}")

        cur.execute(
            """
            SELECT vt.text FROM verse_translations vt
            JOIN translations t ON t.id = vt.translation_id
            WHERE vt.verse_id = %s AND t.code = 'LSV'
            """,
            (vid,),
        )
        row = cur.fetchone()
        r.check(f"LSV text for {vid}", row is not None and len(norm_ws(row["text"])) > 0)

    for vid in TR_MUST_NOT_EXIST:
        cur.execute("SELECT 1 FROM verses WHERE id = %s", (vid,))
        exists = cur.fetchone() is not None
        r.check(f"verse absent (TR numbering): {vid}", not exists)


def section_7_performance(cur, r: Report):
    print("\n=== 7. Performance baseline (sample day load) ===")
    # Typical day load: all LSV text for verses in daily_passages ranges is complex;
    # approximate: join daily_passages + verses in range via verse_order.
    day = "0101"
    t0 = time.perf_counter()
    cur.execute(
        """
        SELECT v.id, vt.text
        FROM daily_passages dp
        JOIN verses vs ON vs.id = dp.start_verse_id
        JOIN verses ve ON ve.id = dp.end_verse_id
        JOIN verses v ON v.verse_order BETWEEN vs.verse_order AND ve.verse_order
        JOIN translations t ON t.code = 'LSV'
        JOIN verse_translations vt ON vt.verse_id = v.id AND vt.translation_id = t.id
        WHERE dp.day = %s
        ORDER BY v.verse_order
        """,
        (day,),
    )
    rows = cur.fetchall()
    ms = (time.perf_counter() - t0) * 1000
    r.check(
        f"Day {day} LSV load returns rows",
        len(rows) > 50,
        f"rows={len(rows)} time={ms:.1f}ms",
    )
    # Soft target: under 2s for local docker (not a hard product SLA yet)
    if ms > 2000:
        r.warn(f"Day load slower than 2s ({ms:.1f}ms) — note for Phase 4 tuning")
    else:
        print(f"  [INFO] Day {day} LSV range load: {len(rows)} rows in {ms:.1f}ms")


def section_8_si_queries(cur, r: Report):
    print("\n=== 8. S.I.-style smoke queries ===")

    # Strong's sample (Elohim) — padding varies H430 / H0430
    cur.execute(
        """
        SELECT count(DISTINCT verse_id) AS verses
        FROM original_tokens
        WHERE strong_number ~ '^H0*430$'
        """
    )
    n = cur.fetchone()["verses"]
    r.check("Strong's H430 (Elohim) hits ≥ 1 verse", n >= 1, f"verses={n}")

    # Sample: GEN.1.1 tokens + LSV
    cur.execute(
        """
        SELECT ot.word_order, ot.surface_text, ot.strong_number
        FROM original_tokens ot
        WHERE ot.verse_id = 'GEN.1.1' AND ot.language = 'hebrew'
        ORDER BY ot.word_order
        LIMIT 5
        """
    )
    gen_tokens = cur.fetchall()
    r.check("GEN.1.1 has Hebrew tokens", len(gen_tokens) >= 3, f"got {len(gen_tokens)}")

    cur.execute(
        """
        SELECT vt.text FROM verse_translations vt
        JOIN translations t ON t.id = vt.translation_id
        WHERE vt.verse_id = 'GEN.1.1' AND t.code = 'LSV'
        """
    )
    gen_lsv = cur.fetchone()
    ok_lsv = gen_lsv is not None and len(norm_ws(gen_lsv["text"])) > 10
    r.check(
        "GEN.1.1 LSV non-empty",
        ok_lsv,
        norm_ws(gen_lsv["text"])[:80] if gen_lsv else "missing",
    )

    # Greek sample JHN.1.1
    cur.execute(
        """
        SELECT string_agg(surface_text, ' ' ORDER BY word_order) AS t
        FROM original_tokens
        WHERE verse_id = 'JHN.1.1' AND language = 'greek'
        """
    )
    jhn = cur.fetchone()
    greek = (jhn or {}).get("t") or ""
    r.check("JHN.1.1 Greek surface present", len(greek) > 10, greek[:60])

    # Day plan query
    cur.execute(
        """
        SELECT section, start_verse_id, end_verse_id, verse_count
        FROM daily_passages WHERE day = '0702' ORDER BY id
        """
    )
    passages = cur.fetchall()
    r.check("0702 has 4 plan sections", len(passages) == 4)


def section_9_json_spot(cur, r: Report, days: list[str]):
    print("\n=== 9. Local JSON spot-check (optional) ===")
    if not days:
        print("  [INFO] skipped (no --json-spot-days)")
        return

    for day in days:
        day_dir = LOCAL_DATA / day
        manifest_path = day_dir / "manifest.json"
        if not manifest_path.exists():
            r.check(f"local pack {day}", False, "manifest missing")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        mismatches = 0
        checked = 0
        for fname in manifest.get("files", [])[:2]:  # first two files per day
            raw = json.loads((day_dir / fname).read_text(encoding="utf-8"))
            parsed = parse_passage_payload(raw, fname)
            # pick first LSV verse
            lsv_map = parsed["translations"].get("LSV") or {}
            for vid, text in list(lsv_map.items())[:3]:
                cur.execute(
                    """
                    SELECT vt.text FROM verse_translations vt
                    JOIN translations t ON t.id = vt.translation_id
                    WHERE vt.verse_id = %s AND t.code = 'LSV'
                    """,
                    (vid,),
                )
                row = cur.fetchone()
                checked += 1
                if not row or norm_ws(row["text"]) != norm_ws(text):
                    mismatches += 1
        r.check(
            f"JSON↔DB LSV sample day {day}",
            checked > 0 and mismatches == 0,
            f"checked={checked} mismatches={mismatches}",
        )


def main():
    parser = argparse.ArgumentParser(description="Phase 3 full DB reconciliation")
    parser.add_argument(
        "--json-spot-days",
        default="0101,0702,1225",
        help="Comma MMDD list for local JSON text compare (empty to skip)",
    )
    args = parser.parse_args()
    spot_days = [d.strip() for d in args.json_spot_days.split(",") if d.strip()]

    print("=== 365DBR Phase 3 — DB Validation & Reconciliation ===")
    print("Truth/Accuracy first. Source of counts: bible_common.BIBLE_DATA")

    r = Report()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            section_1_seeds(cur, r)
            section_2_book_counts(cur, r)
            section_3_daily_plan(cur, r)
            section_4_translations(cur, r)
            section_5_tokens(cur, r)
            section_6_tr_samples(cur, r)
            section_7_performance(cur, r)
            section_8_si_queries(cur, r)
            section_9_json_spot(cur, r, spot_days)
    finally:
        conn.close()

    print("\n" + "=" * 60)
    print(f"PASSED: {r.passed}  FAILED: {r.failed}  WARNINGS: {r.warnings}")
    if r.failures:
        print("Failures:")
        for f in r.failures:
            print(f"  - {f}")
        print("=== OVERALL: FAIL ===")
        sys.exit(1)
    print("=== OVERALL: PASS ===")
    print("Phase 3 reconciliation signed off for this DB snapshot.")


if __name__ == "__main__":
    main()
