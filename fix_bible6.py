import sys

filepath = 'apps/365DBR/bible.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure we force activeVerseId directly when tryScroll lands on the final element!
# Inside tryScroll final jump
target = """// Final scroll using smooth behavior to ensure it lands exactly where intended
                          window.dispatchEvent(new CustomEvent('scrolllock'));
              window.scrollTo({ top: targetY, behavior: 'smooth' });
                          setTargetScrollVerse(null);"""

replacement = """// Final scroll using smooth behavior to ensure it lands exactly where intended
                          window.dispatchEvent(new CustomEvent('scrolllock'));
                          window.scrollTo({ top: targetY, behavior: 'smooth' });
                          setActiveVerseId(resolvedVid);
                          setTargetScrollVerse(null);"""

new_content = content.replace(target, replacement)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Forced setActiveVerseId")
