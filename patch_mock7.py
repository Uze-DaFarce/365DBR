# Let's write a python script to run a Node environment and parse the `verseMap` out of the JSON.
# Wait, let's look at `index.html` `Scroll Restoration`.
# In `bible.html`:
#           if (sortedVids.includes(targetScrollVerse)) {
#               resolvedVid = targetScrollVerse;
#               console.log("Resolved via exact match:", resolvedVid);
#           } else {
#               // Otherwise, targetScrollVerse might be requested based on KJV/LSV.

# Wait! The user's bug report: "It is going to the Original Translation verse number, and it needs to go to the KJV and LSV verse number."
# "Darn, now it just always goes to verse one no matter what verse I choose :("
# Why?
# Because `sortedVids.includes(targetScrollVerse)` IS TRUE!
# So it ALWAYS resolves to `targetScrollVerse`!
# And what is `targetScrollVerse`?
# In Psalms, `targetScrollVerse` is `PSA.51.1`.
# `sortedVids` includes `PSA.51.1`! Because the Original Hebrew ALSO has a verse `PSA.51.1`!
# So `resolvedVid` becomes `PSA.51.1`!
# And it scrolls to `PSA.51.1`.
# But `PSA.51.1` in Hebrew is the title ("To the choirmaster. A Psalm of David...").
# The user wants KJV `PSA.51.1` ("Have mercy upon me, O God...").
# Which is `PSA.51.3` in Hebrew!

# SO WHY DID IT GO TO VERSE 1?
# IT DIDN'T "GO TO VERSE 1 NO MATTER WHAT". IT WENT TO HEBREW VERSE 1 (WHICH IS KJV VERSE 1 TITLE OR WHATEVER).
# WAIT. "always goes to verse one no matter what verse I choose :("
# If the user chose "5", `targetScrollVerse` = `PSA.51.5`.
# `sortedVids.includes("PSA.51.5")` is TRUE.
# `resolvedVid` = `PSA.51.5`.
# It scrolls to `PSA.51.5`.
# Why did the user say it "always goes to verse one"?

# What if `sortedVids.length > 0` but `targetScrollVerse` is wiped out prematurely?
# `setTargetScrollVerse(null);`
# When does `targetScrollVerse` get set?
# In `onSelect(book, chapter, verse)`:
# `setTargetScrollVerse(b.c.v)`
# Then `setSelectedBook(b)` and `setSelectedChapter(c)`.
# This triggers `loadContent`.
# `loadContent` sets `setVerseMap(null)` and `setLoading(true)`.

# Then `useEffect` for Scroll Restoration fires?
# `if (!loading && targetScrollVerse && verseMap && sortedVids.length > 0)`
# It waits until `loading` is false.
# When `loading` is false, it fires.

# Is there another `useEffect` that clears `targetScrollVerse`?
# In `Persistence & URL Sync`:
#       const save = () => {
#           const state = { book: selectedBook, chapter: selectedChapter, verseId: activeVerseId };
#           localStorage.setItem('bible_browser_state', JSON.stringify(state));

# No, that doesn't clear `targetScrollVerse`.
# What about `activeVerseId` initialization?
# `const [activeVerseId, setActiveVerseId] = useState(initialState.verseId || null);`

# What if `IntersectionObserver` fires on page load before `Scroll Restoration`?
# `loading` becomes false. DOM updates.
# `IntersectionObserver` sees the top of the page (Verse 1).
# `setActiveVerseId('GEN.1.1')`.
# Then `Scroll Restoration` fires.
# `Scroll Restoration` calls `el.scrollIntoView()`.
# Then `IntersectionObserver` sees it scroll.
# It should work.

# Wait. Look at the `useEffect` dependencies:
# `}, [loading, targetScrollVerse, verseMap, sortedVids, focalTranslation]);`
# If `focalTranslation` changes, it re-runs.

# Why would it always go to Verse 1?
# Let's comment out `sortedVids.includes(targetScrollVerse)` and FORCE the `displayVid` lookup.
# If we force `displayVid` lookup, we search for `translations[focalTranslation]?.displayVid === targetScrollVerse`.
# If `targetScrollVerse` is `PSA.51.1`, and `translations['kjv'].displayVid` is `PSA.51.1`, it will find the Hebrew verse `PSA.51.3`.
# And then scroll to `PSA.51.3`!
# This is what the user wanted!

# Because `sortedVids.includes(targetScrollVerse)` was TRUE for `PSA.51.1`, it short-circuited the KJV lookup, and just scrolled to the Hebrew `PSA.51.1` (which the user sees as Verse 1).
# And if the user chose "PSA.51.2"?
# `sortedVids.includes(PSA.51.2)` is TRUE.
# It scrolled to Hebrew `PSA.51.2` (which might ALSO be seen as Verse 1 or Title by the KJV user).
# Wait, "always goes to verse one no matter what verse I choose".
# If they chose Verse 5, it goes to Hebrew Verse 5. Hebrew Verse 5 is KJV Verse 3.
# It shouldn't ALWAYS go to Verse 1.
# Unless...

# Let's remove the `sortedVids.includes` exact match bypass, or at least put it AFTER the KJV lookup!
