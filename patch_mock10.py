import re

with open("bible.html", "r") as f:
    html = f.read()

# Let's inspect `groupedVids` rendering.
# <VerseGroup key={group[0]} group={group} verseMap={verseMap} ... />
# Is the id of the verse `verse-${group[0]}`?
# Yes.
# BUT wait. What if the `groupedVids` are rendered, but React hasn't attached them to the DOM when `useEffect` fires?
# It should be attached.

# Let's look at the actual error in `targetScrollVerse` again.
#               el.scrollIntoView({ behavior: 'smooth', block: 'center' });
# What if `behavior: 'smooth'` is interrupted by React's rendering?
# If the user clicks Verse 5, and it smooth scrolls, it might take 500ms.
# Meanwhile, the user says "always goes to verse one".
# That means it's NOT scrolling.
# Why?
# Is `resolvedVid` null?
# Let's write a script to just replace the whole `targetScrollVerse` logic with a console log and force the fallback, then test in Chrome.
# I can't test in Chrome, but I can read the source again.

# Wait, `targetScrollVerse` is set to `GEN.1.2`.
# `displayVid` is `GEN.1.2`.
# But wait, `focalTranslation` is `LSV` or `KJV`.
# Does LSV use `GEN.1.2`?
# In `verseMap['GEN.1.2']['kjv']?.displayVid`, what is the value?
# Wait! In `verseMap`, the original Hebrew is mapped FIRST.
# `processContent(data.content, verseMap, 'original', false);`
# `keyVid` = `GEN.1.2`. `displayVid` = `GEN.1.2`.
# Then KJV is mapped.
# `processContent(parallel.content, verseMap, 'kjv', true);`
# `keyVid` = `verseOrgIds[0]` (e.g. `GEN.1.2`).
# BUT what if `verseOrgIds` is empty or undefined?
# If `verseOrgIds` is empty, `keyVid` falls back to `verseId`.
# What is `verseId` for KJV?
# For api.bible, KJV verseId is `GEN.1.2`.
# So `keyVid` is `GEN.1.2`.
# `displayVid` is `GEN.1.2`.

# SO WHY DID IT ALWAYS GO TO VERSE 1?
# Wait. `targetScrollVerse` is created by `setTargetScrollVerse(`${b}.${c}.${v}`);`
# If they select Book: GEN, Chapter: 1, Verse: 5.
# `setTargetScrollVerse("GEN.1.5")`
# `targetScrollVerse` is `"GEN.1.5"`.
# `sortedVids` includes `"GEN.1.5"`.
# `resolvedVid` = `"GEN.1.5"`.
# It scrolls to `verse-GEN.1.5`.
# THIS LOGIC IS PERFECT FOR GENESIS 1:5.

# So why did the user say "goes to verse one"?
# Did I break `onSelect`?
# Let's check `BibleBrowseDialog`.

#    const handleVerseSelect = (v) => {
#        onSelect(book, chapter, v);
#        onClose();
#    };

# Wait. Look at how `verses` is built:
#        const totalVerses = VERSE_COUNTS[book][chapter - 1] || 1;
#        let verses = Array.from({ length: totalVerses }, (_, i) => i + 1);

# Is it possible that `totalVerses` is calculated wrong, so `verses` is just `[1]`?
# If `verses` is `[1]`, then they can ONLY click Verse 1!
# Let's trace `VERSE_COUNTS[book][chapter - 1]`.
# `book` is "GEN". `chapter` is "1" or 1?
# In `BibleBrowseDialog`:
#        setChapter(c);
# What is `c`?
# In `currentChapterChunk.map(c => ...)`
# `let chapters = Object.keys(index[book]).map(Number);`
# `c` is a Number!
# So `chapter` is a Number.
# `chapter - 1` is `1 - 1 = 0`.
# `VERSE_COUNTS["GEN"][0]` is `31`.
# So `verses` is `[1, ..., 31]`.
# They can click 2, 3, 4, 5.

# What if `VERSE_COUNTS[book]` is undefined?
# `book` is "GEN". It exists.
# What if `VERSE_COUNTS[book]` is defined, but `book` is "PSA Psalms" ?
# Ah!
# `handleBookSelect(b)` sets `book` to `b`.
# What is `b`?
# `displayBooks` comes from `availableBooks`.
# `availableBooks` comes from `newIndex`.
# `newIndex` keys are `GEN`, `EXO`, etc.
# So `book` is `"GEN"`.
# So `VERSE_COUNTS["GEN"]` works.

# Why did it always go to verse 1?
# Did the `sortedVids` search logic match `PSA.51.1` on EVERY verse?
# Let's look at the loop:
#              for (const vid of sortedVids) {
#                  const translations = verseMap[vid];
#                  // Check focal first
#                  if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {
#                      resolvedVid = vid;
#                      break;
#                  }
#                  // ...
#              }

# What if `translations[focalTranslation]?.displayVid` is ALWAYS `undefined`?
# If it's undefined, `undefined === targetScrollVerse` is FALSE.
# What if `translations['kjv']` is missing? It skips.
# If `resolvedVid` remains null, it falls through.
# If `resolvedVid` is null, it does `setTargetScrollVerse(null)` and DOES NOT SCROLL.
# If it DOES NOT SCROLL, the page loads at the top, displaying Verse 1!
# YES!
# "Darn, now it just always goes to verse one no matter what verse I choose :("
# This means `resolvedVid` was NULL!
# It couldn't find a match!

# WHY would it fail to find a match?
# I added the KJV displayVid loop IN PLACE OF the exact match check!
# Wait. In my FIRST commit for this fix (`patch_auto_dialog.py`):
#          if (sortedVids.includes(targetScrollVerse)) {
#              resolvedVid = targetScrollVerse;
#          } else {
#              // search verseMap...

# If `sortedVids.includes(targetScrollVerse)` was TRUE, it SHOULD have found it and scrolled!
# Was `sortedVids.includes("GEN.1.5")` FALSE?!
# Let's check `sortedVids`.
