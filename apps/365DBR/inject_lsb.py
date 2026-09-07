"""Inject local LSB USX text into daily reading JSON parallels (offline)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bible_common import ALL_BOOKS, atomic_write_json, extract_verse_ids
from lsb_usx import extract_directory

ROOT = Path(__file__).resolve().parent
LSB_BIBLE_ID = "8011347e1aa60e8a-01"
SKIP_NAMES = {"manifest.json", "readings.json", "omissions_cache.json"}


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
    original = data.get("content")
    if not original:
        return f"skip {path}: no content"

    needed = sorted(extract_verse_ids(original), key=_vid_key)
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

    for path in files:
        print(inject_file(path, verses, titles, args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
