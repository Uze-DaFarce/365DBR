# Ah! I see what happened.
# `resolvedVid` is getting set correctly.
# But when `scrollIntoView` is called, it triggers the `IntersectionObserver` immediately.
# The `IntersectionObserver` is registered on ALL `verse` elements in `groupedVids`.
# The IntersectionObserver logic:
#         const bestEntry = intersecting.sort((a, b) => Math.abs(a.boundingClientRect.top - 120) - Math.abs(b.boundingClientRect.top - 120))[0];
#         setActiveVerseId(bestEntry.target.id.replace('verse-', ''));

# But why does it scroll to Verse 1?
# It doesn't! The user might be confused because `activeVerseId` gets set to Verse 1 temporarily as it scrolls past? No, the scroll is INSTANT if `behavior` is `smooth` but the page was at the top.
# Wait, if `activeVerseId` changes, does it cause a re-render that interrupts the scroll?
# NO.
# Let's think. What if `document.getElementById('verse-' + resolvedVid)` is NULL?
# If `document.getElementById('verse-' + resolvedVid)` is null, it won't scroll.
# But `resolvedVid` was found in `sortedVids` or `verseMap`!
# So `groupedVids` MUST have rendered it.

# Is there any case where `resolvedVid` is wrong?
# Let's check `verseMap`.
# What does `displayVid` look like?
# In `api.bible`, the `verseId` for KJV is `GEN.1.2`.
# Wait! In the Original translation (Hebrew/Greek), what is the `verseId`?
# It is `GEN.1.2` as well.
# Both translations have the SAME `displayVid` format!
# If both use "GEN.1.2", why did it break?

# Ah!
# Let's look at `sortedVids.includes(targetScrollVerse)`.
# `sortedVids` is built from `Object.keys(verseMap)`.
# In `verseMap`, the keys are `vid`.
# The `vid` comes from:
#     if (item.attrs?.verseId) {
#       let keyVid = item.attrs.verseId;
#       if (useOrgId && item.attrs.verseOrgIds && item.attrs.verseOrgIds.length > 0) keyVid = item.attrs.verseOrgIds[0];

# For Original translation (`useOrgId = false`), `keyVid` is `item.attrs.verseId` (e.g., "GEN.1.2").
# For KJV translation (`useOrgId = true`), `keyVid` is `item.attrs.verseOrgIds[0]` (e.g., "GEN.1.2").
# So `vid` IS "GEN.1.2"!
# The `verseMap` keys ARE "GEN.1.1", "GEN.1.2", etc.!
# THEY ARE NOT "b3b19b..."! (Those are chapter IDs, or maybe verse IDs in other formats, but the parser extracts `item.attrs.verseId`).

# IF the `vid` is "GEN.1.2", then `sortedVids` contains "GEN.1.2".
# IF `targetScrollVerse` is "GEN.1.2", then `sortedVids.includes("GEN.1.2")` IS TRUE!

# SO WHY DID IT ALWAYS GO TO VERSE 1???
# Because...
# `targetScrollVerse` is set to `GEN.1.2` in `BibleBrowseDialog`.
# Then `useEffect` fires. `targetScrollVerse` is `"GEN.1.2"`.
# `resolvedVid` = `"GEN.1.2"`.
# `el` = `document.getElementById('verse-GEN.1.2')`.
# `el.scrollIntoView(...)`.
# Why did it scroll to verse 1?
# Wait. Did it scroll to Verse 1? Or did it STAY at Verse 1?
# If `el` is null, it stays at Verse 1.
# Why would `el` be null?
# Let's look at the `id` of the verse elements.
