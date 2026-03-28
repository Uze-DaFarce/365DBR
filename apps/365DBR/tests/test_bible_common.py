import sys
import os
import pytest

# Ensure bible_common can be imported from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bible_common import is_verse_in_range, parse_reference

def test_parse_reference():
    assert parse_reference("GEN.1.1") == ("GEN", 1, 1)
    assert parse_reference("MAT.28.20") == ("MAT", 28, 20)
    assert parse_reference("PSA.119.176") == ("PSA", 119, 176)

def test_is_verse_in_range_same_chapter():
    # Range: GEN.1.1 - GEN.1.10
    start = ("GEN", 1, 1)
    end = ("GEN", 1, 10)

    # Inside
    assert is_verse_in_range("GEN.1.1", *start, *end) is True
    assert is_verse_in_range("GEN.1.5", *start, *end) is True
    assert is_verse_in_range("GEN.1.10", *start, *end) is True

    # Outside
    assert is_verse_in_range("GEN.1.11", *start, *end) is False
    assert is_verse_in_range("GEN.2.1", *start, *end) is False
    assert is_verse_in_range("EXO.1.1", *start, *end) is False

def test_is_verse_in_range_multi_chapter():
    # Range: GEN.1.20 - GEN.2.5
    start = ("GEN", 1, 20)
    end = ("GEN", 2, 5)

    # Inside
    assert is_verse_in_range("GEN.1.20", *start, *end) is True
    assert is_verse_in_range("GEN.1.31", *start, *end) is True
    assert is_verse_in_range("GEN.2.1", *start, *end) is True
    assert is_verse_in_range("GEN.2.5", *start, *end) is True

    # Outside
    assert is_verse_in_range("GEN.1.19", *start, *end) is False
    assert is_verse_in_range("GEN.2.6", *start, *end) is False
    assert is_verse_in_range("GEN.3.1", *start, *end) is False

def test_is_verse_in_range_cross_book():
    # Range: MAL.4.1 - MAT.1.5
    # MAL is the last book of OT, MAT is the first book of NT.
    start = ("MAL", 4, 1)
    end = ("MAT", 1, 5)

    # Inside
    assert is_verse_in_range("MAL.4.1", *start, *end) is True
    assert is_verse_in_range("MAL.4.6", *start, *end) is True
    assert is_verse_in_range("MAT.1.1", *start, *end) is True
    assert is_verse_in_range("MAT.1.5", *start, *end) is True

    # Outside
    assert is_verse_in_range("MAL.3.18", *start, *end) is False
    assert is_verse_in_range("MAL.4.0", *start, *end) is False # Boundary
    assert is_verse_in_range("MAT.1.6", *start, *end) is False
    assert is_verse_in_range("MAT.2.1", *start, *end) is False
    assert is_verse_in_range("GEN.1.1", *start, *end) is False
    assert is_verse_in_range("REV.22.21", *start, *end) is False

    # Cross-book same chapter number but different book
    # Range: EXO.1.1 - LEV.1.10
    # GEN.1.5 should be False
    assert is_verse_in_range("GEN.1.5", "EXO", 1, 1, "LEV", 1, 10) is False

def test_is_verse_in_range_middle_book():
    # Range: GEN.1.1 - LEV.1.1
    # EXO is in between
    start = ("GEN", 1, 1)
    end = ("LEV", 1, 1)

    assert is_verse_in_range("EXO.1.1", *start, *end) is True
    assert is_verse_in_range("EXO.40.38", *start, *end) is True

def test_is_verse_in_range_unknown_book():
    # Range: GEN.1.1 - GEN.1.10
    start = ("GEN", 1, 1)
    end = ("GEN", 1, 10)

    assert is_verse_in_range("XYZ.1.1", *start, *end) is False

def test_is_verse_in_range_same_book_multi_chapter_long():
    # Range: PSA.1.1 - PSA.150.6
    start = ("PSA", 1, 1)
    end = ("PSA", 150, 6)

    assert is_verse_in_range("PSA.1.1", *start, *end) is True
    assert is_verse_in_range("PSA.23.1", *start, *end) is True
    assert is_verse_in_range("PSA.119.176", *start, *end) is True
    assert is_verse_in_range("PSA.150.6", *start, *end) is True
    assert is_verse_in_range("GEN.1.1", *start, *end) is False
