#!/usr/bin/env python3
"""
365DBR Phase 1: Idempotent books seed script.

Seeds the `books` table using the single source of truth:
    apps/365DBR/bible_common.py  (BIBLE_DATA + BOOK_NAMES)

This guarantees:
- Exact 66 books
- Correct canonical order
- Correct num_chapters per book (from authoritative counts)
- Correct testament assignment
- No drift between code and DB

Run after apply_migrations.py.

Usage:
  cd db
  python scripts/seed_books.py

It is safe to re-run (UPSERT).
"""

import os
import sys
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

# Make bible_common importable when running from db/scripts/
ROOT = Path(__file__).resolve().parents[2]
BIBLE_COMMON_DIR = ROOT / "apps" / "365DBR"
sys.path.insert(0, str(BIBLE_COMMON_DIR))

try:
    import bible_common
except ImportError as e:
    print(f"[ERROR] Could not import bible_common from {BIBLE_COMMON_DIR}")
    print("Make sure you are running from the monorepo root context.")
    raise

# Load .env for convenience
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / "db" / ".env")
except ImportError:
    pass


def get_connection():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        user = os.getenv("POSTGRES_USER", "365dbr_dev")
        pw = os.getenv("POSTGRES_PASSWORD", "dev_password_change_me")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "mt_sinai_365dbr")
        dsn = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
    print(f"[seed_books] Connecting (hiding credentials)...")
    return psycopg.connect(dsn, row_factory=dict_row)


def main():
    print("[seed_books] Using bible_common.BIBLE_DATA as source of truth for 66 books.")
    print(f"[seed_books] Total books defined: {len(bible_common.BIBLE_DATA)}")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            inserted = 0
            updated = 0

            for order, (code, chapter_counts) in enumerate(bible_common.BIBLE_DATA.items(), start=1):
                name = bible_common.BOOK_NAMES.get(code, code)
                testament = "OT" if order <= 39 else "NT"
                num_chapters = len(chapter_counts)

                # is_poetic for known poetic books (per common usage + schema intent)
                is_poetic = code in ("PSA", "PRO", "JOB", "ECC", "SNG", "LAM")

                cur.execute("""
                    INSERT INTO books (code, name, testament, order_canonical, num_chapters, is_poetic)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (code) DO UPDATE SET
                        name = EXCLUDED.name,
                        testament = EXCLUDED.testament,
                        order_canonical = EXCLUDED.order_canonical,
                        num_chapters = EXCLUDED.num_chapters,
                        is_poetic = EXCLUDED.is_poetic
                    RETURNING (xmax = 0) AS inserted;
                """, (code, name, testament, order, num_chapters, is_poetic))

                result = cur.fetchone()
                if result and result.get("inserted"):
                    inserted += 1
                else:
                    updated += 1

            conn.commit()

            # Final verification count
            cur.execute("SELECT COUNT(*) AS total FROM books;")
            total = cur.fetchone()["total"]

            print(f"\n[seed_books] SUCCESS")
            print(f"  Inserted new : {inserted}")
            print(f"  Updated      : {updated}")
            print(f"  Total in DB  : {total}")
            print(f"  Expected     : 66")

            if total != 66:
                print("[FATAL] Book count mismatch after seeding!")
                sys.exit(1)

            # Show a few samples for confidence
            cur.execute("""
                SELECT code, name, testament, order_canonical, num_chapters 
                FROM books 
                WHERE code IN ('GEN', 'PSA', 'MAT', 'REV') 
                ORDER BY order_canonical;
            """)
            print("\n[seed_books] Sample books:")
            for row in cur.fetchall():
                print(f"  {row['code']:4} | {row['name']:20} | {row['testament']} | order={row['order_canonical']:2} | chapters={row['num_chapters']}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
