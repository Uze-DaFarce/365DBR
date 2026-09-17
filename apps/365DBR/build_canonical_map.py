"""Build pre-aligned Canonical Reference maps for the React frontend."""
import json
from pathlib import Path
from collections import defaultdict

from bible_common import ALL_BOOKS

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ENGLISH_CODES = ("LSB", "KJV", "LSV")

def filter_ast_for_vid(node, vid: str):
    if not isinstance(node, dict): return node
    if node.get("type") == "text":
        node_vid = node.get("attrs", {}).get("verseId")
        if node_vid and node_vid != vid:
            return None
        return node

    def contains_target(n):
        if not isinstance(n, dict): return False
        if n.get("type") == "text":
            return n.get("attrs", {}).get("verseId") == vid
        return any(contains_target(child) for child in n.get("items", []))

    if not contains_target(node):
        return None

    new_items = []
    for item in node.get("items", []):
        filtered = filter_ast_for_vid(item, vid)
        if filtered is not None:
            new_items.append(filtered)

    if not new_items and node.get("name") != "para":
        return None

    new_node = node.copy()
    new_node["items"] = new_items
    return new_node

def extract_headings_and_verses(content_array: list) -> tuple:
    headings = defaultdict(list)
    verses = defaultdict(list)
    pending_headings = []

    for node in content_array:
        if not isinstance(node, dict): continue
        
        vids = set()
        def find_vids(items):
            for item in items:
                if not isinstance(item, dict): continue
                if item.get("type") == "text" and "verseId" in item.get("attrs", {}):
                    vids.add(item["attrs"]["verseId"])
                if "items" in item: find_vids(item["items"])
        
        find_vids(node.get("items", []))
        
        if not vids:
            pending_headings.append(node)
        else:
            primary_vid = sorted(list(vids), key=lambda x: int(x.split(".")[2].split("-")[0]))[0]
            if pending_headings:
                headings[primary_vid].extend(pending_headings)
                pending_headings = []
                
            for v in vids:
                filtered_node = filter_ast_for_vid(node, v)
                if filtered_node and filtered_node not in verses[v]:
                    verses[v].append(filtered_node)
                
    return headings, verses

def get_semantic_mapping(content_array: list) -> dict:
    mapping = {}
    def find_orgs(items):
        for item in items:
            if not isinstance(item, dict): continue
            if item.get("type") == "text":
                attrs = item.get("attrs", {})
                v_id = attrs.get("verseId")
                org_ids = attrs.get("verseOrgIds", [])
                if v_id and org_ids:
                    if len(org_ids) > 1 or org_ids[0] != v_id:
                        if v_id not in mapping:
                            mapping[v_id] = org_ids
            if "items" in item:
                find_orgs(item["items"])
    find_orgs(content_array)
    return mapping


def translation_code(par: dict) -> str:
    t_code = par.get("translationCode", "")
    b_id = str(par.get("bibleId", "")).upper()
    code = str(t_code).upper() if t_code else b_id
    if "DE4E12AF" in b_id or code == "KJV":
        return "KJV"
    if "01B29F4B" in b_id or "06125ADA" in b_id or code == "LSV":
        return "LSV"
    if "LSB" in code or "8011347E" in b_id:
        return "LSB"
    return code or "UNK"


def merge_first(dst: dict, src: dict) -> None:
    for key, value in src.items():
        if key not in dst:
            dst[key] = value


def vid_sort_key(vid: str):
    parts = str(vid).split(".")
    if len(parts) != 3:
        return (99, 0, 0, vid)
    book, chapter, verse = parts
    try:
        book_i = ALL_BOOKS.index(book) if book in ALL_BOOKS else 99
        return (book_i, int(chapter), int(str(verse).split("-")[0]))
    except ValueError:
        return (99, 0, 0, vid)


def org_targets(semantic: dict, eng_vid: str) -> list:
    targets = semantic.get(eng_vid, [eng_vid])
    if isinstance(targets, str):
        targets = [targets]
    return list(targets)


def build_all_canonical_maps():
    global_heb_headings = {}
    global_heb_verses = {}
    global_semantic_matrix = {}
    global_parsed_parallels = defaultdict(lambda: ({}, {}))
    day_payloads = {}

    day_dirs = sorted(
        (p for p in DATA_DIR.iterdir() if p.is_dir() and p.name.isdigit()),
        key=lambda p: p.name,
    )

    for day_folder in day_dirs:
        manifest_path = day_folder / "manifest.json"
        if not manifest_path.exists():
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        day_payloads[day_folder] = []

        for filename in manifest.get("files", []):
            filepath = day_folder / filename
            if not filepath.exists():
                continue

            payload = json.loads(filepath.read_text(encoding="utf-8")).get("data", {})
            day_payloads[day_folder].append(payload)

            h_heads, h_verses = extract_headings_and_verses(payload.get("content", []))
            merge_first(global_heb_headings, h_heads)
            merge_first(global_heb_verses, h_verses)

            for par in payload.get("parallels", []):
                code = translation_code(par)
                p_heads, p_verses = extract_headings_and_verses(par.get("content", []))
                merge_first(global_parsed_parallels[code][0], p_heads)
                merge_first(global_parsed_parallels[code][1], p_verses)
                if code != "LSB":
                    merge_first(global_semantic_matrix, get_semantic_mapping(par.get("content", [])))

    claimed_orgs = set()
    for eng_vid, targets in global_semantic_matrix.items():
        claimed_orgs.update(org_targets(global_semantic_matrix, eng_vid))

    count = 0
    chapter_days = defaultdict(lambda: defaultdict(list))
    for day_folder, payloads in day_payloads.items():
        english_vids = set()
        for payload in payloads:
            for par in payload.get("parallels", []):
                code = translation_code(par)
                if code not in ENGLISH_CODES:
                    continue
                _, p_verses = extract_headings_and_verses(par.get("content", []))
                english_vids.update(p_verses.keys())

        english_vids = sorted(english_vids, key=vid_sort_key)

        canonical_map = {}
        for eng_vid in english_vids:
            heb_targets = org_targets(global_semantic_matrix, eng_vid)
            heb_block_headings = []
            heb_block_verses = []
            parts = str(eng_vid).split(".")
            verse_num = parts[2].split("-")[0] if len(parts) == 3 else ""

            # Unclaimed preceding org verses in this chapter (Psalm superscriptions).
            # Never attach an org verse already mapped to another English BCV (e.g. JON.1.17 ← org 2.1).
            if len(parts) == 3 and verse_num == "1" and heb_targets:
                first = str(heb_targets[0]).split(".")
                if len(first) == 3 and first[0] == parts[0] and first[1] == parts[1]:
                    try:
                        first_n = int(first[2].split("-")[0])
                    except ValueError:
                        first_n = 1
                    for i in range(1, first_n):
                        missing_vid = f"{parts[0]}.{parts[1]}.{i}"
                        if missing_vid in claimed_orgs:
                            continue
                        heb_block_headings.extend(global_heb_headings.get(missing_vid, []))
                        heb_block_headings.extend(global_heb_verses.get(missing_vid, []))

            for h_vid in heb_targets:
                heb_block_headings.extend(global_heb_headings.get(h_vid, []))
                heb_block_verses.extend(global_heb_verses.get(h_vid, []))

            canonical_block = {
                "displayVid": eng_vid,
                "headings": {"HEB": heb_block_headings},
                "verses": {"HEB": heb_block_verses},
            }
            for trans_code, (heads, verses) in global_parsed_parallels.items():
                canonical_block["headings"][trans_code] = heads.get(eng_vid, [])
                canonical_block["verses"][trans_code] = verses.get(eng_vid, [])

            canonical_map[eng_vid] = canonical_block
            parts = str(eng_vid).split(".")
            if len(parts) >= 2:
                book, ch = parts[0], str(int(parts[1]))
                day_id = day_folder.name
                if day_id not in chapter_days[book][ch]:
                    chapter_days[book][ch].append(day_id)

        out_path = day_folder / "canonical_map.json"
        out_path.write_text(json.dumps(canonical_map, ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1

    index_path = DATA_DIR / "chapter_days.json"
    index_path.write_text(
        json.dumps({book: dict(chs) for book, chs in chapter_days.items()}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Generated canonical_map.json for {count} days.")
    print(f"Wrote {index_path.name} ({sum(len(chs) for chs in chapter_days.values())} chapters).")

if __name__ == "__main__":
    build_all_canonical_maps()