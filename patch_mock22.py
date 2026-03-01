import re
with open('bible.html', 'r') as f:
    content = f.read()

idx = content.find('const VerseGroup = ({')
if idx != -1:
    end_idx = content.find('};', idx)
    print(content[idx:end_idx+2])
else:
    print("Not found")
