#!/usr/bin/env python3
"""Load STEPBible TAHOT and TAGNT word rows into stepbible_token_rows.

Source directory:
  apps/365DBR/RAW/STEPBible/Translators Amalgamated OT+NT/

Does not write original_tokens, ws/, or day packs.
Connects with POSTGRES_* from db/.env. Ignores DATABASE_URL (the password
contains @, so that URL parses the host wrong).

  python apps/365DBR/load_stepbible_tokens.py --scan
  python apps/365DBR/load_stepbible_tokens.py --execute
  python apps/365DBR/load_stepbible_tokens.py --link-only
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

import bible_common

SCRIPT = Path(__file__).resolve()
APP = SCRIPT.parent
REPO = APP.parents[1]
SRC_DIR = APP / "RAW" / "STEPBible" / "Translators Amalgamated OT+NT"
MIGRATION = REPO / "db" / "migrations" / "009_stepbible_token_rows.sql"

REF_RE = re.compile(
    r"^(?P<book>[1-3]?[A-Za-z]+)\.(?P<ch>\d+)\.(?P<vs>\d+)"
    r"(?:\((?P<heb>[^)]+)\))?"
    r"#(?P<w>\d+)=(?P<typ>\S+)$"
)
GREEK_PAREN_RE = re.compile(r"\(([^)]*)\)\s*$")
MIN_ROWS = 250_000

INSERT_SQL = """
INSERT INTO stepbible_token_rows (
    source, source_file, line_no, ref_raw, book_code, chapter, verse_num,
    verse_id, heb_ref, word_index, text_type, surface, transliteration,
    english, dstrong, grammar, meaning_variants, spelling_variants,
    dictionary_gloss, editions, spanish, sub_meaning, root_strong,
    alt_strongs, conjoin_word, expanded_strong, letters, attach_candidate
) VALUES %s
"""


def read_env(path: Path) -> dict:
    env = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def connect():
    env = read_env(REPO / "db" / ".env")
    password = env.get("POSTGRES_PASSWORD") or ""
    if not password:
        sys.exit("db/.env has no POSTGRES_PASSWORD")
    host = env.get("POSTGRES_HOST") or "localhost"
    port = int(env.get("POSTGRES_PORT") or 5432)
    dbname = env.get("POSTGRES_DB") or "mt_sinai_365dbr"
    user = env.get("POSTGRES_USER") or "365dbr_dev"
    print(f"Connecting to {user}@{host}:{port}/{dbname}")
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=10,
    )


def heb_letters(text: str) -> str:
    # ס and פ after sof pasuq are section marks, not letters of the word.
    if "\u05c3" in text:
        head, _sep, tail = text.partition("\u05c3")
        tail = tail.replace("\u05e1", "").replace("\u05e4", "")
        text = head + tail
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if "\u05d0" <= ch <= "\u05ea")


def grk_letters(text: str) -> str:
    text = GREEK_PAREN_RE.sub("", text)
    text = unicodedata.normalize("NFD", text)
    out = []
    for ch in text:
        if unicodedata.category(ch) == "Mn":
            continue
        if ch == "ς":
            ch = "σ"
        if ch.isalpha() and ("\u0370" <= ch <= "\u03ff" or "\u1f00" <= ch <= "\u1fff"):
            out.append(ch.lower())
    return "".join(out)


def letters_for(source: str, surface: str) -> str:
    if source == "TAHOT":
        return heb_letters(surface)
    return grk_letters(surface)


def is_candidate(source: str, text_type: str) -> bool:
    if source == "TAHOT":
        return text_type[:1] in ("L", "Q")
    return "K" in text_type


def field(cols: list, index: int):
    if index >= len(cols):
        return None
    value = cols[index].strip()
    return value or None


def source_files():
    found = []
    for source, pattern in (("TAHOT", "TAHOT *.txt"), ("TAGNT", "TAGNT *.txt")):
        matches = sorted(SRC_DIR.glob(pattern))
        if len(matches) not in (4, 2):
            sys.exit(f"Expected TAHOT x4 and TAGNT x2 in {SRC_DIR}, found {matches}")
        if source == "TAHOT" and len(matches) != 4:
            sys.exit(f"Expected 4 TAHOT files, found {len(matches)}")
        if source == "TAGNT" and len(matches) != 2:
            sys.exit(f"Expected 2 TAGNT files, found {len(matches)}")
        for path in matches:
            found.append((source, path))
    return found


def parse_file(source: str, path: Path, known_verses: set | None):
    rows = []
    skips = Counter()
    types = Counter()
    samples = []
    other_samples = []
    dup_refs = 0
    seen_refs = set()
    missing_verse = 0
    unknown_books = Counter()

    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.rstrip("\r\n")
            if not line.strip():
                skips["blank"] += 1
                continue
            if line.startswith("#") or line.startswith("\t#"):
                skips["hash"] += 1
                continue
            if "\t" not in line:
                skips["no_tab"] += 1
                if len(other_samples) < 8:
                    other_samples.append((line_no, line[:160]))
                continue
            cols = line.split("\t")
            ref = cols[0].strip()
            match = REF_RE.fullmatch(ref)
            if not match:
                skips["not_ref"] += 1
                if len(other_samples) < 8 and ref[:1].isalpha():
                    other_samples.append((line_no, ref[:160]))
                continue
            surface = cols[1].strip() if len(cols) > 1 else ""
            if not surface and source != "TAHOT":
                skips["no_surface"] += 1
                continue
            book = match.group("book").upper()
            chapter = int(match.group("ch"))
            verse_num = int(match.group("vs"))
            text_type = match.group("typ")
            heb_ref = match.group("heb")
            verse_id = f"{book}.{chapter}.{verse_num}"
            if book not in bible_common.BOOK_NAMES:
                unknown_books[book] += 1
                book_code = None
                verse_id_db = None
            else:
                book_code = book
                if known_verses is None or verse_id in known_verses:
                    verse_id_db = verse_id
                else:
                    verse_id_db = None
                    missing_verse += 1
            if source == "TAHOT":
                transliteration = field(cols, 2)
                english = field(cols, 3)
                dstrong = field(cols, 4)
                grammar = field(cols, 5)
                meaning = field(cols, 6)
                spelling = field(cols, 7)
                root_strong = field(cols, 8)
                alt_strongs = field(cols, 9)
                conjoin = field(cols, 10)
                expanded = field(cols, 11)
                dictionary = None
                editions = None
                spanish = None
                sub_meaning = None
            else:
                paren = GREEK_PAREN_RE.search(surface)
                transliteration = paren.group(1).strip() if paren else None
                english = field(cols, 2)
                morph = field(cols, 3)
                if morph and "=" in morph:
                    dstrong, grammar = morph.split("=", 1)
                    dstrong = dstrong or None
                    grammar = grammar or None
                else:
                    dstrong, grammar = morph, None
                dictionary = field(cols, 4)
                editions = field(cols, 5)
                meaning = field(cols, 6)
                spelling = field(cols, 7)
                spanish = field(cols, 8)
                sub_meaning = field(cols, 9)
                conjoin = field(cols, 10)
                root_strong = field(cols, 11)
                alt_strongs = field(cols, 12)
                expanded = None
            if ref in seen_refs:
                dup_refs += 1
            seen_refs.add(ref)
            candidate = is_candidate(source, text_type)
            letters = letters_for(source, surface)
            types[text_type if len(text_type) <= 12 else text_type[:12] + "…"] += 1
            if len(samples) < 2:
                samples.append((ref, text_type, surface, english, dstrong, letters, candidate))
            rows.append((
                source,
                path.name,
                line_no,
                ref,
                book_code,
                chapter,
                verse_num,
                verse_id_db,
                heb_ref,
                int(match.group("w")),
                text_type,
                surface,
                transliteration,
                english,
                dstrong,
                grammar,
                meaning,
                spelling,
                dictionary,
                editions,
                spanish,
                sub_meaning,
                root_strong,
                alt_strongs,
                conjoin,
                expanded,
                letters or None,
                candidate,
            ))
    stats = {
        "rows": len(rows),
        "skips": skips,
        "types": types,
        "samples": samples,
        "other_samples": other_samples,
        "dup_refs": dup_refs,
        "missing_verse": missing_verse,
        "unknown_books": unknown_books,
    }
    return rows, stats


def print_stats(path: Path, stats: dict):
    print(f"\n{path.name}: {stats['rows']} word rows")
    print(f"  skips {dict(stats['skips'])}  dup_refs {stats['dup_refs']}  missing_verse {stats['missing_verse']}")
    if stats["unknown_books"]:
        print(f"  unknown books {dict(stats['unknown_books'])}")
    top_types = stats["types"].most_common(8)
    print("  types " + ", ".join(f"{name}={count}" for name, count in top_types))
    for sample in stats["samples"]:
        print("  sample " + " | ".join(str(part) for part in sample))
    for line_no, text in stats["other_samples"]:
        print(f"  other line {line_no}: {text}")


def apply_migration(conn):
    sql = MIGRATION.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"Applied {MIGRATION.name}")


def load_known_verses(conn) -> set:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM verses")
        return {row[0] for row in cur.fetchall()}


def insert_rows(conn, rows):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE stepbible_token_rows RESTART IDENTITY")
        execute_values(cur, INSERT_SQL, rows, page_size=2000)
    conn.commit()
    print(f"Inserted {len(rows)} rows")


def link_rows(conn):
    """Attach a STEPBible row to the token with the same letters.

    A full verse whose letters match in order is linked by that text, even
    when the verse numbers differ. An alternate number on the row (heb_ref)
    does not block that match. A row that does not sit in a full-verse match
    still needs one token in its own verse, and an alternate number still
    keeps that single-word guess unlinked.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT language, count(*) FROM original_tokens GROUP BY language")
        languages = dict(cur.fetchall())
    print(f"original_tokens languages: {languages}", flush=True)
    if set(languages) - {"hebrew", "greek"}:
        sys.exit(f"Unexpected original_tokens.language values: {sorted(languages)}")

    token_seq = defaultdict(list)
    token_letters = {}
    by_verse = {}
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, verse_id, surface_text, language
            FROM original_tokens
            ORDER BY verse_id, word_order, id
            """
        )
        for token_id, verse_id, surface, language in cur:
            if not surface:
                continue
            norm = heb_letters(surface) if language == "hebrew" else grk_letters(surface)
            if not norm:
                continue
            token_seq[verse_id].append((token_id, norm, language))
            token_letters[token_id] = norm
            verse_map = by_verse.setdefault(verse_id, {"hebrew": {}, "greek": {}})
            verse_map[language].setdefault(norm, []).append(token_id)

    seq_index = defaultdict(list)
    for verse_id, items in token_seq.items():
        langs = {item[2] for item in items}
        if len(langs) != 1:
            continue
        seq_index[(langs.pop(), tuple(item[1] for item in items))].append(verse_id)

    groups = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, source, verse_id, surface, heb_ref
            FROM stepbible_token_rows
            WHERE attach_candidate
              AND verse_id IS NOT NULL
            ORDER BY verse_id, source, word_index, id
            """
        )
        candidates = cur.fetchall()
    for row_id, source, verse_id, surface, heb_ref in candidates:
        groups[(verse_id, source)].append((row_id, letters_for(source, surface), heb_ref))

    updates = []
    row_letters = {}
    linked_ids = set()
    claimed = set()
    used_tokens = set()
    same_verses = cross_verses = 0

    def link_sequence(rows, token_verse):
        items = token_seq[token_verse]
        if len(items) != len(rows):
            return False
        if any(row[1] != item[1] for row, item in zip(rows, items)):
            return False
        if any(not row[1] for row in rows):
            return False
        if any(item[0] in used_tokens for item in items):
            return False
        for row, item in zip(rows, items):
            updates.append((row[0], item[0]))
            row_letters[row[0]] = row[1]
            linked_ids.add(row[0])
            used_tokens.add(item[0])
        claimed.add(token_verse)
        return True

    for (verse_id, source), rows in groups.items():
        language = "hebrew" if source == "TAHOT" else "greek"
        key = tuple(row[1] for row in rows)
        own = token_seq.get(verse_id) or []
        if own and {item[2] for item in own} == {language} and link_sequence(rows, verse_id):
            same_verses += 1

    for (verse_id, source), rows in groups.items():
        if rows[0][0] in linked_ids:
            continue
        language = "hebrew" if source == "TAHOT" else "greek"
        key = tuple(row[1] for row in rows)
        hits = [vid for vid in seq_index.get((language, key), []) if vid not in claimed]
        if len(hits) == 1 and link_sequence(rows, hits[0]):
            cross_verses += 1

    no_match = ambiguous = empty_letters = 0
    for (verse_id, source), rows in groups.items():
        language = "hebrew" if source == "TAHOT" else "greek"
        for row_id, norm, heb_ref in rows:
            if row_id in linked_ids:
                continue
            if not norm:
                empty_letters += 1
                continue
            if heb_ref:
                no_match += 1
                continue
            hits = [
                token_id
                for token_id in (by_verse.get(verse_id, {}).get(language, {}).get(norm) or [])
                if token_id not in used_tokens
            ]
            if len(hits) == 1:
                updates.append((row_id, hits[0]))
                row_letters[row_id] = norm
                linked_ids.add(row_id)
                used_tokens.add(hits[0])
            elif len(hits) == 0:
                no_match += 1
            else:
                ambiguous += 1

    linked = len(updates)
    if len(used_tokens) != linked:
        conn.rollback()
        sys.exit(f"Link check failed: {linked} rows share {len(used_tokens)} tokens")

    bad = 0
    cross = 0
    for row_id, token_id in updates:
        if row_letters.get(row_id) != token_letters.get(token_id):
            bad += 1
    if bad:
        conn.rollback()
        sys.exit(f"Link check failed: {bad} rows do not match the token letters")

    print(f"Matched {linked} rows. Writing links.", flush=True)
    with conn.cursor() as cur:
        cur.execute("UPDATE stepbible_token_rows SET original_token_id = NULL")
        if updates:
            execute_values(
                cur,
                """
                UPDATE stepbible_token_rows AS s
                SET original_token_id = v.token_id
                FROM (VALUES %s) AS v(row_id, token_id)
                WHERE s.id = v.row_id
                """,
                updates,
                template="(%s, %s)",
                page_size=2000,
            )
        cur.execute(
            """
            SELECT count(*)
            FROM stepbible_token_rows s
            JOIN original_tokens t ON t.id = s.original_token_id
            WHERE (s.source = 'TAHOT' AND t.language <> 'hebrew')
               OR (s.source = 'TAGNT' AND t.language <> 'greek')
            """
        )
        bad_lang = cur.fetchone()[0]
        cur.execute(
            """
            SELECT count(*)
            FROM stepbible_token_rows s
            JOIN original_tokens t ON t.id = s.original_token_id
            WHERE t.verse_id IS DISTINCT FROM s.verse_id
            """
        )
        cross = cur.fetchone()[0]
        if bad_lang:
            conn.rollback()
            sys.exit(f"Link check failed: {bad_lang} rows point at the wrong language")
    conn.commit()
    print(
        f"Link candidates {len(candidates)}: linked {linked}, "
        f"no letter match {no_match}, ambiguous {ambiguous}, empty letters {empty_letters}",
        flush=True,
    )
    print(
        f"Full-verse text matches: {same_verses} on the same number, "
        f"{cross_verses} on a different number ({cross} linked rows cross numbers)",
        flush=True,
    )


def report(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT source,
                   count(*) AS rows,
                   count(verse_id) AS with_verse,
                   count(*) FILTER (WHERE heb_ref IS NOT NULL) AS heb_note,
                   count(*) FILTER (WHERE attach_candidate) AS candidates,
                   count(original_token_id) AS linked
            FROM stepbible_token_rows
            GROUP BY source
            ORDER BY source
            """
        )
        print("\nCounts:")
        for row in cur.fetchall():
            print(" ", row)
        for verse_id in ("SNG.8.14", "2TH.3.18", "PSA.119.176"):
            print(f"\n{verse_id} STEPBible")
            cur.execute(
                """
                SELECT word_index, text_type, surface, english, letters,
                       attach_candidate, original_token_id
                FROM stepbible_token_rows
                WHERE verse_id = %s
                ORDER BY word_index, text_type
                """,
                (verse_id,),
            )
            step_rows = cur.fetchall()
            if not step_rows:
                print("  (no rows)")
            for item in step_rows:
                print(" ", item)
            print(f"{verse_id} original_tokens")
            cur.execute(
                """
                SELECT id, word_order, language, surface_text
                FROM original_tokens
                WHERE verse_id = %s
                ORDER BY word_order
                """,
                (verse_id,),
            )
            for item in cur.fetchall():
                print(" ", item)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--link-only", action="store_true")
    args = parser.parse_args()
    if not args.scan and not args.execute and not args.link_only:
        sys.exit("Pass --scan, --execute, or --link-only")

    assert heb_letters("בְּ/רֵאשִׁ֖ית") == "בראשית"
    assert heb_letters("לְמַהֵר\u05c3 \u05e1") == "למהר"
    assert grk_letters("Ἀβραὰμ (Abraam)") == "αβρααμ"
    assert grk_letters("χάρις") == "χαρισ"
    assert is_candidate("TAHOT", "L")
    assert is_candidate("TAHOT", "Q(K)")
    assert is_candidate("TAHOT", "L(abh)")
    assert not is_candidate("TAHOT", "K")
    assert not is_candidate("TAHOT", "R")
    assert not is_candidate("TAHOT", "X")
    assert is_candidate("TAGNT", "NKO")
    assert is_candidate("TAGNT", "K(O)")
    assert not is_candidate("TAGNT", "N(O)")
    assert not is_candidate("TAGNT", "k(o)")

    if args.link_only:
        conn = connect()
        try:
            link_rows(conn)
            report(conn)
        finally:
            conn.close()
        return

    known = None
    conn = None
    if args.execute:
        conn = connect()
        apply_migration(conn)
        known = load_known_verses(conn)
        print(f"Verses in database: {len(known)}")

    files = source_files()
    all_rows = []
    total = 0
    for source, path in files:
        rows, stats = parse_file(source, path, known)
        print_stats(path, stats)
        if stats["unknown_books"]:
            sys.exit("Unknown STEPBible book codes. Nothing was loaded.")
        all_rows.extend(rows)
        total += stats["rows"]
    print(f"\nTotal word rows: {total}")
    if total < MIN_ROWS:
        sys.exit(f"Only {total} rows. Refusing to load.")

    if args.scan:
        print("Scan only. No database write.")
        return

    try:
        insert_rows(conn, all_rows)
        link_rows(conn)
        report(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
