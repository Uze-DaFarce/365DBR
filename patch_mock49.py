with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('const leftBooks =')
print(text[idx-100:idx+500])
