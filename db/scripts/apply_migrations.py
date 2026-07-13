#!/usr/bin/env python3
"""
365DBR Phase 1: Simple, auditable migration applier.

- Applies numbered .sql files from ../migrations/ in lexical order.
- Uses a schema_migrations table for idempotency.
- Prefers DATABASE_URL env var; falls back to components or .env.
- Designed for truth/accuracy first: explicit logging, fails hard on error.
- Plain SQL for maximum reviewability.

Usage (PowerShell or bash, after DB is running):
  cd db
  pip install -r requirements.txt
  python scripts/apply_migrations.py
  python scripts/apply_migrations.py --status

  # To start completely fresh (with Docker):
  #   docker compose down -v
  #   docker compose up -d
  #   python scripts/apply_migrations.py

See db/README.md for full setup.
"""

import os
import sys
from pathlib import Path
import psycopg
from psycopg.rows import dict_row

# Load .env if present (optional convenience)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "db" / "migrations"


def get_connection():
    """Return a psycopg connection. Prefers DATABASE_URL."""
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        # Fallback components (from .env or defaults)
        user = os.getenv("POSTGRES_USER", "365dbr_dev")
        pw = os.getenv("POSTGRES_PASSWORD", "dev_password_change_me")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "mt_sinai_365dbr")
        dsn = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
    print(f"[apply] Connecting to: {dsn.split('@')[-1] if '@' in dsn else dsn}")  # hide password
    return psycopg.connect(dsn, row_factory=dict_row)


def ensure_schema_migrations_table(conn):
    """Idempotent creation (also created by the first migration)."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT now()
            );
        """)
    conn.commit()


def get_applied_versions(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version;")
        return {row["version"] for row in cur.fetchall()}


def apply_file(conn, sql_path: Path):
    version = sql_path.stem  # e.g. "001_initial_schema"
    print(f"[apply] Applying {sql_path.name} (version={version}) ...")

    sql = sql_path.read_text(encoding="utf-8")

    with conn.cursor() as cur:
        # Execute the whole file as one script (migrations are atomic units)
        try:
            cur.execute(sql)
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Failed applying {sql_path.name}: {e}")
            raise

    # The migration itself should have inserted into schema_migrations.
    # Double-check / ensure record exists.
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING;",
            (version,)
        )
    conn.commit()
    print(f"[apply] SUCCESS: {sql_path.name}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply 365DBR database migrations (plain SQL).")
    parser.add_argument("--status", action="store_true", help="Show applied migrations and exit.")
    parser.add_argument("--list", action="store_true", help="List available migration files.")
    args = parser.parse_args()

    if not MIGRATIONS_DIR.exists():
        print(f"[ERROR] Migrations directory not found: {MIGRATIONS_DIR}")
        sys.exit(1)

    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if args.list:
        for f in sql_files:
            print(f.name)
        return

    conn = get_connection()
    try:
        ensure_schema_migrations_table(conn)
        applied = get_applied_versions(conn)

        if args.status:
            print("\n[status] Applied migrations:")
            for v in sorted(applied):
                print(f"  ✓ {v}")
            print(f"\n  Total files on disk: {len(sql_files)}")
            return

        print(f"\n[apply] Found {len(sql_files)} migration file(s).")
        print(f"[apply] Already applied: {sorted(applied)}\n")

        for sql_file in sql_files:
            version = sql_file.stem
            if version in applied:
                print(f"[apply] SKIP (already applied): {sql_file.name}")
                continue
            apply_file(conn, sql_file)

        final_applied = get_applied_versions(conn)
        print("\n[apply] All done. Current applied set:")
        for v in sorted(final_applied):
            print(f"  ✓ {v}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
