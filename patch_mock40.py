with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('function BibleBrowseDialog')
idx = text.find('Book / Chapter / Verse Views', idx)
print(text[idx-100:idx+2500])
