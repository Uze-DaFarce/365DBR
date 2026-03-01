# WAIT A MINUTE!
# The `verseMap` structure from `test_parse.js`:
# {
#   'GEN.1.2': { original: { text: [], displayVid: 'GEN.1.2' } },
#   'b3b1...': { kjv: { text: [], displayVid: 'GEN.1.2' } }
# }

# BUT IN REALITY, `verseMap` IS MERGED DIFFERENTLY in `loadDailyBread`!
# Let's look at `bible.html` `loadDailyBread`:
#   results.forEach((source) => {
#     const data = source.data;
#     if (!data) return;
#     if (data.content) processContent(data.content, verseMap, 'original', false);
#     if (data.parallels) {
#       data.parallels.forEach(parallel => {
#          if (matchedKey && parallel.content) {
#             processContent(parallel.content, verseMap, matchedKey, true);
#          }
#       });
#     }
#   });

# Yes! `processContent` is called for `original` with `useOrgId = false`.
# Then for `kjv` with `useOrgId = true`.
# Wait! Does the original translation (SBLGNT) HAVE `verseOrgIds`?
# NO! The original translation doesn't have `verseOrgIds` in the API output.
# BUT wait. What is `keyVid`?
# For original, `keyVid` is `item.attrs.verseId` (e.g. `GEN.1.2`).
# For KJV, `keyVid` is `item.attrs.verseOrgIds[0]` (e.g. `GEN.1.2`).
# Wait... if the original is `GEN.1.2` and KJV's `verseOrgId[0]` is `GEN.1.2`, then they MERGE INTO THE SAME OBJECT!
# YES!
# So `verseMap` becomes:
# {
#   'GEN.1.2': {
#       original: { text: [...], displayVid: 'GEN.1.2' },
#       kjv: { text: [...], displayVid: 'GEN.1.2' }
#   }
# }

# So `vid` is `GEN.1.2`.
# And `sortedVids` includes `GEN.1.2`.

# SO WHY DID IT ALWAYS GO TO VERSE 1?
# Let's think.
# `resolvedVid` = `GEN.1.2`.
# `document.getElementById('verse-GEN.1.2')` is called.
# Why would `scrollIntoView` fail?!
# Wait... what if `targetScrollVerse` is parsed as `GEN.1.2` but `sortedVids` doesn't have `GEN.1.2`?
# Does `sortedVids` have `GEN.1.2`?
# Yes.
# Does `VerseGroup` render `id="verse-GEN.1.2"`?
# Yes.
# Does it scroll?

# WHAT IF `loading` is False, but React HAS NOT YET RENDERED `VerseGroup` into the DOM?
# `VerseGroup` rendering is dependent on `groupedVids`.
# `groupedVids` is a `useMemo` dependent on `sortedVids`.
# `sortedVids` is a `useMemo` dependent on `verseMap`.
# `verseMap` is set in `loadContent` right before `setLoading(false)`.
# Since `setVerseMap` and `setLoading(false)` are batched, React renders `App` with `loading=false` and `verseMap=merged`.
# During this render, `sortedVids` is calculated, `groupedVids` is calculated, and `<VerseGroup>` is mapped over and rendered.
# ONLY THEN does the `useEffect` fire.
# So `document.getElementById` SHOULD return the element.
# AND it scrolls!

# IF IT SCROLLS, why did the user say "always goes to verse one"?
# Did it scroll, but `IntersectionObserver` immediately fired and overwrote `activeVerseId` with Verse 1 because Verse 1 was intersecting?
# YES!
# And if `activeVerseId` is overwritten, DOES THE PAGE SNAP BACK TO VERSE 1?
# No! `scrollIntoView` is an asynchronous browser action (smooth scroll).
# Changing `activeVerseId` state does NOT scroll the page back. It just highlights Verse 1!
# Wait! The user says "goes to verse one". That implies it SCROLLS to Verse 1!

# What if `document.getElementById` returns NULL?
# If it returns NULL, then `setTargetScrollVerse(null)` is called.
# And NO scroll occurs!
# So it stays at the top. The user sees Verse 1.
# This means `resolvedVid` is WRONG, or `document.getElementById` is failing.

# Let's test `document.getElementById`.
# Is the `id` really `verse-GEN.1.2`?
# Let's look at `bible.html`:
# <div id={`verse-${group[0]}`} className="verse-block group ...">
# `group[0]` is `vid`.
# `vid` is `GEN.1.2`.
# So the ID is EXACTLY `verse-GEN.1.2`.
