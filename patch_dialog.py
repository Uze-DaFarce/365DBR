import re

with open("bible.html", "r") as f:
    html = f.read()

with open("browse_dialog.jsx", "r") as f:
    dialog_jsx = f.read()

# Replace everything from "// --- BIBLE BROWSE DIALOG ---" to "// --- END BIBLE BROWSE DIALOG ---"
pattern = re.compile(r"// --- BIBLE BROWSE DIALOG ---.*?// --- END BIBLE BROWSE DIALOG ---", re.DOTALL)
if pattern.search(html):
    html = pattern.sub(dialog_jsx, html)
else:
    print("Pattern not found! Inserting before function App()")
    html = html.replace("function App() {", dialog_jsx + "\nfunction App() {\n")

with open("bible.html", "w") as f:
    f.write(html)
print("Replaced dialog successfully.")
