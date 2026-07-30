#!/usr/bin/env python3
"""
Phase 5 minimal: seed curated speaker/theme annotations (idempotent).

Reads db/seeds/phase5_curated_annotations.json and replaces only rows whose
`source` equals the file's source_tag. Does not touch superscription/title
rows from ETL or other curated sources.

Usage (monorepo root):
  python db/scripts/seed_annotations.py
  python db/scripts/seed_annotations.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))

from query import get_connection  # noqa: E402

SEED_PATH = ROOT / "db" / "seeds" / "phase5_curated_annotations.json"


def _norm_bcv(vid: str) -> str:
    parts = (vid or "").strip().split(".")
    if len(parts) < 3:
        raise ValueError(f"invalid BCV: {vid!r}")
    return f"{parts[0].upper()}.{parts[1]}.{parts[2]}"


def load_seed(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("source_tag"):
        raise ValueError("seed file missing source_tag")
    if not data.get("annotations"):
        raise ValueError("seed file has no annotations")
    return data


def validate_verses(conn, annos: list[dict]) -> list[str]:
    missing: list[str] = []
    ids = set()
    for a in annos:
        ids.add(_norm_bcv(a["start_verse_id"]))
        ids.add(_norm_bcv(a["end_verse_id"]))
    with conn.cursor() as cur:
        for vid in sorted(ids):
            cur.execute("SELECT 1 FROM verses WHERE id = %s", (vid,))
            if not cur.fetchone():
                missing.append(vid)
    return missing


def seed(conn, data: dict, *, dry_run: bool = False) -> dict:
    source_tag = data["source_tag"]
    annos = data["annotations"]
    missing = validate_verses(conn, annos)
    if missing:
        raise RuntimeError(
            "missing verses (populate DB first): " + ", ".join(missing[:20])
        )

    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) AS c FROM annotations WHERE source = %s",
            (source_tag,),
        )
        before = cur.fetchone()["c"]

        if dry_run:
            return {
                "dry_run": True,
                "source_tag": source_tag,
                "would_delete": before,
                "would_insert": len(annos),
            }

        cur.execute("DELETE FROM annotations WHERE source = %s", (source_tag,))
        deleted = cur.rowcount

        for a in annos:
            start = _norm_bcv(a["start_verse_id"])
            end = _norm_bcv(a["end_verse_id"])
            # Prefer verse_order range check over lexical BCV compare
            cur.execute(
                """
                SELECT
                  (SELECT verse_order FROM verses WHERE id = %s) AS so,
                  (SELECT verse_order FROM verses WHERE id = %s) AS eo
                """,
                (start, end),
            )
            row = cur.fetchone()
            if row["so"] is None or row["eo"] is None:
                raise RuntimeError(f"verse order missing for {start}..{end}")
            if row["so"] > row["eo"]:
                raise RuntimeError(
                    f"start after end by verse_order: {start} ({row['so']}) "
                    f"> {end} ({row['eo']})"
                )

            meta = a.get("metadata") or {}
            cur.execute(
                """
                INSERT INTO annotations
                    (annotation_type, start_verse_id, end_verse_id,
                     value, metadata, source)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    a["annotation_type"],
                    start,
                    end,
                    a["value"],
                    json.dumps(meta, ensure_ascii=False),
                    source_tag,
                ),
            )

        conn.commit()
        cur.execute(
            "SELECT count(*) AS c FROM annotations WHERE source = %s",
            (source_tag,),
        )
        after = cur.fetchone()["c"]

    return {
        "dry_run": False,
        "source_tag": source_tag,
        "deleted": deleted,
        "inserted": after,
        "types": _type_counts(conn, source_tag),
    }


def _type_counts(conn, source_tag: str) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT annotation_type, count(*) AS c
            FROM annotations
            WHERE source = %s
            GROUP BY annotation_type
            ORDER BY annotation_type
            """,
            (source_tag,),
        )
        return {r["annotation_type"]: r["c"] for r in cur.fetchall()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5: seed curated speaker/theme annotations"
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=SEED_PATH,
        help="Path to curated JSON seed file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report without writing",
    )
    args = parser.parse_args()

    if not args.seed.exists():
        print(f"ERROR: seed file not found: {args.seed}", file=sys.stderr)
        return 1

    data = load_seed(args.seed)
    print(f"[seed_annotations] file={args.seed}")
    print(f"[seed_annotations] version={data.get('version')} tag={data['source_tag']}")
    print(f"[seed_annotations] rows={len(data['annotations'])}")

    conn = get_connection()
    try:
        result = seed(conn, data, dry_run=args.dry_run)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("dry_run"):
        print("[seed_annotations] dry-run OK (no write)")
    else:
        print(
            f"[seed_annotations] OK deleted={result['deleted']} "
            f"inserted={result['inserted']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
