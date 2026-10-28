"""Shared Postgres connection for 365DBR db/ tools."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]


def _docker_env() -> dict[str, str]:
    try:
        out = subprocess.check_output(
            ["docker", "inspect", "-f", "{{json .Config.Env}}", "mt-sinai-365dbr-postgres"],
            text=True,
        ).strip()
        env_list = json.loads(out)
        return dict(item.split("=", 1) for item in env_list if "=" in item)
    except Exception:
        return {}


def get_connection():
    """Return a psycopg connection (dict rows) using exact keyword parameters."""
    denv = _docker_env()
    user = denv.get("POSTGRES_USER") or os.getenv("POSTGRES_USER", "365dbr_dev")
    password = denv.get("POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD", "")
    dbname = denv.get("POSTGRES_DB") or os.getenv("POSTGRES_DB", "mt_sinai_365dbr")
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        row_factory=dict_row,
    )
