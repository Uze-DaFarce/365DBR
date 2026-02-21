import json
import os
import sys
from generate_readings import BIBLE_DATA, ALL_BOOKS, BibleNavigator, format_friendly_range, get_ranges_handling_gaps
from bible_common import atomic_write_json

def main():
    print("Regenerating January Reading Schedule (Hardcoded Fix)...")

    # Define the exact ranges provided by the user
    # Note: These are the "end" ranges for each day.
    # The start is implied by the previous day's end + 1 verse.
    # Except for Day 1 which starts at GEN.1.1 etc.

    # User provided:
    # 0101: GEN.1.1-GEN.2.25, MAT.1.1-MAT.2.12, PSA.1.1-PSA.1.6, PRO.1.1-PRO.1.6 (Explicit JSON content)
    # 0102: GEN.3.1-GEN.5.6, MAT.2.13-MAT.5.3, PSA.1.7-PSA.2.6, PRO.1.7-PRO.1.12
    # ... and so on for 02-10
    # Then every other day (12, 14, 16...)

    # We will build a list of target endpoints for every day.
    # Format: Day -> { OT: EndRef, NT: EndRef, PS: EndRef, PR: EndRef }

    # Helper to parse "Book C:V" to "Book.C.V"
    # Mapping friendly names to codes
    friendly_map = {
        "Genesis": "GEN", "Exodus": "EXO", "Matthew": "MAT", "Psalm": "PSA", "Psalms": "PSA", "Proverbs": "PRO"
    }

    def p(s):
        # s is like "Genesis 5:6" -> "GEN.5.6"
        parts = s.split()
        book = friendly_map.get(parts[0], parts[0])
        cv = parts[-1]
        c, v = cv.split(':')
        return f"{book}.{c}.{v}"

    # Target Endpoints for known days
    # NOTE: The user provided RANGES. We need the END point.
    # 0101 Range: Gen 1:1 - 2:25 -> End: GEN.2.25
    targets = {
        1:  {"OT": "GEN.2.25", "NT": "MAT.2.12", "PSA": "PSA.1.6",  "PRO": "PRO.1.6"},
        2:  {"OT": p("Genesis 5:6"),   "NT": p("Matthew 5:3"),   "PSA": p("Psalm 2:6"),   "PRO": p("Proverbs 1:12")},
        3:  {"OT": p("Genesis 7:16"),  "NT": p("Matthew 6:11"),  "PSA": p("Psalms 3:1"),  "PRO": p("Proverbs 1:15")},
        4:  {"OT": p("Genesis 9:17"),  "NT": p("Matthew 6:33"),  "PSA": p("Psalms 3:8"),  "PRO": p("Proverbs 1:18")},
        5:  {"OT": p("Genesis 11:26"), "NT": p("Matthew 7:21"),  "PSA": p("Psalms 4:8"),  "PRO": p("Proverbs 1:21")},
        6:  {"OT": p("Genesis 13:12"), "NT": p("Matthew 8:15"),  "PSA": p("Psalms 5:7"),  "PRO": p("Proverbs 1:24")},
        7:  {"OT": p("Genesis 16:3"),  "NT": p("Matthew 9:3"),   "PSA": p("Psalms 6:2"),  "PRO": p("Proverbs 1:27")},
        8:  {"OT": p("Genesis 18:14"), "NT": p("Matthew 9:25"),  "PSA": p("Psalms 6:10"), "PRO": p("Proverbs 1:30")},
        9:  {"OT": p("Genesis 19:35"), "NT": p("Matthew 10:9"),  "PSA": p("Psalms 7:7"),  "PRO": p("Proverbs 1:33")},
        10: {"OT": p("Genesis 21:34"), "NT": p("Matthew 10:31"), "PSA": p("Psalms 7:14"), "PRO": p("Proverbs 2:3")},

        # Gap 11
        12: {"OT": p("Genesis 24:65"), "NT": p("Matthew 12:3"),  "PSA": p("Psalms 9:2"),  "PRO": p("Proverbs 2:9")},
        # Gap 13
        14: {"OT": p("Genesis 27:37"), "NT": p("Matthew 12:47"), "PSA": p("Psalms 9:16"), "PRO": p("Proverbs 2:15")},
        # Gap 15 (User provided specific file for 15, let's use it as a target)
        # 0115 Label: "Genesis 27:38 – 29:23..." -> End: GEN.29.23
        15: {"OT": p("Genesis 29:23"), "NT": p("Matthew 13:19"), "PSA": p("Psalms 10:3"), "PRO": p("Proverbs 2:18")},
        16: {"OT": p("Genesis 30:43"), "NT": p("Matthew 13:41"), "PSA": p("Psalms 10:10"),"PRO": p("Proverbs 2:22")},
        # Gap 17
        18: {"OT": p("Genesis 34:2"),  "NT": p("Matthew 14:27"), "PSA": p("Psalms 12:3"), "PRO": p("Proverbs 3:6")},
        # Gap 19
        20: {"OT": p("Genesis 37:7"),  "NT": p("Matthew 15:35"), "PSA": p("Psalms 14:3"), "PRO": p("Proverbs 3:12")},
        # Gap 21
        22: {"OT": p("Genesis 41:3"),  "NT": p("Matthew 17:12"), "PSA": p("Psalms 16:5"), "PRO": p("Proverbs 3:18")},
        # Gap 23
        24: {"OT": p("Genesis 43:16"), "NT": p("Matthew 18:29"), "PSA": p("Psalms 17:8"), "PRO": p("Proverbs 3:24")},
        # Gap 25
        26: {"OT": p("Genesis 46:28"), "NT": p("Matthew 20:8"),  "PSA": p("Psalms 18:7"), "PRO": p("Proverbs 3:30")},
        # Gap 27
        28: {"OT": p("Genesis 50:16"), "NT": p("Matthew 21:18"), "PSA": p("Psalms 18:21"),"PRO": p("Proverbs 3:35")},
        # Gap 29
        30: {"OT": p("Exodus 4:29"),   "NT": p("Matthew 22:16"), "PSA": p("Psalms 18:35"),"PRO": p("Proverbs 4:6")},
        # 31 (User provided specific file for 31)
        # 0131 Label: "Exodus 4:30 – 6:29..." -> End: EXO.6.29
        31: {"OT": p("Exodus 6:29"),   "NT": p("Matthew 22:38"), "PSA": p("Psalms 18:42"),"PRO": p("Proverbs 4:9")}
    }

    # Initialize Navigators
    ot_nav = BibleNavigator(ALL_BOOKS) # Using ALL_BOOKS to be safe, though usually OT_SEQUENTIAL
    nt_nav = BibleNavigator(ALL_BOOKS)
    ps_nav = BibleNavigator(["PSA"])
    pr_nav = BibleNavigator(["PRO"])

    # Start points (Jan 1 start)
    ot_idx = ot_nav.find_index("GEN.1.1")
    nt_idx = nt_nav.find_index("MAT.1.1")
    ps_idx = ps_nav.find_index("PSA.1.1")
    pr_idx = pr_nav.find_index("PRO.1.1")

    new_readings = []

    # Process Day 1 to 31
    for day in range(1, 32):
        date_str = f"01{day:02d}"

        # Do we have a target end for this day?
        if day in targets:
            # Yes, strict target
            t = targets[day]
            ot_end_limit = ot_nav.find_index(t["OT"])
            nt_end_limit = nt_nav.find_index(t["NT"])
            ps_end_limit = ps_nav.find_index(t["PSA"])
            pr_end_limit = pr_nav.find_index(t["PRO"])

            # For strict targets, the reading IS from current ot_idx to ot_end_limit
            ot_end_idx = ot_end_limit
            nt_end_idx = nt_end_limit
            ps_end_idx = ps_end_limit
            pr_end_idx = pr_end_limit

        else:
            # No, this is a gap day (e.g. 11, 13...)
            # We need to interpolate between current start and the NEXT target
            # Find next target day
            next_day = day + 1
            while next_day not in targets and next_day <= 31:
                next_day += 1

            if next_day > 31:
                print(f"Error: No target found after day {day}!")
                sys.exit(1)

            t_next = targets[next_day]
            ot_target_limit = ot_nav.find_index(t_next["OT"])
            nt_target_limit = nt_nav.find_index(t_next["NT"])
            ps_target_limit = ps_nav.find_index(t_next["PSA"])
            pr_target_limit = pr_nav.find_index(t_next["PRO"])

            # Simple interpolation: split remaining verses by remaining days (which should be 2: today and next_day)
            days_remaining = next_day - day + 1 # e.g. 11 -> 12 is 2 days

            def get_midpoint(nav, start, end, div):
                total = end - start
                step = int(total / div)
                return start + step

            ot_end_idx = get_midpoint(ot_nav, ot_idx, ot_target_limit, days_remaining)
            nt_end_idx = get_midpoint(nt_nav, nt_idx, nt_target_limit, days_remaining)
            ps_end_idx = get_midpoint(ps_nav, ps_idx, ps_target_limit, days_remaining)
            pr_end_idx = get_midpoint(pr_nav, pr_idx, pr_target_limit, days_remaining)

        # Calculate counts
        ot_count = ot_end_idx - ot_idx + 1
        nt_count = nt_end_idx - nt_idx + 1
        ps_count = ps_end_idx - ps_idx + 1
        pr_count = pr_end_idx - pr_idx + 1

        # Generate strings
        def process_section_ranges(nav, s_idx, e_idx):
            # Snap to chapter end? No, explicit ranges shouldn't snap unless user asked.
            # User's ranges are explicit verses. We respect them.
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

        # Advance start indices
        ot_idx = ot_end_idx + 1
        nt_idx = nt_end_idx + 1
        ps_idx = ps_end_idx + 1
        pr_idx = pr_end_idx + 1

    print("January schedule generated successfully.")

    # Load Existing Data
    readings_path = "data/readings.json"
    if not os.path.exists(readings_path):
        print(f"Error: {readings_path} not found. Cannot merge.")
        sys.exit(1)

    with open(readings_path, 'r') as f:
        existing_readings = json.load(f)

    # Filter out January (Month "01")
    non_jan_readings = [d for d in existing_readings if not d['day'].startswith("01")]

    print(f"Preserving {len(non_jan_readings)} existing days (Feb-Dec).")

    # Merge: New Jan + Existing Feb-Dec
    final_readings = new_readings + non_jan_readings

    # Sort by day just in case
    final_readings.sort(key=lambda x: x['day'])

    print(f"Total days in new plan: {len(final_readings)}")

    # Write Back
    atomic_write_json(readings_path, final_readings)

    print(f"Successfully updated {readings_path} with regenerated January schedule.")

if __name__ == "__main__":
    main()
