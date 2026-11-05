#!/usr/bin/env python3
"""Insert the OSHB suffix pronouns that original_tokens dropped.

Only verses whose consonant list already matches OSHB except for deletes,
and whose every deleted OSHB word has morph containing Sp. Offset verses
(the whole OSHB list equals a neighboring token verse) are left untouched.

New rows: strong_number NULL, lemma NULL, morph and surface from that <w>.
The OSHB lemma is stored in extra, not as a Strong's number.

One transaction. Commits only after Song 8:14 matches OSHB and 1 Chronicles 12
is unchanged. Then relinks stepbible_token_rows by letters.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from difflib import SequenceMatcher

from psycopg2.extras import execute_values

import load_stepbible_tokens as step
import oshb_wlc

EXPECTED_VERSES = 4236
EXPECTED_WORDS = 5260
SOURCE = "oshb-wlc-4.20"


def shift_verse(verse_id, delta):
    book, chapter, verse = verse_id.split(".")
    number = int(verse) + delta
    if number < 1:
        return None
    return f"{book}.{chapter}.{number}"


def main():
    print("Loading OSHB")
    oshb = oshb_wlc.load_oshb_wlc()
    conn = step.connect()
    cur = conn.cursor()
    cur.execute("SELECT max(word_order) FROM original_tokens")
    max_order = cur.fetchone()[0] or 0
    if max_order >= 1_000_000:
        sys.exit(f"word_order {max_order} is already in the renumber range")
    cur.execute("SELECT count(*) FROM original_tokens WHERE language = 'greek'")
    greek_before = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM original_tokens WHERE language = 'hebrew'")
    hebrew_before = cur.fetchone()[0]

    cur.execute(
        """
        SELECT id, verse_id, word_order, surface_text, source_verse_id
        FROM original_tokens
        WHERE language = 'hebrew'
        ORDER BY verse_id, word_order
        """
    )
    tokens = defaultdict(list)
    for token_id, verse_id, _order, surface, source_verse_id in cur.fetchall():
        tokens[verse_id].append((token_id, surface, source_verse_id))

    cur.execute(
        """
        SELECT id, verse_id, word_order, surface_text
        FROM original_tokens
        WHERE verse_id LIKE '1CH.12.%'
        ORDER BY verse_id, word_order, id
        """
    )
    chronicles = cur.fetchall()

    prepared = []
    offset_verses = {}
    for verse_id, words in oshb.items():
        rows = tokens.get(verse_id)
        if rows is None:
            continue
        left = [item[3] for item in words]
        right = [step.heb_letters(surface or "") for _tid, surface, _src in rows]
        prepared.append((verse_id, words, rows, left, right))
        if left == right:
            continue
        for delta in (1, -1):
            other_id = shift_verse(verse_id, delta)
            other_rows = tokens.get(other_id or "")
            if other_rows is None:
                continue
            other = [step.heb_letters(surface or "") for _tid, surface, _src in other_rows]
            if other == left:
                offset_verses[verse_id] = other_id
                break

    plan = {}
    problems = []
    for verse_id, words, rows, left, right in prepared:
        if left == right or verse_id in offset_verses:
            continue
        opcodes = list(SequenceMatcher(a=left, b=right, autojunk=False).get_opcodes())
        gap_ok = True
        gap_words = 0
        for tag, i1, i2, _j1, _j2 in opcodes:
            if tag == "equal":
                continue
            if tag != "delete":
                gap_ok = False
                break
            for index in range(i1, i2):
                morph = words[index][2] or ""
                if "Sp" not in morph:
                    gap_ok = False
                    break
                gap_words += 1
            if not gap_ok:
                break
        if not (gap_ok and gap_words):
            continue
        sources = {row[2] for row in rows}
        if len(sources) != 1:
            problems.append((verse_id, "source_verse_id differs inside the verse"))
            continue
        source_verse_id = sources.pop()
        items = []
        consumed = []
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "equal":
                if (i2 - i1) != (j2 - j1):
                    problems.append((verse_id, "equal opcode length mismatch"))
                    items = None
                    break
                for offset, index in enumerate(range(j1, j2)):
                    if left[i1 + offset] != right[index]:
                        problems.append((verse_id, "equal opcode letters differ"))
                        items = None
                        break
                    items.append(("keep", rows[index][0]))
                    consumed.append(index)
                if items is None:
                    break
            elif tag == "delete":
                for index in range(i1, i2):
                    surface, lemma, morph, letters = words[index]
                    if not surface or not letters or "Sp" not in (morph or ""):
                        problems.append((verse_id, "deleted word is not an OSHB suffix"))
                        items = None
                        break
                    if step.heb_letters(surface) != letters:
                        problems.append((verse_id, "surface consonants differ from the OSHB norm"))
                        items = None
                        break
                    items.append(("insert", surface, morph, lemma, source_verse_id))
                if items is None:
                    break
            else:
                problems.append((verse_id, f"unexpected opcode {tag}"))
                items = None
                break
        if items is None:
            continue
        if consumed != list(range(len(rows))):
            problems.append((verse_id, "existing tokens were not all kept"))
            continue
        plan[verse_id] = items

    word_count = sum(1 for items in plan.values() for item in items if item[0] == "insert")
    print(f"Clean suffix verses {len(plan)} words {word_count}")
    print(f"Offset verses left untouched {len(offset_verses)}")
    if problems or len(plan) != EXPECTED_VERSES or word_count != EXPECTED_WORDS:
        for row in problems[:8]:
            print(" ", row)
        conn.rollback()
        conn.close()
        sys.exit(
            f"Refusing to write. Expected {EXPECTED_VERSES} verses and "
            f"{EXPECTED_WORDS} words; got {len(plan)} verses, {word_count} words, "
            f"{len(problems)} problems."
        )
    if "SNG.8.14" not in plan:
        conn.close()
        sys.exit("Song 8:14 was not in the suffix plan")
    if any(verse_id.startswith("1CH.12.") for verse_id in plan):
        conn.close()
        sys.exit("1 Chronicles 12 was in the suffix plan")

    keeps = []
    inserts = []
    for verse_id, items in plan.items():
        for order, item in enumerate(items, start=1):
            if item[0] == "keep":
                keeps.append((item[1], order))
            else:
                _kind, surface, morph, lemma, source_verse_id = item
                inserts.append(
                    (
                        verse_id,
                        order,
                        "hebrew",
                        surface,
                        None,
                        None,
                        morph,
                        json.dumps({"source": SOURCE, "oshb_lemma": lemma}, ensure_ascii=False),
                        source_verse_id,
                    )
                )
    print(f"Updating {len(keeps)} existing tokens and inserting {len(inserts)} suffix tokens")
    verse_ids = list(plan)
    cur.execute(
        """
        SELECT count(*) FROM original_tokens
        WHERE verse_id = ANY(%s) AND language <> 'hebrew'
        """,
        (verse_ids,),
    )
    other_language = cur.fetchone()[0]
    if other_language:
        conn.close()
        sys.exit(f"{other_language} non-Hebrew tokens sit in a suffix verse")
    cur.execute(
        """
        UPDATE original_tokens
        SET word_order = word_order + 1000000
        WHERE verse_id = ANY(%s)
        """,
        (verse_ids,),
    )
    execute_values(
        cur,
        """
        UPDATE original_tokens AS t
        SET word_order = v.word_order
        FROM (VALUES %s) AS v(id, word_order)
        WHERE t.id = v.id
        """,
        keeps,
        template="(%s, %s)",
        page_size=2000,
    )
    execute_values(
        cur,
        """
        INSERT INTO original_tokens (
            verse_id, word_order, language, surface_text,
            strong_number, lemma, morph, extra, source_verse_id
        ) VALUES %s
        """,
        inserts,
        template="(%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)",
        page_size=2000,
    )

    cur.execute(
        """
        SELECT count(*),
               count(*) FILTER (WHERE strong_number IS NULL),
               count(*) FILTER (WHERE lemma IS NULL),
               count(DISTINCT verse_id)
        FROM original_tokens
        WHERE extra->>'source' = %s
        """,
        (SOURCE,),
    )
    inserted, null_strong, null_lemma, insert_verses = cur.fetchone()
    cur.execute("SELECT surface_text FROM original_tokens WHERE verse_id = 'SNG.8.14' ORDER BY word_order")
    song = [step.heb_letters(row[0] or "") for row in cur.fetchall()]
    song_expect = [item[3] for item in oshb["SNG.8.14"]]
    cur.execute(
        """
        SELECT id, verse_id, word_order, surface_text
        FROM original_tokens
        WHERE verse_id LIKE '1CH.12.%'
        ORDER BY verse_id, word_order, id
        """
    )
    chronicles_after = cur.fetchall()
    cur.execute("SELECT count(*) FROM original_tokens WHERE language = 'greek'")
    greek_after = cur.fetchone()[0]
    cur.execute(
        """
        SELECT count(*) FROM original_tokens
        WHERE extra->>'source' = %s AND verse_id = ANY(%s)
        """,
        (SOURCE, list(offset_verses)),
    )
    offset_inserts = cur.fetchone()[0]

    failed = []
    if (inserted, null_strong, null_lemma, insert_verses) != (
        EXPECTED_WORDS,
        EXPECTED_WORDS,
        EXPECTED_WORDS,
        EXPECTED_VERSES,
    ):
        failed.append(
            f"insert check {inserted} null_strong {null_strong} "
            f"null_lemma {null_lemma} verses {insert_verses}"
        )
    if song != song_expect:
        failed.append(f"Song 8:14 consonants {song} != OSHB {song_expect}")
    if chronicles_after != chronicles:
        failed.append("1 Chronicles 12 token rows changed")
    if greek_after != greek_before:
        failed.append(f"Greek token count {greek_before} -> {greek_after}")
    if offset_inserts:
        failed.append(f"{offset_inserts} suffix rows landed in offset verses")
    if failed:
        conn.rollback()
        conn.close()
        sys.exit("Rolled back. " + "; ".join(failed))

    conn.commit()
    print(
        f"Committed. Hebrew tokens {hebrew_before} -> {hebrew_before + EXPECTED_WORDS}. "
        "Song 8:14 matches OSHB. 1 Chronicles 12 is unchanged."
    )
    print("Linking STEPBible rows by letters")
    step.link_rows(conn)

    cur.execute(
        """
        SELECT surface, english, original_token_id IS NOT NULL
        FROM stepbible_token_rows
        WHERE verse_id = 'SNG.8.14' AND source = 'TAHOT'
        ORDER BY word_index
        """
    )
    print("Song 8:14 TAHOT")
    for row in cur.fetchall():
        print(" ", row)
    cur.execute(
        """
        SELECT same_english, count(*)
        FROM (
            SELECT bool_and(english IS NOT DISTINCT FROM first_english) AS same_english
            FROM (
                SELECT original_token_id, english,
                       first_value(english) OVER (
                           PARTITION BY original_token_id ORDER BY id
                       ) AS first_english
                FROM stepbible_token_rows
                WHERE original_token_id IS NOT NULL
            ) x
            GROUP BY original_token_id
            HAVING count(*) > 1
        ) y
        GROUP BY same_english
        """
    )
    print("Shared tokens, English agrees?", cur.fetchall())
    conn.close()


if __name__ == "__main__":
    main()
