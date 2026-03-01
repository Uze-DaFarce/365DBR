with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('Split Content: Left Page')
print(text[idx-100:idx+2500])
