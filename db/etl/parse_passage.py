"""
Parse api.bible-shaped passage JSON into structured rows for DB load.

Faithful extraction:
- Hebrew (WLC): word-level tokens with Strong's from char style=w
- Greek (GRCTR): verse-level surface text, split into word tokens (strong often NULL)
- English parallels: joined verse text for KJV / LSV (keyed by modern English verseId)

Alignment (critical — do not invent offsets when API provides them):
- With use-org-id=true, English text nodes carry:
    verseId      = modern English numbering (user-facing)
    verseOrgIds  = original/org id(s) for the same content
- We map org → English from that field (trust + verify), store tokens under English
  verse_id, and keep source_verse_id for provenance.

Titles:
- USFM-like paras (style d, s, s1, …) extracted as superscription/title records.
- Verse body text left as in the edition payload (some LSV verses embed title in v.1).

See docs/365DBR/Verse-Identity-and-Alignment.md
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

# USFM-like para styles treated as titles / superscriptions (not verse body)
TITLE_PARA_STYLES = frozenset({
    "d", "s", "s1", "s2", "s3", "ms", "ms1", "ms2", "mr", "r", "sp", "qa",
})


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


def _collect_text_under(item: dict) -> str:
    parts: list[str] = []
    if item.get("type") == "text" and item.get("text"):
        parts.append(str(item["text"]))
    for child in _walk(item.get("items") or []):
        if child.get("type") == "text" and child.get("text"):
            parts.append(str(child["text"]))
    return "".join(parts).strip()


def extract_titles(content: list | None) -> list[dict[str, Any]]:
    """
    Extract superscription / heading paras (style d, s, …).
    Returns list of {text, style, language_hint}.
    """
    titles: list[dict[str, Any]] = []
    if not content:
        return titles

    def walk(items: list | None):
        if not items:
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            attrs = item.get("attrs") or {}
            style = attrs.get("style") or ""
            if item.get("name") == "para" and style in TITLE_PARA_STYLES:
                text = _collect_text_under(item)
                if text:
                    titles.append({
                        "text": text,
                        "style": style,
                        "annotation_type": (
                            "superscription" if style == "d" else "title"
                        ),
                    })
            if "items" in item:
                walk(item["items"])

    walk(content)
    return titles


def extract_org_english_map_from_content(
    content: list | None,
) -> dict[str, str]:
    """
    From one English parallel content tree:
      source/org id (verseOrgIds[0]) → english verseId
    Only when both present and distinct or same (1:1 still recorded by caller).
    """
    org_to_english: dict[str, str] = {}
    if not content:
        return org_to_english
    for item in _walk(content):
        if item.get("type") != "text":
            continue
        attrs = item.get("attrs") or {}
        eng = attrs.get("verseId")
        orgs = attrs.get("verseOrgIds") or []
        if not eng or not orgs:
            continue
        org = orgs[0]
        if not org:
            continue
        # First wins within this content; prefer stable map
        if org not in org_to_english:
            org_to_english[org] = eng
        elif org_to_english[org] != eng:
            # Conflicting map in same payload — keep first, caller may log
            pass
    return org_to_english


def extract_org_english_map_from_parallels(
    parallels: list | None,
) -> tuple[dict[str, str], str | None]:
    """
    Prefer LSV, then KJV, then any known parallel.
    Returns (org_to_english, established_by_code).
    """
    if not parallels:
        return {}, None

    by_code: dict[str, list] = {}
    for par in parallels:
        code = translation_code_for_bible_id(par.get("bibleId"))
        if code:
            by_code[code] = par.get("content") or []

    for code in ("LSV", "KJV"):
        if code in by_code:
            m = extract_org_english_map_from_content(by_code[code])
            if m:
                return m, code

    for par in parallels:
        code = translation_code_for_bible_id(par.get("bibleId")) or "UNK"
        m = extract_org_english_map_from_content(par.get("content") or [])
        if m:
            return m, code
    return {}, None


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
            # Prefer English verseId; only fall back to org if no verseId
            org = attrs.get("verseOrgIds") or []
            if org:
                vid = org[0]
        if not vid:
            continue
        parts[vid].append(str(text))
    return {
        vid: (
            "".join(chunks)
            if any("\u0590" <= c <= "\u05FF" for c in "".join(chunks))
            else " ".join(s.strip() for s in chunks if s.strip())
        )
        for vid, chunks in parts.items()
    }


def _normalize_english(parts: dict[str, list[str]]) -> dict[str, str]:
    out = {}
    for vid, chunks in parts.items():
        cleaned = []
        for c in chunks:
            t = c.replace("\n", " ").strip()
            if t:
                cleaned.append(t)
        if not cleaned:
            continue
        joined = "".join(chunks)
        if "  " in joined:
            joined = " ".join(joined.split())
        else:
            joined = " ".join(cleaned)
            joined = " ".join(joined.split())
        out[vid] = joined
    return out


def collect_english_verse_text_v2(content: list) -> dict[str, str]:
    """
    English verse text keyed by modern English verseId when present.
    Does not use verseOrgIds as the storage key (that is for alignment only).
    """
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
            continue  # skip text without English verseId (titles handled separately)
        parts[vid].append(str(text))
    return _normalize_english(parts)


def extract_hebrew_tokens(content: list) -> list[dict[str, Any]]:
    """
    Word-tagged Hebrew: char style=w with strong; surface text in child text nodes.
    Returns list of {verse_id, word_order, surface_text, strong_number, language}.
    verse_id here is whatever the original content labels (org id when use-org-id).
    """
    per_verse_orders: dict[str, int] = defaultdict(int)
    tokens: list[dict[str, Any]] = []

    def walk(items: list | None):
        if not items:
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            attrs = item.get("attrs") or {}
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


def apply_english_primary_alignment(
    tokens: list[dict[str, Any]],
    org_to_english: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Remap token verse_id to English-primary id using org→English map.
    Preserves source_verse_id (org/source label from original content).

    Returns (aligned_tokens, source_only_skipped).
    source_only_skipped: org verses not referenced by any English verseOrgIds
    whose BCV string is already claimed as an English display id (typical
    Hebrew superscription counted as v.1). Those must not mix into English v.1
    body tokens; caller may store them as title/superscription text.
    """
    if not org_to_english:
        for t in tokens:
            t.setdefault("source_verse_id", t["verse_id"])
        return tokens, []

    english_claimed = set(org_to_english.values())
    out: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    per_verse_orders: dict[str, int] = defaultdict(int)

    for t in tokens:
        src = t["verse_id"]
        if src in org_to_english:
            eng = org_to_english[src]
        elif src in english_claimed:
            # e.g. org PSA.18.1 superscription while English PSA.18.1 ← org PSA.18.2
            skipped.append({**t, "source_verse_id": src})
            continue
        else:
            eng = src
        per_verse_orders[eng] += 1
        out.append({
            **t,
            "verse_id": eng,
            "source_verse_id": src,
            "word_order": per_verse_orders[eng],
        })
    return out, skipped


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

    source_verse_ids = extract_verse_ids(content)
    tokens_raw = extract_original_tokens(content, language)

    org_to_english, map_from = extract_org_english_map_from_parallels(
        data.get("parallels") or []
    )
    tokens, source_only_skipped = apply_english_primary_alignment(
        tokens_raw, org_to_english
    )

    # Alignments list for DB
    alignments: list[dict[str, str]] = []
    for org, eng in sorted(org_to_english.items()):
        alignments.append({
            "english_verse_id": eng,
            "source_verse_id": org,
            "established_by": map_from or "",
        })

    # Original joined text per *display* (English-primary) verse
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
                    eng = org_to_english.get(vid, vid)
                    verse_text[eng].append(str(item["text"]))
        original_text = {
            vid: "".join(chunks).strip() for vid, chunks in verse_text.items()
        }

    translations: dict[str, dict[str, str]] = {}  # code -> {english_verse_id: text}
    titles: list[dict[str, Any]] = []
    # Titles from original content (rare for Hebrew) + English parallels
    for t in extract_titles(content):
        titles.append({**t, "source": "original"})
    for par in data.get("parallels") or []:
        code = translation_code_for_bible_id(par.get("bibleId"))
        if not code:
            continue
        par_content = par.get("content") or []
        translations[code] = collect_english_verse_text_v2(par_content)
        for t in extract_titles(par_content):
            titles.append({**t, "source": code})

    # Org-only superscription (unmapped source verse colliding with English id)
    if source_only_skipped:
        by_src: dict[str, list[str]] = defaultdict(list)
        for t in source_only_skipped:
            by_src[t["source_verse_id"]].append(t.get("surface_text") or "")
        for src, parts in by_src.items():
            surface = (
                "".join(parts).strip()
                if language == "hebrew"
                else " ".join(p for p in parts if p).strip()
            )
            if surface:
                titles.append({
                    "text": surface,
                    "style": "org-unmapped",
                    "annotation_type": "superscription",
                    "source": f"original:{src}",
                    "source_verse_id": src,
                })

    # Display verse ids = English translation keys ∪ remapped token verses
    display_verse_ids: set[str] = set()
    for t in tokens:
        display_verse_ids.add(t["verse_id"])
    for vmap in translations.values():
        display_verse_ids.update(vmap.keys())

    return {
        "file_ref": file_ref,
        "bible_id": bible_id,
        "book_id": book_id,
        "language": language,
        "verse_ids": sorted(display_verse_ids),  # English-primary when mapped
        "source_verse_ids": sorted(source_verse_ids),
        "tokens": tokens,
        "original_text": original_text,
        "translations": translations,
        "alignments": alignments,
        "org_to_english": org_to_english,
        "alignment_established_by": map_from,
        "titles": titles,
        "source_note": f"{file_ref} bibleId={bible_id}",
    }


def parse_range_endpoints(range_str: str) -> tuple[str, str]:
    """Return (start_verse_id, end_verse_id) for a simple BOOK.C.V-BOOK.C.V range."""
    range_str = range_str.strip()
    if ";" in range_str:
        parts = range_str.split(";")
        start, _ = parse_range_endpoints(parts[0])
        _, end = parse_range_endpoints(parts[-1])
        return start, end
    if "-" in range_str:
        a, b = range_str.split("-", 1)
        return a.strip(), b.strip()
    return range_str, range_str
