"""
Parse api.bible-shaped passage JSON into structured rows for DB load.

Faithful extraction:
- Hebrew (WLC): word-level tokens with Strong's from char style=w
- Greek (GRCTR): verse-level surface text, split into word tokens (strong often NULL)
- English parallels: joined verse text for KJV / LSV
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


# api.bible ids used by the pipeline
BIBLE_ID_TO_TRANS_CODE = {
    "de4e12af7f28f599-01": "KJV",
    "01b29f4b342acc35-01": "LSV",
}
# prefixes for loose match (some payloads vary)
BIBLE_ID_PREFIX_TO_TRANS = {
    "de4e12af": "KJV",
    "01b29f4b": "LSV",
    "06125ada": "LSV",  # historical LSV alt seen in client config
}

NT_BOOKS = {
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH",
    "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS",
    "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
}


def language_for_book(book_code: str) -> str:
    return "greek" if book_code in NT_BOOKS else "hebrew"


def translation_code_for_bible_id(bible_id: str | None) -> str | None:
    if not bible_id:
        return None
    if bible_id in BIBLE_ID_TO_TRANS_CODE:
        return BIBLE_ID_TO_TRANS_CODE[bible_id]
    for prefix, code in BIBLE_ID_PREFIX_TO_TRANS.items():
        if bible_id.startswith(prefix) or prefix in bible_id:
            return code
    return None


def _walk(items: list | None):
    if not items:
        return
    for item in items:
        if isinstance(item, dict):
            yield item
            if "items" in item:
                yield from _walk(item["items"])


def extract_verse_ids(content: list) -> set[str]:
    found: set[str] = set()
    for item in _walk(content):
        attrs = item.get("attrs") or {}
        if "verseId" in attrs:
            found.add(attrs["verseId"])
    return found


def collect_english_verse_text(content: list) -> dict[str, str]:
    """Join text nodes per verseId (space-separated English)."""
    parts: dict[str, list[str]] = defaultdict(list)
    for item in _walk(content):
        if item.get("type") != "text":
            continue
        text = item.get("text")
        if not text or not str(text).strip():
            continue
        attrs = item.get("attrs") or {}
        vid = attrs.get("verseId")
        if not vid:
            # some nodes use verseOrgIds only
            org = attrs.get("verseOrgIds") or []
            if org:
                vid = org[0]
        if not vid:
            continue
        parts[vid].append(str(text))
    return {vid: "".join(chunks) if any("\u0590" <= c <= "\u05FF" for c in "".join(chunks))
            else " ".join(s.strip() for s in chunks if s.strip())
            for vid, chunks in parts.items()}


def _normalize_english(parts: dict[str, list[str]]) -> dict[str, str]:
    out = {}
    for vid, chunks in parts.items():
        # Prefer space join for Latin scripts; preserve internal spaces already present
        cleaned = []
        for c in chunks:
            t = c.replace("\n", " ").strip()
            if t:
                cleaned.append(t)
        if not cleaned:
            continue
        # If chunks already include trailing spaces from source, join without extra space
        joined = "".join(chunks)
        if "  " in joined:
            joined = " ".join(joined.split())
        else:
            # typical api.bible English: fragments without consistent spacing
            joined = " ".join(cleaned)
            joined = " ".join(joined.split())
        out[vid] = joined
    return out


def collect_english_verse_text_v2(content: list) -> dict[str, str]:
    parts: dict[str, list[str]] = defaultdict(list)
    for item in _walk(content):
        if item.get("type") != "text":
            continue
        text = item.get("text")
        if text is None:
            continue
        attrs = item.get("attrs") or {}
        vid = attrs.get("verseId")
        if not vid:
            org = attrs.get("verseOrgIds") or []
            if org:
                vid = org[0]
        if not vid:
            continue
        parts[vid].append(str(text))
    return _normalize_english(parts)


def extract_hebrew_tokens(content: list) -> list[dict[str, Any]]:
    """
    Word-tagged Hebrew: char style=w with strong; surface text in child text nodes.
    Returns list of {verse_id, word_order, surface_text, strong_number, language}.
    """
    # Group by verse, preserve document order
    per_verse_orders: dict[str, int] = defaultdict(int)
    tokens: list[dict[str, Any]] = []

    def walk(items: list | None):
        if not items:
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            attrs = item.get("attrs") or {}
            # Strong's-tagged word
            if item.get("name") == "char" and attrs.get("style") == "w" and attrs.get("strong"):
                strong = attrs["strong"]
                surface_parts = []
                verse_id = None
                for child in _walk(item.get("items") or []):
                    if child.get("type") == "text" and child.get("text"):
                        surface_parts.append(str(child["text"]))
                        ca = child.get("attrs") or {}
                        if ca.get("verseId"):
                            verse_id = ca["verseId"]
                        elif ca.get("verseOrgIds"):
                            verse_id = ca["verseOrgIds"][0]
                surface = "".join(surface_parts).strip()
                if verse_id and surface:
                    per_verse_orders[verse_id] += 1
                    tokens.append({
                        "verse_id": verse_id,
                        "word_order": per_verse_orders[verse_id],
                        "surface_text": surface,
                        "strong_number": strong,
                        "language": "hebrew",
                    })
            elif "items" in item:
                walk(item["items"])

    walk(content)
    return tokens


def extract_greek_tokens(content: list) -> list[dict[str, Any]]:
    """
    GRCTR-style running Greek: text nodes with verseId hold full verse surface.
    Split on whitespace into ordered tokens; strong_number NULL.
    """
    tokens: list[dict[str, Any]] = []
    # Preserve first-seen order of verses
    verse_text: dict[str, list[str]] = defaultdict(list)
    verse_order_seen: list[str] = []

    for item in _walk(content):
        if item.get("type") != "text":
            continue
        text = item.get("text")
        if not text or not str(text).strip():
            continue
        attrs = item.get("attrs") or {}
        vid = attrs.get("verseId")
        if not vid:
            org = attrs.get("verseOrgIds") or []
            if org:
                vid = org[0]
        if not vid:
            continue
        if vid not in verse_text:
            verse_order_seen.append(vid)
        verse_text[vid].append(str(text))

    for vid in verse_order_seen:
        full = "".join(verse_text[vid]).strip()
        # split on whitespace; keep punctuation attached to words (simple, reversible enough)
        words = full.split()
        for i, w in enumerate(words, start=1):
            tokens.append({
                "verse_id": vid,
                "word_order": i,
                "surface_text": w,
                "strong_number": None,
                "language": "greek",
            })
    return tokens


def extract_original_tokens(content: list, language: str) -> list[dict[str, Any]]:
    if language == "hebrew":
        return extract_hebrew_tokens(content)
    return extract_greek_tokens(content)


def parse_passage_payload(raw: dict, file_ref: str) -> dict[str, Any]:
    """
    Parse one passage JSON file (api.bible envelope with data.content + parallels).
    """
    if "data" not in raw:
        raise ValueError(f"{file_ref}: missing data key")
    data = raw["data"]
    content = data.get("content")
    if not content:
        raise ValueError(f"{file_ref}: empty content")

    bible_id = data.get("bibleId")
    book_id = data.get("bookId") or (data.get("id") or "").split(".")[0]
    language = language_for_book(book_id)

    verse_ids = extract_verse_ids(content)
    tokens = extract_original_tokens(content, language)

    # Original joined text per verse (for verification / optional display)
    if language == "hebrew":
        orig_parts: dict[str, list[str]] = defaultdict(list)
        for t in tokens:
            orig_parts[t["verse_id"]].append(t["surface_text"])
        original_text = {vid: "".join(parts) for vid, parts in orig_parts.items()}
    else:
        original_text = {}
        verse_text: dict[str, list[str]] = defaultdict(list)
        for item in _walk(content):
            if item.get("type") == "text" and item.get("text"):
                attrs = item.get("attrs") or {}
                vid = attrs.get("verseId") or (attrs.get("verseOrgIds") or [None])[0]
                if vid:
                    verse_text[vid].append(str(item["text"]))
        original_text = {vid: "".join(chunks).strip() for vid, chunks in verse_text.items()}

    translations: dict[str, dict[str, str]] = {}  # code -> {verse_id: text}
    for par in data.get("parallels") or []:
        code = translation_code_for_bible_id(par.get("bibleId"))
        if not code:
            continue
        translations[code] = collect_english_verse_text_v2(par.get("content") or [])

    return {
        "file_ref": file_ref,
        "bible_id": bible_id,
        "book_id": book_id,
        "language": language,
        "verse_ids": sorted(verse_ids),
        "tokens": tokens,
        "original_text": original_text,
        "translations": translations,
        "source_note": f"{file_ref} bibleId={bible_id}",
    }


def parse_range_endpoints(range_str: str) -> tuple[str, str]:
    """Return (start_verse_id, end_verse_id) for a simple BOOK.C.V-BOOK.C.V range."""
    range_str = range_str.strip()
    if ";" in range_str:
        # multi-segment: use first start and last end
        parts = range_str.split(";")
        start, _ = parse_range_endpoints(parts[0])
        _, end = parse_range_endpoints(parts[-1])
        return start, end
    if "-" in range_str:
        a, b = range_str.split("-", 1)
        return a.strip(), b.strip()
    return range_str, range_str
