"""Inject local LSB USX text into daily reading JSON parallels (offline).

Integrity rules (non-negotiable):
- Verse body is LSB scripture text only. No titles, notes, or USFM/USX styling.
- Do not drop an LSB verse because KJV/LSV/Hebrew used a different number.
- Do not invent LSB text. Do not copy Hebrew/org ids onto LSB English ids.
- Look up LSB only by LSB/English BCV as it stands in the USX.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from bible_common import ALL_BOOKS, atomic_write_json, extract_verse_ids, is_verse_in_range
from lsb_usx import extract_directory

ROOT = Path(__file__).resolve().parent
LSB_BIBLE_ID = "8011347e1aa60e8a-01"
SKIP_NAMES = {"manifest.json", "readings.json", "omissions_cache.json"}
FILE_RANGE_RE = re.compile(
    r"^([1-3]?[A-Z]+)\.(\d+)\.(\d+)-([1-3]?[A-Z]+)\.(\d+)\.(\d+)$"
)


def _vid_key(vid: str):
    parts = str(vid).split(".")
    if len(parts) != 3:
        return (99, 0, 0, vid)
    book, chapter, verse = parts
    try:
        book_i = ALL_BOOKS.index(book)
    except ValueError:
        book_i = 99
    try:
        return (book_i, int(chapter), int(verse))
    except ValueError:
        return (book_i, 0, 0, vid)


def _is_lsb_parallel(item) -> bool:
    if not isinstance(item, dict):
        return False
    if str(item.get("translationCode") or "").upper() == "LSB":
        return True
    return item.get("bibleId") == LSB_BIBLE_ID


def english_verse_ids(data: dict) -> list[str]:
    """LSV/KJV verseId values. Never original-language org ids."""
    ids: set[str] = set()
    
    # 1. ALWAYS get the primary text IDs! (Grok broke this)
    if data.get("content"):
        ids |= extract_verse_ids(data.get("content"))
        
    # 2. Safely check other parallels
    for par in data.get("parallels") or []:
        if _is_lsb_parallel(par):
            continue
        if par.get("content"):
            ids |= extract_verse_ids(par.get("content"))
            
    return sorted(ids, key=_vid_key)


def _filename_range(stem: str):
    match = FILE_RANGE_RE.match(stem)
    if not match:
        return None
    return (
        match.group(1),
        int(match.group(2)),
        int(match.group(3)),
        match.group(4),
        int(match.group(5)),
        int(match.group(6)),
    )


def verse_ids_for_pack(path: Path, data: dict, usx_verses: dict) -> list[str]:
    """KJV/LSV English ids, plus specific LSB tails (like SNG.6.13)."""
    # Start with the EXACT verses required by the primary text
    ids = set(english_verse_ids(data))
    
    bounds = _filename_range(path.stem)
    if bounds:
        end_book, end_chapter, end_verse = bounds[3], bounds[4], bounds[5]
        usx_end = 0
        
        # Check how many verses the LSB USX actually has in the final chapter
        for vid in usx_verses:
            try:
                book, chapter, verse = str(vid).split(".")[:3]
                if book == end_book and int(chapter) == end_chapter:
                    usx_end = max(usx_end, int(verse))
            except Exception:
                continue
                
        # Small numbering tails only (SNG.6.13, 3JN.1.15)
        # We append these WITHOUT doing a dangerous blanket sweep of the whole file.
        if 0 < usx_end - end_verse <= 2:
            for number in range(end_verse + 1, usx_end + 1):
                vid = f"{end_book}.{end_chapter}.{number}"
                if vid in usx_verses:
                    ids.add(vid)
                    
    return sorted(ids, key=_vid_key)

def _para(style: str, items: list) -> dict:
    return {"name": "para", "type": "tag", "attrs": {"style": style}, "items": items}


def _verse_text(vid: str, text: str) -> dict:
    body = text if text.endswith(" ") else f"{text} "
    return {
        "text": body,
        "type": "text",
        "attrs": {"verseId": vid, "verseOrgIds": [vid]},
    }


def build_lsb_content(verse_ids: list[str], verses: dict, titles: dict) -> list:
    content = []
    for vid in verse_ids:
        text = verses.get(vid)
        if not text:
            continue
        content.append(_para("p", [_verse_text(vid, text)]))
    return content

def build_lsb_parallel(payload: dict, content: list) -> dict:
    data = payload.get("data") or {}
    passage_id = data.get("id") or data.get("orgId") or ""
    return {
        "id": passage_id,
        "orgId": data.get("orgId") or passage_id,
        "bibleId": LSB_BIBLE_ID,
        "translationCode": "LSB",
        "bookId": data.get("bookId"),
        "chapterIds": list(data.get("chapterIds") or []),
        "reference": data.get("reference") or passage_id,
        "content": content,
        "verseCount": len(extract_verse_ids(content)),
    }


def inject_file(path: Path, verses: dict, titles: dict, force: bool) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"skip {path}: {exc}"

    if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
        return f"skip {path}: no data object"
    data = payload["data"]
    if not data.get("content"):
        return f"skip {path}: no content"

    needed = verse_ids_for_pack(path, data, verses)
    if not needed:
        return f"skip {path}: no verse ids"

    parallels = data.setdefault("parallels", [])
    if not isinstance(parallels, list):
        data["parallels"] = []
        parallels = data["parallels"]

    existing = [i for i, item in enumerate(parallels) if _is_lsb_parallel(item)]
    if existing:
        if not force:
            return f"skip {path}: LSB already present"
        for index in reversed(existing):
            parallels.pop(index)

    content = build_lsb_content(needed, verses, titles)
    if not content:
        return f"skip {path}: no LSB verses for this range"

    parallels.insert(0, build_lsb_parallel(payload, content))
    atomic_write_json(str(path), payload, ensure_ascii=False)
    return f"inject {path}: {len(content)} blocks"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject local LSB USX text into data/MMDD JSON parallels.")
    parser.add_argument("usx_dir", nargs="?", default="LSB/release/USX_1", help="Directory of LSB .usx files")
    parser.add_argument("--force", action="store_true", help="Replace an existing LSB parallel")
    parser.add_argument("--check", action="store_true", help="Report English verses missing LSB; do not write")
    args = parser.parse_args()

    usx_dir = Path(args.usx_dir)
    if not usx_dir.is_absolute():
        usx_dir = ROOT / usx_dir
    if not usx_dir.exists():
        print(f"USX directory not found: {usx_dir}", file=sys.stderr)
        return 1

    verses, titles = extract_directory(usx_dir)
    if not verses:
        print(f"No verses extracted from {usx_dir}", file=sys.stderr)
        return 1

    files = sorted(p for p in (ROOT / "data").glob("*/*.json") if p.name not in SKIP_NAMES)
    if not files:
        print("No data/*/*.json files found")
        return 1

    if args.check:
        missing = []
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            data = payload.get("data")
            if not isinstance(data, dict):
                continue
            needed = set(verse_ids_for_pack(path, data, verses))
            lsb_ids: set[str] = set()
            for par in data.get("parallels") or []:
                if _is_lsb_parallel(par):
                    lsb_ids |= extract_verse_ids(par.get("content"))
            for vid in sorted(needed, key=_vid_key):
                if vid in verses and vid not in lsb_ids:
                    missing.append(f"{path.name} {vid}")
        if missing:
            print(f"LSB integrity failed: {len(missing)} English verses have USX text but no LSB parallel")
            print("\n".join(f"- {row}" for row in missing[:80]))
            if len(missing) > 80:
                print(f"- … {len(missing) - 80} more")
            return 1
        print("LSB integrity passed: every English verse with USX text is present in LSB parallels")
        return 0

    for path in files:
        print(inject_file(path, verses, titles, args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
