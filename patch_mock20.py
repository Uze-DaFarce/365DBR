import re
with open('bible.html', 'r') as f:
    content = f.read()

# Let's find "Scroll Restoration"
idx = content.find('// Scroll Restoration')
if idx != -1:
    end_idx = content.find('// Dynamic Slots', idx)
    print(content[idx:end_idx])
else:
    print("Not found")
