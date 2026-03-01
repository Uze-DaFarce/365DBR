import re
with open('bible.html', 'r') as f:
    content = f.read()

# Find "Scroll Restoration"
idx = content.find('// Scroll Restoration')
if idx != -1:
    end_idx = content.find('// Scroll Sync (IntersectionObserver)', idx)
    print(content[idx:end_idx])
else:
    print("Not found")
