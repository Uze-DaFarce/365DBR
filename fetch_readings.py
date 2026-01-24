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

# Map Standard Book IDs to OT Hebrew Bible Specific IDs
OT_HEBREW_BOOK_MAP = {
    "JOE": "JOL",
    "NAH": "NAM",
    "SON": "SNG"
}

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
                print(f"  [Error] API returned status {response.status} for {passage_range}")
                return None
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        print(f"  [Error] HTTP {e.code}: {e.reason} for {passage_range}")
        print(f"  URL: {full_url}")
        return None
    except Exception as e:
        print(f"  [Error] {str(e)} for {passage_range}")
        return None

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

def process_day(day_entry, api_key, output_dir):
    day_id = day_entry['day']
    api_format = day_entry['api_format'] # "EXO.7.1-EXO.8.32,MAT..."
    label = day_entry['text_friendly']
    
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
    
    for i, rng_str in enumerate(ranges):
        if i >= len(section_defs): break
        
        section_name, bible_id = section_defs[i]
        filename = f"{rng_str}.json"
        filepath = os.path.join(day_dir, filename)
        
        # Translate range if needed (e.g. JOE -> JOL)
        api_rng_str = translate_range_for_bible(rng_str, bible_id)
        
        # Always fetch to allow updates/fixes
        print(f"  Fetching {section_name}: {api_rng_str} (file: {filename})...")
        data = fetch_passage(api_key, bible_id, api_rng_str)
        
        if data:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            files_list.append(filename)
            time.sleep(0.1) 
        else:
            print(f"  [Failed] Could not save {filename}")
            
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
        targets = [r for r in readings if r['day'] == args.day]
    elif args.month:
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
