import re

with open("bible_common.py", "r") as f:
    content = f.read()

old_list = '"ACT.8.37", "ACT.15.34", "ACT.24.7", "ACT.28.29",'
new_list = '"ACT.8.37", "ACT.15.34", "ACT.19.41", "ACT.24.7", "ACT.28.29",'

if old_list in content:
    new_content = content.replace(old_list, new_list)
    with open("bible_common.py", "w") as f:
        f.write(new_content)
    print("Replaced list successfully")
else:
    print("Could not find old list")
