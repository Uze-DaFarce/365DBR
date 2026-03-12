# The fix:
# When we are navigating via keyboard or programmatically, we set `targetScrollVerse` in `navigateVerse`.
# If `targetScrollVerse` is set, we are actively scrolling to a specific verse.
# We should suppress the "snap to bottom" behavior of `handleScroll` and `IntersectionObserver` while `targetScrollVerse` is active.

# Let's inspect navigateVerse:
