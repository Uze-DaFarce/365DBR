import re

with open("bible.html", "r") as f:
    html = f.read()

# Locate the end of the initIndex logic where we decide whether to show the dialog
# Currently:
#                 if (urlBook && urlChapter && newIndex[urlBook] && newIndex[urlBook][urlChapter]) {
#                     setSelectedBook(urlBook);
#                     setSelectedChapter(urlChapter);
#                     if (urlVerse) setTargetScrollVerse(`${urlBook}.${urlChapter}.${urlVerse}`);
#                 } else {
#                     try {
#                         const saved = localStorage.getItem('bible_browser_state');
#                         if (saved) {
#                             const state = JSON.parse(saved);
#                             if (state.book && state.chapter && newIndex[state.book] && newIndex[state.book][state.chapter]) {
#                                 setSelectedBook(state.book);
#                                 setSelectedChapter(state.chapter);
#                                 if (state.verseId) setTargetScrollVerse(state.verseId);
#                             }
#                         }
#                     } catch (e) { console.warn("Failed to load state", e); }
#                 }

search_block = """                if (urlBook && urlChapter && newIndex[urlBook] && newIndex[urlBook][urlChapter]) {
                    setSelectedBook(urlBook);
                    setSelectedChapter(urlChapter);
                    if (urlVerse) setTargetScrollVerse(`${urlBook}.${urlChapter}.${urlVerse}`);
                } else {
                    try {
                        const saved = localStorage.getItem('bible_browser_state');
                        if (saved) {
                            const state = JSON.parse(saved);
                            if (state.book && state.chapter && newIndex[state.book] && newIndex[state.book][state.chapter]) {
                                setSelectedBook(state.book);
                                setSelectedChapter(state.chapter);
                                if (state.verseId) setTargetScrollVerse(state.verseId);
                            } else {
                                setIsBrowseOpen(true);
                            }
                        } else {
                            setIsBrowseOpen(true);
                        }
                    } catch (e) { console.warn("Failed to load state", e); setIsBrowseOpen(true); }
                }"""

# Actually, the original block looks like:
original_block = """                if (urlBook && urlChapter && newIndex[urlBook] && newIndex[urlBook][urlChapter]) {
                    setSelectedBook(urlBook);
                    setSelectedChapter(urlChapter);
                    if (urlVerse) setTargetScrollVerse(`${urlBook}.${urlChapter}.${urlVerse}`);
                } else {
                    try {
                        const saved = localStorage.getItem('bible_browser_state');
                        if (saved) {
                            const state = JSON.parse(saved);
                            if (state.book && state.chapter && newIndex[state.book] && newIndex[state.book][state.chapter]) {
                                setSelectedBook(state.book);
                                setSelectedChapter(state.chapter);
                                if (state.verseId) setTargetScrollVerse(state.verseId);
                            }
                        }
                    } catch (e) { console.warn("Failed to load state", e); }
                }"""

if original_block in html:
    html = html.replace(original_block, search_block)
    with open("bible.html", "w") as f:
        f.write(html)
    print("Patched init logic successfully.")
else:
    print("Could not find original block.")
