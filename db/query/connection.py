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


def _file_env() -> dict[str, str]:
    path = ROOT / "db" / ".env"
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_connection():
    """Return a psycopg connection (dict rows) using exact keyword parameters.

    db/.env is the live role password. The container env can still hold the
    password from when the container was created, and that one is rejected.
    DATABASE_URL is ignored because the password contains @.
    """
    file_env = _file_env()
    denv = _docker_env()
    user = file_env.get("POSTGRES_USER") or denv.get("POSTGRES_USER") or os.getenv("POSTGRES_USER", "365dbr_dev")
    password = file_env.get("POSTGRES_PASSWORD") or denv.get("POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD", "")
    dbname = file_env.get("POSTGRES_DB") or denv.get("POSTGRES_DB") or os.getenv("POSTGRES_DB", "mt_sinai_365dbr")
    host = file_env.get("POSTGRES_HOST") or os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = int(file_env.get("POSTGRES_PORT") or os.getenv("POSTGRES_PORT", "5432"))
    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        row_factory=dict_row,
    )
