const fs = require('fs');

let content = fs.readFileSync('apps/HeIsRisen/main.js', 'utf8');

// 1. Scene array
content = content.replace(
    "scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene, CursorScene],",
    "scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, EndgameScene, MusicScene, UIScene, CursorScene],"
);

// 2. showExplanation logic
const oldShow = `    const showExplanation = (isCorrect, guessText) => {
        if (isCorrect) {
            this.sound.play('success');
            const correctCount = this.registry.get('correctCategorizations') + 1;
            this.registry.set('correctCategorizations', correctCount);
            this.correctText.setText(\`Correct: \${correctCount}\`);
            this.currentEgg.categorized = true;
        } else {
            this.sound.play('error');
        }`;

const newShow = `    const showExplanation = (isCorrect, guessText) => {
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

content = content.replace(oldShow, newShow);

// 3. End logic
const oldEnd = `        this.currentEgg = null;
        if (this.noEggsText) this.noEggsText.destroy();
        this.noEggsText = this.add.text(offsetX + 420 * scale, offsetY + 220 * scale, "All eggs have been categorized!", {
          fontSize: \`\${28 * scale}px\`,
          fill: '#000',
          fontStyle: 'bold',
          fontFamily: 'Comic Sans MS',
          stroke: '#fff',
          strokeThickness: 3 * scale,
          wordWrap: { width: 480 * scale, useAdvancedWrap: true }
        }).setOrigin(0, 0);

        if (foundEggs.length === TOTAL_EGGS) {
          // PLAY AGAIN Button
          const playBtnContainer = this.add.container(offsetX + 420 * scale, offsetY + 300 * scale).setDepth(100);

          const playBtnWidth = 250 * scale;
          const playBtnHeight = 60 * scale;

          const playBtnBg = this.add.graphics();
          playBtnBg.fillStyle(0xffff00, 1);
          playBtnBg.lineStyle(4 * scale, 0x000000, 1);
          playBtnBg.fillRoundedRect(0, 0, playBtnWidth, playBtnHeight, 15 * scale);
          playBtnBg.strokeRoundedRect(0, 0, playBtnWidth, playBtnHeight, 15 * scale);

          const playBtnText = this.add.text(playBtnWidth / 2, playBtnHeight / 2, 'PLAY AGAIN', {
              fontSize: \`\${28 * scale}px\`,
              fill: '#000',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5, 0.5);

          playBtnContainer.add([playBtnBg, playBtnText]);

          playBtnContainer.setSize(playBtnWidth, playBtnHeight);
          playBtnContainer.setInteractive(new Phaser.Geom.Rectangle(0, 0, playBtnWidth, playBtnHeight), Phaser.Geom.Rectangle.Contains);

          playBtnContainer.on('pointerover', () => {
              this.input.setDefaultCursor('pointer');
              playBtnContainer.setScale(1.05);
          });

          playBtnContainer.on('pointerout', () => {
              this.input.setDefaultCursor('default');
              playBtnContainer.setScale(1);
          });

          const triggerReload = () => {
              this.input.setDefaultCursor('default');
              window.location.reload();
          };

          playBtnContainer.on('pointerdown', triggerReload);
          this.input.keyboard.once('keydown-SPACE', triggerReload);
          this.input.keyboard.once('keydown-ENTER', triggerReload);
        }

        return;`;

const newEnd = `        this.currentEgg = null;
        if (this.noEggsText) this.noEggsText.destroy();

        if (foundEggs.length === TOTAL_EGGS) {
            this.noEggsText = this.add.text(offsetX + 640 * scale, offsetY + 250 * scale, "Congratulations Super Sleuth!\\nYou found and categorized all 60 eggs!", {
                fontSize: \`\${40 * scale}px\`,
                fill: '#ffff00',
                fontStyle: 'bold',
                fontFamily: 'Comic Sans MS',
                stroke: '#000',
                strokeThickness: 6 * scale,
                align: 'center',
                wordWrap: { width: 800 * scale, useAdvancedWrap: true }
            }).setOrigin(0.5).setDepth(100);

            this.time.delayedCall(3000, () => {
                this.scene.start('EndgameScene');
            });
        } else {
            this.noEggsText = this.add.text(offsetX + 420 * scale, offsetY + 220 * scale, "All eggs have been categorized!", {
                fontSize: \`\${28 * scale}px\`,
                fill: '#000',
                fontStyle: 'bold',
                fontFamily: 'Comic Sans MS',
                stroke: '#fff',
                strokeThickness: 3 * scale,
                wordWrap: { width: 480 * scale, useAdvancedWrap: true }
            }).setOrigin(0, 0);
        }

        return;`;

content = content.replace(oldEnd, newEnd);

// 4. Inject EndgameScene
const endgameCode = `class EndgameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'EndgameScene' });
    }

    create() {
        this.input.setDefaultCursor('none');

        const width = this.scale.width;
        const height = this.scale.height;
        const scaleX = width / 1280;
        const scaleY = height / 720;
        const scale = Math.min(scaleX, scaleY);

        const offsetX = (width - 1280 * scale) / 2;
        const offsetY = (height - 720 * scale) / 2;

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

        const panelWidth = 1000 * scale;
        const panelHeight = 600 * scale;
        const panel = this.add.graphics();
        panel.fillStyle(0xfff8dc, 0.95);
        panel.fillRoundedRect(offsetX + (1280*scale - panelWidth)/2, offsetY + (720*scale - panelHeight)/2, panelWidth, panelHeight, 30 * scale);
        panel.lineStyle(10 * scale, 0x8b4513, 1);
        panel.strokeRoundedRect(offsetX + (1280*scale - panelWidth)/2, offsetY + (720*scale - panelHeight)/2, panelWidth, panelHeight, 30 * scale);
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

        this.add.text(width / 2, offsetY + 120 * scale, "Final Score", {
            fontSize: \`\${64 * scale}px\`,
            fill: '#8b4513',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#fff',
            strokeThickness: 8 * scale
        }).setOrigin(0.5).setDepth(3);

        this.add.text(width / 2, offsetY + 220 * scale, \`\${totalScore} Points!\`, {
            fontSize: \`\${80 * scale}px\`,
            fill: '#d4af37',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#000',
            strokeThickness: 10 * scale
        }).setOrigin(0.5).setDepth(3);

        this.add.text(offsetX + 350 * scale, offsetY + 350 * scale, "Egg-Selent (Holy):\\n" +
                                                                    \`Found: \${eggSelentFound}/30\\n\` +
                                                                    \`Perfect Sort: \${eggSelentFirstTry}\`, {
            fontSize: \`\${32 * scale}px\`,
            fill: '#008000',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            align: 'center',
            stroke: '#fff',
            strokeThickness: 4 * scale
        }).setOrigin(0.5).setDepth(3);

        this.add.text(offsetX + 930 * scale, offsetY + 350 * scale, "Egg-stra Stinky (Worldly):\\n" +
                                                                    \`Found: \${eggstraStinkyFound}/30\\n\` +
                                                                    \`Perfect Sort: \${eggstraStinkyFirstTry}\`, {
            fontSize: \`\${32 * scale}px\`,
            fill: '#d32f2f',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            align: 'center',
            stroke: '#fff',
            strokeThickness: 4 * scale
        }).setOrigin(0.5).setDepth(3);

        const playBtnContainer = this.add.container(width / 2, offsetY + 550 * scale).setDepth(100);

        const playBtnWidth = 350 * scale;
        const playBtnHeight = 80 * scale;

        const playBtnBg = this.add.graphics();
        playBtnBg.fillStyle(0xffff00, 1);
        playBtnBg.lineStyle(6 * scale, 0x000000, 1);
        playBtnBg.fillRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 20 * scale);
        playBtnBg.strokeRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 20 * scale);

        const playBtnText = this.add.text(0, 0, 'PLAY AGAIN', {
            fontSize: \`\${40 * scale}px\`,
            fill: '#000',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5, 0.5);

        playBtnContainer.add([playBtnBg, playBtnText]);

        playBtnContainer.setSize(playBtnWidth, playBtnHeight);
        playBtnContainer.setInteractive(new Phaser.Geom.Rectangle(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight), Phaser.Geom.Rectangle.Contains);

        playBtnContainer.on('pointerover', () => {
            this.input.setDefaultCursor('pointer');
            this.tweens.add({
                targets: playBtnContainer,
                scaleX: 1.1,
                scaleY: 1.1,
                duration: 100,
                ease: 'Sine.easeInOut'
            });
        });

        playBtnContainer.on('pointerout', () => {
            this.input.setDefaultCursor('default');
            this.tweens.add({
                targets: playBtnContainer,
                scaleX: 1.0,
                scaleY: 1.0,
                duration: 100,
                ease: 'Sine.easeInOut'
            });
        });

        const resetAndPlay = () => {
            this.input.setDefaultCursor('default');

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
                      const originalX = Phaser.Math.Between(200, 1270);
                      const originalY = Phaser.Math.Between(100, 710);

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

        this.input.keyboard.once('keydown-SPACE', resetAndPlay);
        this.input.keyboard.once('keydown-ENTER', resetAndPlay);

        this.scale.on('resize', () => {
            this.scene.restart();
        });
    }
}
`;

content = content.replace("class EggZamRoom extends Phaser.Scene {", endgameCode + "\nclass EggZamRoom extends Phaser.Scene {");

fs.writeFileSync('apps/HeIsRisen/main.js', content);
