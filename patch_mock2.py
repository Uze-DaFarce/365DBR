import json

with open("bible.html", "r") as f:
    html = f.read()

# Let's check `sortedVids`. How are they formatted?
# They come from `Object.keys(verseMap).sort(...)`.
# In `verseMap`, the keys are the `vid` string.
# Are the `vid` strings "GEN.1.2"?
# Let's check `processContent` logic.
# "item.attrs.verseId" is the `vid`.
# In api.bible format, `verseId` is `GEN.1.2`.
# So `targetScrollVerse` is `GEN.1.2` and `sortedVids` includes `GEN.1.2`.

# Then why does it go to Verse 1?
# Maybe `document.getElementById('verse-GEN.1.2')` fails?
# Why would it fail?
# Because `verse-GEN.1.2` is rendered dynamically?
# `groupedVids.map(group => ...)`
# `id={'verse-' + group[0]}`

# Ah! `verse-GEN.1.2` might not be in the DOM YET when the effect runs!
# When does `Scroll Restoration` effect run?
# `useEffect(() => { ... }, [loading, targetScrollVerse, verseMap, sortedVids, focalTranslation]);`
# When `loading` becomes false, `verseMap` is populated, and `sortedVids` is populated.
# The `useEffect` fires AFTER React renders `groupedVids`.
# So `document.getElementById('verse-GEN.1.2')` should exist.

# Wait, is there a chance that `targetScrollVerse` is wiped out too early?
# In `App`:
#           if (resolvedVid) {
#               const el = document.getElementById(`verse-${resolvedVid}`);
#               if (el) {
#                   el.scrollIntoView({ behavior: 'smooth', block: 'center' });
#                   // Also set active immediately to ensure visual highlight
#                   setActiveVerseId(resolvedVid);
#                   setTargetScrollVerse(null);
#               } else {
#                  setTargetScrollVerse(null); // Wait, this was cleared!
#               }
#           }

# Wait, what if the `vid` in `sortedVids` is "GEN.1.2" but `targetScrollVerse` is "GEN.1.2"?
# That matches. But does the DOM element exist? Yes, it should.
# Unless... what if the verse isn't "GEN.1.2"?
# What if `vid` is "GEN.1.2", but the id of the element is NOT "verse-GEN.1.2"?
# Wait! In `verseGroup`, `id={'verse-' + group[0]}`. `group[0]` is `vid`.

# Could it be that the IntersectionObserver immediately overwrites it?
# In `IntersectionObserver`:
#         const bestEntry = intersecting.sort(...)[0];
#         setActiveVerseId(bestEntry.target.id.replace('verse-', ''));

# If we call `scrollIntoView(..., block: 'center')`, the observer will fire because the scrolling changes what is intersecting.
# It will set `setActiveVerseId` to whatever is at the top.
# But it will STILL have scrolled! The user says "goes to verse one". That implies it SCROLLS to verse 1.
# Or it stays at the top.

# Why would it stay at the top?
# Because `targetScrollVerse` was never matched.
# Why wouldn't it match?
# Let's look at `targetScrollVerse`: it comes from `onSelect(book, chapter, verse)`.
# `setTargetScrollVerse(`${b}.${c}.${v}`);`

# Wait! The original logic handled multiple formats:
# if (targetScrollVerse && verseMap) ...
# What if the user clicked "1-50" then "1" (Chapter 1), then "2" (Verse 2)?
# `targetScrollVerse` is `"GEN.1.2"`.
# Wait, look at the KJV displayVid mapping logic I added:

#                   if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {

# Let's look at `displayVid` in `processContent`:
# `map[keyVid][versionKey] = { text: [], displayVid: item.attrs.verseId };`
# `item.attrs.verseId` is "GEN.1.2". So `displayVid` is "GEN.1.2".

# If `targetScrollVerse` is "GEN.1.2", everything should match perfectly.
# So why did it fail?
# Let's check `targetScrollVerse` in the DOM after selecting from the modal.
# Oh! In `BibleBrowseDialog`:
#        setTargetScrollVerse(`${book}.${chapter}.${v}`);
# BUT in the KJV displayVid, does it use KJV book codes? No, `GEN.1.2` is the KJV ID for Genesis 1:2.

# But wait, KJV book codes might be different? No, `processContent` pulls `displayVid` from the parsed JSON.
# What if the API's JSON for KJV has `verseId: "GEN.1.2"` but the original has `verseId: "GEN.1.2"`?
# Yes, they both have "GEN.1.2".

# Let's trace it.
# The user said: "Darn, now it just always goes to verse one no matter what verse I choose :("
# I modified `useEffect` for `targetScrollVerse`.
# Did I accidentally break the URL routing or the local storage loading?
# When they click a verse in the dialog, `onSelect` fires:
#             setSelectedBook(b);
#             setSelectedChapter(c);
#             setTargetScrollVerse(`${b}.${c}.${v}`);
#             onClose();

# When `selectedBook` changes, `useEffect` for `loadContent` fires:
#             setLoading(true);
#             setVerseMap(null);

# When `setVerseMap` is set to null, `targetScrollVerse` is still `"GEN.1.2"`.
# Then `loadContent` completes:
#             setVerseMap(merged);
#             setLoading(false);

# Then `useEffect` for `targetScrollVerse` fires:
#       if (!loading && targetScrollVerse && verseMap && sortedVids.length > 0) { ... }
# What happens if `sortedVids.includes(targetScrollVerse)` is true?
# `resolvedVid = targetScrollVerse;`
# `const el = document.getElementById(verse-${resolvedVid});`
# `el.scrollIntoView(...)`

# Wait, why wouldn't this work?
# Could it be `sortedVids.length === 0`? No.
# Could `document.getElementById` return null because React hasn't rendered it yet?
# YES!!!
# In React 18 (or general React lifecycle), `useEffect` runs synchronously after DOM mutations, BUT:
# Wait, if `setVerseMap(merged)` and `setLoading(false)` are called, React schedules a re-render.
# The `useEffect` with `[loading, targetScrollVerse, verseMap, sortedVids]` fires AFTER the render completes and the DOM is updated.
# So `document.getElementById` SHOULD find it.

# Let's write a python script to dump the exact `Scroll Restoration` effect to see if I made a typo.
