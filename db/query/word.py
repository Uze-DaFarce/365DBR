"""Place list for one written word.

The key is the lemma's letters when the lemma has letters, otherwise the
surface letters. Greek accents are dropped and final sigma is folded.
Hebrew keeps consonants. A Strong's number is never the key.

The SQL fold below is checked against token_key on every returned row.
A drift raises instead of returning a shorter or longer list.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
_APP = str(ROOT / "apps" / "365DBR")
if _APP not in sys.path:
    sys.path.insert(0, _APP)

from load_stepbible_tokens import grk_letters, heb_letters  # noqa: E402

_GREEK_FOLD = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
_GREEK_LOW = "αβγδεζηθικλμνξοπρστυφχψω"
_SOF = "\u05c3"
_SAMEKH = "\u05e1"
_PE = "\u05e4"


def token_key(language: str | None, lemma: str | None, surface: str | None) -> str | None:
    """Letters of the written word. Same rule as the static word files."""
    letters = heb_letters if (language or "").lower() == "hebrew" else grk_letters
    for text in (lemma, surface):
        key = letters(text or "")
        if key:
            return key
    return None


def _query_key(word: str) -> tuple[str, str]:
    raw = (word or "").strip()
    if not raw:
        raise ValueError("empty word")
    greek = grk_letters(raw)
    hebrew = heb_letters(raw)
    if greek and hebrew:
        raise ValueError(f"word has both Hebrew and Greek letters: {raw!r}")
    if greek:
        return greek, "greek"
    if hebrew:
        return hebrew, "hebrew"
    raise ValueError(
        f"pass the Hebrew or Greek word, not a Strong's number: {raw!r}"
    )


def _greek_letters_sql(expr: str) -> str:
    """SQL mirror of grk_letters. Locale-independent: capitals are translated."""
    return f"""
    regexp_replace(
      replace(
        translate(
          normalize(
            regexp_replace(coalesce({expr}, ''), '\\s*\\([^)]*\\)\\s*$', ''),
            NFD
          ),
          '{_GREEK_FOLD}',
          '{_GREEK_LOW}'
        ),
        'ς', 'σ'
      ),
      '[^α-ω]',
      '',
      'g'
    )
    """


def _hebrew_letters_sql(expr: str) -> str:
    """SQL mirror of heb_letters. Samekh and pe after sof pasuq are section marks."""
    src = f"coalesce({expr}, '')"
    return f"""
    regexp_replace(
      normalize(
        CASE
          WHEN strpos({src}, '{_SOF}') > 0 THEN
            substr({src}, 1, strpos({src}, '{_SOF}') - 1)
            || regexp_replace(
                 substr({src}, strpos({src}, '{_SOF}') + 1),
                 '[{_SAMEKH}{_PE}]', '', 'g')
          ELSE {src}
        END,
        NFKD
      ),
      '[^א-ת]',
      '',
      'g'
    )
    """


def _token_key_sql(language: str) -> str:
    letters = _hebrew_letters_sql if language == "hebrew" else _greek_letters_sql
    lemma = letters("ot.lemma")
    surface = letters("ot.surface_text")
    return f"CASE WHEN ({lemma}) <> '' THEN ({lemma}) ELSE ({surface}) END"


def search_word(conn, word: str, *, limit: int = 40) -> dict[str, Any]:
    """Verses whose written word is this key, in verse order.

    One hit per verse. The surface is the first matching token in that verse.
    Snippet text is LSV, the same text stored in the static word files.
    """
    key, language = _query_key(word)
    lim = max(1, min(int(limit), 100))
    sql = f"""
        SELECT DISTINCT ON (v.verse_order)
            ot.verse_id, ot.surface_text, ot.lemma, ot.language, v.verse_order
        FROM original_tokens ot
        JOIN verses v ON v.id = ot.verse_id
        WHERE lower(ot.language) = %s
          AND ({_token_key_sql(language)}) = %s
        ORDER BY v.verse_order, ot.word_order
    """
    with conn.cursor() as cur:
        cur.execute(sql, (language, key))
        rows = cur.fetchall()

    confirmed = []
    for row in rows:
        got = token_key(row["language"], row["lemma"], row["surface_text"])
        if got != key:
            raise RuntimeError(
                f"word-key SQL drifted at {row['verse_id']}: sql matched {key!r}, "
                f"python key is {got!r}"
            )
        confirmed.append(row)

    total = len(confirmed)
    chosen = confirmed[:lim]
    texts: dict[str, str] = {}
    if chosen:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT vt.verse_id, vt.text
                FROM verse_translations vt
                JOIN translations t ON t.id = vt.translation_id
                WHERE t.code = 'LSV'
                  AND vt.verse_id = ANY(%s)
                """,
                ([r["verse_id"] for r in chosen],),
            )
            texts = {r["verse_id"]: r["text"] or "" for r in cur.fetchall()}

    hits = []
    for row in chosen:
        lsv = texts.get(row["verse_id"]) or ""
        snippet = lsv[:160] if lsv else None
        hits.append(
            {
                "verse_id": row["verse_id"],
                "surface": row["surface_text"],
                "language": row["language"],
                "snippet": snippet,
                "snippet_translation": "LSV",
                "lsv": snippet,
            }
        )

    return {
        "query": key,
        "language": language,
        "total_verses": total,
        "returned": len(hits),
        "hits": hits,
        "source": "db",
    }
