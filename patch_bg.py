import re

with open('./apps/HeIsRisen/m/main.js', 'r') as f:
    content = f.read()

# Replace specifically the backgroundColor line in the config dictionary ONLY
content = re.sub(r"  scene: \[MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene\],\n  backgroundColor: '#000000',\n};", "  scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene]\n};", content)

with open('./apps/HeIsRisen/m/main.js', 'w') as f:
    f.write(content)
