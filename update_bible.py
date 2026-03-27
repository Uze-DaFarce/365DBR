import sys

filepath = 'apps/365DBR/bible.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# I will just replace the - 145 with - 20
new_content = content.replace('targetY = absoluteTop - 145;', 'targetY = absoluteTop - 20;')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated bible.html to use - 20")
