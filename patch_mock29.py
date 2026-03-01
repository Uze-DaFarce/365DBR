with open('bible.html', 'r') as f:
    text = f.read()

# I am an idiot! I didn't actually read `BibleBrowseDialog` correctly from `bible.html`.
idx = text.find('const BibleBrowseDialog')
end_idx = text.find('};', idx)
print(text[idx:idx+1000])
