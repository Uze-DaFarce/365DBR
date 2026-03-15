const fs = require('fs');
let content = fs.readFileSync('apps/HeIsRisen/m/main.js', 'utf8');
content = content.replace("scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene],", "scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, EndgameScene, MusicScene, UIScene],");
fs.writeFileSync('apps/HeIsRisen/m/main.js', content);
