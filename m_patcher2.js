const fs = require('fs');
let content = fs.readFileSync('apps/HeIsRisen/m/main.js', 'utf8');

// 1. Scene array
content = content.replace(
    "scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene],",
    "scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, EndgameScene, MusicScene, UIScene],"
);

// 2. showExplanation
const showIndex = content.indexOf("const showExplanation = (isCorrect, guessText) => {");
if (showIndex !== -1) {
    const errorIndex = content.indexOf("this.sound.play('error');", showIndex);
    const endIndex = content.indexOf("}", errorIndex) + 1; // get the closing brace

    const showOldText = content.substring(showIndex, endIndex);

    // Create replacement while preserving leading indentation of the first line
    const match = content.substring(0, showIndex).match(/\n([ \t]*)$/);
    const indent = match ? match[1] : "    ";

    const newShowText = `const showExplanation = (isCorrect, guessText) => {
        if (this.currentEgg.attempts === undefined) {
            this.currentEgg.attempts = 0;
        }
        this.currentEgg.attempts++;

        if (isCorrect) {
            this.sound.play('success');
            const correctCount = this.registry.get('correctCategorizations') + 1;
            this.registry.set('correctCategorizations', correctCount);
            this.correctText.setText(\`Correct: \${correctCount}\`);
            this.currentEgg.categorized = true;

            if (this.currentEgg.attempts === 1) {
                this.currentEgg.firstTryCorrect = true;
            } else {
                this.currentEgg.firstTryCorrect = false;
            }

            const foundEggs = this.registry.get('foundEggs');
            const index = foundEggs.findIndex(e => e.eggId === this.currentEgg.eggId);
            if (index !== -1) {
                foundEggs[index] = this.currentEgg;
                this.registry.set('foundEggs', foundEggs);
            }
        } else {
            this.sound.play('error');
        }`;

    // Because the old text ends with '}' and newShowText ends with '}', they match.
    content = content.substring(0, showIndex) + newShowText + content.substring(endIndex);
    console.log("Patched showExplanation");
}

// 3. End logic
const eggZamIndex = content.indexOf("class EggZamRoom");
const endStartIndex = content.indexOf("this.currentEgg = null;", eggZamIndex);

if (endStartIndex !== -1) {
    const endEndIndex = content.indexOf("return;", endStartIndex) + 7;

    const endNewText = `this.currentEgg = null;
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

    content = content.substring(0, endStartIndex) + endNewText + content.substring(endEndIndex);
    console.log("Patched End logic");
}

// 4. EndgameScene class insertion
const endgameClassCode = `class EndgameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'EndgameScene' });
    }

    create() {
        this.input.setDefaultCursor('none');
        const width = this.scale.width;
        const height = this.scale.height;
        const scaleX = width / 720;
        const scaleY = height / 1280;
        const scale = Math.min(scaleX, scaleY);

        const offsetX = (width - 720 * scale) / 2;
        const offsetY = (height - 1280 * scale) / 2;

        this.add.rectangle(width/2, height/2, width, height, 0x1a0f00).setDepth(0);

        const particles = this.add.particles(0, 0, 'egg-1', {
            x: { min: 0, max: width },
            y: { min: -100, max: 0 },
            speedY: { min: 100, max: 300 },
            speedX: { min: -50, max: 50 },
            scale: { start: 0.5 * scale, end: 0 },
            alpha: { start: 1, end: 0 },
            rotate: { min: 0, max: 360 },
            lifespan: 5000,
            frequency: 100,
            blendMode: 'ADD'
        }).setDepth(1);

        this.time.addEvent({
            delay: 500,
            loop: true,
            callback: () => {
                const randomEgg = Phaser.Math.Between(1, TOTAL_EGGS);
                particles.setTexture(\`egg-\${randomEgg}\`);
            }
        });

        const panelWidth = 600 * scale;
        const panelHeight = 850 * scale;
        const panel = this.add.graphics();
        panel.fillStyle(0xfff8dc, 0.95);
        panel.fillRoundedRect(offsetX + (720*scale - panelWidth)/2, offsetY + (1280*scale - panelHeight)/2 - 50*scale, panelWidth, panelHeight, 30 * scale);
        panel.lineStyle(10 * scale, 0x8b4513, 1);
        panel.strokeRoundedRect(offsetX + (720*scale - panelWidth)/2, offsetY + (1280*scale - panelHeight)/2 - 50*scale, panelWidth, panelHeight, 30 * scale);
        panel.setDepth(2);

        const foundEggs = this.registry.get('foundEggs') || [];
        const totalFound = foundEggs.length;

        let eggSelentFound = 0;
        let eggSelentFirstTry = 0;
        let eggstraStinkyFound = 0;
        let eggstraStinkyFirstTry = 0;

        foundEggs.forEach(egg => {
            if (egg.categorized) {
                if (egg.symbolData && egg.symbolData.category === 'Christian') {
                    eggSelentFound++;
                    if (egg.firstTryCorrect) eggSelentFirstTry++;
                } else if (egg.symbolData && egg.symbolData.category === 'Pagan') {
                    eggstraStinkyFound++;
                    if (egg.firstTryCorrect) eggstraStinkyFirstTry++;
                }
            }
        });

        const totalScore = (totalFound * 10) +
                           ((eggSelentFound + eggstraStinkyFound) * 10) +
                           ((eggSelentFirstTry + eggstraStinkyFirstTry) * 10);

        this.add.text(width / 2, offsetY + 230 * scale, "Final Score", {
            fontSize: \`\${64 * scale}px\`,
            fill: '#8b4513',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#fff',
            strokeThickness: 8 * scale
        }).setOrigin(0.5).setDepth(3);

        this.add.text(width / 2, offsetY + 330 * scale, \`\${totalScore} Points!\`, {
            fontSize: \`\${80 * scale}px\`,
            fill: '#d4af37',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#000',
            strokeThickness: 10 * scale
        }).setOrigin(0.5).setDepth(3);

        this.add.text(width / 2, offsetY + 480 * scale, "Egg-Selent (Holy):\\n" +
                                                                    \`Found: \${eggSelentFound}/30\\n\` +
                                                                    \`Perfect Sort: \${eggSelentFirstTry}\`, {
            fontSize: \`\${36 * scale}px\`,
            fill: '#008000',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            align: 'center',
            stroke: '#fff',
            strokeThickness: 4 * scale
        }).setOrigin(0.5).setDepth(3);

        this.add.text(width / 2, offsetY + 680 * scale, "Egg-stra Stinky\\n(Worldly):\\n" +
                                                                    \`Found: \${eggstraStinkyFound}/30\\n\` +
                                                                    \`Perfect Sort: \${eggstraStinkyFirstTry}\`, {
            fontSize: \`\${36 * scale}px\`,
            fill: '#d32f2f',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            align: 'center',
            stroke: '#fff',
            strokeThickness: 4 * scale
        }).setOrigin(0.5).setDepth(3);

        const playBtnContainer = this.add.container(width / 2, offsetY + 900 * scale).setDepth(100);

        const playBtnWidth = 400 * scale;
        const playBtnHeight = 100 * scale;

        const playBtnBg = this.add.graphics();
        playBtnBg.fillStyle(0xffff00, 1);
        playBtnBg.lineStyle(6 * scale, 0x000000, 1);
        playBtnBg.fillRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 20 * scale);
        playBtnBg.strokeRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 20 * scale);

        const playBtnText = this.add.text(0, 0, 'PLAY AGAIN', {
            fontSize: \`\${48 * scale}px\`,
            fill: '#000',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5, 0.5);

        playBtnContainer.add([playBtnBg, playBtnText]);

        playBtnContainer.setSize(playBtnWidth, playBtnHeight);
        playBtnContainer.setInteractive(new Phaser.Geom.Rectangle(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight), Phaser.Geom.Rectangle.Contains);

        const resetAndPlay = () => {
            const musicScene = this.scene.get('MusicScene');
            if (musicScene) musicScene.playSFX('menu-click');

            this.registry.set('foundEggs', []);
            this.registry.set('stampedSections', []);
            this.registry.set('correctCategorizations', 0);

            this.registry.remove('eggData');

            const mapSections = this.cache.json.get('map_sections');
            const symbolsData = this.cache.json.get('symbols');

            if (mapSections && symbolsData && symbolsData.symbols) {
                const eggCounts = [];
                let remainingEggs = TOTAL_EGGS;
                const numSections = mapSections.length;

                for (let i = 0; i < numSections - 1; i++) {
                    const maxPossible = remainingEggs - ((numSections - 1 - i) * 3);
                    const minPossible = remainingEggs - ((numSections - 1 - i) * 8);
                    const max = Math.min(8, maxPossible);
                    const min = Math.max(3, minPossible);
                    const count = Phaser.Math.Between(min, max);
                    eggCounts.push(count);
                    remainingEggs -= count;
                }
                eggCounts.push(remainingEggs);

                const eggs = Phaser.Utils.Array.Shuffle(Array.from({ length: TOTAL_EGGS }, (_, i) => i + 1));
                const sections = mapSections.map(section => ({ name: section.name, eggs: [] }));

                let eggIndex = 0;
                const shuffledSymbols = Phaser.Utils.Array.Shuffle([...symbolsData.symbols]);
                const eggData = [];

                sections.forEach((section, index) => {
                  section.eggs = eggs.slice(eggIndex, eggIndex + eggCounts[index]);
                  eggIndex += eggCounts[index];

                  section.eggs.forEach(eggId => {
                      const originalX = Phaser.Math.Between(100, 1180);
                      const originalY = Phaser.Math.Between(100, 2060);

                      eggData.push({
                          eggId: eggId,
                          section: section.name,
                          x: originalX,
                          y: originalY,
                          symbol: shuffledSymbols[eggId - 1] || null,
                          collected: false
                      });
                  });
                });

                this.registry.set('sections', sections);
                this.registry.set('eggData', eggData);
            }

            this.scene.start('MapScene');
        };

        playBtnContainer.on('pointerdown', resetAndPlay);

        this.scale.on('resize', () => {
            this.scene.restart();
        });
    }
}\n\n`;

content = content.replace("class EggZamRoom extends Phaser.Scene {", endgameClassCode + "class EggZamRoom extends Phaser.Scene {");
console.log("Patched EndgameScene");

fs.writeFileSync('apps/HeIsRisen/m/main.js', content);
