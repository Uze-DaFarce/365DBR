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

def main():
    ot_nav = BibleNavigator(OT_SEQUENTIAL_BOOKS)
    nt_nav = BibleNavigator(NT_BOOKS)
    ps_nav = BibleNavigator(["PSA"])
    pr_nav = BibleNavigator(["PRO"])
    
    # Initial Cursors
    # IMPORTANT: The starting cursors must exist in the Hebrew versification!
    # EXO 7:1 (Hebrew) = EXO 7:1 (KJV) usually.
    # MAT 22:39 (Greek) = MAT 22:39 (KJV).
    # PSA 18:43 (Hebrew) = PSA 18:43 (KJV)? 
    #   Let's check: KJV PSA 18 has 50 verses. Hebrew PSA 18 has 51 verses (Title=v1).
    #   So KJV 18:43 might be Hebrew 18:44.
    #   However, the user specified "PSA.18.43" explicitly.
    #   If we stick to "Hebrew Counts", we should interpret this as Hebrew 18:43.
    # PRO 4:10 (Hebrew) = PRO 4:10 (KJV).
    
    ot_idx = ot_nav.find_index("EXO.7.1")
    nt_idx = nt_nav.find_index("MAT.22.39")
    ps_idx = ps_nav.find_index("PSA.18.43")
    pr_idx = pr_nav.find_index("PRO.4.10")
    
    if ot_idx == -1: raise ValueError("Error finding start EXO.7.1")
    if nt_idx == -1: raise ValueError("Error finding start MAT.22.39")
    if ps_idx == -1: raise ValueError("Error finding start PSA.18.43")
    if pr_idx == -1: raise ValueError("Error finding start PRO.4.10")

    # Calculate Base Rates
    TOTAL_DAYS = 334
    
    readings = []
    
    current_month = 2
    current_day = 1
    days_in_month = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    
    for i in range(1, TOTAL_DAYS + 1):
        date_str = f"{current_month:02d}{current_day:02d}"
        days_left = TOTAL_DAYS - i + 1
        
        def get_target(nav, current_idx):
            remaining = len(nav.verses) - current_idx
            if days_left == 1:
                return remaining
            val = remaining / days_left
            target = int(round(val))
            if target < 1: target = 1
            return target

        ot_target = get_target(ot_nav, ot_idx)
        nt_target = get_target(nt_nav, nt_idx)
        ps_target = get_target(ps_nav, ps_idx)
        pr_target = get_target(pr_nav, pr_idx)
        
        # Calculate Readings with Snap
        ot_end_idx, ot_count = ot_nav.get_reading(ot_idx, ot_target, i, snap_radius=10, min_cap=46, max_cap=66)
        nt_end_idx, nt_count = nt_nav.get_reading(nt_idx, nt_target, i, snap_radius=5, min_cap=12, max_cap=32)
        ps_end_idx, ps_count = ps_nav.get_reading(ps_idx, ps_target, i, snap_radius=2)
        pr_end_idx, pr_count = pr_nav.get_reading(pr_idx, pr_target, i, snap_radius=2)
        
        # Formatting
        # Generate API Strings and Friendly Texts handling potential gaps (mostly for OT)
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
        
        friendly_parts = [ot_friendly, nt_friendly, ps_friendly, pr_friendly]
        text_friendly = ", ".join(friendly_parts)
        
        entry = {
            "day": date_str,
            "api_format": api_str,
            "text_friendly": text_friendly,
            "ot_verse_count": ot_count,
            "nt_verse_count": nt_count,
            "ps_verse_count": ps_count,
            "pr_verse_count": pr_count
        }
        readings.append(entry)
        
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
        
    print("First Day:", json.dumps(readings[0], indent=2))
    print("Last Day:", json.dumps(readings[-1], indent=2))

if __name__ == "__main__":
    main()
