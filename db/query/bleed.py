"""Bleed. Read-only. A near neighbor is not the thing itself.

One gate. ask_tier1 calls it before a hit counts and again before the
result returns. Shared words are not the same claim. A hit counts only
when that Hebrew or Greek word is written in the verse.

This layer does not assign the speaker. The place list is not this layer.
Pass 4 stays unbuilt.
"""

from __future__ import annotations

from .word import _query_key, token_key

_PAIR = frozenset({"freedom of religion", "freedom from christianity"})
_MSG = (
    '"freedom of religion" and "freedom from Christianity" share words. '
    "They are not the same claim."
)


class BleedRefusal(Exception):
    """A near neighbor was not allowed to stand in for the claim."""


def _norm(text: str | None) -> str:
    return " ".join((text or "").casefold().split())


def _refuse_pair(*texts: str | None) -> None:
    norms = [_norm(text) for text in texts]
    if len({item for item in norms if item in _PAIR}) == 2:
        raise BleedRefusal(_MSG)
    for item in norms:
        if item in _PAIR:
            raise BleedRefusal(_MSG)
        if "freedom of religion" in item and "freedom from christianity" in item:
            raise BleedRefusal(_MSG)


def word_is_written(conn, verse_id: str, word: str) -> bool:
    """True only when that Hebrew or Greek word is written in the verse.

    The key is the whole word. A shared letter, a neighbor, or a Strong's
    number does not count.
    """
    key, language = _query_key(word)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT lemma, surface_text, language
            FROM original_tokens
            WHERE verse_id = %s
              AND lower(language) = %s
            """,
            (verse_id, language),
        )
        rows = cur.fetchall()
    for row in rows:
        if token_key(row["language"], row["lemma"], row["surface_text"]) == key:
            return True
    return False


def gate(
    conn,
    *,
    phase: str,
    word: str,
    claim: str | None = None,
    verse_id: str | None = None,
    passages: list[str] | None = None,
) -> None:
    """Refuse the contract pair. Then require the written word.

    phase "hit" runs before a hit counts. With a verse id, the hit counts
    only when that word is written there. phase "return" runs again before
    the result is allowed to leave, and checks every counted hit.
    """
    if phase not in ("hit", "return"):
        raise ValueError(f"unknown bleed phase: {phase}")
    _refuse_pair(claim, word)
    if phase == "hit":
        if verse_id is None:
            return
        if not word_is_written(conn, verse_id, word):
            raise BleedRefusal(
                f"{word} is not written at {verse_id}. The hit does not count."
            )
        return
    for hit_id in passages or []:
        if not word_is_written(conn, hit_id, word):
            raise BleedRefusal(
                f"{word} is not written at {hit_id}. The hit does not count."
            )
