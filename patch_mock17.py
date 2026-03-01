# Let's look at the loop:
#              for (const vid of sortedVids) {
#                  const translations = verseMap[vid];
#                  if (!translations) continue;
#
#                  // Check focal first
#                  if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {
#                      resolvedVid = vid;
#                      break;
#                  }
#                  // Fallback to checking any translation
#                  for (const key in translations) {
#                      if (translations[key]?.displayVid === targetScrollVerse) {
#                          resolvedVid = vid;
#                          break;
#                      }
#                  }
#                  if (resolvedVid) {
#                      break;
#                  }
#              }

# WHY DID IT NOT FIND IT?
# Is `targetScrollVerse` NOT equal to `displayVid`?
# What is `targetScrollVerse`? `"GEN.1.5"`
# What is `translations[focalTranslation]?.displayVid`?
# In `api.bible`, the `verseId` for KJV Genesis 1:5 is `"GEN.1.5"`.
# Yes!

# Wait!
# Does `processContent` add `displayVid` to the object?
# Let's check `walkItems`:
# `if (!map[keyVid][versionKey]) map[keyVid][versionKey] = { text: [], displayVid: item.attrs.verseId };`
# Yes!
# `item.attrs.verseId` is `"GEN.1.5"`.

# Is it possible that `targetScrollVerse` is `"GEN.1.5"`, but the translation doesn't have a `kjv` object?
# `if (!translations) continue;`
# `translations['kjv']` might be undefined if `processContent` failed or the JSON omitted it.
# But it checks ALL keys! `for (const key in translations)`!
# `translations['original'].displayVid` IS `"GEN.1.5"`!
# So it SHOULD find `original`!

# BUT wait! I added `// Fallback to exact match (in case it IS an original vid or URL match)`
#          if (!resolvedVid && sortedVids.includes(targetScrollVerse)) {
#              resolvedVid = targetScrollVerse;
#          }

# IF my loop didn't find `resolvedVid`, the FALLBACK should have set `resolvedVid = "GEN.1.5"`!
# IF `resolvedVid = "GEN.1.5"`, it SHOULD have scrolled!

# So why did the user say "goes to verse one"?
# WHAT IF `resolvedVid` was NOT `"GEN.1.5"`?
# What if the loop FOUND something else and `break`d early?

# YES!!!
# The loop found `resolvedVid = "GEN.1.1"`!!!
# HOW?!
# Look at the loop:
#              for (const vid of sortedVids) {
#                  const translations = verseMap[vid];
#
#                  if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {

# How could `displayVid === targetScrollVerse` evaluate to TRUE for Verse 1?
# It CANNOT! `"GEN.1.1"` is NOT `"GEN.1.5"`.
# Unless `targetScrollVerse` IS `"GEN.1.1"`!

# WHY WOULD `targetScrollVerse` BE `"GEN.1.1"`?
# Let's look at `setTargetScrollVerse(`${b}.${c}.${v}`);`
# Is it possible `v` is ALWAYS `1`?!
# NO! The user literally clicked "5".

# Wait. Is the user clicking "1"?
# "now it just always goes to verse one no matter what verse I choose :("
# No, "no matter what verse I choose" implies they tried 5, 10, etc., and it went to Verse 1.
# So `targetScrollVerse` is `"GEN.1.5"`.
# The loop evaluates `"GEN.1.5"`.
# If `displayVid` is `"GEN.1.1"`, it doesn't match.
# If `displayVid` is `"GEN.1.5"`, it MATCHES!
# It sets `resolvedVid = "GEN.1.5"`.
# It breaks.
# `document.getElementById('verse-GEN.1.5')`.
# It scrolls to Verse 5.

# Then why did it go to Verse 1?
