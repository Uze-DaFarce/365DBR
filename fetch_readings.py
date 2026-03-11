import json
import os
import argparse
import time
import re
import urllib.request
import urllib.error
import urllib.parse

from bible_common import (
    BIBLE_DATA,
    API_BASE_URL,
    OT_HEBREW_ID,
    NT_GREEK_ID,
    PARALLEL_IDS,
    NAME_TO_CODE,
    validate_range_for_section,
    translate_range_for_bible,
    split_cross_book_range,
    validate_api_response,
    validate_content_integrity,
    KNOWN_OMISSIONS,
    REVERSE_HEBREW_BOOK_MAP,
    OT_HEBREW_BOOK_MAP,
    atomic_write_json,
    validate_safe_path,
    ALL_BOOKS
)

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

def count_expected_verses(range_str):
    """
    Calculates expected verse count from BIBLE_DATA for a range string.
    Handles single book and cross-book ranges.
    Adjusts count for KNOWN_OMISSIONS.
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

    # Helper to check if a specific verse (vid) is inside the current range [start, end]
    def is_verse_in_range(vid, s_b, s_c, s_v, e_b, e_c, e_v):
        v_book, v_chap, v_verse = parse_reference(vid)

        # 1. Check Book
        # If range is same book:
        if s_b == e_b:
            if v_book != s_b: return False
            # Same book check
            # Case A: Same chapter range
            if s_c == e_c:
                if v_chap != s_c: return False
                return s_v <= v_verse <= e_v
            # Case B: Multi-chapter
            # Start Chapter
            if v_chap == s_c: return v_verse >= s_v
            # End Chapter
            if v_chap == e_c: return v_verse <= e_v
            # Middle Chapter
            return s_c < v_chap < e_c

        # If range is cross-book:
        # Check if book is within [s_b, e_b]
        try:
            v_idx = all_books.index(v_book)
            s_idx = all_books.index(s_b)
            e_idx = all_books.index(e_b)
        except ValueError:
            return False # Unknown book

        if not (s_idx <= v_idx <= e_idx): return False

        # If book is Start Book
        if v_book == s_b:
            if v_chap == s_c: return v_verse >= s_v
            return v_chap > s_c

        # If book is End Book
        if v_book == e_b:
            if v_chap == e_c: return v_verse <= e_v
            return v_chap < e_c

        # If book is strictly between
        return True


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
        if s_book not in all_books or e_book not in all_books:
            print(f"  [Warning] Unknown book in range {range_str}, skipping count check.")
            return -1

        s_idx = all_books.index(s_book)
        e_idx = all_books.index(e_book)

        # 1. Start Book remainder
        chapters_s = BIBLE_DATA[s_book]
        raw_count += (chapters_s[s_chap-1] - s_verse + 1)
        for c in range(s_chap + 1, len(chapters_s) + 1):
            raw_count += chapters_s[c-1]

        # 2. Intermediate Books
        for i in range(s_idx + 1, e_idx):
            book = all_books[i]
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

    # 1. Identify which omissions fall within this range
    # We need to parse range_str start/end
    def parse_reference(ref_str):
        parts = ref_str.split('.')
        return parts[0], int(parts[1]), int(parts[2])

    start_str, end_str = range_str.split('-')
    s_book, s_chap, s_verse = parse_reference(start_str)
    e_book, e_chap, e_verse = parse_reference(end_str)

    all_books = list(BIBLE_DATA.keys())

    # Re-use the is_verse_in_range logic (duplicated for safety/isolation)
    def is_verse_in_range(vid, s_b, s_c, s_v, e_b, e_c, e_v):
        v_book, v_chap, v_verse = parse_reference(vid)

        # Cross-book index check
        try:
            v_idx = all_books.index(v_book)
            s_idx = all_books.index(s_b)
            e_idx = all_books.index(e_b)
        except ValueError:
            return False

        if not (s_idx <= v_idx <= e_idx): return False

        # Book boundary checks
        if v_book == s_b:
            if v_chap == s_c and v_verse < s_v: return False
            if v_chap < s_c: return False

        if v_book == e_b:
            if v_chap == e_c and v_verse > e_v: return False
            if v_chap > e_c: return False

        return True

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

def validate_content_integrity(data, range_str):
    """
    Validates that the fetched content has the expected number of verses
    AND that the content belongs to the expected books.
    """
    # 0. Pre-Process: Inject Missing Verses (Fix for SBLGNT omissions)
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
    if '-' in range_str and ';' not in range_str:
        start_vid, end_vid = range_str.split('-')

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
        atomic_write_json(fpath, content, ensure_ascii=False)

    # Create Manifest
    manifest = {
        "label": label,
        "files": files_list
    }
    manifest_path = os.path.join(day_dir, "manifest.json")
    atomic_write_json(manifest_path, manifest, ensure_ascii=False)
    
    print(f"  Day {day_id} complete.")

def main():
    parser = argparse.ArgumentParser(description="Fetch Bible readings from API.")
    parser.add_argument("--day", help="Process specific day (e.g., 0201)")
    parser.add_argument("--month", help="Process specific month (e.g., 02)")
    parser.add_argument("--all", action="store_true", help="Process all days in readings.json")
    parser.add_argument("--readings", default="data/readings.json", help="Path to readings.json")
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
