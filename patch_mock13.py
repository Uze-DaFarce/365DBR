# WAIT!
# `for (const vid of sortedVids)`
# What is the order of `sortedVids`?
# In Psalms 51, `sortedVids` contains `PSA.51.1`, `PSA.51.2`, `PSA.51.3` (Hebrew IDs).
# Hebrew `PSA.51.1` corresponds to Title.
# `verseMap['PSA.51.1']` has `original.displayVid = "PSA.51.1"`.
# `verseMap['PSA.51.1']` has NO `kjv` translation? Actually, KJV combines it into `PSA.51.1`? No.
# If KJV is omitted, `kjv` is not in `verseMap['PSA.51.1']`.

# Let's say user selects "PSA.51.1" (they want KJV Verse 1).
# Loop `vid = "PSA.51.1"`:
#    `translations = verseMap["PSA.51.1"]`
#    `translations.kjv` is undefined.
#    `translations.original.displayVid` is `"PSA.51.1"`.
#    So `resolvedVid` = `"PSA.51.1"`.
#    `break`!
# So it resolves to Hebrew Verse 1 !!!
# THIS EXPLAINS "It is going to the Original Translation verse number"!
# My patch did NOT fix it! It just found the first translation that had the displayVid, which was ALWAYS the Original!
# Why did it find the Original? Because I checked:
#              for (const key in translations) {
#                  if (translations[key]?.displayVid === targetScrollVerse) {
#                      resolvedVid = vid;
#                      break;
#                  }
#              }
# This loop checks ALL keys, including `original`!

# BUT I DID:
#              if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {
#                  resolvedVid = vid;
#                  break;
#              }
# Why didn't `focalTranslation` match?
# If `targetScrollVerse` is `"PSA.51.1"`.
# Does `translations['kjv']` have `displayVid === "PSA.51.1"` in ANY `vid`?
# Hebrew `PSA.51.3` has `kjv` `displayVid = "PSA.51.1"`.
# But my outer loop iterated over `PSA.51.1` first!
# For `vid = "PSA.51.1"`, it checked `kjv`. `kjv` was missing.
# Then it fell back to checking ALL keys!
# It found `original`, which HAD `displayVid = "PSA.51.1"`!
# So it stopped the loop at `PSA.51.1` and scrolled to Hebrew Verse 1!

# AHHH!!!
# That's why it went to Hebrew Verse 1 for Psalms 51:1!

# But wait, the user said "Darn, now it just always goes to verse one no matter what verse I choose :("
# "Verse one" for EVERYTHING?
# What if they chose "PSA.51.5"?
# `vid = "PSA.51.1"` -> `original` has "PSA.51.1", doesn't match "PSA.51.5".
# `vid = "PSA.51.5"` -> `kjv` might be missing. `original` has "PSA.51.5". Matches!
# It scrolls to Hebrew Verse 5!
# Why did they say "always goes to verse one"?
# Did they mean "it goes to the TITLE (Verse 1 in Hebrew) for Psalms"?
# NO, "no matter what verse I choose".

# Could `targetScrollVerse` be something ELSE entirely?
# What if `setTargetScrollVerse(b.c.v)` was broken?
# `setTargetScrollVerse(`${b}.${c}.${v}`);`
# What if `v` is an Object or Event?
# Oh my goodness!
# In `BibleBrowseDialog`:
#                                          {currentVerseChunk.map(v => (
#                                            <button key={v} onClick={() => handleVerseSelect(v)} ...>
#                                                {v}
#                                            </button>
#                                        ))}
# `v` is mapped from `currentVerseChunk`, which is an array of numbers `[1, 2, ...]`.
# So `v` is a Number.

# What if `BibleBrowseDialog` `onSelect={(b, c, v) => ...}` ?
# `handleVerseSelect(v)` calls `onSelect(book, chapter, v)`.
# `book` is "PSA". `chapter` is 51. `v` is 5.
# `setTargetScrollVerse("PSA.51.5")`.

# Let's consider: if `targetScrollVerse` is `"PSA.51.5"`.
# My loop finds Hebrew Verse 5.
# Did the user say "always goes to verse one" because THEY ONLY TESTED PSALMS?
# Yes!
# Psalms has Titles.
# If they clicked Psalm 51, Verse 1, it went to Title.
# If they clicked Psalm 51, Verse 5, did it go to Title?
# Why would it go to Title for Verse 5?
# Let's see if there is a bug that makes `resolvedVid` equal `"PSA.51.1"` for ANY `targetScrollVerse`.
