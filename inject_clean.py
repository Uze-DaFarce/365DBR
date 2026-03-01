import re

with open("bible.html", "r") as f:
    html = f.read()

# 1. Insert BibleBrowseDialog before function App()
with open("browse_dialog.jsx", "r") as f:
    dialog_jsx = f.read()

if "function BibleBrowseDialog" not in html:
    html = html.replace("function App() {", dialog_jsx + "\nfunction App() {\n")

# 2. Add isBrowseOpen state
if "const [isBrowseOpen, setIsBrowseOpen] = useState(false);" not in html:
    html = html.replace("const [error, setError] = useState(null);", "const [error, setError] = useState(null);\n  const [isBrowseOpen, setIsBrowseOpen] = useState(false);")

# 3. Insert the <BibleBrowseDialog /> component call inside App() render method.
dialog_call = """
      <BibleBrowseDialog
        isOpen={isBrowseOpen}
        onClose={() => setIsBrowseOpen(false)}
        index={index}
        availableBooks={availableBooks}
        onSelect={(b, c, v) => {
            setSelectedBook(b);
            setSelectedChapter(c);
            setTargetScrollVerse(`${b}.${c}.${v}`);
        }}
      />
"""

if "<BibleBrowseDialog" not in html:
    html = html.replace('<main id="main-content"', dialog_call + '\n      <main id="main-content"')

with open("bible.html", "w") as f:
    f.write(html)

print("Injected successfully.")
