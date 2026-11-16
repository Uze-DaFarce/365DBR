#!/usr/bin/env python3
"""
Export Word study packs for GoDaddy static hosting ($0 — no live Postgres on host).

Writes under apps/365DBR/ws/:
  manifest.json          — feature-detect target (same-origin, CSP-safe)
  verse/{BOOK}.json      — map of verse_id → load_verse-compatible payload
  strong/{H430|G26}.json — search_strong-compatible hit lists (capped)
  word/{utf8-hex}.json   — verses of the same written word (capped; ASCII name)

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
from query.verify import classify_link  # noqa: E402
from query.word import token_key as _word_key  # noqa: E402

OUT_DEFAULT = ROOT / "apps" / "365DBR" / "ws"


def _word_filename(key: str) -> str:
    """ASCII name. GoDaddy FTP replaces Greek and Hebrew letters with ?."""
    return key.encode("utf-8").hex() + ".json"


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
    step_labeled = 0
    step_note_tokens = 0

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT original_token_id, min(english) AS english
            FROM stepbible_token_rows
            WHERE original_token_id IS NOT NULL
              AND english IS NOT NULL
            GROUP BY original_token_id
            HAVING min(english) IS NOT DISTINCT FROM max(english)
            """
        )
        agreed_english = {
            row["original_token_id"]: row["english"]
            for row in cur.fetchall()
            if row["english"]
        }

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT original_token_id, source, source_file, surface, letters,
                   dstrong, root_strong, alt_strongs
            FROM stepbible_token_rows
            WHERE original_token_id IS NOT NULL
            ORDER BY original_token_id, word_index
            """
        )
        notes_by: dict[int, list] = defaultdict(list)
        judge_by: dict[int, list] = defaultdict(list)
        for row in cur.fetchall():
            note = {"source": row["source"], "file": row["source_file"]}
            if row["dstrong"]:
                note["dstrong"] = row["dstrong"]
            if row["root_strong"]:
                note["sstrong"] = row["root_strong"]
            if row["alt_strongs"]:
                note["alt"] = row["alt_strongs"]
            notes_by[row["original_token_id"]].append(note)
            judge_by[row["original_token_id"]].append(
                {
                    "source": row["source"],
                    "surface": row["surface"],
                    "letters": row["letters"],
                    "dstrong": row["dstrong"],
                }
            )

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT extended_strong, gloss
            FROM strongs_lexicon
            WHERE gloss IS NOT NULL AND gloss <> ''
            """
        )
        gloss_by = {
            row["extended_strong"]: row["gloss"]
            for row in cur.fetchall()
            if row["extended_strong"] and row["gloss"]
        }

    with conn.cursor() as cur:
        for book, vrows in sorted(by_book.items()):
            ids = [v["id"] for v in vrows]
            # tokens
            cur.execute(
                """
                SELECT id, verse_id, word_order, language, surface_text, strong_number,
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

            # English translations (for Word study context when focal is KJV/LSV/LSB)
            cur.execute(
                """
                SELECT vt.verse_id, t.code, vt.text
                FROM verse_translations vt
                JOIN translations t ON t.id = vt.translation_id
                WHERE vt.verse_id = ANY(%s)
                ORDER BY vt.verse_id, t.code
                """,
                (ids,),
            )
            trans_by: dict[str, dict[str, str]] = defaultdict(dict)
            for r in cur.fetchall():
                trans_by[r["verse_id"]][r["code"]] = r["text"]

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
                token_rows = []
                for t in tokens:
                    row = {
                        "order": t["word_order"],
                        "surface": t["surface_text"] or "",
                        "strong": t["strong_number"],
                        "lemma": t["lemma"],
                        "morph": t["morph"],
                        "language": t["language"],
                        "source_verse_id": t.get("source_verse_id"),
                    }
                    english = agreed_english.get(t["id"])
                    if english:
                        row["step_english"] = english
                        row["step_english_label"] = "STEPBible contextual English"
                        step_labeled += 1
                    notes = notes_by.get(t["id"])
                    if notes:
                        row["step_notes"] = notes
                        step_note_tokens += 1
                    judged = classify_link(
                        t["language"],
                        t["surface_text"],
                        t["strong_number"],
                        judge_by.get(t["id"], []),
                    )
                    row["link"] = judged["link"]
                    if judged["number_match"] is not None:
                        row["number_match"] = judged["number_match"]
                    gloss = gloss_by.get(t["strong_number"])
                    if gloss:
                        row["lexicon_gloss"] = gloss
                        row["lexicon_gloss_label"] = "TBESG lexicon gloss"
                    token_rows.append(row)
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
                        "tokens": token_rows,
                    },
                    "titles": [
                        {
                            "type": t["annotation_type"],
                            "text": t["value"],
                            "source": t["source"],
                        }
                        for t in titles_by.get(vid, [])
                    ],
                    "translations": trans_by.get(vid, {}),
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
        "step_english": step_labeled,
        "step_notes": step_note_tokens,
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


def export_words(conn, out_dir: Path, *, hit_limit: int) -> dict:
    """One JSON per written word. The key is the word's letters, not a Strong's number."""
    word_dir = out_dir / "word"
    if word_dir.exists():
        for p in word_dir.glob("*.json"):
            p.unlink()
    else:
        word_dir.mkdir(parents=True, exist_ok=True)

    lim = max(1, min(int(hit_limit), 100))
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT ot.verse_id, ot.surface_text, ot.lemma, ot.language,
                   v.verse_order, vt.text AS lsv_text
            FROM original_tokens ot
            JOIN verses v ON v.id = ot.verse_id
            LEFT JOIN translations t ON t.code = 'LSV'
            LEFT JOIN verse_translations vt
              ON vt.verse_id = ot.verse_id AND vt.translation_id = t.id
            ORDER BY v.verse_order, ot.word_order
            """
        )
        rows = cur.fetchall()

    buckets: dict[str, list] = defaultdict(list)
    seen: dict[str, set] = defaultdict(set)
    totals: dict[str, set] = defaultdict(set)
    for r in rows:
        key = _word_key(r["language"], r["lemma"], r["surface_text"])
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
                "language": r["language"],
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
        _atomic_write_json(word_dir / _word_filename(key), payload)

    print(f"  word/*.json  words={len(buckets)} (hit_cap={lim})")
    return {"words": len(buckets), "hit_limit": lim}


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
        print("[export_ws] words…")
        wstats = export_words(conn, out, hit_limit=args.strong_limit)
    finally:
        conn.close()

    manifest = {
        "ok": True,
        "mode": "static-ws",
        "version": "1",
        "service": "365DBR-word-study-static",
        "note": (
            "Same-origin static Word study for shared hosting (no live DB). "
            "step_english is present only when every linked STEPBible row on that "
            "token has the same English. It is STEPBible contextual English, not a Strong's gloss. "
            "step_notes copies dStrong, sStrong, and Alt Strongs from each linked STEPBible row, "
            "with that file's name. lexicon_gloss is the TBESG gloss for the stored number when "
            "that number is an exact lexicon key. number_match is true only when "
            "one linked row's letters match the word and its dstrong is the same "
            "plain H or G number, or the same extended tag written the same way. "
            "G2424G matches G2424G and does not match G2424. A compound tag matches only that same compound. "
            "Those notes are not the word. The word is the token surface. "
            "Place lists are verses of that written word: Greek lemma letters without accents, "
            "Hebrew lemma consonants, or the surface letters when the lemma has none."
        ),
        "step_english_tokens": vstats.get("step_english", 0),
        "step_note_tokens": vstats.get("step_notes", 0),
        "verse_books": vstats["books"],
        "verses": vstats["verses"],
        "tokens": vstats["tokens"],
        "strong_numbers": sstats["strong_numbers"],
        "strong_hit_limit": sstats["hit_limit"],
        "words": wstats["words"],
        "paths": {
            "manifest": "manifest.json",
            "verse_book": "verse/{BOOK}.json",
            "strong": "strong/{H430|G26}.json",
            "word": "word/{utf8-hex}.json",
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
