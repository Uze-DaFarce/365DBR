with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find("step === 'testament'")
if idx != -1:
    idx2 = text.find('return (', idx)
    print(text[idx2:idx2+2000])
