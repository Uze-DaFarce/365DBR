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

# Import shared logic and constants from fetch_readings
try:
    from fetch_readings import (
        validate_range_for_section,
        count_actual_verses,
        count_expected_verses,
        translate_range_for_bible,
        OT_HEBREW_ID,
        NT_GREEK_ID,
        API_BASE_URL
    )
except ImportError:
    print("Error: Could not import necessary functions or constants from fetch_readings.py")
    sys.exit(1)

def get_api_key():
    return os.environ.get("API_BIBLE_KEY")

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

        # Validate Section Integrity (Sentinel Check)
        section_codes = ["OT", "NT", "PSA", "PRO"]
        for i, code in enumerate(section_codes):
            composite_range = ranges[i]
            for sub_range in composite_range.split(';'):
                try:
                    validate_range_for_section(code, sub_range)
                except ValueError as e:
                    print(f"❌ {day_id}: Section Integrity Error: {e}")
                    errors += 1

        # Use imported count_expected_verses
        calc_ot = count_expected_verses(ranges[0])
        calc_nt = count_expected_verses(ranges[1])
        calc_ps = count_expected_verses(ranges[2])
        calc_pr = count_expected_verses(ranges[3])

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
        return True # Not a failure, just skipped

    print(f"🌐 Verifying {day_limit} day(s) against api.bible...")

    with open(readings_path, 'r', encoding='utf-8') as f:
        readings = json.load(f)

    targets = readings[:day_limit]
    errors_found = False

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
                api_rng = translate_range_for_bible(rng, bible_id)

                url = f"{API_BASE_URL}/bibles/{bible_id}/passages/{api_rng}?include-verse-spans=true"
                req = urllib.request.Request(url, headers={"api-key": api_key})

                try:
                    with urllib.request.urlopen(req) as res:
                        if res.status == 200:
                            data = json.loads(res.read().decode('utf-8'))
                            content = data['data']['content']

                            # 1. Check content existence
                            if len(str(content)) < 50:
                                print(f"    ⚠️ {label} ({rng}) content seems suspiciously short ({len(str(content))} chars).")
                                # Not necessarily an error, but warning.

                            # 2. Check Verse Count Integrity
                            expected = count_expected_verses(rng)
                            actual = count_actual_verses(content)

                            is_psalm = "PSA" in rng

                            if is_psalm:
                                if abs(expected - actual) > 2:
                                    print(f"    ❌ {label} ({rng}) Verse Count Mismatch! Expected ~{expected}, Got {actual}")
                                    errors_found = True
                                else:
                                    print(f"    ✅ {label} ({rng}) API fetch successful. Count: {actual} (Exp: ~{expected})")
                            else:
                                if expected != actual:
                                    print(f"    ❌ {label} ({rng}) Verse Count Mismatch! Expected {expected}, Got {actual}")
                                    errors_found = True
                                else:
                                    print(f"    ✅ {label} ({rng}) API fetch successful. Count: {actual}")

                        else:
                            print(f"    ❌ {label} ({rng}) API Error {res.status}")
                            errors_found = True

                except Exception as e:
                    print(f"    ❌ {label} ({rng}) Exception: {str(e)}")
                    errors_found = True

                time.sleep(0.2)

    if errors_found:
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Sentinel Data Integrity Checker")
    parser.add_argument("--local", action="store_true", help="Run local consistency check")
    parser.add_argument("--api", action="store_true", help="Run API verification")
    parser.add_argument("--days", type=int, default=1, help="Number of days to verify via API")
    parser.add_argument("--readings", default="readings.json", help="Path to readings.json (default: readings.json)")
    args = parser.parse_args()

    success = True

    if args.local:
        if not verify_local_integrity(args.readings):
            success = False

    if args.api:
        if not verify_with_api(args.readings, args.days):
            success = False

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
