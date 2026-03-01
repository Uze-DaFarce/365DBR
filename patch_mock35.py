import re
with open('bible.html', 'r') as f:
    content = f.read()

# I am replacing the scroll restoration effect in `bible.html`.
# The fix is to add a small retry delay or check with `requestAnimationFrame`
# before resetting `targetScrollVerse` to `null`.
# Or even simpler: if `el` is not found, don't set it to `null`.
# Wait, if we don't set it to `null`, it might infinitely loop if it NEVER renders.
# BUT we only care about it rendering once!
# Actually, the problem was I added `setTargetScrollVerse(null)` to the ELSE block of `if (resolvedVid)`.
# Let's fix it by wrapping the `el.scrollIntoView` in a `setTimeout` to let React commit the DOM completely.

diff = """<<<<<<< SEARCH
          if (resolvedVid) {
              const el = document.getElementById(`verse-${resolvedVid}`);
              if (el) {
                  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  // Also set active immediately to ensure visual highlight
                  setActiveVerseId(resolvedVid);
                  setTargetScrollVerse(null);
              }
          } else {
             // If we can't find it, clear it so we don't infinitely loop
             // (e.g., they requested a verse that doesn't exist in this chapter block)
             setTargetScrollVerse(null);
          }
=======
          if (resolvedVid) {
              // Wait for React to paint the new VerseGroup elements
              setTimeout(() => {
                  const el = document.getElementById(`verse-${resolvedVid}`);
                  if (el) {
                      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                      setActiveVerseId(resolvedVid);
                  }
                  // Clear it after attempting to scroll so we don't re-trigger
                  setTargetScrollVerse(null);
              }, 50);
          } else {
             // If we can't resolve it at all, clear it
             setTargetScrollVerse(null);
          }
>>>>>>> REPLACE"""

with open("diff.txt", "w") as f:
    f.write(diff)
