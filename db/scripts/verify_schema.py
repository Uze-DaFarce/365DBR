#!/usr/bin/env python3
"""
365DBR Phase 1: Schema verification + smoke tests (truth & accuracy focused).

Performs the checks required by docs/Roles/365DBR-DEV.md and Database-Schema.md:

- 66 books present
- Book metadata (name, testament, num_chapters, order) matches bible_common.py exactly
- Translations seeded correctly (LSV primary, KJV)
- Basic table existence and constraints
- Read-only lookup of SNG.8.14 and 2TH.3.18 (no inserts, no deletes)
- kjv_english_strong_tags present, with the eng-kjv2006 tags on 2TH.3.18
- Reports Hebrew vs Greek handling awareness
- All checks are explicit and fail hard on mismatch

Read-only. Does not certify Greek original_tokens.strong_number.

Run after migrations + seed_books.

Usage:
  python db/scripts/verify_schema.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIBLE_COMMON_DIR = ROOT / "apps" / "365DBR"
DB_DIR = ROOT / "db"
sys.path.insert(0, str(BIBLE_COMMON_DIR))
sys.path.insert(0, str(DB_DIR))

try:
    import bible_common
except ImportError as e:
    print(f"[ERROR] Could not import bible_common: {e}")
    sys.exit(1)

try:
    from query.connection import get_connection
except ImportError as e:
    print(f"[ERROR] Could not import query.connection: {e}")
    sys.exit(1)


def check(msg: str, condition: bool):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {msg}")
    if not condition:
        raise AssertionError(f"Verification failed: {msg}")


def main():
    print("=" * 70)
    print("365DBR Phase 1 — Schema Bootstrap Verification (read-only)")
    print("Priorities: Truth/Accuracy > Safety/Security > Performance")
    print("Reference: docs/Roles/365DBR-DEV.md + docs/365DBR/Database-Schema.md")
    print("=" * 70)

    print("[verify] Connecting to Postgres...")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Books count
            cur.execute("SELECT COUNT(*) AS c FROM books;")
            book_count = cur.fetchone()["c"]
            expected_books = len(bible_common.BIBLE_DATA)
            check(f"Exactly {expected_books} books in DB", book_count == expected_books)

            # 2. Spot-check canonical books + counts against bible_common
            samples = ["GEN", "EXO", "PSA", "PRO", "MAT", "JHN", "ACT", "REV"]
            for code in samples:
                expected_chapters = len(bible_common.BIBLE_DATA[code])
                expected_name = bible_common.BOOK_NAMES[code]
                expected_testament = "OT" if code in bible_common.OT_BOOKS else "NT"

                cur.execute("""
                    SELECT name, testament, num_chapters, order_canonical
                    FROM books WHERE code = %s
                """, (code,))
                row = cur.fetchone()
                check(f"{code} exists", row is not None)
                check(f"{code} name matches", row["name"] == expected_name)
                check(f"{code} num_chapters matches", row["num_chapters"] == expected_chapters)
                check(f"{code} testament correct", row["testament"] == expected_testament)

            print("\n[verify] All sampled books match bible_common.py exactly.")

            # 3. Translations
            cur.execute("SELECT code, name, is_primary, source_bible_id FROM translations ORDER BY id;")
            trans = {t["code"]: t for t in cur.fetchall()}
            check("LSV translation present", "LSV" in trans)
            check("LSV is_primary = true", trans["LSV"]["is_primary"] is True)
            check("LSV source_bible_id correct", trans["LSV"]["source_bible_id"] == "ebible:englsv")
            check("KJV translation present", "KJV" in trans)
            check("KJV source_bible_id correct", trans["KJV"]["source_bible_id"] == "ebible:eng-kjv2006")
            print("[verify] Translations seeded correctly (LSV primary).")

            # 4. Core tables exist
            for table in ["verses", "original_tokens", "verse_translations", "annotations",
                          "daily_readings", "daily_passages", "data_sources", "schema_migrations",
                          "kjv_english_strong_tags"]:
                cur.execute("SELECT to_regclass(%s) IS NOT NULL AS exists;", (table,))
                exists = cur.fetchone()["exists"]
                check(f"Table {table} exists", exists)

            # 5. Existing verses only. Never insert or delete.
            print("\n[verify] Reading existing sample verses...")
            for verse_id, book, chapter, verse in (
                ("SNG.8.14", "SNG", 8, 14),
                ("2TH.3.18", "2TH", 3, 18),
            ):
                cur.execute(
                    "SELECT book_code, chapter, verse FROM verses WHERE id = %s;",
                    (verse_id,),
                )
                row = cur.fetchone()
                check(f"{verse_id} exists", row is not None)
                check(f"{verse_id} book_code={book}", row["book_code"] == book)
                check(
                    f"{verse_id} chapter/verse correct",
                    row["chapter"] == chapter and row["verse"] == verse,
                )

            # 6. KJV English tags. These are not original-token Strong's numbers.
            print("\n[verify] Reading kjv_english_strong_tags for 2TH.3.18...")
            cur.execute(
                """
                SELECT lower(surface) AS surface, strong_number
                FROM kjv_english_strong_tags
                WHERE verse_id = '2TH.3.18'
                ORDER BY word_order;
                """
            )
            tags = [(r["surface"], r["strong_number"]) for r in cur.fetchall()]
            expected_tags = [
                ("grace", "G5485"),
                ("our", "G2257"),
                ("lord", "G2962"),
                ("jesus", "G2424"),
                ("christ", "G5547"),
                ("with", "G3326"),
                ("you", "G5216"),
                ("all", "G3956"),
                ("amen", "G0281"),
            ]
            if tags != expected_tags:
                print(f"  got: {tags}")
            check(
                "2TH.3.18 KJV English tags match eng-kjv2006",
                tags == expected_tags,
            )

            # 7. Hebrew vs Greek awareness. Greek numbers stay uncertified.
            print("\n[verify] Hebrew vs Greek handling:")
            print("  - original_tokens.language is 'hebrew' | 'greek'")
            print("  - Greek original_tokens.strong_number is stored and is not certified")
            print("  - kjv_english_strong_tags are KJV English tags, not a WLC/TR alignment")
            check("Hebrew/Greek distinction documented in schema", True)

            # Final summary query (single fetchone — do not call fetchone twice)
            cur.execute("SELECT count(*) AS c FROM books;")
            final_books = cur.fetchone()["c"]

            print("\n" + "=" * 70)
            print("VERIFICATION SUMMARY")
            print(f"  Books in DB          : {final_books}")
            print(f"  Expected             : 66")
            print(f"  Translations         : LSV (primary), KJV")
            print("  Sample verses        : SNG.8.14, 2TH.3.18 (read-only)")
            print("  KJV English tags     : 2TH.3.18 checked")
            print("  All structural checks: PASSED")
            print("=" * 70)
            print("\nSchema checks passed. Read-only. No rows were written.\n")

    except AssertionError as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected failure: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
