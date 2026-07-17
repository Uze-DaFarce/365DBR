"""Shared Postgres connection for 365DBR db/ tools."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / "db" / ".env")
except ImportError:
    pass


def get_connection():
    """Return a psycopg connection (dict rows). Prefers DATABASE_URL."""
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        user = os.getenv("POSTGRES_USER", "365dbr_dev")
        pw = os.getenv("POSTGRES_PASSWORD", "dev_password_change_me")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "mt_sinai_365dbr")
        dsn = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
    return psycopg.connect(dsn, row_factory=dict_row)
