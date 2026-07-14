#!/usr/bin/env python3
"""
365DBR Phase 2: Populate Postgres from one (or more) day packs.

Source priority (truth-first after GRCTR switch):
  --source local  (default): apps/365DBR/data/MMDD/  — your verified fetch output
  --source prod:             https://mt-sin.ai/365DBR/data/MMDD/
  --source auto:             local if manifest exists, else prod

Usage (from monorepo root or db/):
  python db/scripts/populate_day.py --day 0123
  python db/scripts/populate_day.py --day 0123,0702,0823
  python db/scripts/populate_day.py --day 0123 --source prod

Requires: schema applied + books/translations seeded (Phase 1).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))
sys.path.insert(0, str(ROOT / "db"))

from etl.parse_passage import (  # noqa: E402
    parse_passage_payload,
    parse_range_endpoints,
)
import bible_common  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / "db" / ".env")
except ImportError:
    pass

PRODUCTION_BASE = "https://mt-sin.ai/365DBR/data"
LOCAL_DATA = ROOT / "apps" / "365DBR" / "data"
READINGS_PATH = LOCAL_DATA / "readings.json"
SECTION_NAMES = ("OT", "NT", "PSA", "PRO")


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


def build_verse_order_map() -> dict[str, int]:
    order: dict[str, int] = {}
    n = 0
    for book, chapters in bible_common.BIBLE_DATA.items():
        for ci, vc in enumerate(chapters, start=1):
            for v in range(1, vc + 1):
                n += 1
                order[f"{book}.{ci}.{v}"] = n
    return order


def load_readings() -> dict[str, dict]:
    with open(READINGS_PATH, encoding="utf-8") as f:
        rows = json.load(f)
    return {r["day"]: r for r in rows}


def resolve_source(day: str, source: str) -> str:
    local_manifest = LOCAL_DATA / day / "manifest.json"
    if source == "local":
        if not local_manifest.exists():
            raise FileNotFoundError(
                f"Local manifest missing: {local_manifest}. "
                f"Run fetch_readings.py --day {day} first, or use --source prod."
            )
        return "local"
    if source == "prod":
        return "prod"
    # auto
    return "local" if local_manifest.exists() else "prod"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "365DBR-ETL/phase2"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} for {url}")
        return json.loads(resp.read().decode("utf-8"))


def load_day_files(day: str, source: str) -> tuple[dict, list[tuple[str, dict]], str]:
    """
    Returns (manifest, [(filename, raw_json), ...], provenance_base_url_or_path).
    """
    if source == "local":
        base = LOCAL_DATA / day
        manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
        files = []
        for fname in manifest.get("files", []):
            path = base / fname
            if not path.exists():
                raise FileNotFoundError(f"Missing local file: {path}")
            files.append((fname, json.loads(path.read_text(encoding="utf-8"))))
        return manifest, files, str(base.resolve())

    base_url = f"{PRODUCTION_BASE}/{day}"
    manifest = fetch_json(f"{base_url}/manifest.json")
    files = []
    for fname in manifest.get("files", []):
        files.append((fname, fetch_json(f"{base_url}/{fname}")))
    return manifest, files, base_url


def ensure_verse(cur, verse_id: str, verse_order_map: dict[str, int]):
    parts = verse_id.split(".")
    if len(parts) != 3:
        raise ValueError(f"Bad verse id: {verse_id}")
    book, ch, v = parts[0], int(parts[1]), int(parts[2])
    if book not in bible_common.BIBLE_DATA:
        raise ValueError(f"Unknown book in verse id: {verse_id}")
    vo = verse_order_map.get(verse_id)
    if vo is None:
        # still insert with high order for rare edge cases, but warn
        vo = 90_000_000 + ch * 1000 + v
        print(f"  [warn] verse_order not in BIBLE_DATA map: {verse_id} (using {vo})")
    cur.execute(
        """
        INSERT INTO verses (id, book_code, chapter, verse, verse_order)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            book_code = EXCLUDED.book_code,
            chapter = EXCLUDED.chapter,
            verse = EXCLUDED.verse,
            verse_order = EXCLUDED.verse_order
        """,
        (verse_id, book, ch, v, vo),
    )


def get_translation_ids(cur) -> dict[str, int]:
    cur.execute("SELECT id, code FROM translations")
    return {r["code"]: r["id"] for r in cur.fetchall()}


def populate_one_day(conn, day: str, source: str, verse_order_map: dict[str, int], readings: dict):
    if day not in readings:
        raise ValueError(f"Day {day} not found in readings.json")

    plan = readings[day]
    source = resolve_source(day, source)
    print(f"\n=== Populating day {day} (source={source}) ===")
    manifest, file_payloads, provenance = load_day_files(day, source)
    print(f"  provenance: {provenance}")
    print(f"  files: {len(file_payloads)}")

    ranges = plan["api_format"].split(",")
    if len(ranges) != 4:
        raise ValueError(f"{day}: api_format must have 4 sections, got {len(ranges)}")

    parsed_files = []
    all_verse_ids: set[str] = set()
    for fname, raw in file_payloads:
        # integrity vs filename range (no inject)
        range_str = fname.replace(".json", "")
        try:
            bible_common.validate_api_response(raw, context_info=f"{day}/{fname}")
            bible_common.validate_content_integrity(raw, range_str, inject_missing=False)
        except Exception as e:
            raise RuntimeError(f"Integrity failed for {day}/{fname}: {e}") from e

        p = parse_passage_payload(raw, fname)
        parsed_files.append(p)
        all_verse_ids.update(p["verse_ids"])
        print(
            f"  {fname}: lang={p['language']} verses={len(p['verse_ids'])} "
            f"tokens={len(p['tokens'])} trans={list(p['translations'].keys())} "
            f"bibleId={p['bible_id']}"
        )

    with conn.cursor() as cur:
        trans_ids = get_translation_ids(cur)
        for code in ("LSV", "KJV"):
            if code not in trans_ids:
                raise RuntimeError(f"Translation {code} not seeded — run seed_books + migrations")

        # Verses
        for vid in sorted(all_verse_ids):
            ensure_verse(cur, vid, verse_order_map)

        # Tokens: replace per verse for this day load (delete existing tokens for these verses then insert)
        for vid in all_verse_ids:
            cur.execute("DELETE FROM original_tokens WHERE verse_id = %s", (vid,))

        token_rows = 0
        for p in parsed_files:
            for t in p["tokens"]:
                cur.execute(
                    """
                    INSERT INTO original_tokens
                        (verse_id, word_order, language, surface_text, strong_number, lemma, morph, extra)
                    VALUES (%s, %s, %s, %s, %s, NULL, NULL, '{}'::jsonb)
                    ON CONFLICT (verse_id, word_order) DO UPDATE SET
                        language = EXCLUDED.language,
                        surface_text = EXCLUDED.surface_text,
                        strong_number = EXCLUDED.strong_number
                    """,
                    (
                        t["verse_id"],
                        t["word_order"],
                        t["language"],
                        t["surface_text"],
                        t["strong_number"],
                    ),
                )
                token_rows += 1

        # Translations
        vt_rows = 0
        for p in parsed_files:
            for code, verse_map in p["translations"].items():
                tid = trans_ids[code]
                for vid, text in verse_map.items():
                    if vid not in all_verse_ids:
                        # parallel may include slight neighbor bleed — only store for known day verses
                        continue
                    if not text or not text.strip():
                        continue
                    ensure_verse(cur, vid, verse_order_map)
                    cur.execute(
                        """
                        INSERT INTO verse_translations (verse_id, translation_id, text, source_note)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (verse_id, translation_id) DO UPDATE SET
                            text = EXCLUDED.text,
                            source_note = EXCLUDED.source_note
                        """,
                        (vid, tid, text.strip(), p["source_note"]),
                    )
                    vt_rows += 1

        # Daily reading + passages
        label = manifest.get("label") or plan.get("text_friendly") or day
        total_verses = (
            plan.get("ot_verse_count", 0)
            + plan.get("nt_verse_count", 0)
            + plan.get("ps_verse_count", 0)
            + plan.get("pr_verse_count", 0)
        )
        cur.execute(
            """
            INSERT INTO daily_readings (day, label, reading_time_min, total_verses)
            VALUES (%s, %s, NULL, %s)
            ON CONFLICT (day) DO UPDATE SET
                label = EXCLUDED.label,
                total_verses = EXCLUDED.total_verses
            """,
            (day, label, total_verses),
        )

        # Clear and re-insert passages for day (order: OT, NT, PSA, PRO matches files)
        cur.execute("DELETE FROM daily_passages WHERE day = %s", (day,))
        file_names = [f[0] for f in file_payloads]
        for i, section in enumerate(SECTION_NAMES):
            range_str = ranges[i]
            start_id, end_id = parse_range_endpoints(range_str)
            ensure_verse(cur, start_id, verse_order_map)
            ensure_verse(cur, end_id, verse_order_map)
            file_ref = file_names[i] if i < len(file_names) else None
            vc = {
                "OT": plan.get("ot_verse_count"),
                "NT": plan.get("nt_verse_count"),
                "PSA": plan.get("ps_verse_count"),
                "PRO": plan.get("pr_verse_count"),
            }[section]
            cur.execute(
                """
                INSERT INTO daily_passages
                    (day, section, start_verse_id, end_verse_id, file_ref, verse_count)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (day, section, start_id, end_id, file_ref, vc),
            )

        # Provenance
        for p in parsed_files:
            src = f"{provenance.rstrip('/')}/{p['file_ref']}"
            cur.execute(
                """
                INSERT INTO data_sources (source_url, fetch_date, bible_id_used, notes)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    src,
                    date.today(),
                    p["bible_id"],
                    f"phase2 populate day={day} source={source} lang={p['language']}",
                ),
            )

        conn.commit()
        print(
            f"  OK day {day}: verses={len(all_verse_ids)} tokens={token_rows} "
            f"verse_translations={vt_rows}"
        )
        return {
            "day": day,
            "verses": len(all_verse_ids),
            "tokens": token_rows,
            "verse_translations": vt_rows,
            "source": source,
        }


def main():
    parser = argparse.ArgumentParser(description="Phase 2: populate DB from day pack(s)")
    parser.add_argument(
        "--day",
        help="MMDD or comma-separated list (e.g. 0123 or 0123,0702,0823)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Populate every day in readings.json (365 days)",
    )
    parser.add_argument(
        "--source",
        choices=("auto", "local", "prod"),
        default="auto",
        help="Data source (default: auto = local if present else prod)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Log failures and continue (default: stop on first error)",
    )
    args = parser.parse_args()

    if not args.all and not args.day:
        parser.error("Provide --day MMDD or --all")

    readings = load_readings()
    if args.all:
        days = sorted(readings.keys())
    else:
        days = [d.strip() for d in args.day.split(",") if d.strip()]
        for d in days:
            if not (len(d) == 4 and d.isdigit()):
                print(f"[ERROR] Invalid day: {d}")
                sys.exit(1)

    verse_order_map = build_verse_order_map()
    print(
        f"Loaded readings.json ({len(readings)} days); "
        f"will process {len(days)} day(s); verse_order map size={len(verse_order_map)}"
    )

    conn = get_connection()
    results = []
    failures = []
    try:
        for i, day in enumerate(days, start=1):
            print(f"\n----- [{i}/{len(days)}] -----")
            try:
                results.append(
                    populate_one_day(conn, day, args.source, verse_order_map, readings)
                )
            except Exception as e:
                failures.append((day, str(e)))
                print(f"  [ERROR] day {day}: {e}")
                # Rollback any partial work on this day
                try:
                    conn.rollback()
                except Exception:
                    pass
                if not args.continue_on_error:
                    raise
    finally:
        conn.close()

    print("\n=== Phase 2 populate summary ===")
    total_v = sum(r["verses"] for r in results)
    total_t = sum(r["tokens"] for r in results)
    total_vt = sum(r["verse_translations"] for r in results)
    print(f"  days OK:     {len(results)}")
    print(f"  days failed: {len(failures)}")
    print(f"  verses:      {total_v}")
    print(f"  tokens:      {total_t}")
    print(f"  translations:{total_vt}")
    if failures:
        print("  failures:")
        for day, err in failures[:20]:
            print(f"    {day}: {err}")
        if len(failures) > 20:
            print(f"    ... and {len(failures) - 20} more")
    if args.all:
        print("Done. Spot-check: python db/scripts/verify_population.py --day \"0101,0702,1225\"")
        print("Or full verify:     python db/scripts/verify_population.py --all --source local")
    else:
        print("Done. Run: python db/scripts/verify_population.py --day " + ",".join(days))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
