#!/usr/bin/env python3
"""Re-apply canonical verse_order from bible_common.BIBLE_DATA."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))

import bible_common  # noqa: E402
from query import get_connection  # noqa: E402


def build_order() -> dict[str, int]:
    order: dict[str, int] = {}
    n = 0
    for book, chapters in bible_common.BIBLE_DATA.items():
        for ci, vc in enumerate(chapters, start=1):
            for v in range(1, vc + 1):
                n += 1
                order[f"{book}.{ci}.{v}"] = n
    return order


def main() -> int:
    order = build_order()
    conn = get_connection()
    fixed = 0
    try:
        with conn.cursor() as cur:
            for vid, vo in order.items():
                cur.execute(
                    """
                    UPDATE verses
                    SET verse_order = %s
                    WHERE id = %s AND verse_order IS DISTINCT FROM %s
                    """,
                    (vo, vid, vo),
                )
                fixed += cur.rowcount
        conn.commit()
        print(f"repaired verse_order rows: {fixed} (canonical map size {len(order)})")
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, verse_order FROM verses
                WHERE id = ANY(%s)
                ORDER BY id
                """,
                (["REV.21.27", "REV.22.1", "REV.22.2", "MAL.3.24", "MAL.4.1"],),
            )
            print("spot:", cur.fetchall())
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
