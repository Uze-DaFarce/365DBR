with open('bible.html', 'r') as f:
    text = f.read()

idx = text.find('step === \'testament\'')
if idx != -1:
    end = text.find(')', idx)
    print(text[idx:idx+1000])
else:
    print("Not found")
