with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('function BibleBrowseDialog')
idx = text.find('Old Testament', idx)
print(text[idx-200:idx+500])
