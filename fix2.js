const fs = require('fs');
let content = fs.readFileSync('apps/HeIsRisen/m/main.js', 'utf8');
const endgameClassCode = `class EndgameScene extends Phaser.Scene { constructor() { super({ key: 'EndgameScene' }); } create() { } }\n`;
content = content.replace("class EggZamRoom extends Phaser.Scene {", endgameClassCode + "class EggZamRoom extends Phaser.Scene {");
fs.writeFileSync('apps/HeIsRisen/m/main.js', content);
