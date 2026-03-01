with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('Left Page Bucket')
print(text[idx-100:idx+2500])
