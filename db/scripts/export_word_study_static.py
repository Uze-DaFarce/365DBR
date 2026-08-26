#!/usr/bin/env python3
"""
Export Word study packs for GoDaddy static hosting ($0 — no live Postgres on host).

Writes under apps/365DBR/ws/:
  manifest.json          — feature-detect target (same-origin, CSP-safe)
  verse/{BOOK}.json      — map of verse_id → load_verse-compatible payload
  strong/{H430|G26}.json — search_strong-compatible hit lists (capped)

Usage (monorepo root; Docker Postgres up; db/.env set):
  python db/scripts/export_word_study_static.py
  python db/scripts/export_word_study_static.py --strong-limit 40

Then FTP the ws/ folder next to index.html on mt-sin.ai.
Gitignores generated verse/strong/manifest (see root .gitignore).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))

from etl.parse_passage import language_for_book  # noqa: E402
from query import get_connection  # noqa: E402
from query.day_load import _join_original  # noqa: E402

OUT_DEFAULT = ROOT / "apps" / "365DBR" / "ws"


def _norm_strong_key(strong: str | None) -> str | None:
    """H0430 / h430 → H430; empty → None."""
    if not strong:
        return None
    s = str(strong).strip().upper()
    m = re.fullmatch(r"([HG])0*(\d+)", s)
    if not m:
        return None
    return f"{m.group(1)}{int(m.group(2))}"


def _atomic_write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(obj, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    tmp.replace(path)


def export_verses(conn, out_dir: Path) -> dict:
    """One JSON file per book_code with all verses that have tokens (or titles)."""
    verse_dir = out_dir / "verse"
    if verse_dir.exists():
        for p in verse_dir.glob("*.json"):
            p.unlink()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT v.id, v.book_code, v.chapter, v.verse, v.verse_order
            FROM verses v
            WHERE EXISTS (
                SELECT 1 FROM original_tokens ot WHERE ot.verse_id = v.id
            )
            OR EXISTS (
                SELECT 1 FROM annotations a
                WHERE a.start_verse_id = v.id AND a.end_verse_id = v.id
                  AND a.annotation_type IN ('superscription', 'title')
            )
            ORDER BY v.verse_order
            """
        )
        verses = cur.fetchall()

    by_book: dict[str, list] = defaultdict(list)
    for v in verses:
        by_book[v["book_code"]].append(v)

    total_verses = 0
    total_tokens = 0

    with conn.cursor() as cur:
        for book, vrows in sorted(by_book.items()):
            ids = [v["id"] for v in vrows]
            # tokens
            cur.execute(
                """
                SELECT verse_id, word_order, language, surface_text, strong_number,
                       lemma, morph, source_verse_id
                FROM original_tokens
                WHERE verse_id = ANY(%s)
                ORDER BY verse_id, word_order
                """,
                (ids,),
            )
            toks_by: dict[str, list] = defaultdict(list)
            for t in cur.fetchall():
                toks_by[t["verse_id"]].append(t)

            # titles
            cur.execute(
                """
                SELECT start_verse_id, annotation_type, value, source
                FROM annotations
                WHERE start_verse_id = ANY(%s) AND end_verse_id = start_verse_id
                  AND annotation_type IN ('superscription', 'title')
                ORDER BY id
                """,
                (ids,),
            )
            titles_by: dict[str, list] = defaultdict(list)
            for a in cur.fetchall():
                titles_by[a["start_verse_id"]].append(a)

            # light annotations covering these verses (speaker/theme)
            cur.execute(
                """
                SELECT a.annotation_type, a.value, a.source,
                       a.start_verse_id, a.end_verse_id,
                       vs.verse_order AS so, ve.verse_order AS eo
                FROM annotations a
                JOIN verses vs ON vs.id = a.start_verse_id
                JOIN verses ve ON ve.id = a.end_verse_id
                WHERE a.annotation_type IN ('speaker', 'theme')
                  AND vs.book_code = %s
                """,
                (book,),
            )
            ann_rows = cur.fetchall()

            book_map = {}
            lang = language_for_book(book)
            for v in vrows:
                vid = v["id"]
                tokens = toks_by.get(vid, [])
                total_tokens += len(tokens)
                src_ids = sorted(
                    {
                        t.get("source_verse_id")
                        for t in tokens
                        if t.get("source_verse_id")
                    }
                )
                vo = v["verse_order"]
                annos = [
                    {
                        "type": a["annotation_type"],
                        "value": a["value"],
                        "start_verse_id": a["start_verse_id"],
                        "end_verse_id": a["end_verse_id"],
                        "source": a["source"],
                    }
                    for a in ann_rows
                    if a["so"] <= vo <= a["eo"]
                ]
                book_map[vid] = {
                    "ok": True,
                    "verse_id": vid,
                    "book_code": book,
                    "chapter": v["chapter"],
                    "verse": v["verse"],
                    "verse_order": vo,
                    "original": {
                        "text": _join_original(tokens, lang),
                        "language": lang,
                        "source_verse_ids": src_ids,
                        "tokens": [
                            {
                                "order": t["word_order"],
                                "surface": t["surface_text"] or "",
                                "strong": t["strong_number"],
                                "lemma": t["lemma"],
                                "morph": t["morph"],
                                "language": t["language"],
                                "source_verse_id": t.get("source_verse_id"),
                            }
                            for t in tokens
                        ],
                    },
                    "titles": [
                        {
                            "type": t["annotation_type"],
                            "text": t["value"],
                            "source": t["source"],
                        }
                        for t in titles_by.get(vid, [])
                    ],
                    "annotations": annos,
                    "source": "static-ws",
                }
                total_verses += 1

            _atomic_write_json(verse_dir / f"{book}.json", book_map)
            print(f"  verse/{book}.json  verses={len(book_map)}")

    return {
        "books": len(by_book),
        "verses": total_verses,
        "tokens": total_tokens,
    }


def export_strongs(conn, out_dir: Path, *, hit_limit: int) -> dict:
    """One JSON per normalized Strong's number (H430, G26, …)."""
    strong_dir = out_dir / "strong"
    if strong_dir.exists():
        for p in strong_dir.glob("*.json"):
            p.unlink()

    lim = max(1, min(int(hit_limit), 100))

    with conn.cursor() as cur:
        # All token rows with a strong — normalize in Python
        cur.execute(
            """
            SELECT ot.verse_id, ot.surface_text, ot.strong_number, ot.language,
                   v.verse_order, vt.text AS lsv_text
            FROM original_tokens ot
            JOIN verses v ON v.id = ot.verse_id
            LEFT JOIN translations t ON t.code = 'LSV'
            LEFT JOIN verse_translations vt
              ON vt.verse_id = ot.verse_id AND vt.translation_id = t.id
            WHERE ot.strong_number IS NOT NULL AND ot.strong_number != ''
            ORDER BY v.verse_order, ot.word_order
            """
        )
        rows = cur.fetchall()

    # key → ordered unique verse hits
    buckets: dict[str, list] = defaultdict(list)
    seen: dict[str, set] = defaultdict(set)
    totals: dict[str, set] = defaultdict(set)

    for r in rows:
        key = _norm_strong_key(r["strong_number"])
        if not key:
            continue
        vid = r["verse_id"]
        totals[key].add(vid)
        if vid in seen[key]:
            continue
        seen[key].add(vid)
        if len(buckets[key]) >= lim:
            continue
        buckets[key].append(
            {
                "verse_id": vid,
                "surface": r["surface_text"],
                "strong": key,
                "language": r["language"],
                # English context snippet only (not Strong's-per-translation).
                # Field name "snippet"; keep "lsv" alias until packs are re-exported.
                "snippet": (r["lsv_text"] or "")[:160] if r["lsv_text"] else None,
                "snippet_translation": "LSV",
                "lsv": (r["lsv_text"] or "")[:160] if r["lsv_text"] else None,
            }
        )

    for key, hits in buckets.items():
        payload = {
            "ok": True,
            "query": key,
            "total_verses": len(totals[key]),
            "returned": len(hits),
            "hits": hits,
            "source": "static-ws",
        }
        _atomic_write_json(strong_dir / f"{key}.json", payload)

    print(f"  strong/*.json  numbers={len(buckets)} (hit_cap={lim})")
    return {"strong_numbers": len(buckets), "hit_limit": lim}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export static Word study JSON for GoDaddy ($0 publish)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_DEFAULT,
        help=f"Output dir (default {OUT_DEFAULT})",
    )
    parser.add_argument(
        "--strong-limit",
        type=int,
        default=40,
        help="Max hits stored per Strong's number (default 40)",
    )
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    print(f"[export_ws] out={out}")
    t0 = time.time()
    conn = get_connection()
    try:
        print("[export_ws] verses…")
        vstats = export_verses(conn, out)
        print("[export_ws] strongs…")
        sstats = export_strongs(conn, out, hit_limit=args.strong_limit)
    finally:
        conn.close()

    manifest = {
        "ok": True,
        "mode": "static-ws",
        "version": "1",
        "service": "365DBR-word-study-static",
        "note": "Same-origin static Word study for shared hosting (no live DB).",
        "verse_books": vstats["books"],
        "verses": vstats["verses"],
        "tokens": vstats["tokens"],
        "strong_numbers": sstats["strong_numbers"],
        "strong_hit_limit": sstats["hit_limit"],
        "paths": {
            "manifest": "manifest.json",
            "verse_book": "verse/{BOOK}.json",
            "strong": "strong/{H430|G26}.json",
        },
    }
    _atomic_write_json(out / "manifest.json", manifest)
    elapsed = time.time() - t0
    print(json.dumps(manifest, indent=2))
    print(f"[export_ws] DONE in {elapsed:.1f}s")
    print("FTP apps/365DBR/ws/ to https://mt-sin.ai/365DBR/ws/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
