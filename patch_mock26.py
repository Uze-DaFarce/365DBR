# Okay! The `VerseGroup` component renders an outermost `div` with `id={verse-${vid}}`
# BUT `vid` is NOT KJV/LSV `displayVid`!
# `vid` is the ORIGINAL vid (e.g. `GEN.1.1`).

# Look at the Scroll Restoration effect again.
#
#          for (const vid of sortedVids) {
#              const translations = verseMap[vid];
#              if (!translations) continue;
#
#              // Check focal first
#              if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {
#                  resolvedVid = vid;
#                  break;
#              }
#              ...
#          }
#
# Okay, `resolvedVid` is the ORIGINAL vid.
# Then `const el = document.getElementById(verse-${resolvedVid});`
# So `document.getElementById` IS querying for the ORIGINAL vid.
# This should match `VerseGroup`'s `id={verse-${vid}}`.

# BUT wait! React hooks (useEffect) run AFTER the DOM is updated.
# In `App`:
#        {!selectedBook ? ( ... )
#        : loading ? ( <Loader /> )
#        : error ? ( ... )
#        : ( groupedVids.map(group => ( <VerseGroup ... /> )) )
#
# If `loading` goes from `true` to `false`, React schedules a render.
# During that render, `App` returns the `VerseGroup` list instead of `Loader`.
# Then React updates the DOM.
# THEN React calls the `useEffect` callbacks.
# So by the time `Scroll Restoration` effect runs, `loading` is `false` AND the `VerseGroup` elements SHOULD be in the DOM.

# Wait, is `loading` a dependency of `Scroll Restoration`? YES.
# Is `targetScrollVerse` a dependency? YES.
# Does `loading` become `false` BEFORE the DOM updates? No, `loading` state update triggers the render, render creates VDOM, React commits VDOM to DOM, then fires effects.

# SO WHY IS `document.getElementById` RETURNING NULL?
# Let's verify that the effect actually runs and what it sees by inspecting Playwright logs.
# Actually I don't have Playwright logs of this.
