import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # We need to remove the block:
    #      if (this.scoreText) {
    #        this.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
    #      }
    # But leave `const foundEggsCount = foundEggs.length;` and `saveGameState(this.registry);`

    # Let's target it carefully in SectionHunt's collectEgg

    pattern_desktop = r"const foundEggsCount = foundEggs\.length;\s+if \(this\.scoreText\) \{\s+this\.scoreText\.setText\(`\$\{foundEggsCount\}/\$?\{?TOTAL_EGGS\}?`\);\s+\}\s+saveGameState\(this\.registry\);"
    replacement = "const foundEggsCount = foundEggs.length;\n      \n      saveGameState(this.registry);"

    content = re.sub(pattern_desktop, replacement, content)

    with open(filepath, 'w') as f:
        f.write(content)

fix_file('apps/HeIsRisen/main.js')
fix_file('apps/HeIsRisen/m/main.js')

print("Cleaned up duplicate score text setting.")
