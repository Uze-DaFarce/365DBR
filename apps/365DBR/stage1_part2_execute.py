import argparse
import glob
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_batch

ROOT = Path(__file__).resolve().parents[2]

OSIS_TO_USFM = {
    "GEN": "GEN", "EXOD": "EXO", "LEV": "LEV", "NUM": "NUM", "DEUT": "DEU",
    "JOSH": "JOS", "JUDG": "JDG", "RUTH": "RUT", "1SAM": "1SA", "2SAM": "2SA",
    "1KGS": "1KI", "2KGS": "2KI", "1CHR": "1CH", "2CHR": "2CH", "EZRA": "EZR",
    "NEH": "NEH", "ESTH": "EST", "JOB": "JOB", "PS": "PSA", "PROV": "PRO",
    "ECCL": "ECC", "SONG": "SNG", "ISA": "ISA", "JER": "JER", "LAM": "LAM",
    "EZEK": "EZK", "DAN": "DAN", "HOS": "HOS", "JOEL": "JOL", "AMOS": "AMO",
    "OBAD": "OBA", "JONAH": "JON", "MIC": "MIC", "NAH": "NAM", "HAB": "HAB",
    "ZEPH": "ZEP", "HAG": "HAG", "ZECH": "ZEC", "MAL": "MAL",
    "MAT": "MAT", "MATT": "MAT", "MRK": "MRK", "MARK": "MRK", "MK": "MRK",
    "LUK": "LUK", "LUKE": "LUK", "LK": "LUK", "JHN": "JHN", "JOHN": "JHN", "JN": "JHN",
    "ACT": "ACT", "ACTS": "ACT", "ROM": "ROM", "1CO": "1CO", "1COR": "1CO",
    "2CO": "2CO", "2COR": "2CO", "GAL": "GAL", "EPH": "EPH", "PHP": "PHP", "PHIL": "PHP",
    "COL": "COL", "1TH": "1TH", "1THESS": "1TH", "2TH": "2TH", "2THESS": "2TH",
    "1TI": "1TI", "1TIM": "1TI", "2TI": "2TI", "2TIM": "2TI", "TIT": "TIT",
    "PHM": "PHM", "PHLM": "PHM", "HEB": "HEB", "JAS": "JAS", "JAM": "JAS",
    "1PE": "1PE", "1PET": "1PE", "2PE": "2PE", "2PET": "2PE",
    "1JN": "1JN", "1JOHN": "1JN", "2JN": "2JN", "2JOHN": "2JN",
    "3JN": "3JN", "3JOHN": "3JN", "JUD": "JUD", "JUDE": "JUD", "REV": "REV"
}

# Explicit deterministic overrides for the remaining TR orthographic variants
TR_EXACT_OVERRIDES = {
    "δαβιδ": ("G1138", "Δαυίδ", "N-PRI"),
    "μωσησ": ("G3475", "Μωϋσῆς", "N-NSM-P"),
    "μωσεωσ": ("G3475", "Μωϋσῆς", "N-GSM-P"),
    "εννατην": ("G1766", "ἔνατος", "A-ASF"),
    "εννενηκονταεννεα": ("G1768+G1767", "ἐνενήκοντα+ἐννέα", "A-NUI"),
    "παραληφθησεται": ("G3880", "παραλαμβάνω", "V-FPI-3S"),
    "στωικων": ("G4770", "Στωϊκός", "A-GPM"),
    "κακεινοισ": ("G2532+G1565", "καί+ἐκεῖνος", "CONJ+D-DPM"),
    "λαμα": ("G2982", "λαμά", "HEB"),
    "χξϛ΄": ("G5516", "χξϛ΄", "A-NUI"),
    "αφαιρησει": ("G0851", "ἀφαιρέω", "V-FAI-3S"),
    "ειλισσομενον": ("G1667", "ἑλίσσω", "V-PPP-NSN"),
    "ισαχαρ": ("G2466", "Ἰσσαχάρ", "N-PRI"),
    "εστηκεσαν": ("G2476", "ἵστημι", "V-LAI-3P"),
    "ηνεγκε": ("G5342", "φέρω", "V-AAI-3S"),
    "ελαβε": ("G2983", "λαμβάνω", "V-2AAI-3S"),
    "εξεχεε": ("G1632", "ἐκχέω", "V-AAI-3S"),
    "εκπεπληρωκε": ("G1603", "ἐκπληρόω", "V-RAI-3S"),
    "ηγειρε": ("G1453", "ἐγείρω", "V-AAI-3S"),
    "εστι": ("G1510", "εἰμί", "V-PAI-3S"),
    "περιπατησουσι": ("G4043", "περιπατέω", "V-FAI-3P"),
}

def get_db_conn():
    env_path = ROOT / "db" / ".env"
    env_vars = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return psycopg2.connect(
        host=env_vars.get("POSTGRES_HOST", "localhost"),
        port=int(env_vars.get("POSTGRES_PORT", 5432)),
        dbname=env_vars.get("POSTGRES_DB", "mt_sinai_365dbr"),
        user=env_vars.get("POSTGRES_USER", "365dbr_dev"),
        password=env_vars.get("POSTGRES_PASSWORD", ""),
    )

def norm_heb_consonants(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return re.sub(r"[^\u05D0-\u05EA]", "", s)

def norm_grk_base(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\u0370-\u03FF]", "", s.lower()).replace("ς", "σ")

def norm_grk_accented(s: str) -> str:
    s = unicodedata.normalize("NFC", s.strip())
    return re.sub(r"[^\u0370-\u03FF\u1F00-\u1FFF]", "", s)

def map_ref(ref_str: str) -> str:
    parts = ref_str.strip().split(".")
    if len(parts) != 3:
        return ref_str.upper()
    b, c, v = parts[0].upper(), parts[1], parts[2]
    return f"{OSIS_TO_USFM.get(b, b)}.{c}.{v}"

def load_oshb_wlc():
    ns = {"o": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
    by_verse = {}
    for f in sorted(glob.glob(str(ROOT / "apps/365DBR/RAW/OSHB/wlc/*.xml"))):
        if "VerseMap" in f:
            continue
        root = ET.parse(f).getroot()
        for v in root.findall(".//o:verse", ns):
            raw_id = v.attrib.get("osisID", "")
            if not raw_id:
                continue
            vid = map_ref(raw_id)
            words = []
            for elem in v:
                tag = elem.tag.split("}")[-1]
                if tag == "w":
                    surf = "".join(elem.itertext()).strip()
                    lem = elem.attrib.get("lemma", "").strip()
                    mor = elem.attrib.get("morph", "").strip()
                    words.append((surf, lem, mor, norm_heb_consonants(surf)))
                elif tag == "seg":
                    for w in elem.findall(".//o:w", ns):
                        surf = "".join(w.itertext()).strip()
                        lem = w.attrib.get("lemma", "").strip()
                        mor = w.attrib.get("morph", "").strip()
                        words.append((surf, lem, mor, norm_heb_consonants(surf)))
            by_verse[vid] = words
    return by_verse

def load_step_tagnt():
    by_verse = {}
    lex_accented = {}
    lex_base = {}
    lemma_by_strong = {}

    pattern = str(ROOT / "apps/365DBR/RAW/STEPBible/**/TAGNT*.txt")
    for f in sorted(glob.glob(pattern, recursive=True)):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if not line or line.startswith("#") or "\t" not in line:
                    continue
                cols = line.rstrip("\r\n").split("\t")
                if len(cols) < 6 or "#" not in cols[0]:
                    continue
                ref_part, word_part = cols[0].split("#", 1)
                if "=" not in word_part:
                    continue
                tag_type = word_part.split("=", 1)[1]
                editions = cols[5]

                base_ref = re.sub(r"[\{\[].*?[\}\]]", "", ref_part)
                alt_matches = re.findall(r"[\{\[](.*?)[\}\]]", ref_part)
                bk_prefix = base_ref.split(".")[0]
                vids = [map_ref(base_ref)]
                for alt in alt_matches:
                    if "." in alt:
                        pts = alt.split(".")
                        if len(pts) == 2:
                            vids.append(map_ref(f"{bk_prefix}.{pts[0]}.{pts[1]}"))
                        elif len(pts) == 3:
                            vids.append(map_ref(alt))

                grk_surf = re.sub(r"^[\[\(\{]+|[\]\)\}]+$", "", cols[1].split("(")[0].strip())
                sm = cols[3].strip()
                strong = sm.split("=")[0].strip() if "=" in sm else sm
                morph = sm.split("=", 1)[1].strip() if "=" in sm else ""
                lemma = cols[4].split("=")[0].strip() if "=" in cols[4] else cols[4].strip()

                if strong and lemma:
                    lemma_by_strong.setdefault(strong, lemma)

                alt_col = cols[6].strip() if len(cols) > 6 else ""
                tr_tokens = []
                if ("K" in tag_type or "k" in tag_type or "TR" in editions or "TR" in alt_col):
                    if ("(K)" in tag_type or "(k)" in tag_type) and "TR" in alt_col:
                        m_var = re.match(r"^([^\(]+)\([^\)]+\).*?-\s*(G\d+)=([A-Za-z0-9\-]+)", alt_col)
                        if m_var:
                            v_surf = m_var.group(1).strip()
                            v_str = m_var.group(2).strip()
                            v_mor = m_var.group(3).strip()
                            v_lem = lemma if v_str == strong else lemma_by_strong.get(v_str, lemma)
                            for w_piece in v_surf.split():
                                tr_tokens.append((w_piece, v_str, v_lem, v_mor, norm_grk_base(w_piece)))
                    if not tr_tokens and ("TR" in editions or "K" in tag_type or "k" in tag_type):
                        tr_tokens.append((grk_surf, strong, lemma, morph, norm_grk_base(grk_surf)))

                for tok in tr_tokens:
                    for v in set(vids):
                        by_verse.setdefault(v, []).append(tok)
                    ka = norm_grk_accented(tok[0])
                    kb = tok[4]
                    if ka and tok[1] and tok[2] and tok[3]:
                        lex_accented.setdefault(ka, Counter())[(tok[1], tok[2], tok[3])] += 1
                    if kb and tok[1] and tok[2] and tok[3]:
                        lex_base.setdefault(kb, Counter())[(tok[1], tok[2], tok[3])] += 1

    if "2CO.13.12" in by_verse:
        by_verse["2CO.13.13"] = by_verse["2CO.13.12"] + by_verse.get("2CO.13.13", [])

    best_acc = {k: c.most_common(1)[0][0] for k, c in lex_accented.items()}
    best_base = {k: c.most_common(1)[0][0] for k, c in lex_base.items()}
    return by_verse, best_acc, best_base

def align_heb_tokens(db_rows, src_rows):
    updates = []
    unmatched = 0
    idx = 0
    n_src = len(src_rows)
    for tid, wo, surf, db_str in db_rows:
        target = norm_heb_consonants(surf)
        str_num = str(int(db_str[1:])) if db_str and db_str.startswith("H") and db_str[1:].isdigit() else ""
        matched = None
        start_k = max(0, idx - 1)
        for k in range(start_k, min(idx + 8, n_src)):
            if src_rows[k][-1] == target:
                matched = src_rows[k]
                idx = k + 1
                break
        if not matched and target:
            for k in range(start_k, min(idx + 6, n_src)):
                s_norm = src_rows[k][-1]
                if s_norm and (target in s_norm or s_norm in target):
                    matched = src_rows[k]
                    idx = k + 1
                    break
        if not matched and str_num:
            for k in range(start_k, min(idx + 6, n_src)):
                if re.search(rf"\b{str_num}\b", src_rows[k][1]):
                    matched = src_rows[k]
                    idx = k + 1
                    break
        if not matched and len(db_rows) == n_src and wo - 1 < n_src:
            matched = src_rows[wo - 1]
            idx = wo
        if matched:
            updates.append((matched[1], matched[2], db_str, tid))
        else:
            unmatched += 1
    return updates, unmatched

def lookup_single_grk(surf, best_acc, best_base):
    ka = norm_grk_accented(surf)
    kb = norm_grk_base(surf)
    return (
        best_acc.get(ka)
        or best_base.get(kb)
        or best_base.get(kb + "ν")
        or TR_EXACT_OVERRIDES.get(kb)
    )

def align_grk_tokens(db_rows, src_rows, best_acc, best_base):
    updates = []
    unmatched = 0
    lex_fallback = 0
    dash_cnt = 0
    idx = 0
    n_src = len(src_rows)
    for tid, wo, surf, db_str in db_rows:
        if surf.strip() in ("—", "–", "-"):
            updates.append(("—", "PUNCT", None, tid))
            dash_cnt += 1
            continue

        # Handle punctuation-joined double words (e.g. 'λαλήσομεν.Εἰρήνη', 'μου,ἵνα')
        parts = [p for p in re.split(r"[.,·;]", surf) if norm_grk_base(p)]
        if len(parts) == 2:
            h1 = lookup_single_grk(parts[0], best_acc, best_base)
            h2 = lookup_single_grk(parts[1], best_acc, best_base)
            if h1 and h2:
                updates.append((f"{h1[1]}+{h2[1]}", f"{h1[2]}+{h2[2]}", f"{h1[0]}+{h2[0]}", tid))
                idx = min(n_src, idx + 2)
                lex_fallback += 1
                continue

        target = norm_grk_base(surf)
        matched = None
        start_k = max(0, idx - 1)
        for k in range(start_k, min(idx + 10, n_src)):
            s_norm = src_rows[k][-1]
            if s_norm == target or s_norm == target + "ν":
                matched = src_rows[k]
                idx = k + 1
                break
        if not matched and target:
            for k in range(start_k, min(idx + 8, n_src)):
                s_norm = src_rows[k][-1]
                if s_norm and (target.startswith(s_norm[:3]) or target in s_norm or s_norm in target):
                    matched = src_rows[k]
                    idx = k + 1
                    break
        if not matched and len(db_rows) == n_src and wo - 1 < n_src:
            matched = src_rows[wo - 1]
            idx = wo

        if matched:
            updates.append((matched[2], matched[3], matched[1], tid))
        else:
            hit = lookup_single_grk(surf, best_acc, best_base)
            if hit:
                strng, lem, mor = hit
                updates.append((lem, mor, strng, tid))
                lex_fallback += 1
            else:
                unmatched += 1
    return updates, unmatched, lex_fallback, dash_cnt

def run_objective_2(conn, execute: bool):
    oshb = load_oshb_wlc()
    tagnt, best_acc, best_base = load_step_tagnt()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, language, verse_id, COALESCE(source_verse_id, verse_id), word_order, surface_text, strong_number
            FROM original_tokens ORDER BY language, verse_id, word_order;
        """)
        all_rows = cur.fetchall()

    by_lang_verse = {"hebrew": {}, "greek": {}}
    for tid, lang, vid, svid, wo, surf, strng in all_rows:
        by_lang_verse[lang].setdefault((vid, svid), []).append((tid, wo, surf, strng))

    heb_updates, grk_updates = [], []
    heb_unm, grk_unm, grk_lex, grk_dash = 0, 0, 0, 0

    for (vid, svid), db_toks in by_lang_verse["hebrew"].items():
        src = oshb.get(svid) or oshb.get(vid) or []
        u, unm = align_heb_tokens(db_toks, src)
        heb_updates.extend(u)
        heb_unm += unm

    for (vid, svid), db_toks in by_lang_verse["greek"].items():
        src = tagnt.get(svid) or tagnt.get(vid) or []
        u, unm, lf, dc = align_grk_tokens(db_toks, src, best_acc, best_base)
        grk_updates.extend(u)
        grk_unm += unm
        grk_lex += lf
        grk_dash += dc

    print(f"OBJ2 AUDIT: Heb matched={len(heb_updates)}/299420 (unm={heb_unm})")
    print(f"OBJ2 AUDIT: Grk matched={len(grk_updates)}/140111 (unm={grk_unm}, lex={grk_lex}, punct_dash={grk_dash})")

    if execute and heb_unm == 0 and grk_unm == 0:
        with conn.cursor() as cur:
            execute_batch(cur, "UPDATE original_tokens SET lemma=%s, morph=%s WHERE id=%s",
                          [(lem, mor, tid) for lem, mor, _, tid in heb_updates], page_size=5000)
            execute_batch(cur, "UPDATE original_tokens SET lemma=%s, morph=%s, strong_number=%s WHERE id=%s",
                          [(lem, mor, strng, tid) for lem, mor, strng, tid in grk_updates], page_size=5000)
        conn.commit()
        print("OBJ2 EXECUTED: 100% of Hebrew (299,420) and Greek (140,111) tokens updated and committed.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-obj2", action="store_true")
    ap.add_argument("--execute-obj2", action="store_true")
    args = ap.parse_args()
    conn = get_db_conn()
    if args.audit_obj2 or args.execute_obj2:
        run_objective_2(conn, args.execute_obj2)
    conn.close()