const fs = require('fs');
let content = fs.readFileSync('apps/HeIsRisen/m/main.js', 'utf8');

const eggZamIdx = content.indexOf("class EggZamRoom");
const endStartIdx = content.indexOf("this.currentEgg = null;", eggZamIdx);
const reloadIdx = content.indexOf("window.location.reload();", endStartIdx);
const returnIdx = content.indexOf("return;", reloadIdx);
const endEndIdx = returnIdx + 7;

const newEnd = `this.currentEgg = null;
        if (this.noEggsText) this.noEggsText.destroy();

        if (foundEggs.length === TOTAL_EGGS) {
            this.noEggsText = this.add.text(centerX, centerY + 350 * this.gameScale, "Congratulations Super Sleuth!\\nYou found and categorized all 60 eggs!", {
                fontSize: \`\${40 * this.gameScale}px\`,
                fill: '#ffff00',
                fontStyle: 'bold',
                fontFamily: 'Comic Sans MS',
                stroke: '#000',
                strokeThickness: 6 * this.gameScale,
                align: 'center',
                wordWrap: { width: 800 * this.gameScale, useAdvancedWrap: true }
            }).setOrigin(0.5).setDepth(100);

            this.time.delayedCall(3000, () => {
                this.scene.start('EndgameScene');
            });
        } else {
            this.noEggsText = this.add.text(centerX, centerY + 400 * this.gameScale, "All eggs have been categorized!", {
                fontSize: \`\${32 * this.gameScale}px\`,
                fill: '#000',
                fontStyle: 'bold',
                fontFamily: 'Comic Sans MS',
                stroke: '#fff',
                strokeThickness: 3 * this.gameScale,
                wordWrap: { width: 500 * this.gameScale, useAdvancedWrap: true }
            }).setOrigin(0.5, 0.5);
        }

        return;`;

content = content.substring(0, endStartIdx) + newEnd + content.substring(endEndIdx);
fs.writeFileSync('apps/HeIsRisen/m/main.js', content);
