with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('function BibleBrowseDialog')
idx = text.find('return (', idx)
print(text[idx:idx+2000])
