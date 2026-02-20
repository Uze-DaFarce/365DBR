import json
import os
import math
import sys
from generate_readings import BIBLE_DATA, ALL_BOOKS, OT_SEQUENTIAL_BOOKS, NT_BOOKS, BibleNavigator, format_friendly_range, get_ranges_handling_gaps

def main():
    print("Regenerating January Reading Schedule...")

    ot_nav = BibleNavigator(OT_SEQUENTIAL_BOOKS)
    nt_nav = BibleNavigator(NT_BOOKS)
    ps_nav = BibleNavigator(["PSA"])
    pr_nav = BibleNavigator(["PRO"])

    # Start: Jan 1
    ot_idx = ot_nav.find_index("GEN.1.1")
    nt_idx = nt_nav.find_index("MAT.1.1")
    ps_idx = ps_nav.find_index("PSA.1.1")
    pr_idx = pr_nav.find_index("PRO.1.1")

    # Target: Just before Feb 1 (These are the first verses of Feb 1)
    # We want January to end right before these indices.
    ot_end_limit = ot_nav.find_index("EXO.7.1")
    nt_end_limit = nt_nav.find_index("MAT.22.39")
    ps_end_limit = ps_nav.find_index("PSA.18.43")
    pr_end_limit = pr_nav.find_index("PRO.4.10")

    if ot_end_limit == -1 or nt_end_limit == -1:
        print("Error finding target indices! Cannot proceed.")
        sys.exit(1)

    TOTAL_DAYS = 31 # January only

    new_readings = []
    current_day = 1
    current_month = 1

    print(f"Generating {TOTAL_DAYS} days targeting Feb 1 start points...")

    for i in range(1, TOTAL_DAYS + 1):
        date_str = f"{current_month:02d}{current_day:02d}"
        days_left = TOTAL_DAYS - i + 1

        def get_target(nav, current_idx, limit_idx):
            remaining = limit_idx - current_idx
            if days_left == 1:
                return remaining
            val = remaining / days_left
            target = int(round(val))
            if target < 1: target = 1
            return target

        ot_target = get_target(ot_nav, ot_idx, ot_end_limit)
        nt_target = get_target(nt_nav, nt_idx, nt_end_limit)
        ps_target = get_target(ps_nav, ps_idx, ps_end_limit)
        pr_target = get_target(pr_nav, pr_idx, pr_end_limit)

        # Calculate End Index with rudimentary clamping
        # We allow standard navigation logic but force a hard stop at limit_idx

        # OT Logic
        ot_end_idx, ot_count = ot_nav.get_reading(ot_idx, ot_target, i, snap_radius=10)
        if ot_end_idx >= ot_end_limit: ot_end_idx = ot_end_limit - 1
        ot_count = ot_end_idx - ot_idx + 1

        # NT Logic
        nt_end_idx, nt_count = nt_nav.get_reading(nt_idx, nt_target, i, snap_radius=5)
        if nt_end_idx >= nt_end_limit: nt_end_idx = nt_end_limit - 1
        nt_count = nt_end_idx - nt_idx + 1

        # PS Logic
        ps_end_idx, ps_count = ps_nav.get_reading(ps_idx, ps_target, i, snap_radius=2)
        if ps_end_idx >= ps_end_limit: ps_end_idx = ps_end_limit - 1
        ps_count = ps_end_idx - ps_idx + 1

        # PR Logic
        pr_end_idx, pr_count = pr_nav.get_reading(pr_idx, pr_target, i, snap_radius=2)
        if pr_end_idx >= pr_end_limit: pr_end_idx = pr_end_limit - 1
        pr_count = pr_end_idx - pr_idx + 1

        # Force Completion on Day 31
        if days_left == 1:
            ot_end_idx = ot_end_limit - 1
            nt_end_idx = nt_end_limit - 1
            ps_end_idx = ps_end_limit - 1
            pr_end_idx = pr_end_limit - 1
            ot_count = ot_end_idx - ot_idx + 1
            nt_count = nt_end_idx - nt_idx + 1
            ps_count = ps_end_idx - ps_idx + 1
            pr_count = pr_end_idx - pr_idx + 1

        # Generate strings
        def process_section_ranges(nav, s_idx, e_idx):
            sub_ranges = get_ranges_handling_gaps(nav, s_idx, e_idx)
            api_parts = []
            friendly_parts_inner = []
            for (s, e) in sub_ranges:
                s_v = nav.get_verse_at(s)
                e_v = nav.get_verse_at(e)
                api_parts.append(f"{s_v}-{e_v}")
                friendly_parts_inner.append(format_friendly_range(s_v, e_v))
            return ";".join(api_parts), ", ".join(friendly_parts_inner)

        ot_api, ot_friendly = process_section_ranges(ot_nav, ot_idx, ot_end_idx)
        nt_api, nt_friendly = process_section_ranges(nt_nav, nt_idx, nt_end_idx)
        ps_api, ps_friendly = process_section_ranges(ps_nav, ps_idx, ps_end_idx)
        pr_api, pr_friendly = process_section_ranges(pr_nav, pr_idx, pr_end_idx)

        api_str = f"{ot_api},{nt_api},{ps_api},{pr_api}"
        text_friendly = ", ".join([ot_friendly, nt_friendly, ps_friendly, pr_friendly])

        entry = {
            "day": date_str,
            "api_format": api_str,
            "text_friendly": text_friendly,
            "ot_verse_count": ot_count,
            "nt_verse_count": nt_count,
            "ps_verse_count": ps_count,
            "pr_verse_count": pr_count
        }
        new_readings.append(entry)

        ot_idx = ot_end_idx + 1
        nt_idx = nt_end_idx + 1
        ps_idx = ps_end_idx + 1
        pr_idx = pr_end_idx + 1

        current_day += 1

    print("January schedule generated successfully.")

    # Load Existing Data
    readings_path = "data/readings.json"
    if not os.path.exists(readings_path):
        print(f"Error: {readings_path} not found. Cannot merge.")
        sys.exit(1)

    with open(readings_path, 'r') as f:
        existing_readings = json.load(f)

    # Filter out January (Month "01")
    # This ensures we replace any existing January data with the newly generated version
    non_jan_readings = [d for d in existing_readings if not d['day'].startswith("01")]

    print(f"Preserving {len(non_jan_readings)} existing days (Feb-Dec).")

    # Merge: New Jan + Existing Feb-Dec
    final_readings = new_readings + non_jan_readings

    print(f"Total days in new plan: {len(final_readings)}")

    # Validation Check
    if len(final_readings) != 365:
        print(f"Warning: Expected 365 days, got {len(final_readings)}.")

    # Write Back
    with open(readings_path, 'w') as f:
        json.dump(final_readings, f, indent=2)

    print(f"Successfully updated {readings_path} with regenerated January schedule.")

if __name__ == "__main__":
    main()
