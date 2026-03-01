import re

with open("bible.html", "r") as f:
    html = f.read()

# I also need to make sure the app automatically opens the dialog if neither URL nor LocalStorage match.
# In the updated code above, I handled: if (saved) ... else setIsBrowseOpen(true); and catch { setIsBrowseOpen(true); }
# But what if 'saved' exists but the keys are invalid? Let's add an explicit effect to watch selectedBook.

# Or better, just add an effect that opens the dialog if !selectedBook and we're not loading.
effect = """
  // Auto-open Dialog if no book is selected
  useEffect(() => {
      if (!loading && !selectedBook) {
          setIsBrowseOpen(true);
      }
  }, [loading, selectedBook]);
"""

# inject this after the `useEffect(() => { ... initIndex() ... }, []);`
html = html.replace("    initIndex();\n  }, []);", "    initIndex();\n  }, []);\n" + effect)

with open("bible.html", "w") as f:
    f.write(html)
print("Added explicit useEffect.")
