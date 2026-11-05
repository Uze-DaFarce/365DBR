#!/usr/bin/env python3
"""Read-only check of token text against the source files.

Hebrew referee: apps/365DBR/RAW/OSHB/wlc (Open Scriptures Hebrew Bible, WLC 4.20).
Greek referee: apps/365DBR/RAW/GRCTR USX running text. Footnotes are kept out of
the verse body. Paragraphs styled d are colophons, not verse words.

Does not write the database. Does not guess a Strong's number.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import load_stepbible_tokens as step
import oshb_wlc as src

APP = Path(__file__).resolve().parent
GRCTR_DIR = APP / "RAW" / "GRCTR" / "release" / "USX_1"
GREEK_WORD = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]+")
COLOPHON_STYLES = {"d", "s", "s1", "ms", "mr", "r", "sp"}


def opcodes(left, right):
    missing = extra = replaced_left = replaced_right = 0
    samples = []
    matcher = SequenceMatcher(a=left, b=right, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            missing += i2 - i1
            samples.append(("missing_from_right", left[i1:i2]))
        elif tag == "insert":
            extra += j2 - j1
            samples.append(("extra_on_right", right[j1:j2]))
        else:
            replaced_left += i2 - i1
            replaced_right += j2 - j1
            samples.append(("replaced", left[i1:i2], right[j1:j2]))
    return missing, extra, replaced_left, replaced_right, samples


def parse_grctr():
    body = defaultdict(list)
    colophon = defaultdict(list)
    for path in sorted(GRCTR_DIR.glob("*.usx")):
        current = None
        in_note = 0
        in_colophon = 0
        for event, elem in ET.iterparse(path, events=("start", "end")):
            tag = elem.tag.split("}")[-1]
            if event == "start":
                if tag == "verse" and elem.get("sid"):
                    book, rest = elem.get("sid").split(" ", 1)
                    chapter, verse = rest.split(":")
                    current = f"{book}.{int(chapter)}.{int(verse)}"
                elif tag == "note":
                    in_note += 1
                elif tag == "para" and (elem.get("style") or "") in COLOPHON_STYLES:
                    in_colophon += 1
                if current and in_note == 0 and elem.text and tag not in ("verse", "chapter", "book"):
                    bucket = colophon if in_colophon else body
                    bucket[current].extend(GREEK_WORD.findall(elem.text))
            else:
                if tag == "note" and in_note:
                    in_note -= 1
                if current and in_note == 0 and elem.tail:
                    bucket = colophon if in_colophon else body
                    bucket[current].extend(GREEK_WORD.findall(elem.tail))
                if tag == "verse" and elem.get("eid"):
                    current = None
                if tag == "para" and (elem.get("style") or "") in COLOPHON_STYLES and in_colophon:
                    in_colophon -= 1
                elem.clear()
    return body, colophon


def fetch_tokens(conn, language):
    by_verse = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT verse_id, word_order, surface_text
            FROM original_tokens
            WHERE language = %s
            ORDER BY verse_id, word_order
            """,
            (language,),
        )
        for verse_id, _order, surface in cur.fetchall():
            by_verse[verse_id].append(surface or "")
    return by_verse


def fetch_step(conn, source, prefix):
    by_verse = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT verse_id, word_index, text_type, letters, original_token_id IS NOT NULL
            FROM stepbible_token_rows
            WHERE source = %s
              AND verse_id IS NOT NULL
              AND heb_ref IS NULL
              AND attach_candidate
              AND letters IS NOT NULL
              AND text_type LIKE %s
            ORDER BY verse_id, word_index
            """,
            (source, prefix),
        )
        for verse_id, word_index, text_type, letters, linked in cur.fetchall():
            by_verse[verse_id].append((word_index, text_type, letters, linked))
    return by_verse


def compare_maps(left_map, right_map, label, sample_ids):
    both = sorted(set(left_map) & set(right_map))
    exact = 0
    missing = extra = repl_l = repl_r = 0
    bad_verses = []
    for verse_id in both:
        left = left_map[verse_id]
        right = right_map[verse_id]
        if left == right:
            exact += 1
            continue
        m, e, rl, rr, samples = opcodes(left, right)
        missing += m
        extra += e
        repl_l += rl
        repl_r += rr
        if len(bad_verses) < 12 or verse_id in sample_ids:
            bad_verses.append((verse_id, m, e, rl, rr, samples[:4]))
    print(f"\n{label}")
    print(f"  verses only on left {len(set(left_map) - set(right_map))}")
    print(f"  verses only on right {len(set(right_map) - set(left_map))}")
    print(f"  verses compared {len(both)}  exact {exact}")
    print(f"  words missing from right {missing}  extra on right {extra}")
    print(f"  replaced left {repl_l}  replaced right {repl_r}")
    for item in bad_verses[:12]:
        print(" ", item[0], "missing", item[1], "extra", item[2], "replaced", item[3], item[5])


def link_audit(conn):
    mismatch = 0
    checked = 0
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.source, s.surface, s.letters, t.surface_text, t.language, t.verse_id, s.verse_id
            FROM stepbible_token_rows s
            JOIN original_tokens t ON t.id = s.original_token_id
            """
        )
        for source, surface, stored, token_surface, language, token_verse, step_verse in cur.fetchall():
            checked += 1
            expect = step.letters_for(source, surface or "")
            token_letters = step.heb_letters(token_surface or "") if language == "hebrew" else step.grk_letters(token_surface or "")
            if expect != stored or expect != token_letters or token_verse != step_verse:
                mismatch += 1
        cur.execute(
            """
            SELECT count(*) FROM (
                SELECT original_token_id
                FROM stepbible_token_rows
                WHERE original_token_id IS NOT NULL
                GROUP BY original_token_id
                HAVING count(*) > 1
            ) d
            """
        )
        shared = cur.fetchone()[0]
        cur.execute(
            """
            SELECT count(*) FROM (
                SELECT original_token_id
                FROM stepbible_token_rows
                WHERE original_token_id IS NOT NULL
                GROUP BY original_token_id
                HAVING count(DISTINCT letters) > 1
            ) d
            """
        )
        shared_different = cur.fetchone()[0]
        cur.execute(
            """
            SELECT s.verse_id, s.source, s.word_index, t.word_order
            FROM stepbible_token_rows s
            JOIN original_tokens t ON t.id = s.original_token_id
            ORDER BY s.verse_id, s.source, s.word_index
            """
        )
        inversions = 0
        examples = []
        prev = None
        for verse_id, source, word_index, word_order in cur.fetchall():
            key = (verse_id, source)
            if prev and prev[0] == key and word_order < prev[1]:
                inversions += 1
                if len(examples) < 8:
                    examples.append((verse_id, source, prev[2], prev[1], word_index, word_order))
            prev = (key, word_order, word_index)
    print("\nStored links")
    print(f"  checked {checked}  letter or verse mismatches {mismatch}")
    print(f"  tokens used by more than one STEPBible row {shared}")
    print(f"  of those, rows disagree on letters {shared_different}")
    print(f"  order inversions {inversions}")
    for example in examples:
        print(" ", example)


def confirmed_omissions(oshb_cons, tokens, step_rows):
    """OSHB words absent from tokens whose letters are an unlinked TAHOT row."""
    confirmed = 0
    examples = []
    verses = set(oshb_cons) & set(tokens)
    for verse_id in verses:
        left = oshb_cons[verse_id]
        right = tokens[verse_id]
        if left == right:
            continue
        _m, _e, _rl, _rr, samples = opcodes(left, right)
        unlinked = {letters for _i, _t, letters, linked in step_rows.get(verse_id, []) if not linked}
        for kind, words in ((item[0], item[1]) for item in samples if item[0] == "missing_from_right"):
            for word in words:
                if word in unlinked:
                    confirmed += 1
                    if len(examples) < 8:
                        examples.append((verse_id, word))
    print("\nOSHB words missing from original_tokens and present as an unlinked TAHOT row")
    print(f"  {confirmed}")
    for example in examples:
        print(" ", example)


def main():
    print("Loading OSHB WLC 4.20 word file")
    oshb = src.load_oshb_wlc()
    oshb_cons = {vid: [item[3] for item in words] for vid, words in oshb.items()}
    print(f"  OSHB verses {len(oshb_cons)}  words {sum(len(v) for v in oshb_cons.values())}")

    conn = step.connect()
    try:
        link_audit(conn)
        hebrew = {
            vid: [step.heb_letters(surface) for surface in words]
            for vid, words in fetch_tokens(conn, "hebrew").items()
        }
        greek = {
            vid: [step.grk_letters(surface) for surface in words]
            for vid, words in fetch_tokens(conn, "greek").items()
        }
        tahot_l = fetch_step(conn, "TAHOT", "L%")
        tahot_l_letters = {vid: [row[2] for row in rows] for vid, rows in tahot_l.items()}
        compare_maps(oshb_cons, hebrew, "OSHB consonants vs original_tokens", {"SNG.8.14", "PSA.119.176"})
        compare_maps(oshb_cons, tahot_l_letters, "OSHB consonants vs TAHOT rows whose type starts with L", {"SNG.8.14"})
        confirmed_omissions(oshb_cons, hebrew, tahot_l)

        print("\nLoading GRCTR USX running text")
        body, colophon = parse_grctr()
        grctr = {vid: [step.grk_letters(word) for word in words] for vid, words in body.items()}
        colo = {vid: [step.grk_letters(word) for word in words] for vid, words in colophon.items()}
        print(f"  GRCTR verses {len(grctr)}  colophon verses {sum(1 for v in colo.values() if v)}")
        compare_maps(grctr, greek, "GRCTR verse body vs original_tokens", {"2TH.3.18", "1TH.5.28"})
        tagnt = fetch_step(conn, "TAGNT", "%")
        tagnt_letters = {vid: [row[2] for row in rows] for vid, rows in tagnt.items()}
        compare_maps(grctr, tagnt_letters, "GRCTR verse body vs TAGNT K-marked rows", {"2TH.3.18"})
        colo_words = sum(len(v) for v in colo.values())
        print(f"\nGRCTR colophon words kept out of the verse body: {colo_words}")
        if "2TH.3.18" in colo:
            print("  2TH.3.18 colophon", colo["2TH.3.18"])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
