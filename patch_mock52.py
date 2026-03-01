# Let's extract the exact DOM for the "Split Content: Left Page / Right Page Container"
with open('bible.html', 'r') as f:
    text = f.read()

idx_start = text.find('{/* Split Content: Left Page / Right Page Container */}')
idx_end = text.find('</div>\n\n                        </div>\n                    )}', idx_start)
print(text[idx_start:idx_end+6])
