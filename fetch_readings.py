import json
import os
import argparse
import time
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

# Map Standard Book IDs to OT Hebrew Bible Specific IDs
OT_HEBREW_BOOK_MAP = {
    "JOE": "JOL",
    "NAH": "NAM",
    "SON": "SNG"
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
    # Use BIBLE_DATA to find end of first book.
    # Note: range_str comes from readings.json which uses Standard Codes (e.g. SON not SNG).
    # fetch_readings logic:
    #   rng_str (Standard) -> translate -> api_rng_str (Hebrew) -> fetch
    #   If 404, we call this with rng_str (Standard).

    if start_book not in BIBLE_DATA:
        print(f"  [Warning] Unknown book {start_book} in range {range_str}, cannot split safely.")
        return [range_str]

    # Get last chapter and verse of start_book
    chapters = BIBLE_DATA[start_book]
    last_ch_num = len(chapters)
    last_v_num = chapters[-1]

    # First range: Start -> End of Start Book
    # Parse start details to reconstruct fully
    start_parts = start_str.split('.')
    start_loc = f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}" # Keep it clean

    first_range = f"{start_loc}-{start_book}.{last_ch_num}.{last_v_num}"

    # Second range: Start of End Book -> End
    # Parse end details
    end_parts = end_str.split('.')
    end_loc = f"{end_parts[0]}.{end_parts[1]}.{end_parts[2]}"

    second_range = f"{end_book}.1.1-{end_loc}"

    return [first_range, second_range]

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
        print(f"  [Warning] Expected 4 ranges, found {len(ranges)} in {day_id}")
    
    # Map ranges to Types and Bible IDs
    # Order in readings.json is OT, NT, PSA, PRO
    section_defs = [
        ("OT", OT_HEBREW_ID),
        ("NT", NT_GREEK_ID),
        ("PSA", OT_HEBREW_ID),
        ("PRO", OT_HEBREW_ID)
    ]
    
    files_list = []
    
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

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
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
    parser.add_argument("--out", default=".", help="Output directory (root folder containing day folders)")
    
    args = parser.parse_args()
    
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
