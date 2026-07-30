"""
Phase 5: curated annotation queries (speaker / theme / verse coverage).

Uses verse_order for range membership (not lexical BCV string compare).
Static JSON remains primary for the live daily reader.
"""

from __future__ import annotations

from typing import Any


def _norm_bcv(verse_id: str) -> str:
    parts = (verse_id or "").strip().split(".")
    if len(parts) < 3:
        raise ValueError(f"invalid BCV: {verse_id!r}")
    return f"{parts[0].upper()}.{parts[1]}.{parts[2]}"


def _row_to_anno(r: dict) -> dict[str, Any]:
    meta = r.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        # psycopg may already decode jsonb; if str, leave as-is
        pass
    return {
        "id": r["id"],
        "annotation_type": r["annotation_type"],
        "start_verse_id": r["start_verse_id"],
        "end_verse_id": r["end_verse_id"],
        "value": r["value"],
        "metadata": meta if isinstance(meta, dict) else (meta or {}),
        "source": r.get("source"),
    }


def annotations_covering_verse(
    conn,
    verse_id: str,
    *,
    types: list[str] | None = None,
) -> dict[str, Any]:
    """
    Annotations whose verse_order range covers this English-primary BCV.
    """
    vid = _norm_bcv(verse_id)
    type_filter = types or [
        "speaker",
        "theme",
        "audience",
        "chronology",
        "setting",
        "genre",
        "literary_unit",
        "superscription",
        "title",
    ]

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, verse_order FROM verses WHERE id = %s",
            (vid,),
        )
        v = cur.fetchone()
        if not v:
            raise KeyError(f"verse not found: {vid}")

        cur.execute(
            """
            SELECT a.id, a.annotation_type, a.start_verse_id, a.end_verse_id,
                   a.value, a.metadata, a.source
            FROM annotations a
            JOIN verses vs ON vs.id = a.start_verse_id
            JOIN verses ve ON ve.id = a.end_verse_id
            WHERE a.annotation_type = ANY(%s)
              AND %s BETWEEN vs.verse_order AND ve.verse_order
            ORDER BY a.annotation_type, a.id
            """,
            (type_filter, v["verse_order"]),
        )
        rows = cur.fetchall()

    return {
        "verse_id": vid,
        "count": len(rows),
        "annotations": [_row_to_anno(r) for r in rows],
        "source": "db",
    }


def find_by_annotation(
    conn,
    *,
    annotation_type: str,
    value: str | None = None,
    limit: int = 50,
    with_lsv: bool = True,
) -> dict[str, Any]:
    """
    List annotation ranges by type (and optional value, case-insensitive).
    Optionally expand first/last LSV snippets for the range ends.
    """
    atype = (annotation_type or "").strip().lower()
    if not atype:
        raise ValueError("annotation_type required")
    lim = max(1, min(int(limit), 500))
    val = (value or "").strip() if value else None

    with conn.cursor() as cur:
        if val:
            cur.execute(
                """
                SELECT a.id, a.annotation_type, a.start_verse_id, a.end_verse_id,
                       a.value, a.metadata, a.source
                FROM annotations a
                WHERE lower(a.annotation_type) = %s
                  AND a.value ILIKE %s
                ORDER BY a.start_verse_id, a.id
                LIMIT %s
                """,
                (atype, val, lim),
            )
        else:
            cur.execute(
                """
                SELECT a.id, a.annotation_type, a.start_verse_id, a.end_verse_id,
                       a.value, a.metadata, a.source
                FROM annotations a
                WHERE lower(a.annotation_type) = %s
                ORDER BY a.value, a.start_verse_id, a.id
                LIMIT %s
                """,
                (atype, lim),
            )
        rows = cur.fetchall()

        # total without limit
        if val:
            cur.execute(
                """
                SELECT count(*) AS c FROM annotations
                WHERE lower(annotation_type) = %s AND value ILIKE %s
                """,
                (atype, val),
            )
        else:
            cur.execute(
                """
                SELECT count(*) AS c FROM annotations
                WHERE lower(annotation_type) = %s
                """,
                (atype,),
            )
        total = cur.fetchone()["c"]

        hits = []
        for r in rows:
            item = _row_to_anno(r)
            if with_lsv:
                cur.execute(
                    """
                    SELECT vt.text
                    FROM verse_translations vt
                    JOIN translations t ON t.id = vt.translation_id AND t.code = 'LSV'
                    WHERE vt.verse_id = %s
                    """,
                    (r["start_verse_id"],),
                )
                lr = cur.fetchone()
                item["lsv_start"] = (lr["text"] if lr else None) or None
                # verse count in range via verse_order
                cur.execute(
                    """
                    SELECT count(*) AS c
                    FROM verses v
                    JOIN verses vs ON vs.id = %s
                    JOIN verses ve ON ve.id = %s
                    WHERE v.verse_order BETWEEN vs.verse_order AND ve.verse_order
                    """,
                    (r["start_verse_id"], r["end_verse_id"]),
                )
                item["verse_span"] = cur.fetchone()["c"]
            hits.append(item)

    return {
        "annotation_type": atype,
        "value_filter": val,
        "total": total,
        "returned": len(hits),
        "hits": hits,
        "source": "db",
    }


def find_by_speaker(
    conn,
    speaker: str,
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """Convenience: speaker annotations matching value (ILIKE)."""
    payload = find_by_annotation(
        conn, annotation_type="speaker", value=speaker, limit=limit
    )
    payload["speaker"] = speaker
    return payload


def find_by_theme(
    conn,
    theme: str,
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """Convenience: theme annotations matching value (ILIKE)."""
    payload = find_by_annotation(
        conn, annotation_type="theme", value=theme, limit=limit
    )
    payload["theme"] = theme
    return payload


def si_demo_query(
    conn,
    *,
    speaker: str | None = None,
    theme: str | None = None,
    strong: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Minimal S.I.-style intersect demo:
    verses covered by optional speaker and/or theme annotations,
    optionally also containing a Strong's number.

    Example: speaker=Jesus + theme fragment, or speaker=God + strong H430.
    """
    if not speaker and not theme and not strong:
        raise ValueError("provide at least one of speaker, theme, strong")

    lim = max(1, min(int(limit), 200))
    from .day_load import _normalize_strong_pattern

    with conn.cursor() as cur:
        # Build candidate verse set from annotations via verse_order ranges
        params: list[Any] = []
        clauses: list[str] = []

        if speaker:
            clauses.append(
                """
                EXISTS (
                  SELECT 1 FROM annotations a
                  JOIN verses vs ON vs.id = a.start_verse_id
                  JOIN verses ve ON ve.id = a.end_verse_id
                  WHERE lower(a.annotation_type) = 'speaker'
                    AND a.value ILIKE %s
                    AND v.verse_order BETWEEN vs.verse_order AND ve.verse_order
                )
                """
            )
            params.append(speaker)

        if theme:
            clauses.append(
                """
                EXISTS (
                  SELECT 1 FROM annotations a
                  JOIN verses vs ON vs.id = a.start_verse_id
                  JOIN verses ve ON ve.id = a.end_verse_id
                  WHERE lower(a.annotation_type) = 'theme'
                    AND a.value ILIKE %s
                    AND v.verse_order BETWEEN vs.verse_order AND ve.verse_order
                )
                """
            )
            params.append(theme)

        if strong:
            pattern = _normalize_strong_pattern(strong)
            clauses.append(
                """
                EXISTS (
                  SELECT 1 FROM original_tokens ot
                  WHERE ot.verse_id = v.id AND ot.strong_number ~ %s
                )
                """
            )
            params.append(pattern)

        where = " AND ".join(clauses)
        # If only strong, scan tokens-backed verses; else start from verses that
        # appear in any annotation range (or all verses for strong-only).
        if speaker or theme:
            sql = f"""
                SELECT v.id AS verse_id, v.verse_order, vt.text AS lsv
                FROM verses v
                LEFT JOIN translations t ON t.code = 'LSV'
                LEFT JOIN verse_translations vt
                  ON vt.verse_id = v.id AND vt.translation_id = t.id
                WHERE {where}
                ORDER BY v.verse_order
                LIMIT %s
            """
        else:
            sql = f"""
                SELECT DISTINCT v.id AS verse_id, v.verse_order, vt.text AS lsv
                FROM verses v
                JOIN original_tokens ot ON ot.verse_id = v.id
                LEFT JOIN translations t ON t.code = 'LSV'
                LEFT JOIN verse_translations vt
                  ON vt.verse_id = v.id AND vt.translation_id = t.id
                WHERE {where}
                ORDER BY v.verse_order
                LIMIT %s
            """
        params.append(lim)
        cur.execute(sql, params)
        rows = cur.fetchall()

        # Approximate total (uncapped count can be heavy; cap awareness)
        count_sql = f"SELECT count(*) AS c FROM verses v WHERE {where}"
        if not (speaker or theme) and strong:
            count_sql = f"""
                SELECT count(DISTINCT v.id) AS c
                FROM verses v
                JOIN original_tokens ot ON ot.verse_id = v.id
                WHERE {where}
            """
        cur.execute(count_sql, params[:-1])
        total = cur.fetchone()["c"]

    hits = [
        {
            "verse_id": r["verse_id"],
            "lsv": (r["lsv"] or "")[:160] if r["lsv"] else None,
        }
        for r in rows
    ]
    return {
        "filters": {
            "speaker": speaker,
            "theme": theme,
            "strong": strong.strip().upper() if strong else None,
        },
        "total": total,
        "returned": len(hits),
        "hits": hits,
        "source": "db",
        "note": "Demo only; annotations are sparse curated seed, not full Bible coverage",
    }
