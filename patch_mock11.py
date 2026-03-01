# If `sortedVids.includes("GEN.1.5")` is FALSE, then `sortedVids` does not contain "GEN.1.5".
# What does `sortedVids` contain?
# Let's look at `index.html`.
#   const sortedVids = useMemo(() => {
#     if (!verseMap) return [];
#     return Object.keys(verseMap).sort((a,b) => {
#         const [b1, c1, v1] = a.split('.');
#         const [b2, c2, v2] = b.split('.');
#         // ...
#     });
#   }, [verseMap]);

# Wait. `a.split('.')`. So `a` is "GEN.1.5".
# This confirms `vid` format is "GEN.1.5".
# SO WHY WOULD `sortedVids.includes("GEN.1.5")` BE FALSE?
# If `GEN.1.5` is NOT in `verseMap`!
# Why would `GEN.1.5` not be in `verseMap`?
# Is the API ID "GEN.1.5"?
# Let's look at `loadContent`.
# `const days = index[selectedBook][selectedChapter];`
# `const dayDataList = await Promise.all(days.map(d => loadDailyBread(d)));`

# Oh!
# I mocked the API!
# "Failed to fetch at 'https://mt-sin.ai/365DBR/data/0101/manifest.json'"
# If `verseMap` fails to load, `verseMap` is null!
# If `verseMap` is null, NO SCROLLING OCCURS.
# Did the user's internet fail? No, the user saw the chapter!
# The chapter loaded. "goes to verse one no matter what verse I choose".
# So `verseMap` is NOT null. `sortedVids` is NOT empty.

# Then why did it go to verse one?
# Could it be that `targetScrollVerse` was cleared too early?
# Look at the hook:
#  useEffect(() => {
#      if (!loading && targetScrollVerse && verseMap && sortedVids.length > 0) {
#          let resolvedVid = null;
#          // ...
#          if (resolvedVid) {
#              // ...
#          } else {
#             setTargetScrollVerse(null); // <-- Wait!
#          }
#      }
#  }, [loading, targetScrollVerse, verseMap, sortedVids, focalTranslation]);

# IF `loading` becomes false BEFORE `verseMap` is populated?
# NO. `loadContent`:
#        setLoading(true);
#        setVerseMap(null);
#        // fetch...
#        setVerseMap(merged);
#        setLoading(false);
# State updates are batched. `loading=false` and `verseMap=merged` happen together.
# Then `useEffect` fires. `targetScrollVerse` is still `"GEN.1.5"`.
# `sortedVids` is recalculated.
# Wait, `sortedVids` is a `useMemo` that depends on `verseMap`.
# If `useEffect` depends on `sortedVids`, and `sortedVids` is re-evaluating...
# Does `useEffect` see the OLD `sortedVids` first?
# NO, `useMemo` is synchronous during render. `useEffect` is after render. `sortedVids` is correct.

# What if `sortedVids.includes("GEN.1.5")` IS TRUE?
# Then `resolvedVid` = "GEN.1.5".
# Then `document.getElementById('verse-GEN.1.5')`.
# What if it returns null?
# Because `groupedVids` is a `useMemo` depending on `sortedVids`.
# And `VerseGroup` renders `<div id={`verse-${group[0]}`}>`.
# If it's in the DOM, it shouldn't be null.
# Unless... the scroll is happening before the DOM paints?
# `useEffect` runs after paint.

# So WHY did the user see verse 1?
# Let's consider: What if `targetScrollVerse` is `"GEN.1.5"`, but the HTML ID is NOT `"verse-GEN.1.5"`?
# The `id` is `"verse-" + vid`. `vid` is "GEN.1.5".
# So the ID IS `"verse-GEN.1.5"`.

# Is it possible the user is complaining about the Verse PICKER itself?
# "Darn, now it just always goes to verse one no matter what verse I choose :("
# Did they mean the picker goes to page 1?
# No, they meant scrolling.

# Wait, what if `targetScrollVerse` has a zero-padded verse number?
# Like "GEN.1.05"?
# In `BibleBrowseDialog`:
#        setTargetScrollVerse(`${b}.${c}.${v}`);
# `v` is 5. So it's `"GEN.1.5"`.
# In `verseMap`, is it `"GEN.1.5"`?
# Yes, api.bible uses non-padded numbers: "GEN.1.5".

# What if `b` is different?
# `book` is "PSA". `chapter` is 51. `v` is 1.
# `setTargetScrollVerse("PSA.51.1")`.
# `targetScrollVerse` = `"PSA.51.1"`.

# BUT wait.
# KJV displayVid is "PSA.51.1".
# Original translation displayVid is "PSA.51.1".
# The user wants "It is going to the Original Translation verse number, and it needs to go to the KJV and LSV verse number."
# BEFORE my patch, it went to "PSA.51.1" Original.
# The user clicked Verse 1.
# It scrolled to "PSA.51.1" Original.
# This Original verse corresponded to KJV Title, not KJV Verse 1!
# The user noticed they were reading the Title instead of Verse 1.
# They said "It is going to the Original Translation verse number, and it needs to go to the KJV and LSV verse number."

# AFTER my patch:
# My patch changed the `Scroll Restoration` logic to prioritize KJV/LSV lookup.
# But wait! I put the `focalTranslation` check INSIDE a loop.
# Let's look at my last patch logic:
