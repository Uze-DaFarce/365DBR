import json
import os

# =============================================================================
# CONSTANTS (From generate_readings.py)
# =============================================================================

# Hebrew/Greek Verse Counts (Scanned from api.bible IDs)
BIBLE_DATA = {
  "GEN": [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 54, 33, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26],
  "EXO": [22, 25, 22, 31, 23, 30, 29, 28, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 37, 30, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38],
  "LEV": [17, 16, 17, 35, 26, 23, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34],
  "NUM": [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 35, 28, 32, 22, 29, 35, 41, 30, 25, 19, 65, 23, 31, 39, 17, 54, 42, 56, 29, 34, 13],
  "DEU": [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 31, 19, 29, 23, 22, 20, 22, 21, 20, 23, 29, 26, 22, 19, 19, 26, 69, 28, 20, 30, 52, 29, 12],
  "JOS": [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33],
  "JDG": [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25],
  "RUT": [22, 23, 18, 22],
  "1SA": [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 16, 23, 28, 23, 44, 25, 12, 25, 11, 31, 13],
  "2SA": [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 32, 44, 26, 22, 51, 39, 25],
  "1KI": [53, 46, 28, 20, 32, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 54],
  "2KI": [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 20, 22, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30],
  "1CH": [54, 55, 24, 43, 41, 66, 40, 40, 44, 14, 47, 41, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30],
  "2CH": [18, 17, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 23, 14, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23],
  "EZR": [11, 70, 13, 24, 17, 22, 28, 36, 15, 44],
  "NEH": [11, 20, 38, 17, 19, 19, 72, 18, 37, 40, 36, 47, 31],
  "EST": [22, 23, 15, 17, 14, 14, 10, 17, 32, 3],
  "JOB": [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 32, 26, 17],
  "PSA": [6, 12, 9, 9, 13, 11, 18, 10, 21, 18, 7, 9, 6, 7, 5, 11, 15, 51, 15, 10, 14, 32, 6, 10, 22, 12, 14, 9, 11, 13, 25, 11, 22, 23, 28, 13, 40, 23, 14, 18, 14, 12, 5, 27, 18, 12, 10, 15, 21, 23, 21, 11, 7, 9, 24, 14, 12, 12, 18, 14, 9, 13, 12, 11, 14, 20, 8, 36, 37, 6, 24, 20, 28, 23, 11, 13, 21, 72, 13, 20, 17, 8, 19, 13, 14, 17, 7, 19, 53, 17, 16, 16, 5, 23, 11, 13, 12, 9, 9, 5, 8, 29, 22, 35, 45, 48, 43, 14, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 14, 10, 8, 12, 15, 21, 10, 20, 14, 9, 6],
  "PRO": [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31],
  "ECC": [18, 26, 22, 17, 19, 12, 29, 17, 18, 20, 10, 14],
  "SON": [17, 17, 11, 16, 16, 12, 14, 14],
  "ISA": [31, 22, 26, 6, 30, 13, 25, 23, 20, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 11, 25, 24],
  "JER": [19, 37, 25, 31, 31, 30, 34, 23, 25, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34],
  "LAM": [22, 22, 66, 22, 22],
  "EZK": [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 44, 37, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35],
  "DAN": [21, 49, 33, 34, 30, 29, 28, 27, 27, 21, 45, 13],
  "HOS": [9, 25, 5, 19, 15, 11, 16, 14, 17, 15, 11, 15, 15, 10],
  "JOE": [20, 27, 5, 21],
  "AMO": [15, 16, 15, 13, 27, 14, 17, 14, 15],
  "OBA": [21],
  "JON": [16, 11, 10, 11],
  "MIC": [16, 13, 12, 14, 14, 16, 20],
  "NAH": [14, 14, 19],
  "HAB": [17, 20, 19],
  "ZEP": [18, 15, 20],
  "HAG": [15, 23],
  "ZEC": [17, 17, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21],
  "MAL": [14, 17, 24],
  "MAT": [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20],
  "MRK": [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20],
  "LUK": [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 36, 43, 48, 47, 38, 71, 56, 53],
  "JHN": [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25],
  "ACT": [26, 47, 26, 37, 42, 15, 60, 39, 43, 48, 30, 25, 52, 28, 40, 40, 34, 28, 41, 38, 40, 30, 35, 26, 27, 32, 44, 31],
  "ROM": [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 26, 33, 24],
  "1CO": [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24],
  "2CO": [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14],
  "GAL": [24, 21, 29, 31, 26, 18],
  "EPH": [23, 22, 21, 32, 33, 24],
  "PHP": [30, 30, 21, 23],
  "COL": [29, 23, 25, 18],
  "1TH": [10, 20, 13, 18, 28],
  "2TH": [12, 17, 18],
  "1TI": [20, 15, 16, 16, 25, 21],
  "2TI": [18, 26, 17, 22],
  "TIT": [16, 15, 15],
  "PHM": [25],
  "HEB": [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25],
  "JAS": [27, 26, 18, 17, 20],
  "1PE": [25, 25, 22, 19, 14],
  "2PE": [21, 22, 18],
  "1JN": [10, 29, 24, 21, 21],
  "2JN": [13],
  "3JN": [14],
  "JUD": [25],
  "REV": [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]
}

# Book Lists
ALL_BOOKS = list(BIBLE_DATA.keys())
OT_BOOKS = ALL_BOOKS[:39]  # GEN to MAL
NT_BOOKS = ALL_BOOKS[39:]  # MAT to REV

# PSA and PRO are in OT_BOOKS list naturally (indices 18 and 19),
# but per spec we need to exclude them from the sequential OT reading.
OT_SEQUENTIAL_BOOKS = [b for b in OT_BOOKS if b not in ["PSA", "PRO"]]

# Known Omissions in Critical Texts (SBLGNT, NA28, etc.) which API.Bible follows for Greek NT (7644de2e4c5188e5-01).
# Note: These verses ARE present in Textus Receptus based translations (KJV, LSV),
# but since our app drives the reading plan from the Greek text (SBLGNT), the API returns them as missing/empty.
# To avoid "Verse Count Mismatch" errors during validation, we treat them as omitted in our plan.
KNOWN_OMISSIONS = {
    "MAT.17.21", "MAT.18.11", "MAT.23.14",
    "MRK.7.16", "MRK.9.44", "MRK.9.46", "MRK.11.26", "MRK.15.28",
    "LUK.17.36", "LUK.23.17",
    "JHN.5.4",
    "ACT.8.37", "ACT.15.34", "ACT.24.7", "ACT.28.29",
    "ROM.16.24"
}

BOOK_NAMES = {
    "GEN": "Genesis", "EXO": "Exodus", "LEV": "Leviticus", "NUM": "Numbers", "DEU": "Deuteronomy",
    "JOS": "Joshua", "JDG": "Judges", "RUT": "Ruth", "1SA": "1 Samuel", "2SA": "2 Samuel",
    "1KI": "1 Kings", "2KI": "2 Kings", "1CH": "1 Chronicles", "2CH": "2 Chronicles", "EZR": "Ezra",
    "NEH": "Nehemiah", "EST": "Esther", "JOB": "Job", "PSA": "Psalms", "PRO": "Proverbs",
    "ECC": "Ecclesiastes", "SON": "Song of Solomon", "ISA": "Isaiah", "JER": "Jeremiah", "LAM": "Lamentations",
    "EZK": "Ezekiel", "DAN": "Daniel", "HOS": "Hosea", "JOE": "Joel", "AMO": "Amos", "OBA": "Obadiah",
    "JON": "Jonah", "MIC": "Micah", "NAH": "Nahum", "HAB": "Habakkuk", "ZEP": "Zephaniah", "HAG": "Haggai",
    "ZEC": "Zechariah", "MAL": "Malachi",
    "MAT": "Matthew", "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts", "ROM": "Romans",
    "1CO": "1 Corinthians", "2CO": "2 Corinthians", "GAL": "Galatians", "EPH": "Ephesians",
    "PHP": "Philippians", "COL": "Colossians", "1TH": "1 Thessalonians", "2TH": "2 Thessalonians",
    "1TI": "1 Timothy", "2TI": "2 Timothy", "TIT": "Titus", "PHM": "Philemon", "HEB": "Hebrews",
    "JAS": "James", "1PE": "1 Peter", "2PE": "2 Peter", "1JN": "1 John", "2JN": "2 John",
    "3JN": "3 John", "JUD": "Jude", "REV": "Revelation"
}

NAME_TO_CODE = {v: k for k, v in BOOK_NAMES.items()}

# =============================================================================
# UTILITIES
# =============================================================================

def atomic_write_json(filepath, data, indent=2, ensure_ascii=True):
    """
    Writes JSON data to a file atomically using a temporary file and os.replace.
    Ensures that a crash during write does not leave a corrupted file.
    Defaults ensure_ascii=True to maintain compatibility with standard JSON tools and avoid diff noise.
    """
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    tmp_filepath = f"{filepath}.tmp"

    try:
        with open(tmp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_filepath, filepath)
    except Exception as e:
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
        raise IOError(f"Failed to write {filepath} atomically: {str(e)}") from e

def parse_reference(ref_str):
    parts = ref_str.split('.')
    return parts[0], int(parts[1]), int(parts[2])

def is_verse_in_range(vid, start_book, start_chap, start_verse, end_book, end_chap, end_verse):
    """
    Checks if a verse ID (vid) is strictly within the range defined by start and end coordinates.
    Handles single-book and cross-book ranges.
    """
    v_book, v_chap, v_verse = parse_reference(vid)

    # 1. Check Book
    # If range is same book:
    if start_book == end_book:
        if v_book != start_book: return False
        # Same book check
        # Case A: Same chapter range
        if start_chap == end_chap:
            if v_chap != start_chap: return False
            return start_verse <= v_verse <= end_verse
        # Case B: Multi-chapter
        # Start Chapter
        if v_chap == start_chap: return v_verse >= start_verse
        # End Chapter
        if v_chap == end_chap: return v_verse <= end_verse
        # Middle Chapter
        return start_chap < v_chap < end_chap

    # If range is cross-book:
    # Check if book is within [s_b, e_b]
    try:
        v_idx = ALL_BOOKS.index(v_book)
        s_idx = ALL_BOOKS.index(start_book)
        e_idx = ALL_BOOKS.index(end_book)
    except ValueError:
        return False # Unknown book

    if not (s_idx <= v_idx <= e_idx): return False

    # If book is Start Book
    if v_book == start_book:
        if v_chap == start_chap: return v_verse >= start_verse
        return v_chap > start_chap

    # If book is End Book
    if v_book == end_book:
        if v_chap == end_chap: return v_verse <= end_verse
        return v_chap < end_chap

    # If book is strictly between
    return True

# =============================================================================
# CONSTANTS (From fetch_readings.py)
# =============================================================================

OT_HEBREW_ID = "0b262f1ed7f084a6-01"
NT_GREEK_ID = "7644de2e4c5188e5-01"
PARALLEL_IDS = [
    "de4e12af7f28f599-01",  # KJV
    "01b29f4b342acc35-01"   # LSV
]

API_BASE_URL = "https://rest.api.bible/v1"

# Map Standard Book IDs to OT Hebrew Bible Specific IDs
OT_HEBREW_BOOK_MAP = {
    "JOE": "JOL",
    "NAH": "NAM",
    "SON": "SNG"
}

# Reverse map for validation (JOL -> JOE)
REVERSE_HEBREW_BOOK_MAP = {v: k for k, v in OT_HEBREW_BOOK_MAP.items()}

# =============================================================================
# FUNCTIONS (From fetch_readings.py)
# =============================================================================

def get_books_in_range(range_str):
    """
    Extracts all book codes involved in a range string.
    Handles single book ("GEN.1.1") and cross-book ("JOB.1.1-ECC.12.1").
    """
    parts = range_str.split('-')
    start_book = parts[0].split('.')[0]
    books = [start_book]

    if len(parts) > 1:
        end_book = parts[1].split('.')[0]
        if start_book != end_book:
            if start_book not in ALL_BOOKS:
                 raise ValueError(f"[Data Integrity] Unknown start book '{start_book}'")
            if end_book not in ALL_BOOKS:
                 raise ValueError(f"[Data Integrity] Unknown end book '{end_book}'")

            s_idx = ALL_BOOKS.index(start_book)
            e_idx = ALL_BOOKS.index(end_book)

            if s_idx > e_idx:
                 raise ValueError(f"[Data Integrity] Invalid range order: {start_book} comes after {end_book}")

            # Add all intermediate books + end book
            for i in range(s_idx + 1, e_idx + 1):
                books.append(ALL_BOOKS[i])

    return books

def validate_range_for_section(section, range_str):
    """
    Validates that the books in the range string belong to the expected section.
    OT: OT_SEQUENTIAL_BOOKS (Gen-Mal, excluding Psa/Pro)
    NT: NT_BOOKS (Mat-Rev)
    PSA: ['PSA']
    PRO: ['PRO']
    """
    books_to_check = get_books_in_range(range_str)

    allowed_books = []
    if section == "OT":
        allowed_books = OT_SEQUENTIAL_BOOKS
    elif section == "NT":
        allowed_books = NT_BOOKS
    elif section == "PSA":
        allowed_books = ["PSA"]
    elif section == "PRO":
        allowed_books = ["PRO"]
    else:
        # Should not happen given hardcoded sections, but safe to ignore unknowns or raise error.
        # Failing fast is better.
        raise ValueError(f"[Data Integrity] Unknown section '{section}'.")

    for book in books_to_check:
        if book not in allowed_books:
            raise ValueError(f"[Data Integrity] Book '{book}' is not allowed in section '{section}'. Corruption detected.")

def validate_api_response(data, context_info=""):
    """
    Validates that the API response contains actual content.
    Fail Fast!
    """
    if not isinstance(data, dict):
        raise ValueError(f"[Data Integrity] Invalid response type for {context_info}: Expected dict, got {type(data)}")

    if 'data' not in data:
         raise ValueError(f"[Data Integrity] Missing 'data' key in response for {context_info}")

    inner_data = data['data']
    if inner_data is None:
         raise ValueError(f"[Data Integrity] Data block is None in response for {context_info}")

    if 'content' not in inner_data:
        raise ValueError(f"[Data Integrity] Missing 'content' field in response for {context_info}")

    content = inner_data['content']
    # 10 chars is a safe lower bound. "Jesus wept" is shortest verse.
    # HTML wrapper usually adds more: <p class="p"><span data-number="35" class="v">35</span>Jesus wept.</p>
    if not content or len(str(content).strip()) < 10:
        raise ValueError(f"[Data Integrity] Content suspiciously empty/short ({len(str(content)) if content else 0} chars) for {context_info}")

    return True

def extract_verse_ids(content):
    """
    Recursively extracts unique verseIds from the content structure.
    Returns a set of verseId strings.
    """
    found_vids = set()

    def walk(items):
        if not items: return
        for item in items:
            if isinstance(item, dict):
                if 'attrs' in item and 'verseId' in item['attrs']:
                    found_vids.add(item['attrs']['verseId'])

                if 'items' in item:
                    walk(item['items'])

    walk(content)
    return found_vids

def count_actual_verses(content):
    """
    Recursively counts unique verseIds in the content structure (list of objects).
    """
    return len(extract_verse_ids(content))

def count_expected_verses(range_str):
    """
    Calculates expected verse count from BIBLE_DATA for a range string.
    Handles single book and cross-book ranges.
    Adjusts count for KNOWN_OMISSIONS.
    """
    if ';' in range_str:
        return sum(count_expected_verses(r) for r in range_str.split(';'))

    if '-' in range_str:
        start_str, end_str = range_str.split('-')
    else:
        start_str = range_str
        end_str = range_str
    s_book, s_chap, s_verse = parse_reference(start_str)
    e_book, e_chap, e_verse = parse_reference(end_str)

    # Base Count Calculation
    raw_count = 0

    if s_book == e_book:
        if s_chap == e_chap:
            raw_count = e_verse - s_verse + 1
        else:
            # Same book, diff chapters
            chapters = BIBLE_DATA[s_book]
            raw_count = (chapters[s_chap-1] - s_verse + 1)
            for c in range(s_chap + 1, e_chap):
                raw_count += chapters[c-1]
            raw_count += e_verse
    else:
        # Cross book
        if s_book not in ALL_BOOKS or e_book not in ALL_BOOKS:
            print(f"  [Warning] Unknown book in range {range_str}, skipping count check.")
            return -1

        s_idx = ALL_BOOKS.index(s_book)
        e_idx = ALL_BOOKS.index(e_book)

        # 1. Start Book remainder
        chapters_s = BIBLE_DATA[s_book]
        raw_count += (chapters_s[s_chap-1] - s_verse + 1)
        for c in range(s_chap + 1, len(chapters_s) + 1):
            raw_count += chapters_s[c-1]

        # 2. Intermediate Books
        for i in range(s_idx + 1, e_idx):
            book = ALL_BOOKS[i]
            raw_count += sum(BIBLE_DATA[book])

        # 3. End Book start
        chapters_e = BIBLE_DATA[e_book]
        for c in range(1, e_chap):
            raw_count += chapters_e[c-1]
        raw_count += e_verse

    # Note: We do NOT subtract omissions here anymore.
    # The application expects the full count (KJV/LSV).
    # Missing verses in the API are injected during fetching.
    return raw_count

def inject_missing_verses(data, range_str):
    """
    Injects placeholder objects for verses known to be missing in the Critical Text
    but expected by the reading plan (KJV/LSV counts).
    Modifies data in-place.
    """
    if 'data' not in data or 'content' not in data['data']:
        return

    content_list = data['data']['content']

    if '-' in range_str:
        start_str, end_str = range_str.split('-')
    else:
        start_str = range_str
        end_str = range_str
    s_book, s_chap, s_verse = parse_reference(start_str)
    e_book, e_chap, e_verse = parse_reference(end_str)

    verses_to_inject = []
    for omitted_vid in KNOWN_OMISSIONS:
        if is_verse_in_range(omitted_vid, s_book, s_chap, s_verse, e_book, e_chap, e_verse):
            verses_to_inject.append(omitted_vid)

    if not verses_to_inject:
        return

    # 2. Inject them
    for vid in verses_to_inject:
        print(f"    [Injection] Injecting placeholder for missing verse {vid}...")

        # Create the Verse Object
        verse_obj = {
            "name": "para",
            "type": "tag",
            "attrs": { "style": "p" },
            "items": [
                {
                    "name": "verse",
                    "type": "tag",
                    "attrs": { "verseId": vid, "style": "v", "data-number": vid.split('.')[2] },
                    "items": [{ "text": vid.split('.')[2], "type": "text" }] # Verse Number
                },
                {
                    "text": " [Verse omitted in Greek text] ",
                    "type": "text"
                }
            ]
        }

        # Naive Injection: Just append to content.
        # Ideally we place it correctly.
        b, c, v = parse_reference(vid)
        preceding_vid = f"{b}.{c}.{v-1}"

        inserted = False

        for i, item in enumerate(content_list):
            if str(preceding_vid) in str(item):
                content_list.insert(i + 1, verse_obj)
                inserted = True
                break

        if not inserted:
            content_list.append(verse_obj)

def validate_content_integrity(data, range_str, inject_missing=True):
    """
    Validates that the fetched content has the expected number of verses
    AND that the content belongs to the expected books.
    """
    # 0. Pre-Process: Inject Missing Verses (Fix for SBLGNT omissions)
    if inject_missing:
        inject_missing_verses(data, range_str)

    # 1. Calculate Expected Count
    expected = count_expected_verses(range_str)
    if expected == -1:
         raise ValueError(f"[Data Integrity] Unknown book in range {range_str}. Cannot validate verses.")

    # 2. Extract Actual Verse IDs
    # api.bible returns { data: { content: [...] } }
    # validate_api_response already checked structure.
    actual_vids = extract_verse_ids(data['data']['content'])
    actual = len(actual_vids)

    # 3. Sentinel Book Verification (New Security Layer)
    expected_books = set(get_books_in_range(range_str))

    # Parse range components for strict validation
    if '-' in range_str:
        start_str, end_str = range_str.split('-')
    else:
        start_str = range_str
        end_str = range_str

    s_book, s_chap, s_verse = parse_reference(start_str)
    e_book, e_chap, e_verse = parse_reference(end_str)

    for vid in actual_vids:
        # verseId format: BOOK.CHAPTER.VERSE (e.g. JOL.1.1)
        book_code = vid.split('.')[0]

        # Normalize: Convert API code back to Standard code if needed
        # (Needed for book verification)
        norm_book_code = book_code
        if book_code in REVERSE_HEBREW_BOOK_MAP:
            norm_book_code = REVERSE_HEBREW_BOOK_MAP[book_code]

        if norm_book_code not in expected_books:
             raise ValueError(f"[Data Integrity] Book Mismatch! Found verses from '{norm_book_code}' (norm) in range intended for {expected_books}. Full ID: {vid}")

        # 3.5. Sentinel Strict Range Containment Check (Enhanced Security)
        # Verify that the verse is strictly within the requested start/end range.
        # This prevents "gaps" or "out of order" injections (e.g. GEN.2.1 appearing in GEN.1.1-GEN.1.5).
        # We pass the raw 'book_code' from the VID (e.g. JOL) and we must ensure
        # is_verse_in_range handles it or we normalize it first.
        # count_expected_verses uses parse_reference which splits.
        # is_verse_in_range calls parse_reference(vid) -> returns (JOL, 1, 1).
        # But 's_book' comes from range_str which is standard (JOE).
        # So we should NORMALIZE the VID before passing to is_verse_in_range to match the range_str standard.

        normalized_vid = vid
        if book_code != norm_book_code:
            normalized_vid = vid.replace(book_code, norm_book_code)

        if not is_verse_in_range(normalized_vid, s_book, s_chap, s_verse, e_book, e_chap, e_verse):
             raise ValueError(f"[Data Integrity] Corruption Detected! Verse {vid} (normalized: {normalized_vid}) is NOT in range {range_str}.")


    # 4. Compare Counts
    # Special Handling for Psalms: Title merging often reduces count by 1 per chapter involved.
    # We allow a loose tolerance for Psalms.
    is_psalm = "PSA" in range_str

    if is_psalm:
        # Allow +/- 1 per chapter in range?
        # Simplest: Allow +/- 1 total variance (strict).
        # This catches "2 verses missing" in small Psalms while allowing for 1 title/verse merge difference.
        if abs(expected - actual) > 1:
             raise ValueError(f"[Data Integrity] Verse Count Mismatch for {range_str} (Psalms). Expected ~{expected}, Got {actual} (Tolerance 1)")
    else:
        if expected != actual:
             raise ValueError(f"[Data Integrity] Verse Count Mismatch for {range_str}. Expected {expected}, Got {actual}")

    # Additional Sentinel Check: Zero Verses
    if expected > 0 and actual == 0:
         raise ValueError(f"[Data Integrity] Zero verses returned for {range_str}. Expected {expected}.")

    # 5. Strict Boundary Check
    # Ensure start verse and end verse of the range are present.
    # This catches "shifted" ranges where count matches but content is wrong (e.g. MAT.15.14-38 returned for MAT.15.7-31).
    # Also handles single-verse ranges (no hyphen).
    if ';' not in range_str:
        start_vid = start_str
        end_vid = end_str

        # Normalize actual VIDs for lookup
        normalized_actual_vids = set()
        for vid in actual_vids:
            b, c, v = vid.split('.')
            if b in REVERSE_HEBREW_BOOK_MAP:
                b = REVERSE_HEBREW_BOOK_MAP[b]
            normalized_actual_vids.add(f"{b}.{c}.{v}")

        # Check Start
        # Note: We must handle cases where the start verse itself is a KNOWN_OMISSION (rare but possible)
        if start_vid not in normalized_actual_vids and start_vid not in KNOWN_OMISSIONS:
             # Check if it's a Psalm Title issue?
             # If Psalm 18:43 is requested, but API returns 18:44 due to title...
             # But we use Hebrew IDs, so it should match.
             # If it's just missing, it's an error.
             raise ValueError(f"[Data Integrity] Start Verse {start_vid} MISSING in response for {range_str}. Possible range shift or truncation.")

        # Check End
        if end_vid not in normalized_actual_vids and end_vid not in KNOWN_OMISSIONS:
             raise ValueError(f"[Data Integrity] End Verse {end_vid} MISSING in response for {range_str}. Possible range shift or truncation.")

    return True

def translate_range_for_bible(range_str, bible_id):
    """
    Translates book IDs in the range string if required for specific Bibles.
    e.g. JOE.2.1-JOE.2.10 -> JOL.2.1-JOL.2.10 if bible_id is OT Hebrew
    """
    if bible_id != OT_HEBREW_ID:
        return range_str

    # Check if any mapped book is in the string
    translated = range_str
    for std, heb in OT_HEBREW_BOOK_MAP.items():
        if std in translated:
            translated = translated.replace(std, heb)

    return translated

def split_cross_book_range(range_str):
    """
    Splits a cross-book range (e.g. ECC.12.1-SON.3.11) into separate book ranges.
    Returns a list of range strings.
    """
    parts = range_str.split('-')
    if len(parts) != 2:
        return [range_str]

    start_str, end_str = parts

    # Simple parse helper
    def parse_book_code(s):
        return s.split('.')[0]

    start_book = parse_book_code(start_str)
    end_book = parse_book_code(end_str)

    if start_book == end_book:
        return [range_str]

    # It is a cross book range.
    # Use BIBLE_DATA to find all books involved
    all_books = list(BIBLE_DATA.keys())

    if start_book not in all_books or end_book not in all_books:
        print(f"  [Warning] Unknown book {start_book} or {end_book} in range {range_str}, cannot split safely.")
        return [range_str]

    start_idx = all_books.index(start_book)
    end_idx = all_books.index(end_book)

    if start_idx > end_idx:
         print(f"  [Warning] Invalid range order {start_book}-{end_book}, cannot split safely.")
         return [range_str]

    result_ranges = []

    # 1. Start Book: Start -> End of Start Book
    chapters = BIBLE_DATA[start_book]
    last_ch_num = len(chapters)
    last_v_num = chapters[-1]

    # Parse start details to reconstruct fully
    start_parts = start_str.split('.')
    start_loc = f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}" # Keep it clean

    result_ranges.append(f"{start_loc}-{start_book}.{last_ch_num}.{last_v_num}")

    # 2. Intermediate Books (Full)
    for i in range(start_idx + 1, end_idx):
        mid_book = all_books[i]
        chapters = BIBLE_DATA[mid_book]
        last_ch = len(chapters)
        last_v = chapters[-1]
        result_ranges.append(f"{mid_book}.1.1-{mid_book}.{last_ch}.{last_v}")

    # 3. End Book: Start of End Book -> End
    # Parse end details
    end_parts = end_str.split('.')
    end_loc = f"{end_parts[0]}.{end_parts[1]}.{end_parts[2]}"

    result_ranges.append(f"{end_book}.1.1-{end_loc}")

    return result_ranges
