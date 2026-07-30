"""
365DBR Phase 4–5: DB-backed query layer (Option A + curated annotations).

Static JSON remains the primary source for the live daily reader.
This package exposes optional DB capabilities for tooling, diagnostics,
and future optional features (Strong's lookup, day packs, dual-read,
speaker/theme annotations).

Public API:
  get_connection()
  load_day(conn, day) -> day payload (verseMap-compatible shape)
  load_verse(conn, verse_id) -> single verse detail
  search_strong(conn, strong, limit=...) -> hits
  dual_read_day(conn, day, source=local|prod) -> comparison report
  annotations_covering_verse / find_by_speaker / find_by_theme / si_demo_query
"""

from .annotations import (
    annotations_covering_verse,
    find_by_annotation,
    find_by_speaker,
    find_by_theme,
    si_demo_query,
)
from .connection import get_connection
from .day_load import dual_read_day, load_day, load_verse, search_strong

__all__ = [
    "get_connection",
    "load_day",
    "load_verse",
    "search_strong",
    "dual_read_day",
    "annotations_covering_verse",
    "find_by_annotation",
    "find_by_speaker",
    "find_by_theme",
    "si_demo_query",
]
