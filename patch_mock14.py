# If `focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse`
# What if `focalTranslation` is undefined?
# It's `"kjv"`.
# Is `targetScrollVerse` EXACTLY equal to `displayVid`?
# In `api.bible`, KJV verse IDs are "PSA.51.1".
# But wait!
# If the user selects Book: "1SA" Chapter: "1" Verse: 5.
# `setTargetScrollVerse("1SA.1.5")`.
# My loop finds `translations['kjv']?.displayVid === "1SA.1.5"`.
# Wait! In `api.bible`, the book code is "1SA"!
# What if KJV is missing "1SA.1.5"? No, it's there.

# Wait, what if the `focalTranslation` is "original"?
# The user doesn't use "original", they use KJV/LSV.

# Let's think about `verseChunks` again.
# `let verses = Array.from({ length: totalVerses }, (_, i) => i + 1);`
# `v` is just `1, 2, ...`
# `targetScrollVerse` is `"GEN.1.5"`.

# Is it possible that `totalVerses` is `1`?
# `VERSE_COUNTS[book][chapter - 1] || 1`
# What if `chapter` is a string? `chapter - 1` works in JS.
# What if `index[book]` does not contain the selected `chapter`?
# In `BibleBrowseDialog`, `chapterChunks` are built from `Object.keys(index[book]).map(Number)`.
# So `chapter` MUST be in `index[book]`.

# Let's look at the actual text of the user's message:
# "Darn, now it just always goes to verse one no matter what verse I choose :("
# Did they mean literally EVERY verse clicked in the dialog goes to Verse 1?
# Yes! "always goes to verse one no matter what verse I choose".

# Could it be because `sortedVids.includes(targetScrollVerse)`?
# My LAST commit:
#           for (const vid of sortedVids) {
#              if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {
#                  resolvedVid = vid;
#                  break;
#              }
#              for (const key in translations) {
#                  if (translations[key]?.displayVid === targetScrollVerse) {
#                      resolvedVid = vid;
#                      break;
#                  }
#              }
#              if (resolvedVid) break;
#           }

# Wait!
# Is `displayVid` ALWAYS formatted as `GEN.1.5`?
# Let's check `parse_reference` or `item.attrs.verseId`.
# In api.bible, verse IDs are sometimes formatted like `GEN.1.5-GEN.1.6`.
# But for single verses, they are `GEN.1.5`.

# Wait! Look at `targetScrollVerse`.
# `setTargetScrollVerse(`${b}.${c}.${v}`);`
# What if `v` is NOT what we think it is?
# If `v` is `1`, `targetScrollVerse` is `GEN.1.1`.
# What if `v` is `2`, `targetScrollVerse` is `GEN.1.2`.

# WHY would EVERY VERSE go to verse 1?
# Let's think about the `onSelect` callback.
# In `index.html`:
#        onSelect={(b, c, v) => {
#            setSelectedBook(b);
#            setSelectedChapter(c);
#            setTargetScrollVerse(`${b}.${c}.${v}`);
#        }}
# Wait! This is `index.html`!
# BUT the user is testing `bible.html` !!!
# Let's look at `bible.html` `onSelect`:
#        onSelect={(b, c, v) => {
#            setSelectedBook(b);
#            setSelectedChapter(c);
#            setTargetScrollVerse(`${b}.${c}.${v}`);
#        }}
# It's identical.
# But what if `b` is `GEN Genesis`?
# `handleBookSelect(b)` sets `book` to `b`.
# `b` is from `displayBooks`, which is from `availableBooks`.
# `availableBooks` is an array of strings like `['GEN', 'EXO', ...]`.
# So `b` is `"GEN"`.

# Wait... what if `targetScrollVerse` is `GEN.1.5`.
# The `useEffect` fires.
# `loading` is false, `verseMap` is not null.
# The loop:
#           for (const vid of sortedVids) { ... }
# What if `sortedVids` is empty?
# No, `sortedVids.length > 0` is checked.

# WHAT IF `resolvedVid` is NEVER found?
# Then it hits `setTargetScrollVerse(null);`
# And because `targetScrollVerse` is null, NO scroll occurs.
# And because NO scroll occurs, the page just renders at the top (Verse 1).
# YES. This is exactly what "goes to verse one" means: it DOES NOT SCROLL.

# WHY would `resolvedVid` never be found?
# Because `translations[key]?.displayVid` is NEVER equal to `targetScrollVerse`!
# WHY would `displayVid` never equal `targetScrollVerse`?
# Let's look at `displayVid`.
# What is it?
# Let's write a python script to test what `displayVid` actually is by scraping `bible.html`.
