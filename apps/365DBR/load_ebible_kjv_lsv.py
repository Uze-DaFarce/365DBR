#!/usr/bin/env python3
"""Load eBible KJV and LSV verse words into verse_translations.

Strips \\w and \\+w tags from the verse sentence. || stays; it is LSV poetry
punctuation, not an attribute. A marker that touches the next marker keeps
them together (goat + skins with no space).

A single space between two Strong's tags is removed only for compounds this
same eng-kjv2006 file also spells as one word: cannot, wherein, whereunto,
whatsoever. The two tags are still stored separately. "evil doer" in
2 Timothy 2:9 stays two words, because that is the printed sentence.

Dash-only lines (LSV 3JN 1:15 and REV 12:18) are not verse text and are not
merged onto the previous verse.

KJV \\w tags go in kjv_english_strong_tags, edition eng-kjv2006. They are not
written to original_tokens. LSV strong attributes are dropped and not stored.
"""
import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import stage1_ingest_lsb_web_ylt as ingest

KJV_DIR = SCRIPT_DIR / "RAW" / "KJV" / "eBible" / "usfm"
LSV_DIR = SCRIPT_DIR / "RAW" / "LSV" / "eBible" / "usfm"
KJV_ZIP = "eng-kjv2006_usfm.zip"
LSV_ZIP = "englsv_usfm.zip"
KJV_SHA = "BF907642B9A37530EBD9CEDF08273F62A7C2140E414205FD4B8208BE952B4B14"
LSV_SHA = "8EA9837F3FD6B4281CC9F0D0FF27DA51A44FDF8379FCA88733D7A7BCE4BC15AD"
RETRIEVED = "2026-10-28"

KJV_NOTE = (
    f"eBible {KJV_ZIP} sha256 {KJV_SHA} retrieved {RETRIEVED}; "
    "verse words only. Strong's tags are in kjv_english_strong_tags "
    "(edition eng-kjv2006), not on this row"
)
LSV_NOTE = (
    f"eBible {LSV_ZIP} sha256 {LSV_SHA} retrieved {RETRIEVED}; "
    "strong attributes dropped"
)
KJV_LICENSE = (
    "Public domain outside the United Kingdom. "
    "UK printing or import of printed copies needs the Queen's Printers "
    "(Cambridge, Oxford, Collins). Source: eBible eng-kjv2006."
)
LSV_LICENSE = (
    "CC BY-SA 4.0. Copyright 2020 Covenant Press and the Covenant Christian Coalition. "
    "Do not alter the English and present it as the LSV. Source: eBible englsv."
)

# Same file also spells these as one word. The space is only between the two tags.
# Hebrews 9:5 "can" is G2076. Hebrews 9:11 "say" is also G2076 and is not this pair.
# 2 Timothy 2:9 "evil" is untagged and "doer" is G2557. That stays two words.
PROVEN_PAIRS = {
    ("can", "not", "G1410", "G3756"),
    ("can", "not", "G2076", "G3756"),
    ("where", "unto", "G3739", "G1519"),
    ("where", "in", "G3739", "G1722"),
    ("what", "soever", "G5100", "G3956"),
}
EXPECTED_JOIN_VERSES = (
    "1TI.2.7",
    "1TI.5.25",
    "1TI.6.12",
    "2TI.1.11",
    "2TI.2.9",
    "2TI.2.13",
    "ACT.4.16",
    "ACT.4.20",
    "ACT.5.39",
    "COL.3.17",
    "COL.3.23",
    "HEB.6.17",
    "HEB.9.5",
)
ONE_TAG_RE = re.compile(
    r"\\\+?w\s+(?P<word>[A-Za-z']+)\|strong=\"(?P<strong>[^\"]+)\"\\\+?w\*"
)
STRONG_ATTR_RE = re.compile(r'strong="([^"]*)"')
STRONG_OK_RE = re.compile(r"^[HG]\d{1,5}[A-Za-z]?$")
TAG_2TH_3_18 = [
    ("grace", "G5485"),
    ("our", "G2257"),
    ("Lord", "G2962"),
    ("Jesus", "G2424"),
    ("Christ", "G5547"),
    ("with", "G3326"),
    ("you", "G5216"),
    ("all", "G3956"),
    ("Amen", "G0281"),
]

NOTE_RE = re.compile(r"\\(f|fe|x|ef|ex)\b.*?\\\1\*", re.DOTALL)
W_RE = re.compile(r"\\\+?w\s+([^\\]*?)\\\+?w\*")
MARKER_RE = re.compile(r"\\\+?[a-zA-Z0-9]+\*?")
DASH_ONLY = re.compile(r"^[\-\u2013\u2014\u2015.\s]+$")
SKIP_LINE = re.compile(
    r"^\\(id|ide|h|toc\d?|mt\d?|mte\d?|ms\d?|mr|s\d?|sr|r|sp|rem|sts|cl|cp|i[a-z]+\d?)\b"
)
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")


def join_printed_compounds(raw: str) -> tuple:
    """Return (text, join_count). Joins only PROVEN_PAIRS.

    A rejected neighbor must not hide the next pair. Colossians 3:17 is
    tagged And + what + soever, and only what + soever is one printed word.
    """
    matches = list(ONE_TAG_RE.finditer(raw))
    if len(matches) < 2:
        return raw, 0
    count = 0
    pieces = []
    pos = 0
    skip_until = -1
    for i, m in enumerate(matches):
        if m.start() < skip_until or i + 1 >= len(matches):
            continue
        nxt = matches[i + 1]
        between = raw[m.end():nxt.start()]
        key = (
            m.group("word").lower(),
            nxt.group("word").lower(),
            m.group("strong"),
            nxt.group("strong"),
        )
        if between == "" or between.strip() != "" or key not in PROVEN_PAIRS:
            continue
        pieces.append(raw[pos:m.start()])
        pieces.append(m.group("word") + nxt.group("word"))
        pos = nxt.end()
        skip_until = nxt.end()
        count += 1
    pieces.append(raw[pos:])
    return "".join(pieces), count


def extract_tags(raw: str):
    spans = []
    for m in W_RE.finditer(raw):
        inner = m.group(1)
        surface = inner.split("|", 1)[0].strip()
        found = STRONG_ATTR_RE.findall(inner)
        strong = found[0] if found else None
        if len(found) > 1:
            strong = "+".join(found)
        spans.append((surface, strong))
    return spans


def clean_verse(raw: str) -> str:
    txt = NOTE_RE.sub("", raw)
    txt, _n = join_printed_compounds(txt)
    prev = None
    while prev != txt:
        prev = txt
        txt = W_RE.sub(lambda m: m.group(1).split("|", 1)[0], txt)
    txt = MARKER_RE.sub("", txt)
    txt = re.sub(r"\s+([.,;:!?%)\]])", r"\1", txt)
    txt = re.sub(r"([(\[\u201c\u2018\"])\s+", r"\1", txt)
    txt = re.sub(r"\s+([\u2019'])", r"\1", txt)
    txt = re.sub(r"([\u2019'])\s+(s\b)", r"\1\2", txt)
    return ingest.clean_whitespace(txt)


def words(text: str):
    return WORD_RE.findall(text.lower())


def strong_parts_ok(strong: str) -> bool:
    parts = strong.split("+")
    return bool(parts) and all(STRONG_OK_RE.fullmatch(part) for part in parts)


def parse_dir(folder: Path, spine, collect_tags: bool = False):
    out = {}
    dropped = []
    tag_rows = []
    join_count = 0
    joined_vids = []
    for fp in sorted(folder.glob("*.usfm")):
        content = fp.read_text(encoding="utf-8", errors="replace")
        m_id = re.search(r"\\id\s+([A-Z0-9]{3})", content)
        if not m_id:
            continue
        book = m_id.group(1).upper().strip()
        if book == "NAH" and "NAM" in spine:
            book = "NAM"
        if book not in spine:
            continue
        acc = defaultdict(list)
        tag_acc = defaultdict(list)
        ch = v = 0

        def take(part, verse_no):
            nonlocal join_count
            body = NOTE_RE.sub("", part)
            tags = extract_tags(body) if collect_tags else []
            joined, njoin = join_printed_compounds(body)
            if njoin:
                join_count += njoin
                joined_vids.append(f"{book}.{ch}.{verse_no}")
            vt = clean_verse(joined)
            if not vt or DASH_ONLY.match(vt):
                if vt:
                    dropped.append(f"{book}.{ch}.{verse_no}")
                return
            rc, rv = ingest.remap_versification(book, ch, verse_no, spine)
            acc[(rc, rv)].append(vt)
            if tags:
                tag_acc[(rc, rv)].extend(tags)

        for raw in content.splitlines():
            line = raw.strip()
            if not line or SKIP_LINE.match(line):
                continue
            m_ch = re.match(r"^\\c\s+(\d+)", line)
            if m_ch:
                ch = int(m_ch.group(1))
                v = 0
                continue
            if "\\v " in line or line.startswith("\\v\t"):
                for part in re.split(r"(?=\\v\s+\d+)", line):
                    part = part.strip()
                    if not part:
                        continue
                    m_v = re.match(r"^\\v\s+(\d+)(?:[-a-zA-Z0-9]*)\s*(.*)", part, re.DOTALL)
                    if m_v and ch > 0:
                        v = int(m_v.group(1))
                        take(m_v.group(2), v)
                    elif ch > 0 and v > 0:
                        take(part, v)
            elif ch > 0 and v > 0:
                take(line, v)
        for (c, vv), chunks in acc.items():
            txt = ingest.clean_whitespace(" ".join(chunks))
            if txt:
                out[f"{book}.{c}.{vv}"] = txt
        for (c, vv), spans in tag_acc.items():
            vid = f"{book}.{c}.{vv}"
            for i, (surface, strong) in enumerate(spans, start=1):
                if not surface:
                    sys.exit(f"Empty KJV tag surface at {vid}")
                if strong is not None and not strong_parts_ok(strong):
                    sys.exit(f"Unexpected strong value at {vid}: {strong!r} on {surface!r}")
                tag_rows.append((vid, i, surface, strong, "eng-kjv2006"))
    seen = set()
    for vid, order, _surface, _strong, _edition in tag_rows:
        key = (vid, order)
        if key in seen:
            sys.exit(f"Duplicate KJV tag row {vid} word_order {order}")
        seen.add(key)
    missing_text = sorted({vid for vid, *_rest in tag_rows if vid not in out})
    if missing_text:
        sys.exit(f"Tags for verses with no text: {missing_text[:8]}")
    return out, dropped, tag_rows, join_count, joined_vids


def tagged(tag_rows, vid):
    return [(surface, strong) for v, _i, surface, strong, _e in tag_rows if v == vid]


def has_adjacent(rows, left, right):
    return any(rows[i] == left and rows[i + 1] == right for i in range(len(rows) - 1))


def connect():
    ingest.load_dotenv_files()
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST") or "localhost",
        port=int(os.getenv("POSTGRES_PORT") or 5432),
        dbname=os.getenv("POSTGRES_DB") or "mt_sinai_365dbr",
        user=os.getenv("POSTGRES_USER") or "365dbr_dev",
        password=os.getenv("POSTGRES_PASSWORD") or "",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    spine, expected = ingest.load_canonical_spine()
    kjv, kjv_dash, kjv_tags, kjv_joins, kjv_joined = parse_dir(KJV_DIR, spine, collect_tags=True)
    lsv, lsv_dash, lsv_tags, lsv_joins, lsv_joined = parse_dir(LSV_DIR, spine, collect_tags=False)
    if set(kjv) != expected or set(lsv) != expected:
        sys.exit("Parsed verse set does not match the 31,102-verse spine.")
    if kjv_dash:
        sys.exit(f"Unexpected KJV dash-only lines: {kjv_dash}")
    if sorted(lsv_dash) != ["3JN.1.15", "REV.12.18"]:
        sys.exit(f"Unexpected LSV dash-only lines: {lsv_dash}")
    if lsv_joins or lsv_joined or lsv_tags:
        sys.exit(f"LSV produced joins or tags: {lsv_joins} {lsv_joined[:8]}")
    if kjv_joins != 13 or sorted(kjv_joined) != sorted(EXPECTED_JOIN_VERSES):
        sys.exit(
            f"KJV joins {kjv_joins} at {kjv_joined}; expected one join in each of {list(EXPECTED_JOIN_VERSES)}"
        )
    if not kjv_tags:
        sys.exit("KJV tag extract returned no rows")

    for label, corpus in (("KJV", kjv), ("LSV", lsv)):
        bad = [vid for vid, txt in corpus.items() if "strong=" in txt or "\\w" in txt or not txt.strip()]
        if bad:
            sys.exit(f"{label} cleaner leak or empty text: {bad[:8]}")

    if tagged(kjv_tags, "2TH.3.18") != TAG_2TH_3_18:
        sys.exit(f"2TH.3.18 tags {tagged(kjv_tags, '2TH.3.18')}")
    if not has_adjacent(tagged(kjv_tags, "ACT.5.39"), ("can", "G1410"), ("not", "G3756")):
        sys.exit("ACT.5.39 tags are not can/G1410 then not/G3756")
    if not has_adjacent(tagged(kjv_tags, "HEB.9.5"), ("can", "G2076"), ("not", "G3756")):
        sys.exit("HEB.9.5 tags are not can/G2076 then not/G3756")
    two_ti = tagged(kjv_tags, "2TI.2.9")
    if not has_adjacent(two_ti, ("Where", "G3739"), ("in", "G1722")):
        sys.exit("2TI.2.9 tags are not Where/G3739 then in/G1722")
    if ("doer", "G2557") not in two_ti or any(surface.lower() == "evil" for surface, _n in two_ti):
        sys.exit(f"2TI.2.9 tag rows changed the evil/doer split: {two_ti}")

    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT verse_id, translation_id, text FROM verse_translations WHERE translation_id IN (1, 2)"
    )
    db = {(vid, tid): text for vid, tid, text in cur.fetchall()}
    cur.execute("SELECT count(*), count(strong_number) FROM original_tokens")
    token_count, strong_count = cur.fetchone()
    cur.execute(
        "SELECT text FROM verse_translations WHERE verse_id = '2TH.3.18' AND translation_id = 5"
    )
    lsb_before = cur.fetchone()[0]

    diffs = []
    kjv_rows = []
    for vid in sorted(expected):
        new = kjv[vid]
        old = db.get((vid, 2))
        if old is None:
            sys.exit(f"Missing KJV row {vid}")
        if words(new) != words(old):
            diffs.append(vid)
        kjv_rows.append((vid, 2, new, ingest.compute_sha256(new)))
    if diffs:
        sys.exit("KJV word diffs: " + ", ".join(diffs))
    if len(kjv_rows) != 31102:
        sys.exit(f"KJV row count {len(kjv_rows)}")

    lsv_rows = []
    for vid in sorted(expected):
        new = lsv[vid]
        old = db.get((vid, 1))
        if old is None:
            sys.exit(f"Missing LSV row {vid}")
        if words(new) != words(old):
            sys.exit(f"LSV word diff at {vid}")
        lsv_rows.append((vid, 1, new, ingest.compute_sha256(new)))

    spots = {
        (2, "2TH.3.18"): "The grace of our Lord Jesus Christ be with you all. Amen.",
        (1, "2TH.3.18"): "The grace of our Lord Jesus Christ [is] with you all! Amen.",
        (1, "SNG.8.14"): "Or to a young one of the harts on mountains of spices!",
        (2, "SNG.8.14"): "¶ Make haste, my beloved, and be thou like to a roe or to a young hart upon the mountains of spices.",
        (1, "REV.12.17"): "and the dragon was angry against the woman, and went away to make war with the rest of her seed, those keeping the commands of God, and having the testimony of Jesus.",
        (1, "3JN.1.14"): "and I hope to see you soon, and we will speak mouth to mouth. Peace to you! The friends greet you. Be greeting the friends by name.",
    }
    corpus_by_id = {1: lsv, 2: kjv}
    for (tid, vid), expect_txt in spots.items():
        if corpus_by_id[tid][vid] != expect_txt:
            sys.exit(f"Spot mismatch {tid} {vid}: {corpus_by_id[tid][vid]}")

    proofs = {
        "ACT.5.39": ("cannot",),
        "HEB.9.5": ("cannot",),
        "1TI.2.7": ("Whereunto",),
        "COL.3.17": ("whatsoever",),
        "2TI.2.9": ("Wherein", "evil doer"),
    }
    for vid, parts in proofs.items():
        for part in parts:
            if part not in kjv[vid]:
                sys.exit(f"{vid} is missing {part!r}: {kjv[vid]}")
    if "can not" in kjv["ACT.5.39"] or "evildoer" in kjv["2TI.2.9"]:
        sys.exit("A proven compound was left split, or evil doer was glued together")

    print(f"KJV to write {len(kjv_rows)} joins {kjv_joins} tags {len(kjv_tags)}")
    print(f"LSV to write {len(lsv_rows)}")
    print("Joined: " + ", ".join(kjv_joined))
    if not args.execute:
        print("Dry run only. Pass --execute to commit.")
        conn.close()
        return

    kjv_zip = str(SCRIPT_DIR / "RAW" / "KJV" / "eBible" / KJV_ZIP)
    lsv_zip = str(SCRIPT_DIR / "RAW" / "LSV" / "eBible" / LSV_ZIP)
    try:
        cur.execute(
            """
            CREATE TEMP TABLE ebible_load (
                verse_id text NOT NULL,
                translation_id int NOT NULL,
                text text NOT NULL,
                text_sha256 text NOT NULL,
                PRIMARY KEY (verse_id, translation_id)
            ) ON COMMIT DROP
            """
        )
        execute_values(
            cur,
            "INSERT INTO ebible_load (verse_id, translation_id, text, text_sha256) VALUES %s",
            kjv_rows + lsv_rows,
            page_size=2000,
        )
        cur.execute(
            """
            UPDATE verse_translations vt
            SET text = e.text,
                text_sha256 = e.text_sha256,
                source_note = CASE vt.translation_id WHEN 1 THEN %s WHEN 2 THEN %s END
            FROM ebible_load e
            WHERE vt.verse_id = e.verse_id
              AND vt.translation_id = e.translation_id
              AND vt.translation_id IN (1, 2)
            """,
            (LSV_NOTE, KJV_NOTE),
        )
        if cur.rowcount != len(kjv_rows) + len(lsv_rows):
            raise RuntimeError(f"Updated {cur.rowcount} rows, expected {len(kjv_rows) + len(lsv_rows)}")

        cur.execute(
            "UPDATE translations SET license = %s, source_bible_id = %s WHERE id = 1 AND code = 'LSV'",
            (LSV_LICENSE, "ebible:englsv"),
        )
        if cur.rowcount != 1:
            raise RuntimeError("LSV translation row was not updated")
        cur.execute(
            "UPDATE translations SET license = %s, source_bible_id = %s WHERE id = 2 AND code = 'KJV'",
            (KJV_LICENSE, "ebible:eng-kjv2006"),
        )
        if cur.rowcount != 1:
            raise RuntimeError("KJV translation row was not updated")

        cur.execute("SELECT to_regclass('public.kjv_english_strong_tags')")
        if cur.fetchone()[0] is None:
            raise RuntimeError("Apply db/migrations/008_kjv_english_strong_tags.sql before --execute")
        cur.execute("DELETE FROM kjv_english_strong_tags")
        execute_values(
            cur,
            """
            INSERT INTO kjv_english_strong_tags
                (verse_id, word_order, surface, strong_number, edition)
            VALUES %s
            """,
            kjv_tags,
            page_size=5000,
        )

        cur.execute(
            """
            UPDATE data_sources
            SET source_url = %s, fetch_date = %s, bible_id_used = %s, notes = %s
            WHERE id = 1
            """,
            (
                lsv_zip,
                RETRIEVED,
                "englsv",
                "Literal Standard Version from eBible englsv USFM. CC BY-SA 4.0, Covenant Press, 2020. "
                f"Zip sha256 {LSV_SHA}. 31,102 verse texts. Strong attributes were dropped and were not stored. "
                "Dash-only lines 3JN.1.15 and REV.12.18 were not merged into the previous verse.",
            ),
        )
        cur.execute(
            """
            UPDATE data_sources
            SET source_url = %s, fetch_date = %s, bible_id_used = %s, notes = %s
            WHERE id = 2
            """,
            (
                kjv_zip,
                RETRIEVED,
                "eng-kjv2006",
                "King James Version 1769 from eBible eng-kjv2006 USFM. Public domain outside the UK. "
                f"Zip sha256 {KJV_SHA}. All 31,102 verse texts. "
                "Thirteen tag-boundary spaces were closed where this same file spells the compound as one word "
                "(cannot, wherein, whereunto, whatsoever). "
                "2 Timothy 2:9 keeps the two words evil doer. "
                "Strong's tags are in kjv_english_strong_tags, edition eng-kjv2006. "
                "They were not copied onto original_tokens.",
            ),
        )

        cur.execute(
            """
            SELECT translation_id, count(*)
            FROM verse_translations
            WHERE translation_id IN (1, 2)
              AND text <> ''
              AND length(text_sha256) = 64
            GROUP BY translation_id
            ORDER BY translation_id
            """
        )
        counts = cur.fetchall()
        if counts != [(1, 31102), (2, 31102)]:
            raise RuntimeError(f"Row counts {counts}")
        cur.execute(
            """
            SELECT count(*) FROM verse_translations
            WHERE translation_id IN (1, 2)
              AND (position('strong=' in text) > 0 OR position('\\w' in text) > 0)
            """
        )
        if cur.fetchone()[0] != 0:
            raise RuntimeError("strong= or \\w remains in verse text")
        cur.execute(
            "SELECT count(*) FROM verse_translations WHERE translation_id = 1 AND source_note = %s",
            (LSV_NOTE,),
        )
        if cur.fetchone()[0] != 31102:
            raise RuntimeError("LSV source_note count")
        cur.execute(
            "SELECT count(*) FROM verse_translations WHERE translation_id = 2 AND source_note = %s",
            (KJV_NOTE,),
        )
        if cur.fetchone()[0] != 31102:
            raise RuntimeError("KJV source_note count")
        cur.execute(
            """
            SELECT count(*) FROM verse_translations
            WHERE translation_id = 2
              AND (source_note ILIKE '%%api.bible%%' OR source_note ILIKE '%%bibleId=%%')
            """
        )
        if cur.fetchone()[0] != 0:
            raise RuntimeError("KJV api.bible source_note remains")
        cur.execute(
            "SELECT text, source_note FROM verse_translations WHERE verse_id = '2TH.3.18' AND translation_id = 2"
        )
        kjv_218, note_218 = cur.fetchone()
        if kjv_218 != spots[(2, "2TH.3.18")] or note_218 != KJV_NOTE:
            raise RuntimeError("2TH.3.18 KJV")
        cur.execute(
            "SELECT text FROM verse_translations WHERE verse_id = '2TH.3.18' AND translation_id = 1"
        )
        if cur.fetchone()[0] != spots[(1, "2TH.3.18")]:
            raise RuntimeError("2TH.3.18 LSV")
        cur.execute(
            "SELECT text, source_note FROM verse_translations WHERE verse_id = 'ACT.5.39' AND translation_id = 2"
        )
        act_text, act_note = cur.fetchone()
        if "cannot" not in act_text or "can not" in act_text or act_note != KJV_NOTE:
            raise RuntimeError(f"ACT.5.39 text or note: {act_text}")
        cur.execute(
            "SELECT text, source_note FROM verse_translations WHERE verse_id = '2TI.2.9' AND translation_id = 2"
        )
        ti_text, ti_note = cur.fetchone()
        if "Wherein" not in ti_text or "evil doer" not in ti_text or "evildoer" in ti_text or ti_note != KJV_NOTE:
            raise RuntimeError(f"2TI.2.9 text or note: {ti_text}")
        cur.execute(
            """
            SELECT surface, strong_number
            FROM kjv_english_strong_tags
            WHERE verse_id = '2TH.3.18'
            ORDER BY word_order
            """
        )
        if cur.fetchall() != TAG_2TH_3_18:
            raise RuntimeError("2TH.3.18 tag rows")
        cur.execute("SELECT count(*) FROM kjv_english_strong_tags")
        if cur.fetchone()[0] != len(kjv_tags):
            raise RuntimeError("KJV tag row count")
        cur.execute(
            "SELECT text FROM verse_translations WHERE verse_id = '2TH.3.18' AND translation_id = 5"
        )
        if cur.fetchone()[0] != lsb_before:
            raise RuntimeError("LSB 2TH.3.18 changed")
        cur.execute("SELECT count(*), count(strong_number) FROM original_tokens")
        if cur.fetchone() != (token_count, strong_count):
            raise RuntimeError("original_tokens count changed")
        cur.execute(
            """
            SELECT count(*) FROM verse_translations
            WHERE translation_id IN (5, 6, 7)
            """
        )
        if cur.fetchone()[0] != 31102 * 3:
            raise RuntimeError("LSB/WEB/YLT row count changed")
        conn.commit()
        print("Committed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
