import re

with open('./apps/HeIsRisen/m/main.js', 'r') as f:
    content = f.read()

# Replace backgroundColor back into config properly
content = re.sub(r"scene: \[MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene\],\n  backgroundColor: '#000000',\n  };", "scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene],\n  backgroundColor: '#000000',\n};", content)

with open('./apps/HeIsRisen/m/main.js', 'w') as f:
    f.write(content)
