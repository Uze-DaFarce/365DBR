#!/usr/bin/env python3
"""Classify the out-of-order links and the OSHB words missing from original_tokens.

Read-only. Uses the same letter rules as load_stepbible_tokens.py.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from difflib import SequenceMatcher

import load_stepbible_tokens as step
import oshb_wlc as src


def shift_verse(verse_id, delta):
    book, chapter, verse = verse_id.split(".")
    number = int(verse) + delta
    if number < 1:
        return None
    return f"{book}.{chapter}.{number}"


def main():
    print("Loading OSHB")
    oshb = src.load_oshb_wlc()
    conn = step.connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT verse_id, word_order, surface_text
        FROM original_tokens
        WHERE language = 'hebrew'
        ORDER BY verse_id, word_order
        """
    )
    tokens = defaultdict(list)
    for verse_id, _order, surface in cur.fetchall():
        tokens[verse_id].append(step.heb_letters(surface or ""))

    cur.execute(
        """
        SELECT verse_id, letters
        FROM stepbible_token_rows
        WHERE source = 'TAHOT'
          AND attach_candidate
          AND verse_id IS NOT NULL
          AND heb_ref IS NULL
          AND original_token_id IS NULL
          AND letters IS NOT NULL
        """
    )
    unlinked = defaultdict(Counter)
    for verse_id, letters in cur.fetchall():
        unlinked[verse_id][letters] += 1

    missing_n = 0
    morph_class = Counter()
    length_class = Counter()
    fused = dropped = in_offset_verse = 0
    unlinked_hit = 0
    samples = {name: [] for name in ("fused", "dropped", "offset_verse")}
    verse_offset_exact = Counter()
    offset_verses = {}

    compared = exact = 0
    prepared = []
    for verse_id, words in oshb.items():
        right = tokens.get(verse_id)
        if right is None:
            continue
        left = [item[3] for item in words]
        prepared.append((verse_id, words, left, right))
        compared += 1
        if left == right:
            exact += 1
            continue
        for delta in (1, -1):
            other_id = shift_verse(verse_id, delta)
            other = tokens.get(other_id or "")
            if other == left:
                verse_offset_exact[delta] += 1
                offset_verses[verse_id] = other_id
                break

    clean_gap_verses = 0
    clean_gap_words = 0
    for verse_id, words, left, right in prepared:
        if left == right:
            continue
        matcher = SequenceMatcher(a=left, b=right, autojunk=False)
        opcodes = list(matcher.get_opcodes())
        if verse_id not in offset_verses:
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
            if gap_ok and gap_words:
                clean_gap_verses += 1
                clean_gap_words += gap_words
        for tag, i1, i2, _j1, _j2 in opcodes:
            if tag != "delete":
                continue
            for index in range(i1, i2):
                missing_n += 1
                surface, _lemma, morph, letters = words[index]
                length_class[min(len(letters), 8)] += 1
                if "Sp" in (morph or ""):
                    morph_class["suffix_pronoun"] += 1
                elif (morph or "").startswith("HR") or (morph or "").startswith("HTd"):
                    morph_class["preposition_or_article"] += 1
                else:
                    morph_class[(morph or "no_morph").split("/")[0]] += 1
                prev = left[index - 1] if index else ""
                nxt = left[index + 1] if index + 1 < len(left) else ""
                joined = {prev + letters, letters + nxt}
                if verse_id in offset_verses:
                    kind = "offset_verse"
                    in_offset_verse += 1
                elif any(piece and piece in right for piece in joined):
                    kind = "fused"
                    fused += 1
                else:
                    kind = "dropped"
                    dropped += 1
                if unlinked[verse_id][letters]:
                    unlinked_hit += 1
                if len(samples[kind]) < 6:
                    samples[kind].append((verse_id, surface, morph, letters))

    print(f"OSHB verses compared {compared} exact {exact}")
    print(f"OSHB verses whose whole consonant list is the neighboring token verse {dict(verse_offset_exact)}")
    print(f"Verses whose only gap is OSHB suffix pronouns {clean_gap_verses} words {clean_gap_words}")
    print(f"Deleted OSHB words (same set as the 6,072 audit) {missing_n}")
    print(f"  whole verse sits under the neighboring verse id {in_offset_verse}")
    print(f"  fused into an adjacent token {fused}")
    print(f"  not in this verse and not fused into a neighbor token {dropped}")
    print(f"  also an unlinked TAHOT row in that verse {unlinked_hit}")
    print(f"  length {dict(sorted(length_class.items()))}")
    print(f"  morph {morph_class.most_common(12)}")
    for name, rows in samples.items():
        print(f"  sample {name}")
        for row in rows:
            print("   ", row)

    cur.execute(
        """
        SELECT s.verse_id, s.source, s.word_index, s.text_type, s.letters, s.english,
               t.word_order, t.surface_text
        FROM stepbible_token_rows s
        JOIN original_tokens t ON t.id = s.original_token_id
        ORDER BY s.verse_id, s.source, s.word_index
        """
    )
    linked = cur.fetchall()
    by_verse_letters = defaultdict(Counter)
    token_letters = defaultdict(Counter)
    cur.execute(
        """
        SELECT verse_id, language, surface_text
        FROM original_tokens
        """
    )
    for verse_id, language, surface in cur.fetchall():
        norm = step.heb_letters(surface or "") if language == "hebrew" else step.grk_letters(surface or "")
        if norm:
            token_letters[verse_id][norm] += 1
    for verse_id, source, _wi, _typ, letters, _en, _wo, _surf in linked:
        by_verse_letters[(verse_id, source)][letters] += 1

    classes = Counter()
    by_source = Counter()
    gap_by_class = Counter()
    examples = defaultdict(list)
    prev = None
    for row in linked:
        verse_id, source, word_index, text_type, letters, english, word_order, surface = row
        key = (verse_id, source)
        if prev and prev[0] == key and word_order < prev[1]:
            step_n = by_verse_letters[key][letters]
            token_n = token_letters[verse_id][letters]
            gap = prev[1] - word_order
            if step_n > 1:
                kind = "several_step_rows_one_token"
            elif token_n == 1 and step_n == 1:
                kind = "only_one_word_each_side"
            else:
                kind = f"other_step_{step_n}_token_{token_n}"
            classes[kind] += 1
            by_source[(source, kind)] += 1
            gap_by_class[(kind, min(gap, 9))] += 1
            if len(examples[kind]) < 5:
                examples[kind].append(
                    (verse_id, source, text_type, letters, english, f"step {word_index}->token {word_order}", f"gap {gap}")
                )
        prev = (key, word_order, word_index)

    print("\nOut-of-order links", sum(classes.values()))
    print(dict(classes))
    print(" by source", dict(by_source))
    for kind, rows in examples.items():
        print(f" sample {kind}")
        for row in rows:
            print("  ", row)

    cur.execute(
        """
        SELECT same_english, count(*)
        FROM (
            SELECT bool_and(english IS NOT DISTINCT FROM first_english) AS same_english
            FROM (
                SELECT original_token_id, english,
                       first_value(english) OVER (PARTITION BY original_token_id ORDER BY id) AS first_english
                FROM stepbible_token_rows
                WHERE original_token_id IS NOT NULL
            ) x
            GROUP BY original_token_id
            HAVING count(*) > 1
        ) y
        GROUP BY same_english
        """
    )
    print("\nShared tokens, English agrees?", cur.fetchall())
    conn.close()


if __name__ == "__main__":
    main()
