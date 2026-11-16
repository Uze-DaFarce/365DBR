"""Tier 1 loop. Read-only. No summary and no lower tier.

A written Hebrew or Greek word goes in. The verses where that word is
written come back, with the verses around each one. The result is speaks,
contradicts, or silent. Silent stops. Tiers 2–4 stay closed.

contradicts is only for an explicit claim that the word is absent while
the text contains it. The function does not decide what a passage means.

Speaker and genre come only from stored annotations whose range covers
that verse. No stored speaker prints as unknown. A speaker is not copied
onto a neighbor outside its range. Theme is not treated as genre. The
result means the word is written. It does not mean God said it.
"""

from __future__ import annotations

from typing import Any

from .word import search_word

_ENGINE_CODES = ("LSV", "KJV", "YLT")
_MIN_WINDOW = 3
_MAX_WINDOW = 7
_MAX_SHOW = 5


def ask_tier1(
    conn,
    word: str,
    *,
    claim: str | None = None,
    window: int = _MIN_WINDOW,
    show: int = 1,
) -> dict[str, Any]:
    """Run one Tier 1 loop.

    claim None asks whether the word is written.
    claim "absent" asserts that the word is not written.
    Any other claim is refused.
    """
    if claim not in (None, "absent"):
        raise ValueError('claim must be omitted or "absent"')
    span = max(_MIN_WINDOW, min(int(window), _MAX_WINDOW))
    shown = max(1, min(int(show), _MAX_SHOW))
    found = search_word(conn, word, limit=shown)
    total = int(found["total_verses"])
    if total == 0:
        result = "silent"
    elif claim == "absent":
        result = "contradicts"
    else:
        result = "speaks"
    passages = []
    if result != "silent":
        passages = [_passage(conn, hit, span) for hit in found["hits"]]
    return {
        "tier": 1,
        "result": result,
        "stopped": result == "silent",
        "lower_tiers": "closed",
        "word": found["query"],
        "language": found["language"],
        "claim": claim,
        "total_verses": total,
        "shown": len(passages),
        "passages": passages,
    }


def format_tier1(report: dict[str, Any]) -> str:
    """The verses, plus the one result. No paraphrase."""
    lines = [
        "Tier 1",
        f"word: {report['word']}",
        f"language: {report['language']}",
        f"claim: {report['claim'] or 'none'}",
        f"result: {report['result']}",
        f"shown: {report['shown']} of {report['total_verses']}",
        f"stopped: {report['stopped']}",
        "lower tiers: closed",
        "",
    ]
    for passage in report["passages"]:
        lines.append(f"hit {passage['verse_id']}  {passage['surface']}")
        for verse in passage["verses"]:
            mark = " hit" if verse["hit"] else ""
            lines.append(f"{verse['verse_id']}{mark}")
            lines.append(_label_line("speaker", verse["speaker"]))
            lines.append(_label_line("genre", verse["genre"]))
            lines.append(verse["original"])
            for code in _ENGINE_CODES:
                text = verse["translations"].get(code)
                if text:
                    lines.append(f"{code}: {text}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _passage(conn, hit: dict[str, Any], span: int) -> dict[str, Any]:
    verse_ids = _window_ids(conn, hit["verse_id"], span)
    originals = _original_lines(conn, verse_ids)
    translations = _engine_texts(conn, verse_ids)
    labels = _stored_labels(conn, verse_ids)
    verses = []
    for verse_id in verse_ids:
        label = labels.get(verse_id, {"speaker": [], "genre": []})
        verses.append(
            {
                "verse_id": verse_id,
                "hit": verse_id == hit["verse_id"],
                "original": originals.get(verse_id, ""),
                "translations": translations.get(verse_id, {}),
                "speaker": label["speaker"],
                "genre": label["genre"],
            }
        )
    return {
        "verse_id": hit["verse_id"],
        "surface": hit["surface"],
        "verses": verses,
    }


def _label_line(kind: str, rows: list[dict[str, str]]) -> str:
    if not rows:
        return f"{kind}: unknown"
    parts = []
    for row in rows:
        source = row.get("source") or ""
        parts.append(f"{row['value']} [{source}]" if source else row["value"])
    return f"{kind}: " + "; ".join(parts)


def _stored_labels(conn, verse_ids: list[str]) -> dict[str, dict[str, list[dict[str, str]]]]:
    """Speaker and genre rows only. Blank values are not a speaker."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT v.id AS verse_id, a.annotation_type, a.value, a.source, a.id
            FROM verses v
            JOIN annotations a
              ON a.annotation_type IN ('speaker', 'genre')
            JOIN verses vs ON vs.id = a.start_verse_id
            JOIN verses ve ON ve.id = a.end_verse_id
            WHERE v.id = ANY(%s)
              AND v.verse_order BETWEEN vs.verse_order AND ve.verse_order
            ORDER BY v.verse_order, a.annotation_type, a.id
            """,
            (verse_ids,),
        )
        rows = cur.fetchall()
    out: dict[str, dict[str, list[dict[str, str]]]] = {
        verse_id: {"speaker": [], "genre": []} for verse_id in verse_ids
    }
    for row in rows:
        value = (row["value"] or "").strip()
        if not value:
            continue
        kind = row["annotation_type"]
        if kind not in ("speaker", "genre"):
            continue
        out[row["verse_id"]][kind].append(
            {"value": value, "source": row["source"] or ""}
        )
    return out


def _window_ids(conn, verse_id: str, span: int) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT near.id
            FROM verses hit
            JOIN verses near
              ON near.book_code = hit.book_code
             AND near.verse_order BETWEEN hit.verse_order - %s AND hit.verse_order + %s
            WHERE hit.id = %s
            ORDER BY near.verse_order
            """,
            (span, span, verse_id),
        )
        rows = cur.fetchall()
    if not rows:
        raise KeyError(f"verse not found: {verse_id}")
    return [row["id"] for row in rows]


def _original_lines(conn, verse_ids: list[str]) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT verse_id, surface_text
            FROM original_tokens
            WHERE verse_id = ANY(%s)
            ORDER BY verse_id, word_order
            """,
            (verse_ids,),
        )
        rows = cur.fetchall()
    grouped: dict[str, list[str]] = {verse_id: [] for verse_id in verse_ids}
    for row in rows:
        text = row["surface_text"] or ""
        if text:
            grouped[row["verse_id"]].append(text)
    return {verse_id: " ".join(parts) for verse_id, parts in grouped.items()}


def _engine_texts(conn, verse_ids: list[str]) -> dict[str, dict[str, str]]:
    """LSV, KJV, and YLT only. LSB and WEB stay display texts."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT vt.verse_id, t.code, vt.text
            FROM verse_translations vt
            JOIN translations t ON t.id = vt.translation_id
            WHERE vt.verse_id = ANY(%s)
              AND t.code = ANY(%s)
            """,
            (verse_ids, list(_ENGINE_CODES)),
        )
        rows = cur.fetchall()
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["text"]:
            out.setdefault(row["verse_id"], {})[row["code"]] = row["text"]
    return out
