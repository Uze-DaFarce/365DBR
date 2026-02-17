import json
import os
import math

# Hebrew/Greek Verse Counts (Scanned from api.bible IDs)
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

# Book Lists
ALL_BOOKS = list(BIBLE_DATA.keys())
OT_BOOKS = ALL_BOOKS[:39]  # GEN to MAL
NT_BOOKS = ALL_BOOKS[39:]  # MAT to REV

# PSA and PRO are in OT_BOOKS list naturally (indices 18 and 19), 
# but per spec we need to exclude them from the sequential OT reading.
OT_SEQUENTIAL_BOOKS = [b for b in OT_BOOKS if b not in ["PSA", "PRO"]]

# Known Omissions in Critical Texts (SBLGNT, NA28, etc.) which API.Bible follows for Greek NT (7644de2e4c5188e5-01).
# Note: These verses ARE present in Textus Receptus based translations (KJV, LSV),
# but since our app drives the reading plan from the Greek text (SBLGNT), the API returns them as missing/empty.
# To avoid "Verse Count Mismatch" errors during validation, we treat them as omitted in our plan.
KNOWN_OMISSIONS = {
    "MAT.17.21", "MAT.18.11", "MAT.23.14",
    "MRK.7.16", "MRK.9.44", "MRK.9.46", "MRK.11.26", "MRK.15.28",
    "LUK.17.36", "LUK.23.17",
    "JHN.5.4",
    "ACT.8.37", "ACT.15.34", "ACT.24.7", "ACT.28.29",
    "ROM.16.24"
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
                print(f"Warning: {b} not in BIBLE_DATA, skipping.")
                continue
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
    
    if ot_idx == -1: print("Error finding start EXO.7.1")
    if nt_idx == -1: print("Error finding start MAT.22.39")
    if ps_idx == -1: print("Error finding start PSA.18.43")
    if pr_idx == -1: print("Error finding start PRO.4.10")

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
            
    with open("readings.json", "w") as f:
        json.dump(readings, f, indent=2)
        
    print("First Day:", json.dumps(readings[0], indent=2))
    print("Last Day:", json.dumps(readings[-1], indent=2))

if __name__ == "__main__":
    main()
