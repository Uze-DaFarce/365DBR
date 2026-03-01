with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('Right Page Bucket')
print(text[idx-100:idx+2500])
