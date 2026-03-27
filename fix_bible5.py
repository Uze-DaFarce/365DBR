import re

filepath = 'apps/365DBR/bible.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to dispatch a custom event to lock the state when we programmatic scroll in the tryScroll block
# and in navigateVerse and handleVerseClick.
# This prevents IntersectionObserver from overriding activeVerseId while the user is jumping to a specific verse.

new_content = content.replace(
    "window.scrollTo({ top: targetY, behavior: 'smooth' });",
    "window.dispatchEvent(new CustomEvent('scrolllock'));\n              window.scrollTo({ top: targetY, behavior: 'smooth' });"
)

# And for tryScroll final jump
new_content = new_content.replace(
    "window.scrollTo({ top: targetY, behavior: 'auto' });",
    "window.dispatchEvent(new CustomEvent('scrolllock'));\n                      window.scrollTo({ top: targetY, behavior: 'auto' });"
)

# Now, we need to modify the IntersectionObserver block to respect the lock.
# We will add a simple boolean lock and an event listener to set it.
observer_block = """  // Observer for Scroll Tracking
  useEffect(() => {
    let scrollLockTimer = null;
    let isLocked = false;

    const handleLock = () => {
        isLocked = true;
        if (scrollLockTimer) clearTimeout(scrollLockTimer);
        scrollLockTimer = setTimeout(() => { isLocked = false; }, 800);
    };
    window.addEventListener('scrolllock', handleLock);

    const handleVerseClickedEvent = (e) => {
        setTargetScrollVerse(e.detail.vid);
    };
    window.addEventListener('verseclicked', handleVerseClickedEvent);

    if (playbackStatus === 'playing' || loading || !verseMap || groupedVids.length === 0 || targetScrollVerse) {
        window.removeEventListener('scrolllock', handleLock);
        return () => window.removeEventListener('verseclicked', handleVerseClickedEvent);
    }
    const observer = new IntersectionObserver((entries) => {
      if (isLocked) return; // Prevent observer from stealing focus during programmatic scrolls
"""

old_observer_block = """  // Observer for Scroll Tracking
  useEffect(() => {
    const handleVerseClickedEvent = (e) => {
        setTargetScrollVerse(e.detail.vid);
    };
    window.addEventListener('verseclicked', handleVerseClickedEvent);

    if (playbackStatus === 'playing' || loading || !verseMap || groupedVids.length === 0 || targetScrollVerse) {
        return () => window.removeEventListener('verseclicked', handleVerseClickedEvent);
    }
    const observer = new IntersectionObserver((entries) => {"""

new_content = new_content.replace(old_observer_block, observer_block)

cleanup_block = """    return () => {
        window.removeEventListener('scrolllock', handleLock);
        if (scrollLockTimer) clearTimeout(scrollLockTimer);
        window.removeEventListener('verseclicked', handleVerseClickedEvent);
        observer.disconnect();
        window.removeEventListener('scroll', handleScroll);
    };"""

old_cleanup_block = """    return () => {
        window.removeEventListener('verseclicked', handleVerseClickedEvent);
        observer.disconnect();
        window.removeEventListener('scroll', handleScroll);
    };"""

new_content = new_content.replace(old_cleanup_block, cleanup_block)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated bible.html to use scrolllock to fix the blue highlighting issue.")
