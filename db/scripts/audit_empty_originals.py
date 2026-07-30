#!/usr/bin/env python3
"""
Audit English BCVs that have LSV/KJV text but zero original_tokens.

Classifies:
  fixable  — alignment exists and tokens live under source_verse_id (wrong key)
  orphan_align — alignment points to source but source also has no tokens
  no_align — no verse_alignments row; pure English-only or missing original day
  self_align — alignment english==source with tokens still empty

Truth/Accuracy audit — does not invent offsets. Run:
  python db/scripts/audit_empty_originals.py
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))
load_dotenv(ROOT / "db" / ".env")

import psycopg
from psycopg.rows import dict_row


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set", file=sys.stderr)
        return 1

    with psycopg.connect(url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT v.id AS verse_id,
                       COUNT(DISTINCT vt.translation_id) AS n_trans,
                       COUNT(ot.id) AS n_tokens
                FROM verses v
                JOIN verse_translations vt ON vt.verse_id = v.id
                LEFT JOIN original_tokens ot ON ot.verse_id = v.id
                GROUP BY v.id
                HAVING COUNT(ot.id) = 0
                ORDER BY v.id
                """
            )
            empty = cur.fetchall()
            print(f"English BCVs with ≥1 translation but tokens=0: {len(empty)}")

            if not empty:
                print("Nothing to classify.")
                return 0

            ids = [r["verse_id"] for r in empty]

            cur.execute(
                """
                SELECT english_verse_id, source_verse_id, source_system, established_by
                FROM verse_alignments
                WHERE english_verse_id = ANY(%s)
                ORDER BY english_verse_id, source_verse_id
                """,
                (ids,),
            )
            aligns = cur.fetchall()
            by_eng: dict[str, list] = defaultdict(list)
            for a in aligns:
                by_eng[a["english_verse_id"]].append(a)

            # Token counts under source ids that appear in alignments
            src_ids = sorted({a["source_verse_id"] for a in aligns})
            src_token_counts: dict[str, int] = {}
            if src_ids:
                cur.execute(
                    """
                    SELECT verse_id, COUNT(*) AS n
                    FROM original_tokens
                    WHERE verse_id = ANY(%s)
                    GROUP BY verse_id
                    """,
                    (src_ids,),
                )
                src_token_counts = {r["verse_id"]: r["n"] for r in cur.fetchall()}

                # Also: tokens that have source_verse_id = eng id (inverse)
                cur.execute(
                    """
                    SELECT source_verse_id, verse_id, COUNT(*) AS n
                    FROM original_tokens
                    WHERE source_verse_id = ANY(%s)
                       OR verse_id = ANY(%s)
                    GROUP BY source_verse_id, verse_id
                    """,
                    (ids, src_ids),
                )
                inv = cur.fetchall()
            else:
                inv = []

            # Tokens whose source_verse_id equals empty english id (should have verse_id=eng)
            cur.execute(
                """
                SELECT source_verse_id, verse_id, COUNT(*) AS n
                FROM original_tokens
                WHERE source_verse_id = ANY(%s)
                GROUP BY source_verse_id, verse_id
                ORDER BY source_verse_id
                """,
                (ids,),
            )
            tokens_by_source_eq_eng = cur.fetchall()

            # Tokens on any source of empty eng verses
            tokens_on_source_of_empty: dict[str, list] = defaultdict(list)
            for a in aligns:
                eng, src = a["english_verse_id"], a["source_verse_id"]
                n = src_token_counts.get(src, 0)
                if n:
                    tokens_on_source_of_empty[eng].append((src, n))

            classes = {
                "fixable_tokens_on_source_bcv": [],
                "orphan_align_no_tokens_either": [],
                "self_align_empty": [],
                "no_align": [],
            }

            for r in empty:
                vid = r["verse_id"]
                als = by_eng.get(vid, [])
                if not als:
                    classes["no_align"].append(vid)
                    continue
                sources = [a["source_verse_id"] for a in als]
                if all(s == vid for s in sources):
                    classes["self_align_empty"].append(vid)
                    continue
                on_src = tokens_on_source_of_empty.get(vid, [])
                if on_src:
                    classes["fixable_tokens_on_source_bcv"].append(
                        {"verse_id": vid, "tokens_on": on_src, "aligns": sources}
                    )
                else:
                    classes["orphan_align_no_tokens_either"].append(
                        {"verse_id": vid, "aligns": sources}
                    )

            print("\n=== CLASSIFICATION ===")
            for k, v in classes.items():
                print(f"\n{k}: {len(v)}")
                for item in v[:25]:
                    print(f"  {item}")
                if len(v) > 25:
                    print(f"  ... +{len(v) - 25} more")

            print("\n=== tokens where source_verse_id ∈ empty-eng set ===")
            print(f"  rows: {len(tokens_by_source_eq_eng)}")
            for r in tokens_by_source_eq_eng[:20]:
                print(
                    f"  source_verse_id={r['source_verse_id']} "
                    f"stored_under_verse_id={r['verse_id']} n={r['n']}"
                )

            # Sample texts for first few of each class
            print("\n=== SAMPLE TEXTS (first 5 empty overall) ===")
            for r in empty[:8]:
                vid = r["verse_id"]
                cur.execute(
                    """
                    SELECT t.code, LEFT(vt.text, 80) AS text
                    FROM verse_translations vt
                    JOIN translations t ON t.id = vt.translation_id
                    WHERE vt.verse_id = %s
                    ORDER BY t.code
                    """,
                    (vid,),
                )
                texts = cur.fetchall()
                als = by_eng.get(vid, [])
                print(f"\n{vid} aligns={[a['source_verse_id'] for a in als]}")
                for t in texts:
                    print(f"  [{t['code']}] {t['text']!r}")

            # Book distribution
            print("\n=== BY BOOK (empty tokens with English) ===")
            by_book: dict[str, int] = defaultdict(int)
            for r in empty:
                book = r["verse_id"].split(".")[0]
                by_book[book] += 1
            for b, n in sorted(by_book.items(), key=lambda x: -x[1]):
                print(f"  {b}: {n}")

            fixable_n = len(classes["fixable_tokens_on_source_bcv"])
            if fixable_n:
                print(
                    f"\nFAIL: {fixable_n} dual-claim empties "
                    f"(likely cross-day source_verse_id wipe — re-populate after clear fix)"
                )
                return 1
            print("\nOK: no dual-claim empty originals (fixable=0)")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
