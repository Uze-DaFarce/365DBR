#!/usr/bin/env python3
"""Print one Tier 1 loop. Read-only. Does not query tiers 2–4.

Usage, from the monorepo root:
  python db/scripts/tier1_ask.py Μάρκος
  python db/scripts/tier1_ask.py Μάρκος absent
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))

from query.connection import get_connection  # noqa: E402
from query.tier1 import ask_tier1, format_tier1  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("pass the Hebrew or Greek word")
    word = sys.argv[1]
    claim = sys.argv[2] if len(sys.argv) > 2 else None
    conn = get_connection()
    try:
        report = ask_tier1(conn, word, claim=claim)
    finally:
        conn.close()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(format_tier1(report))


if __name__ == "__main__":
    main()
