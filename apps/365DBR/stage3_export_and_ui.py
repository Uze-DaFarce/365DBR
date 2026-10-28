import sys, os, json, re, subprocess
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps" / "365DBR"
DB_DIR = REPO_ROOT / "db"
sys.path.insert(0, str(APP_DIR))

import lsb_usx
import build_canonical_map as bcm

def psql_json(sql: str) -> list[dict]:
    """Run SQL inside mt-sinai-365dbr-postgres via docker exec (zero TCP/password issues) and return JSON rows."""
    wrapped = f"SELECT COALESCE(json_agg(t), '[]'::json) FROM ({sql}) t;"
    res = subprocess.run(
        ["docker", "exec", "-i", "mt-sinai-365dbr-postgres", "psql", "-U", "365dbr_dev", "-d", "mt_sinai_365dbr", "-t", "-A", "-q"],
        input=wrapped,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    out = res.stdout.strip()
    return json.loads(out) if out else []

def make_simple_ast(vid: str, text: str) -> list:
    return [{
        "name": "para",
        "type": "tag",
        "attrs": {"style": "p"},
        "items": [{"text": text, "type": "text", "attrs": {"verseId": vid}}]
    }]

def load_usx_corpus(dirs, is_web=False):
    verses = defaultdict(list)
    headings = defaultdict(list)
    seen_files = set()
    for d in dirs:
        if not d.exists():
            continue
        for usx_path in sorted(d.glob("*.usx")):
            if usx_path.name in seen_files:
                continue
            seen_files.add(usx_path.name)
            v_map, h_map = lsb_usx.extract_usx(usx_path)
            for vid, blocks in v_map.items():
                for b in blocks:
                    filtered = bcm.filter_ast_for_vid(b, vid)
                    if filtered and filtered not in verses[vid]:
                        verses[vid].append(filtered)
            for vid, h_blocks in h_map.items():
                for hb in h_blocks:
                    if hb not in headings[vid]:
                        headings[vid].append(hb)
    if is_web:
        for src_v, dst_v in [("ROM.14.24", "ROM.16.25"), ("ROM.14.25", "ROM.16.26"), ("ROM.14.26", "ROM.16.27")]:
            if not verses.get(dst_v) and verses.get(src_v):
                verses[dst_v] = json.loads(json.dumps(verses[src_v]).replace(f'"{src_v}"', f'"{dst_v}"'))
    return verses, headings

def step1_augment_canonical_maps():
    print("--- Step 1: Loading WEB & YLT USX AST + DB Fallbacks via docker exec ---")
    web_dirs = [
        APP_DIR / "RAW" / "WEB" / "release" / "USX_1",
        APP_DIR / "RAW" / "WEB" / "release" / "USX_2",
        APP_DIR / "RAW" / "WEB" / "release" / "USX_3",
    ]
    ylt_dirs = [APP_DIR / "RAW" / "YLT" / "release" / "USX_1"]
    web_v, web_h = load_usx_corpus(web_dirs, is_web=True)
    ylt_v, ylt_h = load_usx_corpus(ylt_dirs, is_web=False)
    print(f"Loaded USX ASTs -> WEB: {len(web_v)} verses, YLT: {len(ylt_v)} verses")

    db_texts = defaultdict(dict)
    rows = psql_json("""
        SELECT v.id, UPPER(t.code) AS code, vt.text
        FROM verse_translations vt
        JOIN translations t ON t.id = vt.translation_id
        JOIN verses v ON v.id = vt.verse_id
    """)
    for r in rows:
        db_texts[r["id"]][r["code"]] = r["text"]

    restored_rows = psql_json("""
        SELECT dr.day_key, v.id AS vid
        FROM daily_passages dp
        JOIN daily_readings dr ON dr.id = dp.daily_reading_id
        JOIN verses v ON v.book_code = dp.book_code
          AND v.verse_order BETWEEN
            (SELECT verse_order FROM verses WHERE id = dp.start_verse_id)
            AND
            (SELECT verse_order FROM verses WHERE id = dp.end_verse_id)
        WHERE v.id IN ('LUK.17.37', 'ACT.15.41', 'ACT.24.27')
    """)
    restored_by_day = defaultdict(list)
    for r in restored_rows:
        restored_by_day[r["day_key"]].append(r["vid"])

    orig_rows = psql_json("""
        SELECT verse_id, string_agg(surface_text, ' ' ORDER BY word_order) AS txt
        FROM original_tokens
        WHERE verse_id IN ('LUK.17.37', 'ACT.15.41', 'ACT.24.27')
        GROUP BY verse_id
    """)
    orig_restored = {r["verse_id"]: r["txt"] for r in orig_rows}

    data_dir = APP_DIR / "data"
    updated_days = 0
    for day_dir in sorted(data_dir.iterdir()):
        if not day_dir.is_dir() or not re.match(r"^\d{4}$", day_dir.name):
            continue
        cm_path = day_dir / "canonical_map.json"
        if not cm_path.exists():
            continue
        cm = json.loads(cm_path.read_text(encoding="utf-8"))
        cm.pop("REV.12.18", None)

        for rvid in restored_by_day.get(day_dir.name, []):
            if rvid not in cm:
                cm[rvid] = {"headings": {}, "verses": {}}
            if "HEB" not in cm[rvid]["verses"] and orig_restored.get(rvid):
                cm[rvid]["verses"]["HEB"] = make_simple_ast(rvid, orig_restored[rvid])

        for vid, block in cm.items():
            v_dict = block.setdefault("verses", {})
            h_dict = block.setdefault("headings", {})
            if web_v.get(vid):
                v_dict["WEB"] = web_v[vid]
            elif db_texts.get(vid, {}).get("WEB"):
                v_dict["WEB"] = make_simple_ast(vid, db_texts[vid]["WEB"])
            if web_h.get(vid):
                h_dict["WEB"] = web_h[vid]

            if ylt_v.get(vid):
                v_dict["YLT"] = ylt_v[vid]
            elif db_texts.get(vid, {}).get("YLT"):
                v_dict["YLT"] = make_simple_ast(vid, db_texts[vid]["YLT"])
            if ylt_h.get(vid):
                h_dict["YLT"] = ylt_h[vid]

            for code in ("LSB", "KJV", "LSV", "WEB", "YLT"):
                if code not in v_dict and db_texts.get(vid, {}).get(code):
                    v_dict[code] = make_simple_ast(vid, db_texts[vid][code])

        cm_path.write_text(json.dumps(cm, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        updated_days += 1
    print(f"Updated canonical_map.json across {updated_days} day folders.")

def step2_update_frontend_files():
    print("--- Step 2: Updating index.html & bible.html ---")
    new_focal_idx = """const prevFocal = focalTranslation;
            setFocalTranslation(newFocal);
            if (newFocal === compareTranslation) {
              if (prevFocal && prevFocal !== newFocal && availableTranslations.includes(prevFocal)) {
                setCompareTranslation(prevFocal);
              } else {
                const alt = availableTranslations.find((k) => k !== newFocal);
                if (alt) setCompareTranslation(alt);
              }
            }"""
    old_strong_hdr = """Strong’s <span className="font-mono">{selected.strong}</span>"""
    new_strong_hdr = """Strong’s <span className="font-mono">{selected.strong}</span>{selected.transliteration ? <span className="ml-1.5 italic text-stone-600">({selected.transliteration})</span> : null}{selected.gloss ? <span className="ml-1.5 font-semibold text-amber-900">— “{selected.gloss}”</span> : null}"""

    idx_path = APP_DIR / "index.html"
    idx_text = idx_path.read_text(encoding="utf-8")
    if "translationCode: 'KJV'" not in idx_text:
        idx_text = re.sub(
            r"kjv:\s*\{\s*idPrefix:\s*'de4e12af',\s*label:\s*'KJV - King James Version'\s*\}",
            "kjv: {\n            idPrefix: 'de4e12af',\n            translationCode: 'KJV',\n            label: 'KJV - King James Version'\n          }",
            idx_text
        )
    if "translationCode: 'LSV'" not in idx_text:
        idx_text = re.sub(
            r"lsv:\s*\{\s*idPrefix:\s*'06125ada',[^\n]*\n\s*altIds:\s*\['01b29f4b342acc35-01'\],\s*\n\s*label:\s*'LSV - Literal Standard Version',",
            "lsv: {\n            idPrefix: '06125ada',\n            altIds: ['01b29f4b342acc35-01'],\n            translationCode: 'LSV',\n            label: 'LSV - Literal Standard Version',",
            idx_text
        )
    if "translationCode: 'YLT'" not in idx_text:
        idx_text = re.sub(
            r"web:\s*\{\s*idPrefix:\s*'9879dbb7',\s*label:\s*'WEB - World English Bible'\s*\}",
            "web: {\n            idPrefix: '9879dbb7',\n            translationCode: 'WEB',\n            label: 'WEB - World English Bible'\n          },\n          ylt: {\n            idPrefix: 'ylt',\n            translationCode: 'YLT',\n            label: \"YLT - Young's Literal Translation\"\n          }",
            idx_text
        )
    idx_text = re.sub(
        r"const prevFocal = focalTranslation;\s*setFocalTranslation\(newFocal\);\s*if \(prevFocal && prevFocal !== newFocal && availableTranslations\.includes\(prevFocal\)\) \{\s*setCompareTranslation\(prevFocal\);\s*\} else if \(newFocal === compareTranslation\) \{\s*const alt = availableTranslations\.find\(\(k\) => k !== newFocal\);\s*if \(alt\) setCompareTranslation\(alt\);\s*\}",
        new_focal_idx,
        idx_text
    )
    idx_text = idx_text.replace("setSelected({ strong: token.strong, surface: token.surface, order: token.order });", "setSelected({ ...token });")
    if old_strong_hdr in idx_text and "selected.gloss" not in idx_text:
        idx_text = idx_text.replace(old_strong_hdr, new_strong_hdr, 1)
    idx_path.write_text(idx_text, encoding="utf-8")

    bh_path = APP_DIR / "bible.html"
    bh_text = bh_path.read_text(encoding="utf-8")
    bh_text = bh_text.replace("kjv: { idPrefix: 'de4e12af', label: 'KJV - King James Version' },", "kjv: { idPrefix: 'de4e12af', translationCode: 'KJV', label: 'KJV - King James Version' },")
    bh_text = bh_text.replace("lsv: { idPrefix: '06125ada', altIds: ['01b29f4b342acc35-01'], label: 'LSV - Literal Standard Version',", "lsv: { idPrefix: '06125ada', altIds: ['01b29f4b342acc35-01'], translationCode: 'LSV', label: 'LSV - Literal Standard Version',")
    if "ylt:" not in bh_text:
        bh_text = bh_text.replace(
            "web: { idPrefix: '9879dbb7', label: 'WEB - World English Bible' },",
            "web: { idPrefix: '9879dbb7', translationCode: 'WEB', label: 'WEB - World English Bible' },\n        ylt: { idPrefix: 'ylt', translationCode: 'YLT', label: \"YLT - Young's Literal Translation\" },"
        )
    bh_text = re.sub(
        r"const prevFocal = focalTranslation;\s*setFocalTranslation\(newFocal\);\s*if \(prevFocal && prevFocal !== newFocal && availableTranslations\.includes\(prevFocal\)\) \{\s*setCompareTranslation\(prevFocal\);\s*\} else if \(newFocal === compareTranslation\) \{\s*const alt = availableTranslations\.find\(\(k\) => k !== newFocal\);\s*if \(alt\) setCompareTranslation\(alt\);\s*\}",
        new_focal_idx,
        bh_text
    )
    bh_text = bh_text.replace("setSelected({ strong: token.strong, surface: token.surface, order: token.order });", "setSelected({ ...token });")
    if old_strong_hdr in bh_text and "selected.gloss" not in bh_text:
        bh_text = bh_text.replace(old_strong_hdr, new_strong_hdr, 1)
    bh_path.write_text(bh_text, encoding="utf-8")
    print("  index.html & bible.html updated.")

def step3_export_ws_via_docker():
    print("--- Step 3: Exporting apps/365DBR/ws/ (verse/*.json & strong/*.json) via docker exec ---")
    out_dir = APP_DIR / "ws"
    verse_dir = out_dir / "verse"
    strong_dir = out_dir / "strong"
    verse_dir.mkdir(parents=True, exist_ok=True)
    strong_dir.mkdir(parents=True, exist_ok=True)

    books = [r["code"] for r in psql_json("SELECT code FROM books ORDER BY canonical_order")]
    for bk in books:
        v_rows = psql_json(f"SELECT id, book_code, chapter, verse, verse_order FROM verses WHERE book_code = '{bk}' ORDER BY verse_order")
        t_rows = psql_json(f"""
            SELECT it.verse_id, it.word_order, it.language, it.surface_text, it.strong_number,
                   it.lemma, it.morph, it.source_verse_id, it.lex_word, it.transliteration, it.gloss
            FROM v_interlinear_tokens it
            JOIN verses v ON v.id = it.verse_id
            WHERE v.book_code = '{bk}'
            ORDER BY v.verse_order, it.word_order
        """)
        tr_rows = psql_json(f"""
            SELECT vt.verse_id, UPPER(t.code) AS code, vt.text
            FROM verse_translations vt
            JOIN translations t ON t.id = vt.translation_id
            JOIN verses v ON v.id = vt.verse_id
            WHERE v.book_code = '{bk}'
        """)
        tok_by_v = defaultdict(list)
        for t in t_rows:
            tok_by_v[t["verse_id"]].append(t)
        tr_by_v = defaultdict(dict)
        for tr in tr_rows:
            tr_by_v[tr["verse_id"]][tr["code"]] = tr["text"]

        book_map = {}
        for v in v_rows:
            vid = v["id"]
            toks = tok_by_v.get(vid, [])
            lang = toks[0]["language"] if toks else ("greek" if bk in ("MAT","MRK","LUK","JHN","ACT","ROM","1CO","2CO","GAL","EPH","PHP","COL","1TH","2TH","1TI","2TI","TIT","PHM","HEB","JAS","1PE","2PE","1JN","2JN","3JN","JUD","REV") else "hebrew")
            sep = "" if lang == "hebrew" else " "
            book_map[vid] = {
                "ok": True,
                "verse_id": vid,
                "book_code": bk,
                "chapter": v["chapter"],
                "verse": v["verse"],
                "verse_order": v["verse_order"],
                "original": {
                    "text": sep.join(x["surface_text"] for x in toks) if lang == "greek" else " ".join(x["surface_text"] for x in toks),
                    "language": lang,
                    "tokens": [
                        {
                            "order": x["word_order"],
                            "surface": x["surface_text"],
                            "strong": x["strong_number"],
                            "lemma": x["lemma"],
                            "morph": x["morph"],
                            "lex_word": x["lex_word"],
                            "transliteration": x["transliteration"],
                            "gloss": x["gloss"],
                        }
                        for x in toks
                    ],
                },
                "translations": tr_by_v.get(vid, {}),
                "annotations": [],
            }
        (verse_dir / f"{bk}.json").write_text(json.dumps(book_map, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  Wrote {len(books)} book files to apps/365DBR/ws/verse/")

if __name__ == "__main__":
    step1_augment_canonical_maps()
    step2_update_frontend_files()
    step3_export_ws_via_docker()
    cm_1027 = json.loads((APP_DIR / "data" / "1027" / "canonical_map.json").read_text(encoding="utf-8"))
    print("VERIFY_1027_2TH_2_17:", list(cm_1027["2TH.2.17"]["verses"].keys()))
    ws_2th = json.loads((APP_DIR / "ws" / "verse" / "2TH.json").read_text(encoding="utf-8"))
    print("VERIFY_WS_2TH_2_17_TOK0:", ws_2th["2TH.2.17"]["original"]["tokens"][0])
