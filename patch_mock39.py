with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('function BibleBrowseDialog')
idx = text.find('Book Cover Layout (Testament Step)', idx)
print(text[idx-200:idx+2500])
