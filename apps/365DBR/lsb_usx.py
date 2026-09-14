"""USX 2.x/3.x extraction helpers for the local LSB translation."""

from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

VERSE_ID_RE = re.compile(r"^(?P<book>[A-Za-z0-9]{3})\s+(?P<chapter>\d+):(?P<verse>\d+(?:-\d+)?)$")
TITLE_STYLES = {"d", "qa", "sp"} # Keep only true descriptions

def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]

def _verse_id(value: str, book: str) -> Optional[str]:
    match = VERSE_ID_RE.match(value.strip())
    if not match: return None
    return f"{match.group('book').upper()}.{match.group('chapter')}.{match.group('verse')}"

def _create_text_node(text: str, vid: Optional[str]) -> dict:
    node = {"text": text, "type": "text"}
    if vid:
        node["attrs"] = {"verseId": vid, "verseOrgIds": [vid]}
    return node

def extract_usx(path: str | Path) -> Tuple[Dict[str, list[dict]], Dict[str, list[dict]]]:
    root = ET.parse(path).getroot()
    book = next((str(node.attrib.get("code", "")).upper() for node in root.iter() if _local_name(node.tag) == "book"), "")
    if not book: raise ValueError(f"{path}: missing <book code=...>")

    verses: Dict[str, list[dict]] = {}
    titles: Dict[str, list[dict]] = {}
    pending_titles: list[dict] = []
    active_vid: Optional[str] = None
    first_verse_seen = False

    def process_node(node: ET.Element, current_vid: Optional[str]) -> Tuple[list[dict], Optional[str]]:
        nonlocal active_vid, first_verse_seen
        items = []
        name = _local_name(node.tag)
        
        if name in {"note", "sidebar"}: return items, current_vid
        
        if name == "chapter":
            active_vid = current_vid = None

        sid = node.attrib.get("sid") if name == "verse" else None
        eid = node.attrib.get("eid") if name == "verse" else None
        vid = node.attrib.get("vid") if name != "verse" else None

        if sid or vid:
            parsed_vid = _verse_id(sid or vid, book)
            if parsed_vid:
                current_vid = active_vid = parsed_vid
                verses.setdefault(current_vid, [])
                
                if not first_verse_seen and pending_titles:
                    titles.setdefault(current_vid, []).extend(pending_titles)
                    pending_titles.clear()
                    first_verse_seen = True

        if node.text and node.text.strip() and name not in {"verse", "chapter", "book", "usx"}:
            items.append(_create_text_node(node.text, current_vid))

        for child in list(node):
            child_items, returned_vid = process_node(child, current_vid)
            items.extend(child_items)
            current_vid = active_vid = returned_vid

            if child.tail and child.tail.strip() and name not in {"verse", "chapter", "book", "usx"}:
                items.append(_create_text_node(child.tail, current_vid))

        if eid:
            ended = _verse_id(eid, book)
            if ended and active_vid == ended:
                active_vid = current_vid = None

        style = node.attrib.get("style", "")
        if name == "para":
            # Explicitly drop "s" styles to delete headers like "Yahweh, Save Me"
            if style.startswith("ms") or style.startswith("toc") or style.startswith("mt") or style == "mr" or style == "qa" or style in {"s", "s1", "s2", "s3", "r"}:
                return [], current_vid 
            
            para_node = {"name": "para", "type": "tag", "attrs": {"style": style}, "items": items}
            
            if style in TITLE_STYLES:
                if current_vid:
                    titles.setdefault(current_vid, []).append(para_node)
                else:
                    pending_titles.append(para_node)
                return [], current_vid
            else:
                return [para_node], current_vid
                
        elif name == "char" and items:
            char_node = {"name": "char", "type": "tag", "attrs": {"style": style}, "items": items}
            return [char_node], current_vid

        return items, current_vid

    for child in list(root):
        top_items, _ = process_node(child, None)
        for para in top_items:
            vids_in_para = set()
            def find_vids(items):
                for item in items:
                    if item.get("type") == "text" and "verseId" in item.get("attrs", {}):
                        vids_in_para.add(item["attrs"]["verseId"])
                    if "items" in item: find_vids(item["items"])
            find_vids(para.get("items", []))
            
            if not vids_in_para:
                pending_titles.append(para)
            else:
                primary_vid = sorted(list(vids_in_para), key=lambda x: int(x.split(".")[2].split("-")[0]))[0]
                if pending_titles:
                    titles.setdefault(primary_vid, []).extend(pending_titles)
                    pending_titles.clear()
                    first_verse_seen = True
                for v in vids_in_para:
                    verses.setdefault(v, []).append(para)

    if pending_titles and verses:
        first_v = sorted(verses.keys(), key=lambda x: (x.split(".")[0], int(x.split(".")[1]), int(x.split(".")[2].split("-")[0])))[0]
        titles.setdefault(first_v, []).extend(pending_titles)

    return verses, titles

def extract_directory(directory: str | Path) -> Tuple[Dict[str, list[dict]], Dict[str, list[dict]]]:
    verses: Dict[str, list[dict]] = {}
    titles: Dict[str, list[dict]] = {}
    for path in sorted(Path(directory).rglob("*.usx")):
        book_verses, book_titles = extract_usx(path)
        verses.update(book_verses)
        for vid, items in book_titles.items():
            titles.setdefault(vid, []).extend(items)
    return verses, titles