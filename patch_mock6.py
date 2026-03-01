# In `bible.html`:
# `<div id={`verse-${group[0]}`} className="verse-block group transition-all duration-700 scroll-mt-12 md:scroll-mt-14 opacity-100 cursor-pointer">`
# If `group[0]` is `"GEN.1.2"`, `id="verse-GEN.1.2"`.

# Is it possible that `targetScrollVerse` is NOT `"GEN.1.2"`?
# In `BibleBrowseDialog`:
#        onSelect={(b, c, v) => {
#            setSelectedBook(b);
#            setSelectedChapter(c);
#            setTargetScrollVerse(`${b}.${c}.${v}`);
#        }}
# `b` = "GEN", `c` = 1, `v` = 2.
# `${b}.${c}.${v}` = `"GEN.1.2"`.
# It is EXACTLY `"GEN.1.2"`.

# So `el = document.getElementById("verse-GEN.1.2")` should find it.
# Then `el.scrollIntoView()` is called.
# Why did the user say "always goes to verse one no matter what verse I choose"?

# Let's think about `verseChunks` again.
# `let verses = Array.from({ length: totalVerses }, (_, i) => i + 1);`
# `VERSE_COUNTS[book][chapter - 1] || 1`
# Wait... what if `book` is "GEN" and `chapter` is "1" (as a string)?
# `"1" - 1` is `0`.
# `VERSE_COUNTS["GEN"][0]` is `31`.
# So `totalVerses` is `31`.
# `verses` is `[1, 2, ..., 31]`.

# Wait!
# Let's look at `index[book][chapter]` in `BibleBrowseDialog`.
# Before, it was `let verses = index[book][chapter].map(Number);`
# `index[book][chapter]` contained `["0101"]`.
# So `verses` was `[101]`.
# So `v` was `101`.
# So `targetScrollVerse` was `"GEN.1.101"`.
# `"GEN.1.101"` did not exist in `sortedVids`.
# The `else` block would run.
# `translations[key]?.displayVid === "GEN.1.101"` would NEVER match.
# So `resolvedVid` was null.
# So it NEVER scrolled!
# The user was confused because it loaded the chapter, but stayed at the top (Verse 1), because `resolvedVid` was null!

# Wait! No!
# The bug report "Darn, now it just always goes to verse one no matter what verse I choose :("
# THIS WAS SUBMITTED *AFTER* I FIXED `BibleBrowseDialog`!
# Let's re-read the timeline.
# 1. I submitted "fix: correct verse picker in Bible Browse Dialog". In this PR, I changed `v` from `101` to `1, 2, ...`.
# 2. User accepted it.
# 3. User said: "Awesome, just one last tweak. It is going to the Original Translation verse number, and it needs to go to the KJV and LSV verse number."
# 4. I changed the scroll logic (`Scroll Restoration` effect).
# 5. User said: "Darn, now it just always goes to verse one no matter what verse I choose :("

# THIS MEANS MY SCROLL LOGIC CHANGE BROKE IT!
# Let's look at what I changed.

# Old:
#          if (sortedVids.includes(targetScrollVerse)) {
#              const el = document.getElementById(`verse-${targetScrollVerse}`); ...

# New:
#          if (sortedVids.includes(targetScrollVerse)) {
#              resolvedVid = targetScrollVerse;
#          } else {
#              for (const vid of sortedVids) {
#                 // ...
#              }
#          }
#          if (resolvedVid) { ... }

# Wait! If `targetScrollVerse` is `"GEN.1.2"`, and `sortedVids.includes("GEN.1.2")` is True, `resolvedVid = "GEN.1.2"`.
# It SHOULD work exactly as before for `"GEN.1.2"`.

# Did I introduce a bug in my `useEffect` patch?
# Let's check `patch_auto_dialog.py` that caused the regression.
