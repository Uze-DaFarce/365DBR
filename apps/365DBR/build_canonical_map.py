"""Build pre-aligned Canonical Reference maps for the React frontend."""
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

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

def build_all_canonical_maps():
    global_heb_headings = {}
    global_heb_verses = {}
    global_semantic_matrix = {}
    
    global_parsed_parallels = defaultdict(lambda: ({}, {}))
    day_payloads = {}
    
    for day_folder in DATA_DIR.iterdir():
        if not (day_folder.is_dir() and day_folder.name.isdigit()): continue
        manifest_path = day_folder / "manifest.json"
        if not manifest_path.exists(): continue
        
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        day_payloads[day_folder] = []
        
        for filename in manifest.get("files", []):
            filepath = day_folder / filename
            if not filepath.exists(): continue
            
            payload = json.loads(filepath.read_text(encoding="utf-8")).get("data", {})
            day_payloads[day_folder].append(payload)
            
            h_heads, h_verses = extract_headings_and_verses(payload.get("content", []))
            for k, v in h_heads.items():
                if k not in global_heb_headings: global_heb_headings[k] = v
            for k, v in h_verses.items():
                if k not in global_heb_verses: global_heb_verses[k] = v
            
            for par in payload.get("parallels", []):
                t_code = par.get("translationCode", "")
                b_id = par.get("bibleId", "")
                code = str(t_code).upper() if t_code else str(b_id).upper()
                
                if "DE4E12AF" in str(b_id).upper() or code == "KJV": code = "KJV"
                elif "01B29F4B" in str(b_id).upper() or "06125ADA" in str(b_id).upper() or code == "LSV": code = "LSV"
                elif "LSB" in code or "8011347E" in str(b_id).upper(): code = "LSB"
                
                p_heads, p_verses = extract_headings_and_verses(par.get("content", []))
                for k, v in p_heads.items():
                    if k not in global_parsed_parallels[code][0]: global_parsed_parallels[code][0][k] = v
                for k, v in p_verses.items():
                    if k not in global_parsed_parallels[code][1]: global_parsed_parallels[code][1][k] = v
                
                if code != "LSB":
                    global_semantic_matrix.update(get_semantic_mapping(par.get("content", [])))

    count = 0
    for day_folder, payloads in day_payloads.items():
        canonical_map = {}
        
        lsb_keys_for_day = set()
        for payload in payloads:
            for par in payload.get("parallels", []):
                code = str(par.get("translationCode", "")).upper() or str(par.get("bibleId", "")).upper()
                if "LSB" in code or "8011347E" in str(par.get("bibleId", "")).upper():
                    _, p_verses = extract_headings_and_verses(par.get("content", []))
                    lsb_keys_for_day.update(p_verses.keys())
                    
        english_vids = sorted(list(lsb_keys_for_day), key=lambda x: (x.split(".")[0], int(x.split(".")[1]), int(x.split(".")[2].split("-")[0])))
        
        for eng_vid in english_vids:
            heb_targets = global_semantic_matrix.get(eng_vid, [eng_vid])
            if isinstance(heb_targets, str):
                heb_targets = [heb_targets]
                
            heb_block_headings = []
            heb_block_verses = []
            
            SUPERSCRIPTION_BOOKS = {"PSA", "HAB", "SNG", "ISA", "JER", "JOL", "JON"}
            b, c, v = eng_vid.split(".")[0], eng_vid.split(".")[1], eng_vid.split(".")[2]
            
            final_display_vid = eng_vid
            
            if b in SUPERSCRIPTION_BOOKS and v == "1":
                heb_v1 = f"{b}.{c}.1"
                
                if heb_targets and heb_targets[0] != heb_v1:
                    first_target = heb_targets[0]
                    tb, tc, tv = first_target.split(".")
                    if tb == b and tc == c and int(tv) > 1:
                        for i in range(1, int(tv)):
                            missing_vid = f"{b}.{c}.{i}"
                            heb_block_headings.extend(global_heb_headings.get(missing_vid, []))
                            heb_block_headings.extend(global_heb_verses.get(missing_vid, []))
                        final_display_vid = f"{b}.{c}.1-{tv}"
                        
                elif len(heb_targets) > 1 and heb_targets[0] == heb_v1:
                    heb_block_headings.extend(global_heb_headings.get(heb_v1, []))
                    heb_block_headings.extend(global_heb_verses.get(heb_v1, []))
                    heb_targets = heb_targets[1:]
                    last_tv = heb_targets[-1].split(".")[2]
                    final_display_vid = f"{b}.{c}.1-{last_tv}"
                    
            for h_vid in heb_targets:
                heb_block_headings.extend(global_heb_headings.get(h_vid, []))
                heb_block_verses.extend(global_heb_verses.get(h_vid, []))
                
            canonical_block = {
                "displayVid": final_display_vid,
                "headings": {
                    "HEB": heb_block_headings,
                    "LSB": global_parsed_parallels["LSB"][0].get(eng_vid, [])
                },
                "verses": {
                    "HEB": heb_block_verses,
                    "LSB": global_parsed_parallels["LSB"][1].get(eng_vid, [])
                }
            }
            
            for trans_code in global_parsed_parallels.keys():
                if trans_code == "LSB": continue
                canonical_block["headings"][trans_code] = global_parsed_parallels[trans_code][0].get(eng_vid, [])
                canonical_block["verses"][trans_code] = global_parsed_parallels[trans_code][1].get(eng_vid, [])
            
            canonical_map[eng_vid] = canonical_block
            
        out_path = day_folder / "canonical_map.json"
        out_path.write_text(json.dumps(canonical_map, ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1
        
    print(f"✅ Generated canonical_map.json for {count} days.")

if __name__ == "__main__":
    build_all_canonical_maps()