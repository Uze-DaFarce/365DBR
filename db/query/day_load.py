"""
DB day / verse / Strong's queries + dual-read (JSON pack vs DB).

verseMap shape (lowercase keys, matching frontend TRANSLATION_REGISTRY):
  {
    "GEN.1.1": {
      "original": {"text": "...", "tokens": [{"surface": "...", "strong": "H7225", "order": 1}]},
      "lsv": {"text": "..."},
      "kjv": {"text": "..."}
    }
  }

Hebrew original text is joined with '' (no space); Greek with ' '.
English translations are stored already-joined in verse_translations.
"""

from __future__ import annotations

import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = ROOT / "apps" / "365DBR" / "data"
PRODUCTION_BASE = "https://mt-sin.ai/365DBR/data"

# Import path for parse helpers (JSON dual-read)
import sys

sys.path.insert(0, str(ROOT / "db"))
sys.path.insert(0, str(ROOT / "apps" / "365DBR"))

from etl.parse_passage import (  # noqa: E402
    language_for_book,
    parse_passage_payload,
)

NT_BOOKS = {
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH",
    "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS",
    "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
}


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _book_of(verse_id: str) -> str:
    # Handles "1CO.1.1" and "GEN.1.1"
    parts = verse_id.split(".")
    return parts[0] if parts else ""


def _join_original(tokens: list[dict], language: str) -> str:
    surfaces = [t.get("surface_text") or t.get("surface") or "" for t in tokens]
    surfaces = [s for s in surfaces if s]
    if language == "hebrew":
        return "".join(surfaces)
    return " ".join(surfaces)


def _normalize_strong_pattern(strong: str) -> str:
    """
    Accept H430, H0430, G26, g0026 → regex for original_tokens.strong_number.
    Hebrew often zero-padded to 4 digits in WLC (H0430); Greek may be bare.
    """
    s = (strong or "").strip().upper()
    if not s:
        raise ValueError("empty Strong's number")
    m = re.fullmatch(r"([HG])0*(\d+)", s)
    if not m:
        raise ValueError(f"invalid Strong's number: {strong!r} (expected H#### or G####)")
    prefix, digits = m.group(1), m.group(2)
    # Match optional leading zeros after letter
    return f"^{prefix}0*{int(digits)}$"


def load_day(conn, day: str) -> dict[str, Any]:
    """
    Load one MMDD day from DB into a verseMap-compatible payload.

    Returns:
      {
        "day": "0101",
        "label": "...",
        "passages": [...],
        "availableTranslations": ["lsv", "kjv"],
        "verseMap": { vid: { original, lsv, kjv } },
        "verseCount": N,
        "source": "db"
      }
    """
    day = day.strip()
    if not re.fullmatch(r"\d{4}", day):
        raise ValueError(f"day must be MMDD (4 digits), got {day!r}")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT day, label FROM daily_readings WHERE day = %s",
            (day,),
        )
        reading = cur.fetchone()
        if not reading:
            raise KeyError(f"day {day} not in daily_readings")

        cur.execute(
            """
            SELECT section, start_verse_id, end_verse_id, file_ref, verse_count
            FROM daily_passages
            WHERE day = %s
            ORDER BY id
            """,
            (day,),
        )
        passages = cur.fetchall()
        if len(passages) != 4:
            raise RuntimeError(
                f"day {day}: expected 4 daily_passages, got {len(passages)}"
            )

        # Plan ranges are often org/source numbering (Hebrew fetch + use-org-id).
        # Resolve to English-primary display ids via verse_alignments when present.
        cur.execute(
            """
            SELECT DISTINCT v.id AS verse_id, v.verse_order, v.book_code
            FROM daily_passages dp
            JOIN verses vs ON vs.id = dp.start_verse_id
            JOIN verses ve ON ve.id = dp.end_verse_id
            JOIN verses v ON v.verse_order BETWEEN vs.verse_order AND ve.verse_order
            WHERE dp.day = %s
            ORDER BY v.verse_order
            """,
            (day,),
        )
        plan_range_rows = cur.fetchall()
        plan_range_ids = [r["verse_id"] for r in plan_range_rows]
        if not plan_range_ids:
            raise RuntimeError(f"day {day}: no verses in plan ranges")

        # Per-source resolve: if org→English map exists for that source id, use
        # English display id(s); otherwise keep the plan BCV (1:1).
        # NEVER replace the whole day with only the subset that has map rows
        # (that produced load_day 1231 → 1 verse when only REV.21.27 was mapped).
        cur.execute(
            """
            SELECT source_verse_id, english_verse_id
            FROM verse_alignments
            WHERE source_verse_id = ANY(%s)
            """,
            (plan_range_ids,),
        )
        src_to_eng: dict[str, list[str]] = defaultdict(list)
        for row in cur.fetchall():
            src_to_eng[row["source_verse_id"]].append(row["english_verse_id"])

        display_ids: list[str] = []
        seen: set[str] = set()
        for sid in plan_range_ids:
            targets = src_to_eng.get(sid)
            if targets:
                for eid in targets:
                    if eid not in seen:
                        seen.add(eid)
                        display_ids.append(eid)
            else:
                if sid not in seen:
                    seen.add(sid)
                    display_ids.append(sid)

        cur.execute(
            """
            SELECT v.id AS verse_id, v.verse_order, v.book_code
            FROM verses v
            WHERE v.id = ANY(%s)
            ORDER BY v.verse_order, v.id
            """,
            (display_ids,),
        )
        verse_rows = cur.fetchall()
        # Preserve plan order if some ids missing from verses table
        if len(verse_rows) < len(display_ids):
            by_id = {r["verse_id"]: r for r in verse_rows}
            verse_rows = [by_id[i] for i in display_ids if i in by_id]

        verse_ids = [r["verse_id"] for r in verse_rows]
        if not verse_ids:
            raise RuntimeError(f"day {day}: no display verses after alignment")

        # Translations (LSV + KJV)
        cur.execute(
            """
            SELECT vt.verse_id, t.code, vt.text
            FROM verse_translations vt
            JOIN translations t ON t.id = vt.translation_id
            WHERE vt.verse_id = ANY(%s) AND t.code IN ('LSV', 'KJV')
            """,
            (verse_ids,),
        )
        trans_rows = cur.fetchall()

        # Original tokens (English-primary verse_id after ETL remap)
        cur.execute(
            """
            SELECT verse_id, word_order, language, surface_text, strong_number,
                   source_verse_id
            FROM original_tokens
            WHERE verse_id = ANY(%s)
            ORDER BY verse_id, word_order
            """,
            (verse_ids,),
        )
        token_rows = cur.fetchall()

    by_trans: dict[str, dict[str, str]] = defaultdict(dict)
    for row in trans_rows:
        code = row["code"].lower()  # lsv / kjv for frontend shape
        by_trans[row["verse_id"]][code] = row["text"]

    tokens_by_vid: dict[str, list[dict]] = defaultdict(list)
    for row in token_rows:
        tokens_by_vid[row["verse_id"]].append(row)

    verse_map: dict[str, dict[str, Any]] = {}
    for vr in verse_rows:
        vid = vr["verse_id"]
        book = vr["book_code"] or _book_of(vid)
        lang = language_for_book(book) if book else (
            "greek" if _book_of(vid) in NT_BOOKS else "hebrew"
        )
        toks = tokens_by_vid.get(vid, [])
        entry: dict[str, Any] = {}

        if toks:
            entry["original"] = {
                "text": _join_original(toks, lang),
                "tokens": [
                    {
                        "order": t["word_order"],
                        "surface": t["surface_text"] or "",
                        "strong": t["strong_number"],
                        "language": t["language"],
                        "source_verse_id": t.get("source_verse_id"),
                    }
                    for t in toks
                ],
            }
            # Provenance when English id ≠ org/source id
            src_ids = {
                t.get("source_verse_id")
                for t in toks
                if t.get("source_verse_id") and t.get("source_verse_id") != vid
            }
            if src_ids:
                entry["original"]["source_verse_ids"] = sorted(src_ids)
        else:
            entry["original"] = {"text": "", "tokens": []}

        for code in ("lsv", "kjv"):
            text = by_trans.get(vid, {}).get(code)
            if text is not None:
                entry[code] = {"text": text}

        verse_map[vid] = entry

    available = []
    # Detect which English keys appear at least once
    for key in ("lsv", "kjv"):
        if any(key in verse_map[v] for v in verse_map):
            available.append(key)

    return {
        "day": day,
        "label": reading["label"],
        "passages": [
            {
                "section": p["section"],
                "start_verse_id": p["start_verse_id"],
                "end_verse_id": p["end_verse_id"],
                "file_ref": p["file_ref"],
                "verse_count": p["verse_count"],
            }
            for p in passages
        ],
        "availableTranslations": available,
        "verseMap": verse_map,
        "verseCount": len(verse_map),
        "source": "db",
    }


def load_verse(conn, verse_id: str) -> dict[str, Any]:
    """Load one BCV verse: translations + original tokens."""
    verse_id = verse_id.strip().upper()
    # Normalize book portion only loosely — keep as stored (e.g. 1CO.1.1)
    # Allow mixed case input; standard is UPPER book codes.
    parts = verse_id.split(".")
    if len(parts) >= 3:
        verse_id = f"{parts[0].upper()}.{parts[1]}.{parts[2]}"

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, book_code, chapter, verse, verse_order FROM verses WHERE id = %s",
            (verse_id,),
        )
        vrow = cur.fetchone()
        if not vrow:
            raise KeyError(f"verse not found: {verse_id}")

        cur.execute(
            """
            SELECT t.code, vt.text
            FROM verse_translations vt
            JOIN translations t ON t.id = vt.translation_id
            WHERE vt.verse_id = %s
            ORDER BY t.code
            """,
            (verse_id,),
        )
        translations = {r["code"]: r["text"] for r in cur.fetchall()}

        cur.execute(
            """
            SELECT word_order, language, surface_text, strong_number, lemma, morph,
                   source_verse_id
            FROM original_tokens
            WHERE verse_id = %s
            ORDER BY word_order
            """,
            (verse_id,),
        )
        tokens = cur.fetchall()

        cur.execute(
            """
            SELECT source_verse_id, established_by
            FROM verse_alignments
            WHERE english_verse_id = %s
            """,
            (verse_id,),
        )
        alignments = cur.fetchall()

        cur.execute(
            """
            SELECT annotation_type, value, metadata, source
            FROM annotations
            WHERE start_verse_id = %s AND end_verse_id = %s
              AND annotation_type IN ('superscription', 'title')
            ORDER BY id
            """,
            (verse_id, verse_id),
        )
        titles = cur.fetchall()

    book = vrow["book_code"] or _book_of(verse_id)
    lang = language_for_book(book)
    src_ids = sorted({
        t.get("source_verse_id")
        for t in tokens
        if t.get("source_verse_id")
    })
    return {
        "verse_id": verse_id,
        "book_code": book,
        "chapter": vrow["chapter"],
        "verse": vrow["verse"],
        "verse_order": vrow["verse_order"],
        "translations": translations,
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
        "alignments": [
            {
                "source_verse_id": a["source_verse_id"],
                "established_by": a["established_by"],
            }
            for a in alignments
        ],
        "titles": [
            {
                "type": t["annotation_type"],
                "text": t["value"],
                "source": t["source"],
            }
            for t in titles
        ],
        "source": "db",
    }


def search_strong(
    conn,
    strong: str,
    *,
    limit: int = 50,
    with_lsv: bool = True,
) -> dict[str, Any]:
    """
    Find verses containing a Strong's number (Hebrew H#### or Greek G####).

    Returns hits with optional LSV text snippet.
    """
    pattern = _normalize_strong_pattern(strong)
    lim = max(1, min(int(limit), 5000))

    with conn.cursor() as cur:
        # Total distinct verses (uncapped)
        cur.execute(
            """
            SELECT count(DISTINCT verse_id) AS c
            FROM original_tokens
            WHERE strong_number ~ %s
            """,
            (pattern,),
        )
        total = cur.fetchone()["c"]

        if with_lsv:
            cur.execute(
                """
                SELECT DISTINCT ON (v.verse_order)
                    ot.verse_id,
                    ot.surface_text,
                    ot.strong_number,
                    ot.language,
                    vt.text AS lsv_text
                FROM original_tokens ot
                JOIN verses v ON v.id = ot.verse_id
                LEFT JOIN translations t ON t.code = 'LSV'
                LEFT JOIN verse_translations vt
                    ON vt.verse_id = ot.verse_id AND vt.translation_id = t.id
                WHERE ot.strong_number ~ %s
                ORDER BY v.verse_order, ot.word_order
                LIMIT %s
                """,
                (pattern, lim),
            )
        else:
            cur.execute(
                """
                SELECT DISTINCT ON (v.verse_order)
                    ot.verse_id,
                    ot.surface_text,
                    ot.strong_number,
                    ot.language,
                    NULL::text AS lsv_text
                FROM original_tokens ot
                JOIN verses v ON v.id = ot.verse_id
                WHERE ot.strong_number ~ %s
                ORDER BY v.verse_order, ot.word_order
                LIMIT %s
                """,
                (pattern, lim),
            )
        rows = cur.fetchall()

    hits = [
        {
            "verse_id": r["verse_id"],
            "surface": r["surface_text"],
            "strong": r["strong_number"],
            "language": r["language"],
            "lsv": r["lsv_text"],
        }
        for r in rows
    ]
    return {
        "query": strong.strip().upper(),
        "pattern": pattern,
        "total_verses": total,
        "returned": len(hits),
        "hits": hits,
        "source": "db",
    }


def _fetch_json_url(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "365DBR-query/phase4"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _load_local_pack_translations(day: str) -> dict[str, dict[str, str]]:
    """
    Parse local day pack → { 'LSV'|'KJV': { verse_id: text } }.
    """
    day_dir = LOCAL_DATA / day
    manifest_path = day_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"local manifest missing: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {"LSV": {}, "KJV": {}}

    for fname in manifest.get("files", []):
        path = day_dir / fname
        if not path.exists():
            raise FileNotFoundError(f"missing passage file: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        parsed = parse_passage_payload(raw, fname)
        for code, vmap in (parsed.get("translations") or {}).items():
            if code not in out:
                out[code] = {}
            out[code].update(vmap)
    return out


def _load_prod_pack_translations(day: str) -> dict[str, dict[str, str]]:
    base = f"{PRODUCTION_BASE}/{day}"
    manifest = _fetch_json_url(f"{base}/manifest.json")
    out: dict[str, dict[str, str]] = {"LSV": {}, "KJV": {}}
    for fname in manifest.get("files", []):
        raw = _fetch_json_url(f"{base}/{fname}")
        parsed = parse_passage_payload(raw, fname)
        for code, vmap in (parsed.get("translations") or {}).items():
            if code not in out:
                out[code] = {}
            out[code].update(vmap)
    return out


def _lookup_translation_global(conn, verse_id: str, code: str) -> str | None:
    """Look up LSV/KJV text anywhere in DB (not limited to day plan)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT vt.text
            FROM verse_translations vt
            JOIN translations t ON t.id = vt.translation_id
            WHERE vt.verse_id = %s AND t.code = %s
            """,
            (verse_id, code.upper()),
        )
        row = cur.fetchone()
    return row["text"] if row else None


def dual_read_day(
    conn,
    day: str,
    *,
    source: str = "local",
    sample_limit: int | None = None,
) -> dict[str, Any]:
    """
    Compare JSON day pack (local or prod) English texts vs DB.

    Classification (truth-first):
    - **plan_match / plan_mismatch / plan_missing_in_db**: JSON verse is inside
      this day's plan ranges (what load_day returns).
    - **spillover_***: JSON parallel includes a verse *outside* the plan range
      (common for Psalms superscription / numbering drift, e.g. PSA.31 25 vs 24).
      Spillover is checked against *global* verse_translations when present.
    - **plan_verse_missing_english**: plan verse has original tokens but no LSV/KJV.

    Does not mutate frontend paths — diagnostic only.
    """
    day = day.strip()
    if source not in ("local", "prod"):
        raise ValueError("source must be local or prod")

    if source == "local":
        pack = _load_local_pack_translations(day)
    else:
        pack = _load_prod_pack_translations(day)

    db_payload = load_day(conn, day)
    verse_map = db_payload["verseMap"]
    plan_ids = set(verse_map.keys())

    checked = 0
    plan_checked = 0
    spillover_checked = 0
    mismatches: list[dict[str, Any]] = []
    spillovers: list[dict[str, Any]] = []
    plan_missing_english: list[str] = []

    for code in ("LSV", "KJV"):
        jmap = pack.get(code) or {}
        key = code.lower()
        for vid, jtext in jmap.items():
            if sample_limit is not None and checked >= sample_limit:
                break
            checked += 1
            in_plan = vid in plan_ids

            if in_plan:
                plan_checked += 1
                db_entry = verse_map.get(vid)
                if not db_entry or key not in db_entry:
                    mismatches.append(
                        {
                            "verse_id": vid,
                            "translation": code,
                            "reason": "plan_missing_in_db",
                            "json": norm_ws(jtext)[:120],
                            "db": None,
                        }
                    )
                    continue
                dtext = db_entry[key]["text"]
                if norm_ws(jtext) != norm_ws(dtext):
                    mismatches.append(
                        {
                            "verse_id": vid,
                            "translation": code,
                            "reason": "plan_text_mismatch",
                            "json": norm_ws(jtext)[:120],
                            "db": norm_ws(dtext)[:120],
                        }
                    )
            else:
                # Neighbor bleed / numbering drift — not part of this day's plan
                spillover_checked += 1
                global_text = _lookup_translation_global(conn, vid, code)
                entry = {
                    "verse_id": vid,
                    "translation": code,
                    "json": norm_ws(jtext)[:120],
                    "db": norm_ws(global_text)[:120] if global_text else None,
                }
                if global_text is None:
                    entry["reason"] = "spillover_missing_in_db"
                    entry["note"] = (
                        "JSON parallel has this BCV outside day plan; "
                        "no verse_translations row in DB (often Psalm numbering drift)"
                    )
                    spillovers.append(entry)
                    # Truth: English text exists in pack for a valid BCV but never stored
                    mismatches.append(entry)
                elif norm_ws(jtext) != norm_ws(global_text):
                    entry["reason"] = "spillover_text_mismatch"
                    spillovers.append(entry)
                    mismatches.append(entry)
                else:
                    entry["reason"] = "spillover_ok_global"
                    spillovers.append(entry)

    # Plan verses lacking English (informational — pack may also lack them when
    # Hebrew 25-verse / English 24-verse Psalms diverge). Not a dual-read hard fail;
    # dual-read judges JSON English cells vs DB only.
    for vid in sorted(plan_ids):
        entry = verse_map[vid]
        for key, code in (("lsv", "LSV"), ("kjv", "KJV")):
            if key not in entry:
                plan_missing_english.append(f"{code}:{vid}")

    # Hard fail only when JSON has English text that DB lacks or mismatches.
    hard_mismatch_reasons = {
        "plan_missing_in_db",
        "plan_text_mismatch",
        "spillover_missing_in_db",
        "spillover_text_mismatch",
    }
    hard = [m for m in mismatches if m.get("reason") in hard_mismatch_reasons]
    ok = checked > 0 and len(hard) == 0

    notes: list[str] = []
    if spillovers:
        notes.append(
            f"{len(spillovers)} JSON English verse(s) outside day plan "
            "(Psalms superscription/numbering drift is a common cause)."
        )
    if plan_missing_english:
        notes.append(
            f"{len(plan_missing_english)} plan verse(s) lack LSV/KJV in DB "
            "(often Hebrew-only numbering, e.g. PSA.31.25 vs English 24-verse chapter)."
        )

    return {
        "day": day,
        "source": source,
        "ok": ok,
        "checked": checked,
        "plan_checked": plan_checked,
        "spillover_checked": spillover_checked,
        "mismatch_count": len(hard),
        "mismatches": hard[:50],
        "spillovers": spillovers[:30],
        "plan_missing_english_count": len(plan_missing_english),
        "plan_missing_english_sample": plan_missing_english[:20],
        "db_verse_count": db_payload["verseCount"],
        "json_lsv_count": len(pack.get("LSV") or {}),
        "json_kjv_count": len(pack.get("KJV") or {}),
        "label": db_payload["label"],
        "notes": notes,
    }
