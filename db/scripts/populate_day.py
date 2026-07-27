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


def ensure_verse(
    cur,
    verse_id: str,
    verse_order_map: dict[str, int],
    *,
    order_hint: int | None = None,
    quiet: bool = False,
):
    """
    Upsert a verses row. English-primary BCVs may not exist in Hebrew-oriented
    BIBLE_DATA (e.g. GEN.31.55 English vs GEN.31 max 54 in WLC inventory).
    Those are still valid display keys — insert with order_hint or synthetic order.
    """
    parts = verse_id.split(".")
    if len(parts) != 3:
        raise ValueError(f"Bad verse id: {verse_id}")
    book, ch, v = parts[0], int(parts[1]), int(parts[2])
    if book not in bible_common.BIBLE_DATA:
        raise ValueError(f"Unknown book in verse id: {verse_id}")
    vo = verse_order_map.get(verse_id)
    if vo is None and order_hint is not None:
        vo = order_hint
    if vo is None:
        # English-only / Protestant BCV not in BIBLE_DATA — keep near chapter
        # using a synthetic order that sorts after known verses in that chapter.
        base = None
        for prev in range(v - 1, 0, -1):
            base = verse_order_map.get(f"{book}.{ch}.{prev}")
            if base is not None:
                break
        if base is None:
            for nxt in range(v + 1, v + 50):
                base = verse_order_map.get(f"{book}.{ch}.{nxt}")
                if base is not None:
                    base = base - 1
                    break
        if base is not None:
            vo = base  # same continuum slot as neighbor; unique id still differs
        else:
            vo = 90_000_000 + bible_common.ALL_BOOKS.index(book) * 100_000 + ch * 200 + v
        if not quiet:
            print(
                f"  [info] English/display BCV not in BIBLE_DATA inventory: {verse_id} "
                f"(verse_order={vo}; Hebrew/org counts differ — expected for English-primary)"
            )
    # Never overwrite verse_order on conflict for existing BIBLE_DATA rows —
    # clobbering caused REV.22.1 and REV.21.27 to share order and broke ranges.
    cur.execute(
        """
        INSERT INTO verses (id, book_code, chapter, verse, verse_order)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            book_code = EXCLUDED.book_code,
            chapter = EXCLUDED.chapter,
            verse = EXCLUDED.verse
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
    all_verse_ids: set[str] = set()  # English-primary display ids
    all_source_ids: set[str] = set()  # org/source ids from original content
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
        all_source_ids.update(p.get("source_verse_ids") or [])
        n_align = len(p.get("alignments") or [])
        n_titles = len(p.get("titles") or [])
        print(
            f"  {fname}: lang={p['language']} display_verses={len(p['verse_ids'])} "
            f"source_verses={len(p.get('source_verse_ids') or [])} "
            f"tokens={len(p['tokens'])} trans={list(p['translations'].keys())} "
            f"alignments={n_align} titles={n_titles} bibleId={p['bible_id']}"
        )
        if p.get("org_to_english"):
            # compact sample of map for audit
            sample = list(p["org_to_english"].items())[:3]
            print(f"    org→english sample: {sample} (via {p.get('alignment_established_by')})")

    with conn.cursor() as cur:
        trans_ids = get_translation_ids(cur)
        for code in ("LSV", "KJV"):
            if code not in trans_ids:
                raise RuntimeError(f"Translation {code} not seeded — run seed_books + migrations")

        # Build order hints: English display id → source org verse_order when mapped
        order_hints: dict[str, int] = {}
        for p in parsed_files:
            for a in p.get("alignments") or []:
                eng, src = a["english_verse_id"], a["source_verse_id"]
                svo = verse_order_map.get(src)
                if svo is not None:
                    order_hints[eng] = svo

        # Verses: ALWAYS ensure English-primary + source ids (not only BIBLE_DATA keys).
        # Skipping non-map ids caused FK failures on GEN.31.55, EXO.8.29, etc.
        extra_english = 0
        for vid in sorted(all_verse_ids | all_source_ids):
            was_extra = vid not in verse_order_map
            ensure_verse(
                cur,
                vid,
                verse_order_map,
                order_hint=order_hints.get(vid),
                quiet=not was_extra,
            )
            if was_extra and vid in all_verse_ids:
                extra_english += 1
        if extra_english:
            print(
                f"  [info] ensured {extra_english} English/display BCV(s) "
                f"outside BIBLE_DATA inventory (Protestant vs Hebrew counts)"
            )

        # Clear tokens for both display and prior source keys (re-run safe)
        clear_ids = all_verse_ids | all_source_ids
        for vid in clear_ids:
            cur.execute("DELETE FROM original_tokens WHERE verse_id = %s", (vid,))
            cur.execute(
                "DELETE FROM original_tokens WHERE source_verse_id = %s",
                (vid,),
            )

        token_rows = 0
        for p in parsed_files:
            for t in p["tokens"]:
                src = t.get("source_verse_id") or t["verse_id"]
                # Defensive: token display id must exist in verses
                ensure_verse(
                    cur,
                    t["verse_id"],
                    verse_order_map,
                    order_hint=order_hints.get(t["verse_id"]) or verse_order_map.get(src),
                    quiet=True,
                )
                cur.execute(
                    """
                    INSERT INTO original_tokens
                        (verse_id, word_order, language, surface_text, strong_number,
                         lemma, morph, extra, source_verse_id)
                    VALUES (%s, %s, %s, %s, %s, NULL, NULL, '{}'::jsonb, %s)
                    ON CONFLICT (verse_id, word_order) DO UPDATE SET
                        language = EXCLUDED.language,
                        surface_text = EXCLUDED.surface_text,
                        strong_number = EXCLUDED.strong_number,
                        source_verse_id = EXCLUDED.source_verse_id
                    """,
                    (
                        t["verse_id"],
                        t["word_order"],
                        t["language"],
                        t["surface_text"],
                        t["strong_number"],
                        src,
                    ),
                )
                token_rows += 1

        # Translations — English verseId is storage key (modern numbering)
        vt_rows = 0
        for p in parsed_files:
            for code, verse_map in p["translations"].items():
                tid = trans_ids[code]
                for vid, text in verse_map.items():
                    if not text or not text.strip():
                        continue
                    ensure_verse(
                        cur,
                        vid,
                        verse_order_map,
                        order_hint=order_hints.get(vid),
                        quiet=True,
                    )
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

        # Alignments from api.bible verseOrgIds
        align_rows = 0
        for p in parsed_files:
            for a in p.get("alignments") or []:
                eng, src = a["english_verse_id"], a["source_verse_id"]
                ensure_verse(
                    cur,
                    eng,
                    verse_order_map,
                    order_hint=order_hints.get(eng) or verse_order_map.get(src),
                    quiet=True,
                )
                cur.execute(
                    """
                    INSERT INTO verse_alignments
                        (english_verse_id, source_verse_id, source_system, established_by, note)
                    VALUES (%s, %s, 'api.bible-org', %s, %s)
                    ON CONFLICT (english_verse_id, source_verse_id, source_system) DO UPDATE SET
                        established_by = EXCLUDED.established_by,
                        note = EXCLUDED.note
                    """,
                    (
                        eng,
                        src,
                        a.get("established_by") or None,
                        f"from {p['file_ref']}",
                    ),
                )
                align_rows += 1
        if align_rows:
            print(f"  [info] verse_alignments upserted: {align_rows}")

        # Titles / superscriptions → annotations (not fused into verse body by us)
        title_rows = 0
        for p in parsed_files:
            for t in p.get("titles") or []:
                text = (t.get("text") or "").strip()
                if not text:
                    continue
                # Anchor to first display verse of this file if available
                anchor = (p["verse_ids"][0] if p.get("verse_ids") else None)
                if not anchor or anchor not in verse_order_map:
                    continue
                ensure_verse(cur, anchor, verse_order_map)
                # Idempotent-ish: delete same type/value/range for re-run
                cur.execute(
                    """
                    DELETE FROM annotations
                    WHERE annotation_type = %s
                      AND start_verse_id = %s AND end_verse_id = %s
                      AND value = %s
                    """,
                    (t.get("annotation_type") or "title", anchor, anchor, text),
                )
                cur.execute(
                    """
                    INSERT INTO annotations
                        (annotation_type, start_verse_id, end_verse_id, value, metadata, source)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                    """,
                    (
                        t.get("annotation_type") or "title",
                        anchor,
                        anchor,
                        text,
                        json.dumps({
                            "style": t.get("style"),
                            "from_parallel": t.get("source"),
                            "file_ref": p["file_ref"],
                        }),
                        f"api.bible-title:{t.get('source') or 'original'}",
                    ),
                )
                title_rows += 1
        if title_rows:
            print(f"  [info] title/superscription annotations: {title_rows}")

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
