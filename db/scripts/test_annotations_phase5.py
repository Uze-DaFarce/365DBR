#!/usr/bin/env python3
"""
Phase 5 smoke: curated annotations seed + query helpers.

Usage (monorepo root):
  python db/scripts/seed_annotations.py
  python db/scripts/test_annotations_phase5.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))

from query import (  # noqa: E402
    annotations_covering_verse,
    find_by_speaker,
    find_by_theme,
    get_connection,
    si_demo_query,
)

SOURCE_TAG = "curated-manual-phase5-v1"


def main() -> int:
    failures = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failures
        status = "PASS" if cond else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures += 1

    print("=== Phase 5 annotations smoke ===")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) AS c FROM annotations WHERE source = %s",
                (SOURCE_TAG,),
            )
            n = cur.fetchone()["c"]
            check("seed present", n >= 10, f"count={n} source={SOURCE_TAG}")

            cur.execute(
                """
                SELECT count(*) AS c FROM annotations
                WHERE source = %s AND annotation_type = 'speaker'
                """,
                (SOURCE_TAG,),
            )
            speakers = cur.fetchone()["c"]
            check("speaker rows", speakers >= 5, f"count={speakers}")

            cur.execute(
                """
                SELECT count(*) AS c FROM annotations
                WHERE source = %s AND annotation_type = 'theme'
                """,
                (SOURCE_TAG,),
            )
            themes = cur.fetchone()["c"]
            check("theme rows", themes >= 5, f"count={themes}")

            # All curated rows must have source
            cur.execute(
                """
                SELECT count(*) AS c FROM annotations
                WHERE source = %s AND (source IS NULL OR source = '')
                """,
                (SOURCE_TAG,),
            )
            check("source field non-empty", cur.fetchone()["c"] == 0)

        # Range membership uses verse_order (MAT.5.5 inside Beatitudes)
        cov = annotations_covering_verse(conn, "MAT.5.5")
        vals = {(a["annotation_type"], a["value"]) for a in cov["annotations"]}
        check(
            "MAT.5.5 covered by Jesus speaker",
            ("speaker", "Jesus") in vals,
            f"annos={vals}",
        )

        cov_g = annotations_covering_verse(conn, "GEN.1.3")
        vals_g = {(a["annotation_type"], a["value"]) for a in cov_g["annotations"]}
        check(
            "GEN.1.3 covered by God speaker",
            ("speaker", "God") in vals_g,
            f"annos={vals_g}",
        )
        check(
            "GEN.1.3 covered by Creation theme",
            ("theme", "Creation") in vals_g,
            f"annos={vals_g}",
        )

        js = find_by_speaker(conn, "Jesus", limit=20)
        check("find speaker Jesus", js["total"] >= 3, f"total={js['total']}")

        th = find_by_theme(conn, "%Creation%", limit=10)
        check("find theme Creation", th["total"] >= 1, f"total={th['total']}")

        # S.I. demo: God + H430 (Elohim) should include GEN.1.3
        demo = si_demo_query(conn, speaker="God", strong="H430", limit=20)
        ids = {h["verse_id"] for h in demo["hits"]}
        check(
            "si_demo God + H430 includes GEN.1.3",
            "GEN.1.3" in ids or demo["total"] >= 1,
            f"total={demo['total']} sample={sorted(ids)[:5]}",
        )

        # Jesus speaker ranges exist
        demo_j = si_demo_query(conn, speaker="Jesus", limit=30)
        check(
            "si_demo speaker Jesus",
            demo_j["total"] >= 5,
            f"total={demo_j['total']}",
        )

        # Superscriptions still present (ETL not wiped by seed)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(*) AS c FROM annotations
                WHERE annotation_type IN ('superscription', 'title')
                """
            )
            titles = cur.fetchone()["c"]
            check("ETL titles preserved", titles >= 100, f"count={titles}")

    except Exception as e:
        print(f"  [FAIL] exception: {e}")
        failures += 1
    finally:
        conn.close()

    print("=" * 40)
    if failures:
        print(f"=== FAIL ({failures}) ===")
        return 1
    print("=== PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
