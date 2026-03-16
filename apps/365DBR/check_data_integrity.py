import json
import os
import argparse
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import re

from bible_common import (
    BIBLE_DATA,
    ALL_BOOKS,
    validate_range_for_section,
    validate_content_integrity,
    count_actual_verses,
    count_expected_verses,
    translate_range_for_bible,
    validate_api_response,
    OT_HEBREW_ID,
    NT_GREEK_ID,
    API_BASE_URL,
    validate_safe_path
)

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
    seen_days = set()

    for day in readings:
        day_id = day['day']

        # Validate Day ID Uniqueness
        if day_id in seen_days:
            print(f"❌ {day_id}: Duplicate Day ID found!")
            errors += 1
        seen_days.add(day_id)

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
        if len(ranges) != 4:
            print(f"❌ {day_id}: Malformed api_format (expected 4 ranges, got {len(ranges)})")
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

def verify_local_content(readings_path):
    print(f"🔍 Verifying local content integrity for {readings_path}...")

    if not os.path.exists(readings_path):
        print(f"❌ Error: {readings_path} not found.")
        return False

    with open(readings_path, 'r', encoding='utf-8') as f:
        readings = json.load(f)

    data_dir = os.path.dirname(readings_path)
    errors = 0
    checked_files = 0

    for day in readings:
        day_id = day['day']
        if not validate_safe_path(day_id):
            raise ValueError(f"❌ Path traversal detected in day_id: {day_id}")

        day_dir = os.path.join(data_dir, day_id)
        manifest_path = os.path.join(day_dir, "manifest.json")

        if not os.path.exists(manifest_path):
            # If the day directory doesn't exist, maybe it hasn't been generated yet.
            # We only error if the directory exists but manifest is missing,
            # OR if we want to enforce all days must exist (but that might be too strict if incremental).
            if os.path.exists(day_dir):
                 raise ValueError(f"❌ {day_id}: Day directory exists but manifest is missing!")
            continue

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"❌ {day_id}: Manifest is corrupt JSON!")

        files = manifest.get('files', [])
        if not files:
            print(f"⚠️ {day_id}: Manifest lists no files.")
            continue

        for filename in files:
            if not validate_safe_path(filename):
                raise ValueError(f"Path traversal detected in filename: {filename}")
            filepath = os.path.join(day_dir, filename)
            if not os.path.exists(filepath):
                raise ValueError(f"❌ {day_id}: Missing file listed in manifest: {filename}")

            # Infer range from filename (e.g. "GEN.1.1-GEN.1.5.json")
            range_str = filename.replace('.json', '')

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Validate Structure
                validate_api_response(data, context_info=f"{day_id}/{filename}")

                # Validate Content (NO INJECTION)
                # We expect the file to ALREADY contain any necessary injections.
                # So we count exact verses.
                validate_content_integrity(data, range_str, inject_missing=False)

                checked_files += 1

            except json.JSONDecodeError as e:
                 raise ValueError(f"❌ {day_id}/{filename}: Corrupt JSON!") from e
            except ValueError as e:
                 raise ValueError(f"❌ {day_id}/{filename}: Content Error: {e}") from e
            except Exception as e:
                 raise ValueError(f"❌ {day_id}/{filename}: Unexpected Error: {e}") from e

    if errors == 0:
        if checked_files == 0:
            print("⚠️ No content files found to verify.")
        else:
            print(f"✅ Local content verification passed ({checked_files} files checked).")
        return True
    else:
        print(f"❌ Found {errors} content integrity issues.")
        return False

import random

def verify_with_api(readings_path, day_limit=1, random_days=False):
    api_key = get_api_key()
    if not api_key:
        print("⚠️ No API_BIBLE_KEY found. Skipping API verification.")
        return True # Not a failure, just skipped

    print(f"🌐 Verifying {day_limit} day(s) against api.bible...")

    with open(readings_path, 'r', encoding='utf-8') as f:
        readings = json.load(f)

    if random_days:
        targets = random.sample(readings, min(day_limit, len(readings)))
    else:
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

                safe_api_rng = urllib.parse.quote(api_rng)
                safe_bible_id = urllib.parse.quote(bible_id)

                url = f"{API_BASE_URL}/bibles/{safe_bible_id}/passages/{safe_api_rng}?include-verse-spans=true"
                req = urllib.request.Request(url, headers={"api-key": api_key})

                try:
                    with urllib.request.urlopen(req) as res:
                        if res.status == 200:
                            data = json.loads(res.read().decode('utf-8'))
                            content = data['data']['content']

                            # 1. Check content existence using shared validator (Structural check)
                            try:
                                validate_api_response(data, context_info=f"{label} ({rng})")
                            except ValueError as ve:
                                print(f"    ❌ {label} ({rng}) Structure Error: {ve}")
                                errors_found = True
                                continue

                            # 2. Check Verse Count Integrity (Shared Logic)
                            # This handles missing verse injection and strict counting logic
                            try:
                                validate_content_integrity(data, rng)
                                # Recalculate actual for display purposes (optional, since validation passed)
                                actual = count_actual_verses(content)
                                print(f"    ✅ {label} ({rng}) API fetch successful. Count: {actual}")
                            except ValueError as ve:
                                print(f"    ❌ {label} ({rng}) Integrity Failure: {ve}")
                                errors_found = True

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
    parser.add_argument("--content", action="store_true", help="Verify local file content integrity")
    parser.add_argument("--api", action="store_true", help="Run API verification")
    parser.add_argument("--days", type=int, default=1, help="Number of days to verify via API")
    parser.add_argument("--random", action="store_true", help="Randomly select days to verify with API")
    parser.add_argument("--readings", default="data/readings.json", help="Path to readings.json (default: data/readings.json)")
    args = parser.parse_args()

    success = True

    if args.local:
        if not verify_local_integrity(args.readings):
            success = False

    if args.content:
        if not verify_local_content(args.readings):
            success = False

    if args.api:
        if not verify_with_api(args.readings, args.days, args.random):
            success = False

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
