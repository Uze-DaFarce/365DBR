"""USX 2.x/3.x extraction helpers for the local LSB translation."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, Optional

VERSE_ID_RE = re.compile(r"^(?P<book>[A-Za-z0-9]{3})\s+(?P<chapter>\d+):(?P<verse>\d+(?:-\d+)?)$")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _verse_id(value: str, book: str) -> Optional[str]:
    match = VERSE_ID_RE.match(value.strip())
    if not match:
        return None
    return f"{match.group('book').upper()}.{match.group('chapter')}.{match.group('verse')}"


def extract_usx(path: str | Path) -> Dict[str, str]:
    """Return ``BOOK.chapter.verse`` to cleaned LSB text from one USX file.

    USX milestones are deliberately handled as a document-order state machine:
    a verse may start in one paragraph and end in a later paragraph carrying
    ``vid``. Notes are skipped, while their tail text remains part of the verse.
    """
    root = ET.parse(path).getroot()
    book = next(
        (str(node.attrib.get("code", "")).upper() for node in root.iter() if _local_name(node.tag) == "book"),
        "",
    )
    if not book:
        raise ValueError(f"{path}: missing <book code=...>")

    verses: Dict[str, list[str]] = {}
    active: Optional[str] = None

    def add_text(verse: Optional[str], text: Optional[str]) -> None:
        if verse and text:
            verses.setdefault(verse, []).append(text)

    def walk(node: ET.Element, current: Optional[str]) -> Optional[str]:
        nonlocal active
        name = _local_name(node.tag)
        if name in {"note", "sidebar"}:
            return current

        local = current
        sid = node.attrib.get("sid") if name == "verse" else None
        eid = node.attrib.get("eid") if name == "verse" else None
        vid = node.attrib.get("vid") if name != "verse" else None

        if sid:
            local = _verse_id(sid, book)
            if local:
                verses.setdefault(local, [])
                active = local
        elif vid:
            candidate = _verse_id(vid, book)
            if candidate:
                local = candidate
                verses.setdefault(local, [])
                active = local

        if name not in {"verse", "chapter", "book", "usx"}:
            add_text(local, node.text)

        for child in list(node):
            child_local = walk(child, local)
            add_text(child_local, child.tail)
            local = active if active else local

        if eid:
            ended = _verse_id(eid, book)
            if ended and active == ended:
                active = None
                local = None

        return local

    walk(root, None)
    return {verse_id: _normalize("".join(parts)) for verse_id, parts in verses.items() if _normalize("".join(parts))}


def extract_directory(directory: str | Path) -> Dict[str, str]:
    """Extract all ``*.usx`` files below a directory into one verse map."""
    result: Dict[str, str] = {}
    for path in sorted(Path(directory).rglob("*.usx")):
        result.update(extract_usx(path))
    return result


def inventory_usx(path: str | Path) -> set[str]:
    """Return every verse start declared by a USX file, including empty text."""
    root = ET.parse(path).getroot()
    book = next(
        (str(node.attrib.get("code", "")).upper() for node in root.iter() if _local_name(node.tag) == "book"),
        "",
    )
    result: set[str] = set()
    for node in root.iter():
        if _local_name(node.tag) != "verse":
            continue
        value = node.attrib.get("sid")
        if value:
            verse_id = _verse_id(value, book)
            if verse_id:
                result.add(verse_id)
    return result
