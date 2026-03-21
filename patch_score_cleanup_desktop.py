import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Desktop has slightly different spacing or code, let's find it.

    # We want to replace:
    #       const foundEggsCount = foundEggs.length;
    #       if (this.scoreText) {
    #           this.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
    #       }
    #
    # With:
    #       const foundEggsCount = foundEggs.length;

    pattern = r"const foundEggsCount = foundEggs\.length;\s+if \(this\.scoreText\) \{\s+this\.scoreText\.setText\(`\$\{foundEggsCount\}/\$?\{?TOTAL_EGGS\}?`\);\s+\}"
    replacement = "const foundEggsCount = foundEggs.length;"

    content = re.sub(pattern, replacement, content)

    with open(filepath, 'w') as f:
        f.write(content)

fix_file('apps/HeIsRisen/main.js')

print("Cleaned up duplicate score text setting on desktop.")
