#!/usr/bin/env python3
"""
Psalm audit: titles/superscriptions, English↔org alignment, empty originals.

Usage (monorepo root; Docker up):
  python db/scripts/audit_psalms.py
  python db/scripts/audit_psalms.py --json db/_psalm_audit.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))

from bible_common import BIBLE_DATA  # noqa: E402
from query import get_connection  # noqa: E402

TITLE_PAT = re.compile(
    r"(Psalm|Song|Prayer|Michtam|Maschil|Maskil|Miktam|Shiggaion|chief Musician|Overseer)",
    re.I,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Psalm titles/alignment/empties")
    parser.add_argument("--json", type=Path, default=None, help="Write full report JSON")
    args = parser.parse_args()

    conn = get_connection()
    cur = conn.cursor()
    report: dict = {
        "empties": [],
        "suspicious_title_anchors": [],
        "fused_lsv_v1": [],
        "chapter_anomalies": [],
    }

    # English with no tokens
    cur.execute(
        """
        SELECT DISTINCT vt.verse_id
        FROM verse_translations vt
        JOIN verses v ON v.id = vt.verse_id
        WHERE v.book_code = 'PSA'
          AND NOT EXISTS (
            SELECT 1 FROM original_tokens ot WHERE ot.verse_id = vt.verse_id
          )
        ORDER BY vt.verse_id
        """
    )
    for r in cur.fetchall():
        vid = r["verse_id"]
        cur.execute(
            "SELECT source_verse_id FROM verse_alignments WHERE english_verse_id = %s",
            (vid,),
        )
        aligns = [x["source_verse_id"] for x in cur.fetchall()]
        cur.execute(
            "SELECT english_verse_id FROM verse_alignments WHERE source_verse_id = %s",
            (vid,),
        )
        claimed = [x["english_verse_id"] for x in cur.fetchall()]
        report["empties"].append(
            {"verse_id": vid, "aligns": aligns, "org_claimed_by": claimed}
        )

    # Titles not on *.1 (except acrostic letters / intentional mid-psalm headings)
    cur.execute(
        """
        SELECT annotation_type, start_verse_id, left(value, 100) AS value, source
        FROM annotations
        WHERE annotation_type IN ('superscription', 'title')
          AND start_verse_id LIKE 'PSA.%'
          AND start_verse_id !~ '^PSA\\.[0-9]+\\.1$'
        ORDER BY start_verse_id
        """
    )
    for t in cur.fetchall():
        val = t["value"] or ""
        # Acrostic letters like "א ALEPH." are OK mid-119
        if re.match(r"^[\u0590-\u05FFA-Za-z]\s+[A-Z]+\.?$", val.strip()):
            continue
        if TITLE_PAT.search(val):
            report["suspicious_title_anchors"].append(dict(t))

    # Fused LSV v.1 (edition body includes title — documented, not auto-stripped)
    cur.execute(
        """
        SELECT v.id, left(vt.text, 120) AS lsv
        FROM verses v
        JOIN verse_translations vt ON vt.verse_id = v.id
        JOIN translations t ON t.id = vt.translation_id AND t.code = 'LSV'
        WHERE v.book_code = 'PSA' AND v.verse = 1
        ORDER BY v.chapter
        """
    )
    for r in cur.fetchall():
        text = r["lsv"] or ""
        low = text.lower()
        if TITLE_PAT.search(text) and (
            low.startswith("a psalm")
            or low.startswith("to the")
            or "michtam" in low
            or "maschil" in low
            or "maskil" in low
            or low.startswith("a song")
            or low.startswith("a prayer")
        ):
            report["fused_lsv_v1"].append({"verse_id": r["id"], "lsv": text})

    psa_counts = BIBLE_DATA.get("PSA") or []
    for ch, expected in enumerate(psa_counts, start=1):
        cur.execute(
            "SELECT count(*) AS c FROM verses WHERE book_code='PSA' AND chapter=%s",
            (ch,),
        )
        db_n = cur.fetchone()["c"]
        cur.execute(
            """
            SELECT count(DISTINCT ot.verse_id) AS c
            FROM original_tokens ot
            JOIN verses v ON v.id = ot.verse_id
            WHERE v.book_code='PSA' AND v.chapter=%s
            """,
            (ch,),
        )
        tok_n = cur.fetchone()["c"]
        if tok_n < expected - 1 or db_n != expected:
            report["chapter_anomalies"].append(
                {
                    "ch": ch,
                    "bible_data": expected,
                    "verses_rows": db_n,
                    "with_tokens": tok_n,
                }
            )

    cur.execute(
        """
        SELECT count(*) AS c FROM verse_alignments
        WHERE english_verse_id LIKE 'PSA.%'
          AND english_verse_id != source_verse_id
        """
    )
    offsets = cur.fetchone()["c"]
    cur.execute(
        """
        SELECT count(*) AS c FROM annotations
        WHERE annotation_type IN ('superscription','title')
          AND start_verse_id LIKE 'PSA.%'
        """
    )
    titles = cur.fetchone()["c"]
    conn.close()

    summary = {
        "english_no_tokens": len(report["empties"]),
        "suspicious_title_anchors": len(report["suspicious_title_anchors"]),
        "fused_lsv_v1": len(report["fused_lsv_v1"]),
        "chapter_anomalies": len(report["chapter_anomalies"]),
        "align_offsets": offsets,
        "titles_total": titles,
    }
    print("=== Psalm audit ===")
    print(json.dumps(summary, indent=2))
    if report["empties"]:
        print("empties:", report["empties"])
    if report["suspicious_title_anchors"]:
        print("suspicious title anchors:")
        for s in report["suspicious_title_anchors"][:25]:
            print(" ", s)
    if args.json:
        args.json.write_text(
            json.dumps({"summary": summary, **report}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print("wrote", args.json)

    # Fail if classic superscriptions still mid-chapter (not acrostic)
    if report["suspicious_title_anchors"] or report["empties"]:
        print("=== AUDIT: issues remain ===")
        return 1
    print("=== AUDIT: PASS (no empties / no mis-anchored superscriptions) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
