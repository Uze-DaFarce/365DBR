#!/usr/bin/env python3
"""
Stage 1, Part 1 — Schema Upgrade & LSB/WEB/YLT Ingestion
"""

import argparse
import hashlib
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

import psycopg2
from psycopg2.extras import execute_values

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import bible_common


def load_dotenv_files():
    for env_path in (REPO_ROOT / "db" / ".env", REPO_ROOT / ".env", SCRIPT_DIR / ".env"):
        if env_path.is_file():
            for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v


def load_canonical_spine() -> Tuple[Dict[str, dict], Set[str]]:
    raw = bible_common.BIBLE_DATA
    spine_by_usfm = {}
    expected_verse_ids = set()

    for idx, (usfm, chapters) in enumerate(raw.items(), start=1):
        code = usfm.upper().strip()
        spine_by_usfm[code] = {
            "book_num": idx,
            "usfm": code,
            "chapters": list(chapters),
        }
        for ch_idx, max_v in enumerate(chapters, start=1):
            for v_idx in range(1, max_v + 1):
                expected_verse_ids.add(f"{code}.{ch_idx}.{v_idx}")

    if len(spine_by_usfm) != 66:
        raise RuntimeError(f"Expected 66 books in BIBLE_DATA; found {len(spine_by_usfm)}")

    return spine_by_usfm, expected_verse_ids


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def remap_versification(usfm: str, chapter: int, verse: int, spine_by_usfm: Dict[str, dict]) -> Tuple[int, int]:
    ch_limits = spine_by_usfm[usfm]["chapters"]

    if usfm == "3JN" and chapter == 1 and verse == 15 and ch_limits[0] == 14:
        return (1, 14)
    if usfm == "REV" and chapter == 12 and verse == 18 and ch_limits[11] == 17:
        return (12, 17)
    if usfm == "MAL" and chapter == 3 and verse >= 19:
        return (4, verse - 18)
    if usfm == "JOL" and chapter == 4:
        return (3, verse)
    if usfm == "MIC" and chapter == 4 and verse == 14:
        return (5, 1)
    if usfm == "EXO" and chapter == 7 and verse >= 26:
        return (8, verse - 25)
    if usfm == "LEV" and chapter == 5 and verse >= 20:
        return (6, verse - 19)
    if usfm == "JOB" and chapter == 40 and verse >= 25:
        return (41, verse - 24)
    # WEB places Romans 16:25-27 doxology at 14:24-26
    if usfm == "ROM" and chapter == 14 and verse in (24, 25, 26):
        return (16, verse + 1)

    return (chapter, verse)


SKIP_PARA_STYLES = {
    "mt", "mt1", "mt2", "mt3", "mte", "mte1", "mte2",
    "ms", "ms1", "ms2", "mr",
    "s", "s1", "s2", "s3", "s4", "sr", "r", "sp",
    "h", "toc1", "toc2", "toc3", "toca1", "toca2", "toca3",
    "imt", "imt1", "imt2", "is", "is1", "ip", "ipi", "im", "imi",
    "ipq", "imq", "ipr", "iq", "iq1", "iq2", "iq3", "ib", "ili",
    "ili1", "ili2", "iot", "io", "io1", "io2", "io3", "io4",
    "iex", "iqt", "ie", "ide", "rem", "sts", "restore", "cl", "cp"
}

SKIP_CHAR_STYLES = {"rq", "vp", "va", "ca"}


def extract_note_text(note_el: ET.Element) -> str:
    parts = []
    for el in note_el.iter():
        if el.tag.lower() == "char" and el.attrib.get("style", "").lower() in ("fr", "xo"):
            continue
        if el.text:
            parts.append(el.text)
        if el.tail and el is not note_el:
            parts.append(el.tail)
    return clean_whitespace("".join(parts))


def parse_usx_file(filepath: Path, spine_by_usfm: Dict[str, dict]) -> Tuple[str, Dict[Tuple[int, int], str]]:
    tree = ET.parse(filepath)
    root = tree.getroot()

    book_el = root.find("book")
    if book_el is None:
        return ("UNKNOWN", {})

    book_code = book_el.attrib.get("code", "").upper().strip()
    if book_code not in spine_by_usfm:
        return (book_code, {})

    verses_acc: Dict[Tuple[int, int], List[str]] = defaultdict(list)
    notes_acc: Dict[Tuple[int, int], List[str]] = defaultdict(list)
    seen_milestones: Set[Tuple[int, int]] = set()
    current_chapter = 0
    current_verse = 0
    in_verse = False

    def parse_verse_num(raw_num: str) -> int:
        m = re.match(r"^(\d+)", str(raw_num).strip())
        return int(m.group(1)) if m else 0

    def walk_node(node: ET.Element):
        nonlocal current_chapter, current_verse, in_verse
        tag = node.tag.lower()

        if tag == "book":
            return

        if tag == "chapter":
            if "eid" in node.attrib and "number" not in node.attrib:
                in_verse = False
                return
            ch_num = node.attrib.get("number")
            if ch_num:
                current_chapter = int(re.match(r"^(\d+)", ch_num.strip()).group(1))
                current_verse = 0
                in_verse = False
            return

        if tag == "verse":
            if "eid" in node.attrib and "number" not in node.attrib:
                in_verse = False
                return
            v_num = node.attrib.get("number")
            if v_num:
                current_verse = parse_verse_num(v_num)
                in_verse = current_verse > 0
                if in_verse and current_chapter > 0:
                    ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                    seen_milestones.add((ch, v))

            if node.text and in_verse and current_chapter > 0 and current_verse > 0:
                ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                verses_acc[(ch, v)].append(node.text)

            for child in node:
                walk_node(child)

            if node.tail and in_verse and current_chapter > 0 and current_verse > 0:
                ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                verses_acc[(ch, v)].append(node.tail)
            return

        if tag in ("note", "figure", "sidebar", "ref"):
            if tag == "note" and in_verse and current_chapter > 0 and current_verse > 0:
                ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                nt = extract_note_text(node)
                if nt:
                    notes_acc[(ch, v)].append(f"[{nt}]")
            if node.tail and in_verse and current_chapter > 0 and current_verse > 0:
                ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                verses_acc[(ch, v)].append(node.tail)
            return

        if tag == "para":
            style = node.attrib.get("style", "").lower()
            if style in SKIP_PARA_STYLES:
                return
            if style == "d" and book_code == "PSA" and current_chapter > 0 and current_verse == 0:
                current_verse = 1
                in_verse = True
                seen_milestones.add((current_chapter, 1))

            if in_verse and current_chapter > 0 and current_verse > 0:
                ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                if verses_acc[(ch, v)]:
                    verses_acc[(ch, v)].append(" ")

            if node.text and in_verse and current_chapter > 0 and current_verse > 0:
                ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                verses_acc[(ch, v)].append(node.text)

            for child in node:
                walk_node(child)
            return

        if tag == "char":
            style = node.attrib.get("style", "").lower()
            if style in SKIP_CHAR_STYLES:
                if node.tail and in_verse and current_chapter > 0 and current_verse > 0:
                    ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                    verses_acc[(ch, v)].append(node.tail)
                return

        if node.text and in_verse and current_chapter > 0 and current_verse > 0:
            ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
            verses_acc[(ch, v)].append(node.text)

        for child in node:
            walk_node(child)

        if node.tail and in_verse and current_chapter > 0 and current_verse > 0:
            ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
            verses_acc[(ch, v)].append(node.tail)

    for top_child in root:
        walk_node(top_child)

    cleaned_verses: Dict[Tuple[int, int], str] = {}
    for (ch, v) in seen_milestones | set(verses_acc.keys()):
        txt = clean_whitespace("".join(verses_acc.get((ch, v), [])))
        if not txt and notes_acc.get((ch, v)):
            # Fallback to footnote text for bracketed/omitted verses (e.g. WEB LUK 17:36, ACT 8:37, 15:34, 24:7)
            txt = clean_whitespace(" ".join(notes_acc[(ch, v)]))
        if txt:
            cleaned_verses[(ch, v)] = txt

    return (book_code, cleaned_verses)


USFM_NOTE_RE = re.compile(r"\\(f|fe|x|ef|ex)\b.*?\\\1\*", re.DOTALL)
USFM_ATTR_RE = re.compile(r"\|[^\\*]*?(?=\\|\*)")
USFM_MARKER_RE = re.compile(r"\\\+?[a-zA-Z0-9]+\*?")


def clean_usfm_inline(raw_text: str) -> str:
    txt = USFM_NOTE_RE.sub("", raw_text)
    txt = USFM_ATTR_RE.sub("", txt)
    txt = USFM_MARKER_RE.sub(" ", txt)
    return clean_whitespace(txt)


def parse_usfm_file(filepath: Path, spine_by_usfm: Dict[str, dict]) -> Tuple[str, Dict[Tuple[int, int], str]]:
    content = filepath.read_text(encoding="utf-8", errors="replace")
    m_id = re.search(r"\\id\s+([A-Z0-9]{3})", content)
    if not m_id:
        return ("UNKNOWN", {})

    book_code = m_id.group(1).upper().strip()
    if book_code == "NAH" and "NAM" in spine_by_usfm:
        book_code = "NAM"
    if book_code not in spine_by_usfm:
        return (book_code, {})

    verses_acc: Dict[Tuple[int, int], List[str]] = defaultdict(list)
    current_chapter = 0
    current_verse = 0

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"^\\(id|ide|h|toc\d?|mt\d?|mte\d?|ms\d?|mr|s\d?|sr|r|sp|rem|sts|cl|cp|i[a-z]+\d?)\b", line):
            continue

        m_ch = re.match(r"^\\c\s+(\d+)", line)
        if m_ch:
            current_chapter = int(m_ch.group(1))
            current_verse = 0
            continue

        if "\\v " in line or line.startswith("\\v\t"):
            parts = re.split(r"(?=\\v\s+\d+)", line)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                m_v = re.match(r"^\\v\s+(\d+)(?:[-a-zA-Z0-9]*)\s*(.*)", part, re.DOTALL)
                if m_v and current_chapter > 0:
                    current_verse = int(m_v.group(1))
                    v_text = clean_usfm_inline(m_v.group(2))
                    if v_text:
                        ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                        verses_acc[(ch, v)].append(v_text)
                elif current_chapter > 0 and current_verse > 0:
                    v_text = clean_usfm_inline(part)
                    if v_text:
                        ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                        verses_acc[(ch, v)].append(v_text)
        else:
            if current_chapter > 0 and current_verse > 0:
                v_text = clean_usfm_inline(line)
                if v_text:
                    ch, v = remap_versification(book_code, current_chapter, current_verse, spine_by_usfm)
                    verses_acc[(ch, v)].append(v_text)

    cleaned_verses = {
        (ch, v): clean_whitespace(" ".join(chunks))
        for (ch, v), chunks in verses_acc.items()
        if clean_whitespace(" ".join(chunks))
    }
    return (book_code, cleaned_verses)


def apply_schema_and_spine_migration(conn, expected_verse_ids: Set[str]):
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # 1. Ensure all 31,102 canonical coordinates exist in `verses` (inserts LUK.17.37, ACT.15.41, ACT.24.27)
    cur.execute("SELECT id FROM verses;")
    existing_vids = {r[0] for r in cur.fetchall()}
    missing_vids = sorted(expected_verse_ids - existing_vids)

    for vid in missing_vids:
        b_code, ch_s, v_s = vid.split(".")
        ch_i, v_i = int(ch_s), int(v_s)
        cur.execute(
            "SELECT COALESCE(MAX(verse_order), 0) + 1 FROM verses WHERE book_code = %s AND chapter = %s;",
            (b_code, ch_i),
        )
        next_order = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO verses (id, book_code, chapter, verse, verse_order)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            (vid, b_code, ch_i, v_i, next_order),
        )

    # 2. Add flags to translations and text_sha256 to verse_translations
    cur.execute(
        """
        ALTER TABLE translations
            ADD COLUMN IF NOT EXISTS allow_tier1_logic BOOLEAN NOT NULL DEFAULT false,
            ADD COLUMN IF NOT EXISTS is_non_commercial_only BOOLEAN NOT NULL DEFAULT false;

        UPDATE translations
        SET allow_tier1_logic = true,
            is_non_commercial_only = false
        WHERE UPPER(code) IN ('KJV', 'LSV');

        ALTER TABLE verse_translations
            ADD COLUMN IF NOT EXISTS text_sha256 TEXT;

        UPDATE verse_translations
        SET text_sha256 = encode(digest(text, 'sha256'), 'hex')
        WHERE text_sha256 IS NULL;
        """
    )
    conn.commit()
    print(f"[Migration] Complete. Added {len(missing_vids)} missing canonical coordinate(s) to `verses`: {missing_vids}")


def parse_and_validate_corpus(
    trans_code: str,
    source_paths: List[Path],
    fmt: str,
    spine_by_usfm: Dict[str, dict],
    expected_verse_ids: Set[str],
    strict_halt: bool = True,
) -> Tuple[Dict[str, Tuple[str, str]], List[str]]:
    books_seen = set()
    skipped_apocrypha = set()
    corpus_texts: Dict[str, str] = {}

    # Deduplicate by filename (WEB USX_1..3 contains overlapping canonical files across folders)
    seen_Book_files: Dict[str, Path] = {}
    files: List[Path] = []
    for sp in source_paths:
        if sp.is_file():
            files.append(sp)
        elif sp.is_dir():
            for f in sorted(sp.rglob("*")):
                if f.is_file() and f.suffix.lower() in (".usx", ".usfm", ".sfm"):
                    files.append(f)

    for fpath in files:
        if fmt == "usx":
            book_code, book_verses = parse_usx_file(fpath, spine_by_usfm)
        else:
            book_code, book_verses = parse_usfm_file(fpath, spine_by_usfm)

        if book_code not in spine_by_usfm:
            if book_code != "UNKNOWN":
                skipped_apocrypha.add(book_code)
            continue

        # Avoid duplicate file overwrites if WEB USX_1, USX_2, USX_3 repeat the same book
        if book_code in books_seen and len(book_verses) > 0:
            continue

        books_seen.add(book_code)
        for (ch, v), text in book_verses.items():
            vid = f"{book_code}.{ch}.{v}"
            if vid in corpus_texts:
                corpus_texts[vid] = clean_whitespace(f"{corpus_texts[vid]} {text}")
            else:
                corpus_texts[vid] = text

    actual_ids = set(corpus_texts.keys())
    missing_ids = sorted(expected_verse_ids - actual_ids)
    extra_ids = sorted(actual_ids - expected_verse_ids)

    print(f"\n[Corpus Audit: {trans_code}]")
    print(f"  - Canonical Books Parsed : {len(books_seen)} / 66")
    if skipped_apocrypha:
        print(f"  - Rejected Apocrypha ({len(skipped_apocrypha):>2}): {', '.join(sorted(skipped_apocrypha))}")
    print(f"  - Total Verses Parsed    : {len(actual_ids):,}")
    print(f"  - Missing vs BIBLE_DATA  : {len(missing_ids)}")
    print(f"  - Extra vs BIBLE_DATA    : {len(extra_ids)}")

    if missing_ids:
        print(f"    * Missing: {', '.join(missing_ids[:25])}")
    if extra_ids:
        print(f"    * Extra  : {', '.join(extra_ids[:25])}")

    if strict_halt and (len(books_seen) != 66 or missing_ids or extra_ids):
        print(f"\n[FATAL] Stopping immediately due to versification mismatch in {trans_code}.")
        sys.exit(1)

    result = {vid: (txt, compute_sha256(txt)) for vid, txt in corpus_texts.items()}
    return result, sorted(skipped_apocrypha)


def upsert_translation_corpus(
    conn,
    code: str,
    name: str,
    license_str: str,
    allow_tier1_logic: bool,
    is_non_commercial_only: bool,
    corpus: Dict[str, Tuple[str, str]],
):
    cur = conn.cursor()

    cur.execute("SELECT id FROM translations WHERE UPPER(code) = UPPER(%s);", (code,))
    row = cur.fetchone()
    if row:
        trans_id = row[0]
        cur.execute(
            """
            UPDATE translations
            SET name = %s,
                license = COALESCE(license, %s),
                allow_tier1_logic = %s,
                is_non_commercial_only = %s
            WHERE id = %s;
            """,
            (name, license_str, allow_tier1_logic, is_non_commercial_only, trans_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO translations (code, name, language, is_primary, license, allow_tier1_logic, is_non_commercial_only)
            VALUES (%s, %s, 'en', false, %s, %s, %s)
            RETURNING id;
            """,
            (code, name, license_str, allow_tier1_logic, is_non_commercial_only),
        )
        trans_id = cur.fetchone()[0]

    formatted_rows = [(vid, trans_id, txt, sha) for vid, (txt, sha) in sorted(corpus.items())]
    insert_sql = """
        INSERT INTO verse_translations (verse_id, translation_id, text, text_sha256)
        VALUES %s
        ON CONFLICT (verse_id, translation_id) DO UPDATE
        SET text = EXCLUDED.text,
            text_sha256 = EXCLUDED.text_sha256;
    """
    execute_values(
        cur,
        insert_sql,
        formatted_rows,
        template="(%s, %s, %s, %s)",
        page_size=2000,
    )
    conn.commit()


def print_verification_table(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            t.id,
            t.code,
            t.allow_tier1_logic,
            t.is_non_commercial_only,
            COUNT(DISTINCT v.book_code) AS book_count,
            COUNT(vt.verse_id) AS total_verses,
            COUNT(vt.text_sha256) FILTER (WHERE vt.text_sha256 IS NOT NULL AND LENGTH(vt.text_sha256) = 64) AS sha256_count
        FROM translations t
        LEFT JOIN verse_translations vt ON vt.translation_id = t.id
        LEFT JOIN verses v ON v.id = vt.verse_id
        GROUP BY t.id, t.code, t.allow_tier1_logic, t.is_non_commercial_only
        ORDER BY t.id;
        """
    )
    rows = cur.fetchall()

    print("\n" + "=" * 96)
    print("TASK 4: FINAL VERIFICATION TABLE (mt_sinai_365dbr)")
    print("=" * 96)
    print(
        f"{'ID':<4} | {'Code':<6} | {'Tier1 Logic':<12} | {'Non-Comm Only':<14} | "
        f"{'Books':<6} | {'Total Verses':<13} | {'SHA-256 Hashes':<14}"
    )
    print("-" * 96)
    for t_id, code, tier1, non_comm, b_cnt, v_cnt, h_cnt in rows:
        print(
            f"{t_id:<4} | {code:<6} | {str(tier1):<12} | {str(non_comm):<14} | "
            f"{b_cnt:<6} | {v_cnt:<13,} | {h_cnt:<14,}"
        )
    print("=" * 96)


def main():
    load_dotenv_files()

    parser = argparse.ArgumentParser()
    parser.add_argument("--db-host", default=os.getenv("POSTGRES_HOST") or os.getenv("PGHOST", "localhost"))
    parser.add_argument("--db-port", type=int, default=int(os.getenv("POSTGRES_PORT") or os.getenv("PGPORT", "5432")))
    parser.add_argument("--db-name", default=os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE", "mt_sinai_365dbr"))
    parser.add_argument("--db-user", default=os.getenv("POSTGRES_USER") or os.getenv("PGUSER", "365dbr_dev"))
    parser.add_argument("--db-pass", default=os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD", ""))
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if not args.inspect_only and not args.execute:
        args.inspect_only = True

    spine_by_usfm, expected_verse_ids = load_canonical_spine()

    conn = psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_pass,
    )

    try:
        targets = [
            {
                "code": "LSB",
                "name": "Legacy Standard Bible",
                "license": "Lockman Foundation (Non-Commercial)",
                "fmt": "usx",
                "paths": [SCRIPT_DIR / "LSB"],
                "allow_tier1_logic": False,
                "is_non_commercial_only": True,
            },
            {
                "code": "WEB",
                "name": "World English Bible",
                "license": "Public Domain",
                "fmt": "usx",
                "paths": [
                    SCRIPT_DIR / "RAW" / "WEB" / "release" / "USX_1",
                    SCRIPT_DIR / "RAW" / "WEB" / "release" / "USX_2",
                    SCRIPT_DIR / "RAW" / "WEB" / "release" / "USX_3",
                ],
                "allow_tier1_logic": False,
                "is_non_commercial_only": False,
            },
            {
                "code": "YLT",
                "name": "Young's Literal Translation",
                "license": "Public Domain",
                "fmt": "usfm",
                "paths": [SCRIPT_DIR / "RAW" / "YLT" / "USFM"],
                "allow_tier1_logic": True,
                "is_non_commercial_only": False,
            },
        ]

        if args.inspect_only and not args.execute:
            for t in targets:
                parse_and_validate_corpus(
                    trans_code=t["code"],
                    source_paths=t["paths"],
                    fmt=t["fmt"],
                    spine_by_usfm=spine_by_usfm,
                    expected_verse_ids=expected_verse_ids,
                    strict_halt=False,
                )
            return

        apply_schema_and_spine_migration(conn, expected_verse_ids)

        for t in targets:
            corpus, _ = parse_and_validate_corpus(
                trans_code=t["code"],
                source_paths=t["paths"],
                fmt=t["fmt"],
                spine_by_usfm=spine_by_usfm,
                expected_verse_ids=expected_verse_ids,
                strict_halt=True,
            )
            print(f"  -> Upserting {len(corpus):,} verses and SHA-256 hashes for {t['code']}...")
            upsert_translation_corpus(
                conn=conn,
                code=t["code"],
                name=t["name"],
                license_str=t["license"],
                allow_tier1_logic=t["allow_tier1_logic"],
                is_non_commercial_only=t["is_non_commercial_only"],
                corpus=corpus,
            )

        print_verification_table(conn)

    finally:
        conn.close()


if __name__ == "__main__":
    main()