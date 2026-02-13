import json
import os
import argparse
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import re

# Import BIBLE_DATA and ALL_BOOKS from generate_readings
try:
    from generate_readings import BIBLE_DATA, ALL_BOOKS
except ImportError:
    print("Error: Could not import BIBLE_DATA or ALL_BOOKS from generate_readings.py")
    sys.exit(1)

# API Configuration (Shared with fetch_readings logic)
API_BASE_URL = "https://rest.api.bible/v1"
OT_HEBREW_ID = "0b262f1ed7f084a6-01"
NT_GREEK_ID = "7644de2e4c5188e5-01"

def get_api_key():
    return os.environ.get("API_BIBLE_KEY")

def parse_reference(ref_str):
    """
    Parses a reference string like 'GEN.1.1' into (Book, Chapter, Verse).
    """
    parts = ref_str.split('.')
    if len(parts) < 3:
        return None
    return parts[0], int(parts[1]), int(parts[2])

def get_expected_verse_count(range_str):
    """
    Calculates the expected verse count for a given range string (e.g. 'GEN.1.1-GEN.1.31')
    using the local BIBLE_DATA source of truth.
    Handles semicolon-separated multi-ranges and cross-book ranges correctly.
    """
    if ';' in range_str:
        total = 0
        for sub in range_str.split(';'):
            total += get_expected_verse_count(sub)
        return total

    if '-' not in range_str:
        return 1 # Single verse?

    start_str, end_str = range_str.split('-')
    start = parse_reference(start_str)
    end = parse_reference(end_str)

    if not start or not end:
        print(f"Error: Invalid reference format in {range_str}")
        return 0

    s_book, s_chap, s_verse = start
    e_book, e_chap, e_verse = end

    # Validate books exist
    if s_book not in BIBLE_DATA:
        print(f"Error: Unknown book {s_book}")
        return 0
    if e_book not in BIBLE_DATA:
        print(f"Error: Unknown book {e_book}")
        return 0

    # Same Book
    if s_book == e_book:
        if s_chap == e_chap:
            return e_verse - s_verse + 1

        # Same Book, Different Chapters
        chapters = BIBLE_DATA[s_book]
        # Rest of start chapter
        total = (chapters[s_chap-1] - s_verse + 1)

        # Full intermediate chapters
        # range(start, end) excludes end, so range(s_chap, e_chap-1) gives chapters between s_chap and e_chap
        # BUT chapters array is 0-indexed.
        # Chapter N is at index N-1.
        # We want chapters s_chap+1 to e_chap-1.
        # s_chap+1 index is s_chap.
        # e_chap-1 index is e_chap-2.
        # So range(s_chap, e_chap-1) iterates indices of chapters between start and end.

        for c in range(s_chap, e_chap-1):
            total += chapters[c]

        total += e_verse # Verses in end chapter
        return total

    # Cross Book
    try:
        s_idx = ALL_BOOKS.index(s_book)
        e_idx = ALL_BOOKS.index(e_book)
    except ValueError:
        return 0

    if s_idx > e_idx:
        print(f"Error: Range {range_str} is backwards or invalid order.")
        return 0

    total = 0

    # 1. Start Book
    chapters_s = BIBLE_DATA[s_book]
    # Remaining verses in start chapter
    total += (chapters_s[s_chap-1] - s_verse + 1)
    # Remaining chapters in start book (from s_chap+1 to end)
    # Indices: s_chap to len-1
    for c in range(s_chap, len(chapters_s)):
        total += chapters_s[c]

    # 2. Intermediate Books
    for i in range(s_idx + 1, e_idx):
        mid_book = ALL_BOOKS[i]
        total += sum(BIBLE_DATA[mid_book])

    # 3. End Book
    chapters_e = BIBLE_DATA[e_book]
    # Full chapters before end chapter (Ch 1 to e_chap-1)
    # Indices: 0 to e_chap-2
    for c in range(0, e_chap-1):
        total += chapters_e[c]
    # Verses in end chapter
    total += e_verse

    return total

def verify_local_integrity(readings_path):
    print(f"🔍 Verifying local data integrity for {readings_path}...")

    if not os.path.exists(readings_path):
        print(f"❌ Error: {readings_path} not found.")
        return False

    with open(readings_path, 'r', encoding='utf-8') as f:
        readings = json.load(f)

    errors = 0
    for day in readings:
        day_id = day['day']

        # Validate Day ID format
        if not re.match(r'^(\d{4}|\d{4}-\d{4})$', day_id):
             print(f"⚠️ {day_id}: Invalid Day ID format!")
             errors += 1

        api_format = day['api_format']

        # Expected counts from JSON
        json_counts = {
            'OT': day.get('ot_verse_count', 0),
            'NT': day.get('nt_verse_count', 0),
            'PSA': day.get('ps_verse_count', 0),
            'PRO': day.get('pr_verse_count', 0)
        }

        # Ranges: OT, NT, PSA, PRO
        ranges = api_format.split(',')
        if len(ranges) < 4:
            print(f"❌ {day_id}: Malformed api_format (less than 4 ranges)")
            errors += 1
            continue

        calc_ot = get_expected_verse_count(ranges[0])
        calc_nt = get_expected_verse_count(ranges[1])
        calc_ps = get_expected_verse_count(ranges[2])
        calc_pr = get_expected_verse_count(ranges[3])

        if calc_ot != json_counts['OT']:
            print(f"⚠️ {day_id}: OT Count Mismatch! JSON says {json_counts['OT']}, Calc says {calc_ot}")
            errors += 1
        if calc_nt != json_counts['NT']:
            print(f"⚠️ {day_id}: NT Count Mismatch! JSON says {json_counts['NT']}, Calc says {calc_nt}")
            errors += 1
        if calc_ps != json_counts['PSA']:
            print(f"⚠️ {day_id}: PSA Count Mismatch! JSON says {json_counts['PSA']}, Calc says {calc_ps}")
            errors += 1
        if calc_pr != json_counts['PRO']:
            print(f"⚠️ {day_id}: PRO Count Mismatch! JSON says {json_counts['PRO']}, Calc says {calc_pr}")
            errors += 1

    if errors == 0:
        print("✅ Local integrity check passed: readings.json matches BIBLE_DATA logic.")
        return True
    else:
        print(f"❌ Found {errors} integrity issues.")
        return False

def verify_with_api(readings_path, day_limit=1):
    api_key = get_api_key()
    if not api_key:
        print("⚠️ No API_BIBLE_KEY found. Skipping API verification.")
        return

    print(f"🌐 Verifying {day_limit} day(s) against api.bible...")

    with open(readings_path, 'r', encoding='utf-8') as f:
        readings = json.load(f)

    targets = readings[:day_limit]

    for day in targets:
        day_id = day['day']
        print(f"  Checking Day {day_id}...")
        ranges = day['api_format'].split(',')

        sections = [
            ("OT", OT_HEBREW_ID, ranges[0]),
            ("NT", NT_GREEK_ID, ranges[1]),
            ("PSA", OT_HEBREW_ID, ranges[2]),
            ("PRO", OT_HEBREW_ID, ranges[3])
        ]

        for label, bible_id, composite_rng in sections:
            sub_ranges = composite_rng.split(';')

            for rng in sub_ranges:
                # Need to translate range for Hebrew bible if needed (e.g. JOE -> JOL)
                from fetch_readings import translate_range_for_bible
                api_rng = translate_range_for_bible(rng, bible_id)

                url = f"{API_BASE_URL}/bibles/{bible_id}/passages/{api_rng}?include-verse-spans=true"
                req = urllib.request.Request(url, headers={"api-key": api_key})

                try:
                    with urllib.request.urlopen(req) as res:
                        if res.status == 200:
                            data = json.loads(res.read().decode('utf-8'))
                            content = data['data']['content']
                            if len(content) < 50:
                                print(f"    ⚠️ {label} ({rng}) content seems suspiciously short ({len(content)} chars).")
                            else:
                                print(f"    ✅ {label} ({rng}) API fetch successful.")
                        else:
                            print(f"    ❌ {label} ({rng}) API Error {res.status}")
                except Exception as e:
                    print(f"    ❌ {label} ({rng}) Exception: {str(e)}")

                time.sleep(0.2)

def main():
    parser = argparse.ArgumentParser(description="Sentinel Data Integrity Checker")
    parser.add_argument("--local", action="store_true", help="Run local consistency check")
    parser.add_argument("--api", action="store_true", help="Run API verification")
    parser.add_argument("--days", type=int, default=1, help="Number of days to verify via API")
    args = parser.parse_args()

    if args.local:
        if not verify_local_integrity("readings.json"):
            sys.exit(1)

    if args.api:
        verify_with_api("readings.json", args.days)

if __name__ == "__main__":
    main()
