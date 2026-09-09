import os
import re
from pathlib import Path
from collections import defaultdict
from bible_common import BIBLE_DATA, BOOK_NAMES

DATA_DIR = Path("data")
VERSE_ID_RE = re.compile(r'\b([1-3]?[A-Z]{2,3})\.(\d+)\.(\d+)\b')

def audit_counts():
    print("Scanning injected JSON for verse count anomalies...")
    
    # Store the max verse found per chapter
    max_found = defaultdict(lambda: defaultdict(int))
    
    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            if not filename.endswith(".json") or filename == "manifest.json":
                continue
                
            filepath = Path(root) / filename
            try:
                content = filepath.read_text(encoding="utf-8")
                for match in VERSE_ID_RE.finditer(content):
                    book, chapter, verse = match.groups()
                    chapter_int = int(chapter)
                    verse_int = int(verse)
                    
                    if verse_int > max_found[book][chapter_int]:
                        max_found[book][chapter_int] = verse_int
            except Exception as e:
                pass

    # Compare found maximums against BIBLE_DATA
    anomalies = []
    for book, chapters in max_found.items():
        for chap_int, highest_verse in chapters.items():
            try:
                # BIBLE_DATA is 0-indexed for chapters (so Chapter 1 is index 0)
                current_max = BIBLE_DATA[book][chap_int - 1]
                if highest_verse > current_max:
                    anomalies.append(
                        f"UPDATE REQUIRED: {BOOK_NAMES.get(book, book)} {chap_int} "
                        f"- BIBLE_DATA says {current_max}, but LSB data requires {highest_verse}"
                    )
            except (KeyError, IndexError):
                pass
                
    if not anomalies:
        print("\n✅ Perfect! BIBLE_DATA is large enough to cover all LSB verses.")
    else:
        print(f"\n❌ Found {len(anomalies)} chapters where BIBLE_DATA is too small:")
        for a in anomalies:
            print(a)

if __name__ == "__main__":
    audit_counts()