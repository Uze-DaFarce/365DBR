with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('const splitArray')
print(text[idx-100:idx+500])
