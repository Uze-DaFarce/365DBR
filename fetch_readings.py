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
    extract_verse_ids,
    count_expected_verses,
    inject_missing_verses,
    get_books_in_range,
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

            # Proactive API Bug Mitigation: Force split ALL cross-book ranges.
            # api.bible has a bug where cross-book queries (e.g. JDG.20.35-RUT.1.22)
            # return garbage data from completely different books (like 1SA) instead of a 404.
            # Splitting guarantees clean requests for each book.
            if '-' in rng_str:
                start_book = rng_str.split('-')[0].split('.')[0]
                end_book = rng_str.split('-')[1].split('.')[0]
                if start_book != end_book:
                    splits = split_cross_book_range(rng_str)
                    if len(splits) > 1:
                        print(f"  [Proactive Split] Splitting cross-book range {rng_str} -> {splits} to prevent API corruption.")
                        for s in reversed(splits):
                            processing_queue.insert(0, s)
                        continue # Re-process the split ranges

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
                # Fallback: We no longer handle 404 splitting here because we proactively split above.
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
