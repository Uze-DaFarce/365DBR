with open("bible.html", "r") as f:
    html = f.read()

import re

# Find Scroll Restoration block
m = re.search(r"// Scroll Restoration(.*?)\}, \[loading, targetScrollVerse, verseMap, sortedVids, focalTranslation\]\);", html, re.DOTALL)
if m:
    print(m.group(0))
