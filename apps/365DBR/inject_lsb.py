"""Inject local LSB USX text into daily reading JSON parallels (offline)."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

from bible_common import ALL_BOOKS, atomic_write_json, extract_verse_ids, is_verse_in_range
from lsb_usx import extract_directory

ROOT = Path(__file__).resolve().parent
LSB_BIBLE_ID = "8011347e1aa60e8a-01"
SKIP_NAMES = {"manifest.json", "readings.json", "omissions_cache.json", "canonical_map.json"}
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
    """English BCV only. Original `content` verseIds are org numbering — do not mix them in."""
    ids: set[str] = set()
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
    ids = set(english_verse_ids(data))
    bounds = _filename_range(path.stem)
    if bounds:
        s_book, s_chap, s_verse, e_book, e_chap, e_verse = bounds
        for vid in usx_verses:
            if is_verse_in_range(vid, s_book, s_chap, s_verse, e_book, e_chap, e_verse):
                ids.add(vid)
    return sorted(ids, key=_vid_key)

def _verse_allowed(vid: str, allowed: set[str]) -> bool:
    if vid in allowed:
        return True
    book_ch, _, span = vid.rpartition(".")
    if "-" not in span:
        return False
    start_s, end_s = span.split("-", 1)
    try:
        start, end = int(start_s), int(end_s)
    except ValueError:
        return False
    return any(f"{book_ch}.{n}" in allowed for n in range(start, end + 1))


def _prune_node(node, allowed: set[str]):
    """Copy a USX block, dropping text whose verseId is outside this reading."""
    if not isinstance(node, dict):
        return copy.deepcopy(node)
    if node.get("type") == "text":
        vid = (node.get("attrs") or {}).get("verseId")
        if vid and not _verse_allowed(vid, allowed):
            return None
        return copy.deepcopy(node)
    items = node.get("items")
    if not isinstance(items, list):
        return copy.deepcopy(node)
    pruned_items = []
    for child in items:
        pruned = _prune_node(child, allowed)
        if pruned is not None:
            pruned_items.append(pruned)
    if node.get("type") == "tag" and not any(_has_visible_text(item) for item in pruned_items):
        return None
    cloned = copy.deepcopy({key: value for key, value in node.items() if key != "items"})
    cloned["items"] = pruned_items
    return cloned


def _has_visible_text(node) -> bool:
    if not isinstance(node, dict):
        return False
    if node.get("type") == "text":
        return bool((node.get("text") or "").strip())
    return any(_has_visible_text(child) for child in node.get("items") or [])


def build_lsb_content(verse_ids: list[str], verses: dict, titles: dict) -> list:
    """One copy of each paragraph, limited to the requested verses.

    lsb_usx stores a multi-verse paragraph on every verse in it. Concatenating
    those lists repeats the paragraph and keeps the verses just outside the reading.
    """
    allowed = set(verse_ids)
    content = []
    seen: set[int] = set()
    for vid in verse_ids:
        for block in (titles.get(vid) or []):
            if id(block) in seen:
                continue
            seen.add(id(block))
            pruned = _prune_node(block, allowed)
            if pruned is not None:
                content.append(pruned)
        for block in (verses.get(vid) or []):
            if id(block) in seen:
                continue
            seen.add(id(block))
            pruned = _prune_node(block, allowed)
            if pruned is not None:
                content.append(pruned)
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

    for path in files:
        print(inject_file(path, verses, titles, args.force))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())