import json
import os
import math

from bible_common import (
    BIBLE_DATA,
    ALL_BOOKS,
    OT_BOOKS,
    NT_BOOKS,
    OT_SEQUENTIAL_BOOKS,
    BOOK_NAMES,
    atomic_write_json
)

class BibleLocation:
    def __init__(self, book, chapter, verse):
        self.book = book
        self.chapter = chapter
        self.verse = verse

    def __str__(self):
        return f"{self.book}.{self.chapter}.{self.verse}"
    
    def to_friendly(self):
        return f"{BOOK_NAMES[self.book]} {self.chapter}:{self.verse}"
        
    def copy(self):
        return BibleLocation(self.book, self.chapter, self.verse)

class BibleNavigator:
    def __init__(self, book_list):
        self.book_list = book_list
        # Flatten structure for easy indexing
        self.verses = []
        for b in self.book_list:
            if b not in BIBLE_DATA:
                raise ValueError(f"Error: Book {b} not in BIBLE_DATA.")
            chapters = BIBLE_DATA[b]
            for c_idx, v_count in enumerate(chapters):
                c_num = c_idx + 1
                for v in range(1, v_count + 1):
                    # We do NOT exclude KNOWN_OMISSIONS here.
                    # The reading plan must include ALL verses (e.g. KJV/LSV count).
                    # fetch_readings.py will be responsible for filling in missing data from the API.
                    self.verses.append(BibleLocation(b, c_num, v))
        self.total_verses = len(self.verses)
        
    def find_index(self, loc_str):
        # loc_str e.g., "EXO.7.1"
        parts = loc_str.split('.')
        b, c, v = parts[0], int(parts[1]), int(parts[2])
        
        for i, loc in enumerate(self.verses):
            if loc.book == b and loc.chapter == c and loc.verse == v:
                return i
        return -1

    def get_verse_at(self, index):
        if index >= len(self.verses):
            return self.verses[-1] # Clamp to end
        return self.verses[index]
        
    def get_chapter_end_index_forward(self, index):
        """Finds the index of the last verse of the current chapter (forward search)."""
        if index >= len(self.verses): return len(self.verses) - 1
        current_loc = self.verses[index]
        curr = index
        while curr < len(self.verses):
            loc = self.verses[curr]
            if loc.book != current_loc.book or loc.chapter != current_loc.chapter:
                return curr - 1
            curr += 1
        return len(self.verses) - 1

    def get_chapter_end_index_backward(self, index):
        """Finds the index of the last verse of the PREVIOUS chapter."""
        if index >= len(self.verses): return len(self.verses) - 1
        current_loc = self.verses[index]
        curr = index
        while curr >= 0:
            loc = self.verses[curr]
            if loc.book != current_loc.book or loc.chapter != current_loc.chapter:
                return curr
            curr -= 1
        return -1 

    def get_reading(self, start_index, target_count, day_num, snap_radius=10, min_cap=None, max_cap=None):
        # Check if already done
        if start_index >= len(self.verses):
            return start_index, 0

        # Ensure we don't go past end
        remaining = len(self.verses) - start_index
        if target_count > remaining:
            target_count = remaining
            
        # 1. Exact End
        exact_end_idx = start_index + target_count - 1
        
        # If we reached the very end
        if exact_end_idx >= len(self.verses) - 1:
            return len(self.verses) - 1, len(self.verses) - 1 - start_index + 1
            
        # 2. Find Boundaries
        next_ch_end_idx = self.get_chapter_end_index_forward(exact_end_idx)
        forward_dist = next_ch_end_idx - exact_end_idx
        
        prev_ch_end_idx = self.get_chapter_end_index_backward(exact_end_idx)
        if prev_ch_end_idx < start_index:
            backward_dist = 9999
        else:
            backward_dist = exact_end_idx - prev_ch_end_idx

        # 3. Adjustment Decision
        chosen_end_idx = exact_end_idx
        
        # Helper to check validity
        def is_valid(idx):
            count = idx - start_index + 1
            if min_cap is not None and count < min_cap: return False
            if max_cap is not None and count > max_cap: return False
            return True

        # Logic: 
        # If fwd <= snap_radius and back <= snap_radius: choose smaller. Tie -> alternate.
        # Else if fwd <= snap_radius: choose fwd
        # Else if back <= snap_radius: choose back
        # Else: exact
        
        candidate_fwd = next_ch_end_idx
        candidate_back = prev_ch_end_idx
        
        can_go_fwd = (forward_dist <= snap_radius) and is_valid(candidate_fwd)
        can_go_back = (backward_dist <= snap_radius) and is_valid(candidate_back)
        
        if can_go_fwd and can_go_back:
            if forward_dist < backward_dist:
                chosen_end_idx = candidate_fwd
            elif backward_dist < forward_dist:
                chosen_end_idx = candidate_back
            else:
                if day_num % 2 == 0:
                    chosen_end_idx = candidate_fwd
                else:
                    chosen_end_idx = candidate_back
        elif can_go_fwd:
            chosen_end_idx = candidate_fwd
        elif can_go_back:
            chosen_end_idx = candidate_back
        else:
            chosen_end_idx = exact_end_idx
        
        final_count = chosen_end_idx - start_index + 1
        return chosen_end_idx, final_count

def format_friendly_range(start_loc, end_loc):
    if start_loc.book == end_loc.book and start_loc.chapter == end_loc.chapter and start_loc.verse == end_loc.verse:
        return f"{BOOK_NAMES[start_loc.book]} {start_loc.chapter}:{start_loc.verse}"
    if start_loc.book == end_loc.book:
        if start_loc.chapter == end_loc.chapter:
            return f"{BOOK_NAMES[start_loc.book]} {start_loc.chapter}:{start_loc.verse}–{end_loc.verse}"
        else:
            return f"{BOOK_NAMES[start_loc.book]} {start_loc.chapter}:{start_loc.verse} – {end_loc.chapter}:{end_loc.verse}"
    else:
        return f"{BOOK_NAMES[start_loc.book]} {start_loc.chapter}:{start_loc.verse} – {BOOK_NAMES[end_loc.book]} {end_loc.chapter}:{end_loc.verse}"

def get_ranges_handling_gaps(nav, start_idx, end_idx):
    """
    Splits the range [start_idx, end_idx] into multiple sub-ranges if it spans
    across non-adjacent books in the canonical order (ALL_BOOKS).
    Returns a list of tuples: [(sub_start_idx, sub_end_idx), ...]
    """
    ranges = []
    current_start = start_idx

    for i in range(start_idx, end_idx):
        curr_verse = nav.get_verse_at(i)
        next_verse = nav.get_verse_at(i+1)

        curr_book_idx = ALL_BOOKS.index(curr_verse.book)
        next_book_idx = ALL_BOOKS.index(next_verse.book)

        # Check continuity:
        # 1. Same book -> OK
        # 2. Different book, but canonical neighbor (diff is 1) -> OK
        # 3. Otherwise -> GAP -> Split

        if curr_verse.book == next_verse.book:
            continue
        elif next_book_idx == curr_book_idx + 1:
            continue
        else:
            # Gap detected (e.g. JOB->ECC skipping PSA,PRO)
            ranges.append((current_start, i))
            current_start = i + 1

    # Append final range
    ranges.append((current_start, end_idx))
    return ranges


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


def make_entry(date_str, ot_nav, nt_nav, ps_nav, pr_nav, ot_idx, nt_idx, ps_idx, pr_idx,
               ot_end_idx, nt_end_idx, ps_end_idx, pr_end_idx):
    ot_api, ot_friendly = process_section_ranges(ot_nav, ot_idx, ot_end_idx)
    nt_api, nt_friendly = process_section_ranges(nt_nav, nt_idx, nt_end_idx)
    ps_api, ps_friendly = process_section_ranges(ps_nav, ps_idx, ps_end_idx)
    pr_api, pr_friendly = process_section_ranges(pr_nav, pr_idx, pr_end_idx)
    return {
        "day": date_str,
        "api_format": f"{ot_api},{nt_api},{ps_api},{pr_api}",
        "text_friendly": ", ".join([ot_friendly, nt_friendly, ps_friendly, pr_friendly]),
        "ot_verse_count": ot_end_idx - ot_idx + 1,
        "nt_verse_count": nt_end_idx - nt_idx + 1,
        "ps_verse_count": ps_end_idx - ps_idx + 1,
        "pr_verse_count": pr_end_idx - pr_idx + 1,
    }


def _jan_ref(s):
    friendly_map = {
        "Genesis": "GEN", "Exodus": "EXO", "Matthew": "MAT",
        "Psalm": "PSA", "Psalms": "PSA", "Proverbs": "PRO",
    }
    parts = s.split()
    book = friendly_map.get(parts[0], parts[0])
    c, v = parts[-1].split(":")
    return f"{book}.{c}.{v}"


# Explicit January end-verses (owner schedule). Gap days interpolate to the next target.
JANUARY_TARGETS = {
    1:  {"OT": "GEN.2.25", "NT": "MAT.2.12", "PSA": "PSA.1.6", "PRO": "PRO.1.6"},
    2:  {"OT": _jan_ref("Genesis 5:6"), "NT": _jan_ref("Matthew 5:3"), "PSA": _jan_ref("Psalm 2:6"), "PRO": _jan_ref("Proverbs 1:12")},
    3:  {"OT": _jan_ref("Genesis 7:16"), "NT": _jan_ref("Matthew 6:11"), "PSA": _jan_ref("Psalms 3:1"), "PRO": _jan_ref("Proverbs 1:15")},
    4:  {"OT": _jan_ref("Genesis 9:17"), "NT": _jan_ref("Matthew 6:33"), "PSA": _jan_ref("Psalms 3:8"), "PRO": _jan_ref("Proverbs 1:18")},
    5:  {"OT": _jan_ref("Genesis 11:26"), "NT": _jan_ref("Matthew 7:21"), "PSA": _jan_ref("Psalms 4:8"), "PRO": _jan_ref("Proverbs 1:21")},
    6:  {"OT": _jan_ref("Genesis 13:12"), "NT": _jan_ref("Matthew 8:15"), "PSA": _jan_ref("Psalms 5:7"), "PRO": _jan_ref("Proverbs 1:24")},
    7:  {"OT": _jan_ref("Genesis 16:3"), "NT": _jan_ref("Matthew 9:3"), "PSA": _jan_ref("Psalms 6:2"), "PRO": _jan_ref("Proverbs 1:27")},
    8:  {"OT": _jan_ref("Genesis 18:14"), "NT": _jan_ref("Matthew 9:25"), "PSA": _jan_ref("Psalms 6:10"), "PRO": _jan_ref("Proverbs 1:30")},
    9:  {"OT": _jan_ref("Genesis 19:35"), "NT": _jan_ref("Matthew 10:9"), "PSA": _jan_ref("Psalms 7:7"), "PRO": _jan_ref("Proverbs 1:33")},
    10: {"OT": _jan_ref("Genesis 21:34"), "NT": _jan_ref("Matthew 10:31"), "PSA": _jan_ref("Psalms 7:14"), "PRO": _jan_ref("Proverbs 2:3")},
    12: {"OT": _jan_ref("Genesis 24:65"), "NT": _jan_ref("Matthew 12:3"), "PSA": _jan_ref("Psalms 9:2"), "PRO": _jan_ref("Proverbs 2:9")},
    14: {"OT": _jan_ref("Genesis 27:37"), "NT": _jan_ref("Matthew 12:47"), "PSA": _jan_ref("Psalms 9:16"), "PRO": _jan_ref("Proverbs 2:15")},
    15: {"OT": _jan_ref("Genesis 29:23"), "NT": _jan_ref("Matthew 13:19"), "PSA": _jan_ref("Psalms 10:3"), "PRO": _jan_ref("Proverbs 2:18")},
    16: {"OT": _jan_ref("Genesis 30:43"), "NT": _jan_ref("Matthew 13:41"), "PSA": _jan_ref("Psalms 10:10"), "PRO": _jan_ref("Proverbs 2:22")},
    18: {"OT": _jan_ref("Genesis 34:2"), "NT": _jan_ref("Matthew 14:27"), "PSA": _jan_ref("Psalms 12:3"), "PRO": _jan_ref("Proverbs 3:6")},
    20: {"OT": _jan_ref("Genesis 37:7"), "NT": _jan_ref("Matthew 15:35"), "PSA": _jan_ref("Psalms 14:3"), "PRO": _jan_ref("Proverbs 3:12")},
    22: {"OT": _jan_ref("Genesis 41:3"), "NT": _jan_ref("Matthew 17:12"), "PSA": _jan_ref("Psalms 16:5"), "PRO": _jan_ref("Proverbs 3:18")},
    24: {"OT": _jan_ref("Genesis 43:16"), "NT": _jan_ref("Matthew 18:29"), "PSA": _jan_ref("Psalms 17:8"), "PRO": _jan_ref("Proverbs 3:24")},
    26: {"OT": _jan_ref("Genesis 46:28"), "NT": _jan_ref("Matthew 20:8"), "PSA": _jan_ref("Psalms 18:7"), "PRO": _jan_ref("Proverbs 3:30")},
    28: {"OT": _jan_ref("Genesis 50:16"), "NT": _jan_ref("Matthew 21:18"), "PSA": _jan_ref("Psalms 18:21"), "PRO": _jan_ref("Proverbs 3:35")},
    30: {"OT": _jan_ref("Exodus 4:29"), "NT": _jan_ref("Matthew 22:16"), "PSA": _jan_ref("Psalms 18:35"), "PRO": _jan_ref("Proverbs 4:6")},
    31: {"OT": _jan_ref("Exodus 6:29"), "NT": _jan_ref("Matthew 22:38"), "PSA": _jan_ref("Psalms 18:42"), "PRO": _jan_ref("Proverbs 4:9")},
}


def _find(nav, loc_str, context):
    idx = nav.find_index(loc_str)
    if idx == -1:
        raise ValueError(f"Verse not found: {loc_str} ({context})")
    return idx


def build_january(ot_nav, nt_nav, ps_nav, pr_nav):
    ot_idx = _find(ot_nav, "GEN.1.1", "Jan start")
    nt_idx = _find(nt_nav, "MAT.1.1", "Jan start")
    ps_idx = _find(ps_nav, "PSA.1.1", "Jan start")
    pr_idx = _find(pr_nav, "PRO.1.1", "Jan start")
    readings = []

    for day in range(1, 32):
        date_str = f"01{day:02d}"
        if day in JANUARY_TARGETS:
            t = JANUARY_TARGETS[day]
            ot_end_idx = _find(ot_nav, t["OT"], f"Jan {day} OT")
            nt_end_idx = _find(nt_nav, t["NT"], f"Jan {day} NT")
            ps_end_idx = _find(ps_nav, t["PSA"], f"Jan {day} PSA")
            pr_end_idx = _find(pr_nav, t["PRO"], f"Jan {day} PRO")
        else:
            next_day = day + 1
            while next_day not in JANUARY_TARGETS and next_day <= 31:
                next_day += 1
            if next_day > 31:
                raise ValueError(f"No January target after day {day}")
            t_next = JANUARY_TARGETS[next_day]
            days_remaining = next_day - day + 1

            def midpoint(start, end, div):
                return start + int((end - start) / div)

            ot_end_idx = midpoint(ot_idx, _find(ot_nav, t_next["OT"], f"Jan {day} OT"), days_remaining)
            nt_end_idx = midpoint(nt_idx, _find(nt_nav, t_next["NT"], f"Jan {day} NT"), days_remaining)
            ps_end_idx = midpoint(ps_idx, _find(ps_nav, t_next["PSA"], f"Jan {day} PSA"), days_remaining)
            pr_end_idx = midpoint(pr_idx, _find(pr_nav, t_next["PRO"], f"Jan {day} PRO"), days_remaining)

        readings.append(make_entry(
            date_str, ot_nav, nt_nav, ps_nav, pr_nav,
            ot_idx, nt_idx, ps_idx, pr_idx,
            ot_end_idx, nt_end_idx, ps_end_idx, pr_end_idx,
        ))
        ot_idx = ot_end_idx + 1
        nt_idx = nt_end_idx + 1
        ps_idx = ps_end_idx + 1
        pr_idx = pr_end_idx + 1

    return readings, (ot_idx, nt_idx, ps_idx, pr_idx)


def main():
    ot_nav = BibleNavigator(OT_SEQUENTIAL_BOOKS)
    nt_nav = BibleNavigator(NT_BOOKS)
    ps_nav = BibleNavigator(["PSA"])
    pr_nav = BibleNavigator(["PRO"])

    readings, (ot_idx, nt_idx, ps_idx, pr_idx) = build_january(ot_nav, nt_nav, ps_nav, pr_nav)

    TOTAL_DAYS = 334
    current_month = 2
    current_day = 1
    days_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

    for i in range(1, TOTAL_DAYS + 1):
        date_str = f"{current_month:02d}{current_day:02d}"
        days_left = TOTAL_DAYS - i + 1

        def get_target(nav, current_idx):
            remaining = len(nav.verses) - current_idx
            if days_left == 1:
                return remaining
            val = remaining / days_left
            target = int(round(val))
            if target < 1:
                target = 1
            return target

        ot_end_idx, ot_count = ot_nav.get_reading(ot_idx, get_target(ot_nav, ot_idx), i, snap_radius=10, min_cap=46, max_cap=66)
        nt_end_idx, nt_count = nt_nav.get_reading(nt_idx, get_target(nt_nav, nt_idx), i, snap_radius=5, min_cap=12, max_cap=32)
        ps_end_idx, ps_count = ps_nav.get_reading(ps_idx, get_target(ps_nav, ps_idx), i, snap_radius=2)
        pr_end_idx, pr_count = pr_nav.get_reading(pr_idx, get_target(pr_nav, pr_idx), i, snap_radius=2)

        readings.append(make_entry(
            date_str, ot_nav, nt_nav, ps_nav, pr_nav,
            ot_idx, nt_idx, ps_idx, pr_idx,
            ot_end_idx, nt_end_idx, ps_end_idx, pr_end_idx,
        ))
        
        if ot_count > 0: ot_idx = ot_end_idx + 1
        if nt_count > 0: nt_idx = nt_end_idx + 1
        if ps_count > 0: ps_idx = ps_end_idx + 1
        if pr_count > 0: pr_idx = pr_end_idx + 1
        
        current_day += 1
        if current_day > days_in_month[current_month]:
            current_day = 1
            current_month += 1
            
    # Atomic Write: Use shared utility to prevent corruption
    atomic_write_json("data/readings.json", readings)
    print(f"Wrote {len(readings)} days to data/readings.json")
    print("First Day:", json.dumps(readings[0], indent=2))
    print("Last Day:", json.dumps(readings[-1], indent=2))

if __name__ == "__main__":
    main()
