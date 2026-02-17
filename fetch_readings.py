import json
import os
import argparse
import time
import re
import urllib.request
import urllib.error
import urllib.parse

# Configuration
OT_HEBREW_ID = "0b262f1ed7f084a6-01"
NT_GREEK_ID = "7644de2e4c5188e5-01"
PARALLEL_IDS = [
    "de4e12af7f28f599-01",  # KJV
    "01b29f4b342acc35-01"   # LSV
]

API_BASE_URL = "https://rest.api.bible/v1"

# Hebrew/Greek Verse Counts (Imported from generate_readings.py)
try:
    from generate_readings import BIBLE_DATA, BOOK_NAMES, OT_SEQUENTIAL_BOOKS, NT_BOOKS, ALL_BOOKS
except ImportError:
    print("Error: Could not import BIBLE_DATA, BOOK_NAMES, OT_SEQUENTIAL_BOOKS, NT_BOOKS, or ALL_BOOKS from generate_readings.py")
    exit(1)

# Map Standard Book IDs to OT Hebrew Bible Specific IDs
OT_HEBREW_BOOK_MAP = {
    "JOE": "JOL",
    "NAH": "NAM",
    "SON": "SNG"
}

# Reverse map for validation (JOL -> JOE)
REVERSE_HEBREW_BOOK_MAP = {v: k for k, v in OT_HEBREW_BOOK_MAP.items()}

NAME_TO_CODE = {v: k for k, v in BOOK_NAMES.items()}

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

def get_api_key():
    key = os.environ.get("API_BIBLE_KEY")
    if not key:
        print("Error: API_BIBLE_KEY environment variable not set.")
        print("To set it in PowerShell:")
        print('$env:API_BIBLE_KEY = "your_api_key_here"')
        exit(1)
    
    key = key.strip()
    # Debug print to verify key (masked)
    masked_key = key[:4] + "..." + key[-4:] if len(key) > 8 else "***"
    print(f"DEBUG: Using API Key: '{masked_key}' (Length: {len(key)})")
    return key

def validate_safe_path(name):
    """
    Validates that the filename/path component is safe and does not contain
    directory traversal characters or separators.
    """
    if ".." in name:
        return False
    if "/" in name or "\\" in name:
        return False
    return True

def validate_args(args):
    """
    Validates command line arguments to prevent injection or misuse.
    """
    # 1. Validate Output Directory
    # We allow full paths if they are safe, but simplest check is no '..'
    if args.out and ".." in args.out:
        raise ValueError(f"[Security Error] Invalid output path: '{args.out}'. Path traversal detected.")

    # 2. Validate Day Format (MMDD or MMDD-MMDD)
    if args.day:
        if not re.match(r'^(\d{4}|\d{4}-\d{4})$', args.day):
             raise ValueError(f"[Input Error] Invalid day format: '{args.day}'. Expected MMDD or MMDD-MMDD.")

    # 3. Validate Month Format (MM or MM-MM)
    if args.month:
        if not re.match(r'^(\d{2}|\d{2}-\d{2})$', args.month):
             raise ValueError(f"[Input Error] Invalid month format: '{args.month}'. Expected MM or MM-MM.")

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
    """
    if ';' in range_str:
        return sum(count_expected_verses(r) for r in range_str.split(';'))

    def parse_reference(ref_str):
        parts = ref_str.split('.')
        return parts[0], int(parts[1]), int(parts[2])

    start_str, end_str = range_str.split('-')
    s_book, s_chap, s_verse = parse_reference(start_str)
    e_book, e_chap, e_verse = parse_reference(end_str)

    all_books = list(BIBLE_DATA.keys())

    if s_book == e_book:
        if s_chap == e_chap:
            return e_verse - s_verse + 1

        # Same book, diff chapters
        chapters = BIBLE_DATA[s_book]
        count = (chapters[s_chap-1] - s_verse + 1)
        for c in range(s_chap + 1, e_chap):
            count += chapters[c-1]
        count += e_verse
        return count

    # Cross book
    if s_book not in all_books or e_book not in all_books:
        # Fallback for unknown books (shouldn't happen with valid data)
        print(f"  [Warning] Unknown book in range {range_str}, skipping count check.")
        return -1

    s_idx = all_books.index(s_book)
    e_idx = all_books.index(e_book)

    count = 0

    # 1. Start Book remainder
    chapters_s = BIBLE_DATA[s_book]
    count += (chapters_s[s_chap-1] - s_verse + 1)
    for c in range(s_chap + 1, len(chapters_s) + 1):
        count += chapters_s[c-1]

    # 2. Intermediate Books
    for i in range(s_idx + 1, e_idx):
        book = all_books[i]
        count += sum(BIBLE_DATA[book])

    # 3. End Book start
    chapters_e = BIBLE_DATA[e_book]
    for c in range(1, e_chap):
        count += chapters_e[c-1]
    count += e_verse

    return count

def validate_content_integrity(data, range_str):
    """
    Validates that the fetched content has the expected number of verses
    AND that the content belongs to the expected books.
    """
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

    for vid in actual_vids:
        # verseId format: BOOK.CHAPTER.VERSE (e.g. JOL.1.1)
        book_code = vid.split('.')[0]

        # Normalize: Convert API code back to Standard code if needed
        if book_code in REVERSE_HEBREW_BOOK_MAP:
            book_code = REVERSE_HEBREW_BOOK_MAP[book_code]

        if book_code not in expected_books:
             raise ValueError(f"[Data Integrity] Book Mismatch! Found verses from '{book_code}' (norm) in range intended for {expected_books}. Full ID: {vid}")

    # 4. Compare Counts
    # Special Handling for Psalms: Title merging often reduces count by 1 per chapter involved.
    # We allow a loose tolerance for Psalms.
    is_psalm = "PSA" in range_str

    if is_psalm:
        # Allow +/- 1 per chapter in range?
        # Simplest: Allow +/- 2 total variance.
        if abs(expected - actual) > 2:
             raise ValueError(f"[Data Integrity] Verse Count Mismatch for {range_str} (Psalms). Expected ~{expected}, Got {actual}")
    else:
        if expected != actual:
             raise ValueError(f"[Data Integrity] Verse Count Mismatch for {range_str}. Expected {expected}, Got {actual}")

    return True

def fetch_passage(api_key, bible_id, passage_range):
    """
    Fetches a passage from api.bible.
    """
    # Construct parallel string
    parallels_str = ",".join(PARALLEL_IDS)
    
    url = f"{API_BASE_URL}/bibles/{bible_id}/passages/{passage_range}"
    
    params = {
        "content-type": "json",
        "include-notes": "false",
        "include-titles": "true",
        "include-chapter-numbers": "false",
        "include-verse-numbers": "false",
        "include-verse-spans": "false",
        "parallels": parallels_str,
        "use-org-id": "true"
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    headers = {
        "api-key": api_key,
        "accept": "application/json",
        "User-Agent": "curl/8.5.0" 
    }
    
    req = urllib.request.Request(full_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise RuntimeError(f"API returned status {response.status} for {passage_range}")
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        # Re-raise with context
        raise RuntimeError(f"HTTP {e.code}: {e.reason} for {passage_range} (URL: {full_url})") from e
    except Exception as e:
        # Re-raise
        raise RuntimeError(f"Network/Parse Error: {str(e)} for {passage_range}") from e

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

def process_day(day_entry, api_key, output_dir):
    day_id = day_entry['day']

    # Security Check: Validate day_id
    if not validate_safe_path(day_id):
        raise ValueError(f"[Security Error] Invalid day_id detected: '{day_id}'. Path traversal characters detected.")

    api_format = day_entry['api_format'] # "EXO.7.1-EXO.8.32,MAT..."
    label = day_entry['text_friendly']
    
    # FUTURE PROOFING: Convert long book names to short codes in the label
    # e.g., "Psalms 19:7-14" -> "PSA 19:7-14"
    # Sort by length descending to avoid partial matches (e.g. replacing 'John' inside '1 John')
    sorted_names = sorted(NAME_TO_CODE.keys(), key=len, reverse=True)
    for name in sorted_names:
        if name in label:
            label = label.replace(name, NAME_TO_CODE[name])

    print(f"Processing Day {day_id}...")
    
    # Create directory: root/day_id/
    day_dir = os.path.join(output_dir, day_id)
    os.makedirs(day_dir, exist_ok=True)
    
    # Split ranges
    ranges = api_format.split(',')
    if len(ranges) != 4:
        raise ValueError(f"[Data Integrity] Expected 4 ranges, found {len(ranges)} in {day_id}")
    
    # Map ranges to Types and Bible IDs
    # Order in readings.json is OT, NT, PSA, PRO
    section_defs = [
        ("OT", OT_HEBREW_ID),
        ("NT", NT_GREEK_ID),
        ("PSA", OT_HEBREW_ID),
        ("PRO", OT_HEBREW_ID)
    ]
    
    files_list = []
    pending_writes = [] # (filepath, data) - Atomic Write Buffer
    
    for i, composite_rng_str in enumerate(ranges):
        if i >= len(section_defs): break
        
        section_name, bible_id = section_defs[i]

        # Handle split ranges (e.g. JOB...;ECC...)
        sub_ranges = composite_rng_str.split(';')
        
        # We process sub_ranges using a queue/list to allow dynamic splitting
        processing_queue = list(sub_ranges)

        while processing_queue:
            rng_str = processing_queue.pop(0)

            # Security Check: Validate rng_str
            if not validate_safe_path(rng_str):
                raise ValueError(f"[Security Error] Invalid range string detected: '{rng_str}'. Path traversal characters detected.")

            # Integrity Check: Validate range belongs to section
            # This catches cases where a split range (e.g. from a 404 recovery) might include prohibited books for the section.
            validate_range_for_section(section_name, rng_str)

            filename = f"{rng_str}.json"
            filepath = os.path.join(day_dir, filename)

            # Translate range if needed (e.g. JOE -> JOL)
            api_rng_str = translate_range_for_bible(rng_str, bible_id)

            # Always fetch to allow updates/fixes
            print(f"  Fetching {section_name}: {api_rng_str} (file: {filename})...")
            
            try:
                data = fetch_passage(api_key, bible_id, api_rng_str)

                # Security/Integrity Check: Validate content before writing
                validate_api_response(data, context_info=f"{filename} ({api_rng_str})")

                # Sentinel Integrity Check: Ensure verse count matches BIBLE_DATA
                validate_content_integrity(data, rng_str)

                # Atomic Write: Store in memory first
                pending_writes.append((filepath, data))
                files_list.append(filename)
                time.sleep(0.1)

            except RuntimeError as e:
                # Check for 404 and try to recover by splitting if it's a cross-book range
                is_404 = "404" in str(e)
                if is_404 and bible_id == OT_HEBREW_ID:
                    splits = split_cross_book_range(rng_str)
                    if len(splits) > 1:
                        print(f"    [Recovered] 404 encountered for cross-book range. Splitting {rng_str} -> {splits}")
                        # Insert splits at the front of the queue to be processed next
                        for s in reversed(splits):
                            processing_queue.insert(0, s)
                        continue # Retry with new splits

                # If not recovered, raise
                raise e

    # All parts fetched successfully. Commit to disk.
    print(f"  [Atomic Write] Writing {len(pending_writes)} files for Day {day_id}...")
    for fpath, content in pending_writes:
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    # Create Manifest
    manifest = {
        "label": label,
        "files": files_list
    }
    manifest_path = os.path.join(day_dir, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"  Day {day_id} complete.")

def main():
    parser = argparse.ArgumentParser(description="Fetch Bible readings from API.")
    parser.add_argument("--day", help="Process specific day (e.g., 0201)")
    parser.add_argument("--month", help="Process specific month (e.g., 02)")
    parser.add_argument("--all", action="store_true", help="Process all days in readings.json")
    parser.add_argument("--readings", default="readings.json", help="Path to readings.json")
    parser.add_argument("--out", default="data", help="Output directory (root folder containing day folders)")
    
    args = parser.parse_args()

    # 0. Validate Arguments
    validate_args(args)
    
    # 1. Load Readings
    if not os.path.exists(args.readings):
        print(f"Error: {args.readings} not found.")
        return

    with open(args.readings, 'r', encoding='utf-8') as f:
        readings = json.load(f)
        
    # 2. Get API Key
    api_key = get_api_key()
    
    # 3. Filter Entries
    targets = []
    if args.day:
        if '-' in args.day:
            start, end = args.day.split('-')
            # Lexicographical comparison works for MMDD strings
            targets = [r for r in readings if r['day'] >= start and r['day'] <= end]
        else:
            targets = [r for r in readings if r['day'] == args.day]
    elif args.month:
        if '-' in args.month:
            start_m, end_m = args.month.split('-')
            # Handle month wrap-around if needed, but simpler linear check first
            # Assuming strictly increasing months in file? No, file is sorted by date usually.
            # Convert to ints for range check
            s_int = int(start_m)
            e_int = int(end_m)

            # Helper to check if month is in range [s, e] (inclusive)
            # Handles wrap around logic like 12-02 (Dec, Jan, Feb)
            def is_in_month_range(day_str, s, e):
                m = int(day_str[:2])
                if s <= e:
                    return s <= m <= e
                else:
                    # Wrap around: (m >= s) OR (m <= e)
                    return m >= s or m <= e

            targets = [r for r in readings if is_in_month_range(r['day'], s_int, e_int)]
        else:
            targets = [r for r in readings if r['day'].startswith(args.month)]
    elif args.all:
        targets = readings
    else:
        print("Please specify --day, --month, or --all")
        return

    if not targets:
        print("No readings found matching criteria.")
        return
        
    print(f"Found {len(targets)} days to process.")
    
    # 4. Process
    for entry in targets:
        process_day(entry, api_key, args.out)
        
    print("Done.")

if __name__ == "__main__":
    main()
