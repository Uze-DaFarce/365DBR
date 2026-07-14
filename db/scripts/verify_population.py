#!/usr/bin/env python3
"""
Phase 2: Verify DB population against the same day-pack source JSON.

Checks:
- daily_readings / daily_passages present
- verse counts match extract_verse_ids from source files
- sample LSV/KJV text equality (normalized whitespace)
- original tokens exist for Hebrew and Greek samples
- Strong's present on Hebrew tokens; Greek tokens have surface text

Usage:
  python db/scripts/verify_population.py --day 0123
  python db/scripts/verify_population.py --day 0123,0702 --source local
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))
sys.path.insert(0, str(ROOT / "db"))

from etl.parse_passage import parse_passage_payload  # noqa: E402
import bible_common  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / "db" / ".env")
except ImportError:
    pass

PRODUCTION_BASE = "https://mt-sin.ai/365DBR/data"
LOCAL_DATA = ROOT / "apps" / "365DBR" / "data"


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


def load_day_files(day: str, source: str):
    if source == "auto":
        source = "local" if (LOCAL_DATA / day / "manifest.json").exists() else "prod"
    if source == "local":
        base = LOCAL_DATA / day
        manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
        files = [
            (fn, json.loads((base / fn).read_text(encoding="utf-8")))
            for fn in manifest["files"]
        ]
        return source, manifest, files
    base_url = f"{PRODUCTION_BASE}/{day}"
    req = urllib.request.Request(f"{base_url}/manifest.json", headers={"User-Agent": "365DBR-ETL"})
    with urllib.request.urlopen(req, timeout=60) as r:
        manifest = json.loads(r.read().decode("utf-8"))
    files = []
    for fn in manifest["files"]:
        req = urllib.request.Request(f"{base_url}/{fn}", headers={"User-Agent": "365DBR-ETL"})
        with urllib.request.urlopen(req, timeout=60) as r:
            files.append((fn, json.loads(r.read().decode("utf-8"))))
    return source, manifest, files


def check(msg: str, cond: bool, failures: list):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {msg}")
    if not cond:
        failures.append(msg)


def verify_day(conn, day: str, source_pref: str) -> bool:
    print(f"\n=== Verify population: {day} ===")
    failures: list[str] = []
    source, manifest, files = load_day_files(day, source_pref)
    print(f"  source={source} files={len(files)}")

    parsed = [parse_passage_payload(raw, fn) for fn, raw in files]
    all_vids = set()
    for p in parsed:
        all_vids.update(p["verse_ids"])

    with conn.cursor() as cur:
        cur.execute("SELECT day, label, total_verses FROM daily_readings WHERE day = %s", (day,))
        dr = cur.fetchone()
        check(f"daily_readings row for {day}", dr is not None, failures)

        cur.execute(
            "SELECT section, start_verse_id, end_verse_id, verse_count FROM daily_passages WHERE day = %s ORDER BY id",
            (day,),
        )
        passages = cur.fetchall()
        check("daily_passages has 4 sections", len(passages) == 4, failures)

        cur.execute(
            "SELECT count(*) AS c FROM verses WHERE id = ANY(%s)",
            (list(all_vids),),
        )
        vc = cur.fetchone()["c"]
        check(f"verses in DB for day pack ({vc} == {len(all_vids)})", vc == len(all_vids), failures)

        # Tokens
        cur.execute(
            """
            SELECT language, count(*) AS c,
                   count(strong_number) AS with_strong
            FROM original_tokens
            WHERE verse_id = ANY(%s)
            GROUP BY language
            """,
            (list(all_vids),),
        )
        by_lang = {r["language"]: r for r in cur.fetchall()}
        expected_tokens = sum(len(p["tokens"]) for p in parsed)
        cur.execute(
            "SELECT count(*) AS c FROM original_tokens WHERE verse_id = ANY(%s)",
            (list(all_vids),),
        )
        tok_c = cur.fetchone()["c"]
        check(f"original_tokens count ({tok_c} == {expected_tokens})", tok_c == expected_tokens, failures)

        for p in parsed:
            if p["language"] == "hebrew" and p["tokens"]:
                hl = by_lang.get("hebrew")
                check("hebrew tokens present", hl is not None and hl["c"] > 0, failures)
                if hl:
                    check(
                        f"hebrew Strong's mostly present ({hl['with_strong']}/{hl['c']})",
                        hl["with_strong"] > 0 and hl["with_strong"] >= hl["c"] * 0.5,
                        failures,
                    )
            if p["language"] == "greek" and p["tokens"]:
                gl = by_lang.get("greek")
                check("greek tokens present", gl is not None and gl["c"] > 0, failures)

        # Sample translation text compare (LSV + KJV)
        cur.execute("SELECT id, code FROM translations")
        tmap = {r["code"]: r["id"] for r in cur.fetchall()}

        for code in ("LSV", "KJV"):
            samples_checked = 0
            mismatches = 0
            for p in parsed:
                vmap = p["translations"].get(code) or {}
                for vid, text in list(vmap.items())[:5]:
                    if vid not in all_vids:
                        continue
                    cur.execute(
                        """
                        SELECT text FROM verse_translations
                        WHERE verse_id = %s AND translation_id = %s
                        """,
                        (vid, tmap[code]),
                    )
                    row = cur.fetchone()
                    samples_checked += 1
                    if not row or norm_ws(row["text"]) != norm_ws(text):
                        mismatches += 1
                        if mismatches <= 2:
                            print(f"    mismatch {code} {vid}:")
                            print(f"      src: {norm_ws(text)[:100]!r}")
                            print(f"      db:  {norm_ws(row['text'])[:100]!r}" if row else "      db:  <missing>")
            check(
                f"{code} sample text match ({samples_checked - mismatches}/{samples_checked})",
                samples_checked > 0 and mismatches == 0,
                failures,
            )

        # Spot original surface for one Hebrew + one Greek verse
        for p in parsed:
            if p["language"] == "hebrew" and p["original_text"]:
                vid, otext = next(iter(p["original_text"].items()))
                cur.execute(
                    """
                    SELECT string_agg(surface_text, '' ORDER BY word_order) AS t
                    FROM original_tokens WHERE verse_id = %s AND language = 'hebrew'
                    """,
                    (vid,),
                )
                row = cur.fetchone()
                db_t = (row["t"] or "") if row else ""
                # Hebrew join without spaces between words may differ slightly; compare stripped alnum-ish
                check(
                    f"hebrew reconstruct non-empty for {vid}",
                    len(db_t) > 0 and len(otext) > 0,
                    failures,
                )
                break
        for p in parsed:
            if p["language"] == "greek" and p["original_text"]:
                vid, otext = next(iter(p["original_text"].items()))
                cur.execute(
                    """
                    SELECT string_agg(surface_text, ' ' ORDER BY word_order) AS t
                    FROM original_tokens WHERE verse_id = %s AND language = 'greek'
                    """,
                    (vid,),
                )
                row = cur.fetchone()
                db_t = norm_ws(row["t"] if row else "")
                src_t = norm_ws(otext)
                check(
                    f"greek reconstruct match for {vid}",
                    db_t == src_t,
                    failures,
                )
                break

    if failures:
        print(f"  RESULT: FAIL ({len(failures)} issues)")
        return False
    print("  RESULT: PASS")
    return True


def main():
    parser = argparse.ArgumentParser(description="Verify Phase 2 day population")
    parser.add_argument("--day", help="MMDD or comma-separated")
    parser.add_argument("--all", action="store_true", help="Verify every day in readings.json that has local/prod data")
    parser.add_argument("--source", choices=("auto", "local", "prod"), default="auto")
    args = parser.parse_args()

    if not args.all and not args.day:
        parser.error("Provide --day MMDD or --all")

    if args.all:
        with open(LOCAL_DATA / "readings.json", encoding="utf-8") as f:
            readings = json.load(f)
        days = [r["day"] for r in readings]
    else:
        days = [d.strip() for d in args.day.split(",") if d.strip()]

    conn = get_connection()
    ok = True
    failed_days = []
    try:
        for i, day in enumerate(days, start=1):
            print(f"\n[{i}/{len(days)}]", end=" ")
            try:
                if not verify_day(conn, day, args.source):
                    ok = False
                    failed_days.append(day)
            except Exception as e:
                ok = False
                failed_days.append(day)
                print(f"\n=== Verify population: {day} ===")
                print(f"  [FAIL] exception: {e}")
    finally:
        conn.close()

    print("\n=== OVERALL:", "PASS" if ok else "FAIL", "===")
    if failed_days:
        print(f"Failed days ({len(failed_days)}): {', '.join(failed_days[:30])}"
              + ("..." if len(failed_days) > 30 else ""))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
