"""Read-only check of a stored STEPBible link.

A link is exact and unique only when one source row already points at the
token, the row's letters equal the token's letters, and the language matches.
The stored Strong's number is reported as stored. It matches the source only
when that one row's dstrong is the same plain number, or the same extended
tag written the same way. Nothing is guessed or written.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
_APP = str(ROOT / "apps" / "365DBR")
if _APP not in sys.path:
    sys.path.insert(0, _APP)

from load_stepbible_tokens import grk_letters, heb_letters, letters_for  # noqa: E402

_STRONG_RE = re.compile(r"([HG])0*(\d+)")


def _verse_id(verse_id: str) -> str:
    parts = (verse_id or "").strip().split(".")
    if len(parts) < 3:
        raise ValueError(f"invalid BCV: {verse_id!r}")
    return f"{parts[0].upper()}.{parts[1]}.{parts[2]}"


def _token_letters(language: str | None, surface: str | None) -> str:
    if (language or "").lower() == "hebrew":
        return heb_letters(surface or "")
    if (language or "").lower() == "greek":
        return grk_letters(surface or "")
    return ""


def _plain_strong(value: str | None) -> str | None:
    """H0430 and H430 are the same plain number. G2424G is not plain."""
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    match = _STRONG_RE.fullmatch(text)
    if not match:
        return None
    return f"{match.group(1)}{int(match.group(2))}"


def _numbers_agree(stored_strong: str | None, dstrong: str | None) -> bool | None:
    """True when both sides are the same tag.

    Plain numbers ignore leading zeros. An extended tag matches only the
    same text, so G2424G agrees with G2424G and not with G2424. A compound
    tag agrees only with that same compound.
    """
    stored_text = str(stored_strong).strip() if stored_strong else ""
    source_text = str(dstrong).strip() if dstrong else ""
    if not stored_text and not source_text:
        return None
    left = _plain_strong(stored_text)
    right = _plain_strong(source_text)
    if left is not None and right is not None:
        return left == right
    return stored_text.upper() == source_text.upper()


def _language_ok(language: str | None, source: str | None) -> bool:
    lang = (language or "").lower()
    if source == "TAHOT":
        return lang == "hebrew"
    if source == "TAGNT":
        return lang == "greek"
    return False


def classify_link(
    language: str | None,
    surface: str | None,
    stored_strong: str | None,
    sources: list[dict],
) -> dict[str, Any]:
    """Judge stored source rows. `sources` use source, surface, letters, and dstrong."""
    letters = _token_letters(language, surface)
    link = "unlinked"
    number_match = None
    if len(sources) == 1:
        src = sources[0]
        fresh = letters_for(src.get("source"), src.get("surface") or "")
        column = src.get("letters") or ""
        column_ok = (not column) or column == fresh
        if (
            letters
            and fresh == letters
            and column_ok
            and _language_ok(language, src.get("source"))
        ):
            link = "exact_unique"
            number_match = _numbers_agree(stored_strong, src.get("dstrong"))
        elif not _language_ok(language, src.get("source")):
            link = "language_mismatch"
        else:
            link = "letters_differ"
    elif len(sources) > 1:
        link = "not_unique"
    return {"letters": letters, "link": link, "number_match": number_match}


def verify_verse(conn, verse_id: str) -> dict[str, Any]:
    """Every token in one verse, with a stored link quoted only when it is exact."""
    vid = _verse_id(verse_id)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM verses WHERE id = %s", (vid,))
        if cur.fetchone() is None:
            raise KeyError(f"verse not found: {vid}")
        cur.execute(
            """
            SELECT t.id AS token_id, t.word_order, t.language, t.surface_text,
                   t.strong_number,
                   s.id AS row_id, s.source, s.source_file, s.line_no, s.ref_raw,
                   s.verse_id AS source_verse_id, s.surface AS source_surface,
                   s.letters AS source_letters, s.english, s.dstrong, s.root_strong
            FROM original_tokens t
            LEFT JOIN stepbible_token_rows s ON s.original_token_id = t.id
            WHERE t.verse_id = %s
            ORDER BY t.word_order, s.word_index, s.id
            """,
            (vid,),
        )
        rows = cur.fetchall()

    grouped: dict[int, dict[str, Any]] = {}
    order: list[int] = []
    for row in rows:
        token_id = row["token_id"]
        if token_id not in grouped:
            grouped[token_id] = {"token": row, "sources": []}
            order.append(token_id)
        if row["row_id"] is not None:
            grouped[token_id]["sources"].append(row)

    tokens = []
    for token_id in order:
        item = grouped[token_id]
        token = item["token"]
        sources = item["sources"]
        stored = token["strong_number"]
        judged = classify_link(
            token["language"],
            token["surface_text"],
            stored,
            [
                {
                    "source": src["source"],
                    "surface": src["source_surface"],
                    "letters": src["source_letters"],
                    "dstrong": src["dstrong"],
                }
                for src in sources
            ],
        )
        letters = judged["letters"]
        link = judged["link"]
        number_match = judged["number_match"]
        source = None
        if link == "exact_unique":
            src = sources[0]
            source = {
                "source": src["source"],
                "file": src["source_file"],
                "line_no": src["line_no"],
                "ref": src["ref_raw"],
                "verse_id": src["source_verse_id"],
                "dstrong": src["dstrong"],
                "sstrong": src["root_strong"],
                "english": src["english"],
            }

        tokens.append(
            {
                "word_order": token["word_order"],
                "surface": token["surface_text"],
                "language": token["language"],
                "letters": letters,
                "stored_strong": stored,
                "link": link,
                "source_row_count": len(sources),
                "source": source,
                "number_match": number_match,
            }
        )

    return {
        "verse_id": vid,
        "tokens": tokens,
        "exact_unique": sum(1 for t in tokens if t["link"] == "exact_unique"),
        "source": "db",
    }
