/* -= main.js =- */
// Define total eggs as a variable to avoid hardcoding
const TOTAL_EGGS = 60;

function announceToScreenReader(message) {
    const announcer = document.getElementById('sr-announcer');
    if (announcer) {
        announcer.textContent = message;
        // Clear after a short delay to allow re-announcing the same text
        setTimeout(() => {
            if (announcer.textContent === message) {
                announcer.textContent = '';
            }
        }, 1000);
    }
}

class Confirmation extends Phaser.GameObjects.Container {
    constructor(scene, x, y, text, onYes, onNo) {
        super(scene, x, y);
        this.scene = scene;
        this.onYes = onYes;
        this.onNo = onNo;

        const overlay = this.scene.add.rectangle(0, 0, this.scene.cameras.main.width, this.scene.cameras.main.height, 0x000000, 0.7)
            .setOrigin(0)
            .setInteractive();
        this.add(overlay);

        const panel = this.scene.add.rectangle(this.scene.cameras.main.width / 2, this.scene.cameras.main.height / 2, 400, 200, 0x333333)
            .setStrokeStyle(4, 0xffffff);
        this.add(panel);

        const title = this.scene.add.text(this.scene.cameras.main.width / 2, this.scene.cameras.main.height / 2 - 50, text, {
            fontSize: '24px',
            fontFamily: 'Comic Sans MS',
            fill: '#ffffff'
        }).setOrigin(0.5);
        this.add(title);

        const yesBtnContainer = this.scene.add.container(this.scene.cameras.main.width / 2 - 100, this.scene.cameras.main.height / 2 + 50);
        const yesBg = this.scene.add.graphics();
        yesBg.fillStyle(0x00ff00, 1);
        yesBg.fillRoundedRect(-50, -25, 100, 50, 10);
        yesBg.lineStyle(2, 0xffffff, 1);
        yesBg.strokeRoundedRect(-50, -25, 100, 50, 10);
        const yesText = this.scene.add.text(0, 0, 'Yes', {
            fontSize: '20px',
            fontFamily: 'Comic Sans MS',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        yesBtnContainer.add([yesBg, yesText]);
        yesBtnContainer.setSize(100, 50);
        yesBtnContainer.setInteractive();
        addButtonInteraction(this.scene, yesBtnContainer, 'menu-click');
        yesBtnContainer.on('pointerdown', () => {
            if (this.onYes) this.onYes();
            this.destroy();
        });
        this.add(yesBtnContainer);

        const noBtnContainer = this.scene.add.container(this.scene.cameras.main.width / 2 + 100, this.scene.cameras.main.height / 2 + 50);
        const noBg = this.scene.add.graphics();
        noBg.fillStyle(0xff0000, 1);
        noBg.fillRoundedRect(-50, -25, 100, 50, 10);
        noBg.lineStyle(2, 0xffffff, 1);
        noBg.strokeRoundedRect(-50, -25, 100, 50, 10);
        const noText = this.scene.add.text(0, 0, 'No', {
            fontSize: '20px',
            fontFamily: 'Comic Sans MS',
            fill: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        noBtnContainer.add([noBg, noText]);
        noBtnContainer.setSize(100, 50);
        noBtnContainer.setInteractive();
        addButtonInteraction(this.scene, noBtnContainer, 'menu-click');
        noBtnContainer.on('pointerdown', () => {
            if (this.onNo) this.onNo();
            this.destroy();
        });
        this.add(noBtnContainer);

        this.escListener = (e) => {
            if (e.code === 'Escape') {
                if (this.onNo) this.onNo();
                this.destroy();
            }
        };
        this.enterListener = (e) => {
            if (e.code === 'Enter') {
                if (this.onYes) this.onYes();
                this.destroy();
            }
        };
        window.addEventListener('keydown', this.escListener);
        window.addEventListener('keydown', this.enterListener);
        this.on('destroy', () => {
            window.removeEventListener('keydown', this.escListener);
            window.removeEventListener('keydown', this.enterListener);
        });

        this.scene.add.existing(this);
    }
}

function saveGameState(registry) {
    const state = {
        eggData: registry.get('eggData'),
        sections: registry.get('sections'),
        foundEggs: registry.get('foundEggs'),
        stampedSections: registry.get('stampedSections'),
        correctCategorizations: registry.get('correctCategorizations'),
        currentScore: registry.get('currentScore')
    };
    try {
        try { localStorage.setItem('heIsRisenGameState', JSON.stringify(state)); } catch (e) { console.warn('localStorage error', e); }
    } catch (e) {
        console.warn('Failed to save game state to localStorage', e);
    }
}

function initializeGameData(registry, cache, forceNew = false) {
    if (!forceNew) {
        try {
            let savedStateStr = null;
            try { savedStateStr = localStorage.getItem('heIsRisenGameState'); } catch (e) { console.warn('localStorage error', e); }
            if (savedStateStr) {
                let savedState = null;
                try {
                    savedState = JSON.parse(savedStateStr);
                } catch (e) {
                    console.warn('Invalid saved game state in localStorage', e);
                }
                if (savedState && typeof savedState === 'object' && Array.isArray(savedState.eggData) && Array.isArray(savedState.sections)) {
                    registry.set('eggData', savedState.eggData);
                    registry.set('sections', savedState.sections);

                    registry.set('foundEggs', Array.isArray(savedState.foundEggs) ? savedState.foundEggs : []);
                    registry.set('stampedSections', Array.isArray(savedState.stampedSections) ? savedState.stampedSections : []);

                    let loadedCorrect = savedState.correctCategorizations !== null && savedState.correctCategorizations !== '' ? Number(savedState.correctCategorizations) : NaN;
                    if (isNaN(loadedCorrect) || !isFinite(loadedCorrect) || loadedCorrect < 0) loadedCorrect = 0;
                    registry.set('correctCategorizations', loadedCorrect);

                    let loadedScore = savedState.currentScore !== null && savedState.currentScore !== '' ? Number(savedState.currentScore) : NaN;
                    if (isNaN(loadedScore) || !isFinite(loadedScore) || loadedScore < 0) loadedScore = 0;
                    registry.set('currentScore', loadedScore);

                    // Always ensure highScore is loaded/initialized correctly
                    try {
                        let highScoreVal = null;
                        try { highScoreVal = localStorage.getItem('highScore'); } catch (e) { console.warn('localStorage error', e); }
                        let loadedScore = highScoreVal !== null && highScoreVal !== '' ? Number(highScoreVal) : NaN;
                        if (isNaN(loadedScore) || !isFinite(loadedScore) || loadedScore < 0) {
                            loadedScore = 0;
                        }
                        registry.set('highScore', loadedScore);
                    } catch (e) {
                        registry.set('highScore', 0);
                    }

                    // We also need to restore symbols from cache just in case the scene needs them
                    const symbolsData = cache.json.get('symbols');
                    if (symbolsData && symbolsData.symbols && Array.isArray(symbolsData.symbols)) {
                        const validSymbols = symbolsData.symbols.filter(s => {
                            return s && typeof s === 'object' &&
                                   typeof s.filename === 'string' &&
                                   !s.filename.includes('..') &&
                                   /^[a-zA-Z0-9_\-\/]+\.(png|jpg|jpeg)$/i.test(s.filename);
                        });
                        symbolsData.symbols = validSymbols;
                        registry.set('symbols', symbolsData);
                    }
                    return; // Successfully loaded from save
                }
            }
        } catch (e) {
            console.warn('Failed to load saved game state, starting fresh.', e);
        }
    }

    // Normal fresh initialization logic below...
    const symbolsData = cache.json.get('symbols');
    if (symbolsData && symbolsData.symbols && Array.isArray(symbolsData.symbols)) {
        // Pre-validate and inject into registry just as originally done in MainMenu
        const validSymbols = symbolsData.symbols.filter(s => {
            return s && typeof s === 'object' &&
                   typeof s.filename === 'string' &&
                   !s.filename.includes('..') &&
                   /^[a-zA-Z0-9_\-\/]+\.(png|jpg|jpeg)$/i.test(s.filename);
        });
        if (validSymbols.length !== symbolsData.symbols.length) {
            console.warn(`Security: Filtered ${symbolsData.symbols.length - validSymbols.length} invalid symbols.`);
            symbolsData.symbols = validSymbols;
        }
        registry.set('symbols', symbolsData);
    }

    let mapSections = cache.json.get('map_sections');
    if (!Array.isArray(mapSections)) {
        console.warn('Security: map_sections.json failed to load or is invalid. Using empty fallback.');
        mapSections = [];
    }
    if (mapSections && mapSections.length > 0) {
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
        let shuffledSymbols = [];
        if (symbolsData && symbolsData.symbols) {
            shuffledSymbols = Phaser.Utils.Array.Shuffle([...symbolsData.symbols]);
        }

        const eggData = [];
        let eggIndex = 0;

        // Use fallback static bounds if window is not available to prevent crashes during headless reset
        const screenWidth = window.innerWidth || 844;
        const screenHeight = window.innerHeight || 390;
        const scale = Math.min(screenWidth / 1280, screenHeight / 720);

        const sections = mapSections.map((section, index) => {
            const sectionEggs = eggs.slice(eggIndex, eggIndex + eggCounts[index]);
            eggIndex += eggCounts[index];

            sectionEggs.forEach(eggId => {
                // Mobile layout viewport calculation with correct lens margin mappings
                const minX = 50 * scale;
                const maxX = Math.max(minX, screenWidth - (160 * scale));
                const minY = 50 * scale;
                const maxY = Math.max(minY, screenHeight - (200 * scale));

                const x = Phaser.Math.Between(minX, maxX);
                const y = Phaser.Math.Between(minY, maxY);

                eggData.push({
                    eggId: eggId,
                    section: section.name,
                    x: x,
                    y: y,
                    symbol: shuffledSymbols[eggId - 1] || null, // Guarantees strictly uniform unique symbols mapped from 1..60
                    collected: false
                });
            });

            return {
                name: section.name,
                eggs: sectionEggs
            };
        });

        registry.set('sections', sections);
        registry.set('eggData', eggData);
    }

    if (!registry.has('sections')) registry.set('sections', []);
    if (!registry.has('eggData')) registry.set('eggData', []);
    registry.set('foundEggs', []);
    registry.set('stampedSections', []);
    registry.set('correctCategorizations', 0);
    registry.set('currentScore', 0);

    saveGameState(registry);
}

// Define all scene classes first

class MusicScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MusicScene' });

    const getSafeVol = (key) => {
      let val = null;
      try { val = localStorage.getItem(key); } catch (e) { console.warn('localStorage error', e); }
      let parsed = parseFloat(val);
      if (isNaN(parsed) || parsed < 0 || parsed > 1) {
          let backupVal = null;
          try { backupVal = localStorage.getItem(key + '_backup'); } catch (e) { console.warn('localStorage error', e); }
          parsed = parseFloat(backupVal);
          if (isNaN(parsed) || parsed < 0 || parsed > 1) {
              return 0.5;
          }
      }
      return parsed;
    };

    this.musicVolume = getSafeVol('musicVolume');
    this.ambientVolume = getSafeVol('ambientVolume');
    this.sfxVolume = getSafeVol('sfxVolume');
  }

  create() {
    const music = this.sound.get('background-music');
    if (!music) {
      this.sound.add('background-music', { loop: true, volume: this.musicVolume }).play();
    } else if (!music.isPlaying) {
      // Ensure volume is updated if restarting
      music.setVolume(this.musicVolume);
      music.play();
    }

    // Schedule random ambient sound to play periodically
    this.scheduleAmbientSound();

    // Global UI update listeners for static elements that shouldn't be polled in update loops
    const scenesWithScore = ['MapScene', 'SectionHunt', 'EggZamRoom'];
    this.registry.events.on('changedata', (parent, key, data) => {
        if (key === 'foundEggs') {
            // ⚡ Bolt Optimization: Replace forEach with fast for loop to prevent closure allocations
            for (let i = 0, len = scenesWithScore.length; i < len; i++) {
                const scene = this.scene.get(scenesWithScore[i]);
                if (scene && scene.sys.isActive() && scene.scoreText) {
                    scene.scoreText.setText(`${data.length}/${TOTAL_EGGS}`);
                }
            }
        }
    });

    // Listen for volume changes via Registry
    this.registry.events.on('changedata', (parent, key, data) => {
      if (key === 'musicVolume') {
        this.musicVolume = data;
        const bgMusic = this.sound.get('background-music');
        if (bgMusic) bgMusic.setVolume(this.musicVolume);
      } else if (key === 'ambientVolume') {
        this.ambientVolume = data;
      } else if (key === 'sfxVolume') {
        this.sfxVolume = data;
      }
    });

    // Initialize from registry if available
    if (this.registry.has('musicVolume')) this.musicVolume = this.registry.get('musicVolume');
    if (this.registry.has('ambientVolume')) this.ambientVolume = this.registry.get('ambientVolume');
    if (this.registry.has('sfxVolume')) this.sfxVolume = this.registry.get('sfxVolume');

    // Save settings on change
    this.registry.events.on('changedata', (parent, key, data) => {
        if (['musicVolume', 'ambientVolume', 'sfxVolume'].includes(key)) {
            try {
                localStorage.setItem(key, data);
                localStorage.setItem(key + '_backup', data);
            } catch (e) {
                console.warn('localStorage error', e);
            }
        }
    });
  }

  scheduleAmbientSound() {
    const delay = Phaser.Math.Between(10000, 80000); // 10-80 seconds in ms
    this.time.delayedCall(delay, () => {
      let randomAmbient = `ambient${Phaser.Math.Between(1, 10)}`;

      // Fallback to ambient1 if the randomly selected ambient track hasn't loaded yet into cache
      if (!this.cache.audio.exists(randomAmbient)) {
          if (this.cache.audio.exists('ambient1')) {
              randomAmbient = 'ambient1';
          } else {
              // If even ambient1 isn't loaded yet, just try again next loop
              this.scheduleAmbientSound();
              return;
          }
      }

      const ambientSound = this.sound.add(randomAmbient, { volume: this.ambientVolume });
      ambientSound.once('complete', () => {
        ambientSound.destroy();
        this.scheduleAmbientSound(); // Reschedule after it finishes
      });
      ambientSound.play();
    });
  }

  playSFX(key, config = {}) {
    if (this.cache.audio.exists(key)) {
        this.sound.play(key, { volume: this.sfxVolume, ...config });
    } else {
        console.warn(`MusicScene: Audio key '${key}' missing from cache!`);
    }
  }
}

class UIScene extends Phaser.Scene {
  constructor() {
    super({ key: 'UIScene' });
  }

  create() {
    this.createGearIcon();
    this.createSettingsPanel();

    // Add ESC and ENTER key support to toggle settings
    const toggleSettings = () => {
        if (this.settingsContainer && this.settingsContainer.visible) {
            this.closeSettings();
        } else {
            this.openSettings();
        }
    };
    if (this.input.keyboard) {
        this.input.keyboard.on('keydown-ESC', toggleSettings);
        this.input.keyboard.on('keydown-ENTER', () => this.closeSettings());
    }

    // Listen for resize events to update UI positions
    this.scale.on('resize', this.resize, this);
  }

  resize(gameSize) {
    const width = gameSize.width;
    const height = gameSize.height;
    this.repositionUI(width, height);
  }

  repositionUI(width, height) {
    // Reposition gear
    if (this.gearIcon) {
        this.gearIcon.setPosition(30, height - 30);
    }

    // Reposition settings panel
    if (this.settingsContainer) {
        const isVisible = this.settingsContainer.visible;
        this.settingsContainer.removeAll(true);
        this.createSettingsPanelContent(width, height);
        this.settingsContainer.setVisible(isVisible);
    }
  }

  createGearIcon() {
    const x = 30;
    const y = this.cameras.main.height - 30;

    // Create a container to hold the background and the cog
    const gearContainer = this.add.container(x, y).setDepth(1); // Keep below cursor

    // Draw white circle with yellow border
    // Tightly wrap the 25x25 mobile cog (radius 15 -> 30px diam)
    const bg = this.add.graphics();
    bg.fillStyle(0xffffff, 1);
    bg.fillCircle(0, 0, 15);
    bg.lineStyle(3, 0xffd700, 1); // Yellow border
    bg.strokeCircle(0, 0, 15);

    // Add the cog icon scaled down
    const gearImg = this.add.image(0, 0, 'cog').setDisplaySize(25, 25);

    gearContainer.add([bg, gearImg]);

    // Add an invisible hit area graphic so setInteractive works perfectly
    const hitAreaBg = this.add.graphics();
    hitAreaBg.fillStyle(0xffffff, 0.01);
    hitAreaBg.fillCircle(0, 0, 40); // Generous hit area for mobile
    gearContainer.add(hitAreaBg);

    gearContainer.setSize(50, 50);
    gearContainer.setInteractive(new Phaser.Geom.Circle(0, 0, 40), Phaser.Geom.Circle.Contains);

    gearContainer.baseScaleX = gearContainer.scaleX;
    gearContainer.baseScaleY = gearContainer.scaleY;

    gearContainer.on('pointerdown', () => {
        // Prioritize egg collection in SectionHunt
        const sectionHunt = this.scene.get('SectionHunt');
        if (sectionHunt && sectionHunt.scene.isActive()) {
            const pointer = this.input.activePointer;
            const scale = sectionHunt.gameScale;

            // Re-calculate the clamped lensX/lensY exactly as done in SectionHunt update()
            const lensOffsetX = -97.5 * scale;
            const lensOffsetY = -135 * scale;
            const rawLensX = pointer.x + lensOffsetX;
            const rawLensY = pointer.y + lensOffsetY;
            const lensRadius = 75 * scale;
            const lensX = Phaser.Math.Clamp(rawLensX, lensRadius, this.game.config.width - lensRadius);
            const lensY = Phaser.Math.Clamp(rawLensY, lensRadius, this.game.config.height - lensRadius);

            const captureRadius = 80 * scale;
            const captureRadiusSq = captureRadius * captureRadius;

            let eggCollected = false;
            const children = sectionHunt.eggs.getChildren();
            for (let i = children.length - 1; i >= 0; i--) {
                const egg = children[i];
                if (egg && egg.active && !egg.getData('collected')) {
              const distSq = Phaser.Math.Distance.Squared(lensX, lensY, egg.x, egg.y);
                    if (distSq < captureRadiusSq) {
                  egg.setData('animX', lensX);
                  egg.setData('animY', lensY);
                        sectionHunt.collectEgg(egg);
                        egg.destroy();
                        if (egg.symbolSprite) egg.symbolSprite.destroy();
                        eggCollected = true;
                    }
                }
            }
            // If we successfully collected an egg, intercept the click and DO NOT open settings
            if (eggCollected) return;
        }

        this.tweens.add({
            targets: gearContainer,
            scaleX: gearContainer.baseScaleX * 0.9,
            scaleY: gearContainer.baseScaleY * 0.9,
            duration: 50,
            ease: 'Power1',
            yoyo: true,
            onComplete: () => {
                gearContainer.setScale(gearContainer.baseScaleX, gearContainer.baseScaleY);
                this.openSettings();
            }
        });
    });

    this.gearIcon = gearContainer;
  }

  createSettingsPanel() {
    this.settingsContainer = this.add.container(0, 0).setVisible(false).setDepth(10);
    this.createSettingsPanelContent(this.cameras.main.width, this.cameras.main.height);
  }

  createSettingsPanelContent(screenWidth, screenHeight) {
    // Dynamic sizing for responsiveness
    const maxWidth = 500;
    const maxHeight = 500;
    const margin = 20;
    const width = Math.min(maxWidth, screenWidth - margin * 2);
    const height = Math.min(maxHeight, screenHeight - margin * 2);
    const x = (screenWidth - width) / 2;
    const y = (screenHeight - height) / 2;

    // Overlay
    const overlay = this.add.rectangle(0, 0, screenWidth, screenHeight, 0x000000, 0.7)
        .setOrigin(0)
        .setInteractive();
    this.settingsContainer.add(overlay);

    // Panel Background
    const panel = this.add.graphics();
    panel.fillStyle(0x333333, 1);
    panel.fillRoundedRect(x, y, width, height, 16);
    panel.lineStyle(4, 0xffffff, 1);
    panel.strokeRoundedRect(x, y, width, height, 16);
    this.settingsContainer.add(panel);

    // Title
    const title = this.add.text(screenWidth / 2, y + 40, 'Audio Settings', {
        fontSize: '32px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff'
    }).setOrigin(0.5);
    this.settingsContainer.add(title);

    // Cute Close Button (Top Right)
    const closeSize = 40;
    const closeX = x + width - 30;
    const closeY = y + 30;

    const closeBtn = this.add.container(closeX, closeY);

    const closeBg = this.add.graphics();
    // Transparent expanded hit area drawn explicitly so bounds compute automatically
    closeBg.fillStyle(0xffffff, 0.01);
    closeBg.fillCircle(0, 0, 80);

    closeBg.fillStyle(0xff4444, 1); // Reddish
    closeBg.fillCircle(0, 0, closeSize / 2);
    closeBg.lineStyle(2, 0xffffff, 1);
    closeBg.strokeCircle(0, 0, closeSize / 2);

    // Draw X
    const xSize = closeSize / 4;
    closeBg.lineStyle(3, 0xffffff, 1);
    closeBg.beginPath();
    closeBg.moveTo(-xSize, -xSize);
    closeBg.lineTo(xSize, xSize);
    closeBg.moveTo(xSize, -xSize);
    closeBg.lineTo(-xSize, xSize);
    closeBg.strokePath();

    closeBtn.add(closeBg);
    // When adding an interactive circle to a container, coordinate 0,0 represents the container origin.
    // Since closeBg is drawn at 0,0, the hit area circle should be at 0,0 too.
    closeBtn.setInteractive(new Phaser.Geom.Circle(0, 0, 80), Phaser.Geom.Circle.Contains);

    closeBtn.on('pointerdown', () => {
        this.tweens.add({
            targets: closeBtn, scaleX: 0.9, scaleY: 0.9, duration: 50, ease: 'Power1', yoyo: true,
            onComplete: () => {
                this.closeSettings();
                closeBtn.setScale(1); // Reset
            }
        });
    });
    this.settingsContainer.add(closeBtn);

    // Calculate layout for sliders
    // Space available below title (y + 80) to bottom (y + height - 20)
    const contentTop = y + 80;
    const contentHeight = height - 100;
    const spacing = contentHeight / 4;
    const trackWidth = Math.min(200, width - 60);

    this.createSlider('Music', contentTop + spacing * 0.5, screenWidth / 2, 'music', trackWidth);
    this.createSlider('Ambient', contentTop + spacing * 1.5, screenWidth / 2, 'ambient', trackWidth);
    this.createSlider('SFX', contentTop + spacing * 2.5, screenWidth / 2, 'sfx', trackWidth);

    // Start New Game Button
    const resetBtnContainer = this.add.container(screenWidth / 2, y + height - 40);
    const resetBg = this.add.graphics();
    resetBg.fillStyle(0xff4444, 1);
    resetBg.fillRoundedRect(-100, -20, 200, 40, 10);
    resetBg.lineStyle(2, 0xffffff, 1);
    resetBg.strokeRoundedRect(-100, -20, 200, 40, 10);

    const resetText = this.add.text(0, 0, 'START NEW GAME', {
        fontSize: '18px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff',
        fontStyle: 'bold'
    }).setOrigin(0.5);

    resetBtnContainer.add([resetBg, resetText]);
    resetBtnContainer.setSize(200, 40);
    resetBtnContainer.setInteractive();

    resetBtnContainer.baseScaleX = 1;
    resetBtnContainer.baseScaleY = 1;
    addButtonInteraction(this, resetBtnContainer, 'menu-click');

    resetBtnContainer.on('pointerdown', () => {
        const confirmation = new Confirmation(this, 0, 0, 'Your current game will be reset,\nare you sure?', () => {
            try { localStorage.removeItem('heIsRisenGameState'); } catch (e) { console.warn('localStorage error', e); }
            const mainScene = this.scene.get('MainMenu');
            if (mainScene) {
                initializeGameData(mainScene.registry, mainScene.cache, true);
            }

            // Stop active gameplay scenes and restart
            if (this.scene.isActive('MapScene')) this.scene.stop('MapScene');
            if (this.scene.isActive('SectionHunt')) this.scene.stop('SectionHunt');
            if (this.scene.isActive('EggZamRoom')) this.scene.stop('EggZamRoom');

            this.scene.launch('MapScene');

            // Close settings
            this.time.delayedCall(150, () => {
                this.closeSettings();
            });
        });
        this.settingsContainer.add(confirmation);
    });
    this.settingsContainer.add(resetBtnContainer);
  }

  createSlider(label, y, centerX, type, trackWidth = 200) {
    const startX = centerX - (trackWidth / 2);
    const endX = centerX + (trackWidth / 2);

    const text = this.add.text(centerX, y - 25, label, {
        fontSize: '24px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff'
    }).setOrigin(0.5);
    this.settingsContainer.add(text);

    // Increase track hit area for easier tapping (60px height)
    const track = this.add.rectangle(centerX, y + 10, trackWidth, 60, 0x888888).setAlpha(0.01).setInteractive();
    // Visual track
    const visualTrack = this.add.rectangle(centerX, y + 10, trackWidth, 4, 0x888888);
    this.settingsContainer.add(track);
    this.settingsContainer.add(visualTrack);

    // Handle
    let currentVol = 0.5;
    if (this.registry.has(`${type}Volume`)) currentVol = this.registry.get(`${type}Volume`);

    const handleX = startX + (currentVol * trackWidth);
    // Larger handle hit area (30px radius = 60px target)
    // Handle container for easier dragging and visual hierarchy
    const handle = this.add.container(handleX, y + 10);
    handle.setSize(60, 60); // 30px radius * 2
    handle.setInteractive(new Phaser.Geom.Circle(0, 0, 30), Phaser.Geom.Circle.Contains);
    this.input.setDraggable(handle);

    // Visuals
    const outer = this.add.circle(0, 0, 15, 0xffffff);
    handle.add(outer);

    this.settingsContainer.add(handle);

    const updateVolume = (x) => {
        const clampedX = Phaser.Math.Clamp(x, startX, endX);
        handle.x = clampedX;
        const volume = (clampedX - startX) / trackWidth;
        this.registry.set(`${type}Volume`, volume);
    };

    handle.on('drag', (p, x) => updateVolume(x));
    track.on('pointerdown', (p) => updateVolume(p.x));

    // Tactile feedback
    handle.on('pointerdown', () => this.tweens.add({ targets: handle, scale: 1.3, duration: 100, ease: 'Back.out' }));
    handle.on('pointerup', () => this.tweens.add({ targets: handle, scale: 1, duration: 100, ease: 'Back.out' }));
    handle.on('pointerout', () => this.tweens.add({ targets: handle, scale: 1, duration: 100, ease: 'Back.out' }));
  }

  closeSettings() {
      if (this.settingsContainer && this.settingsContainer.visible) {
          this.tweens.killTweensOf(this.settingsContainer);
          this.tweens.add({
              targets: this.settingsContainer,
              alpha: 0,
              duration: 200,
              ease: 'Power2',
              onComplete: () => {
                  this.settingsContainer.setVisible(false);
                  this.settingsContainer.setAlpha(1); // Reset for next time
                  if (this.gearIcon) {
                      this.gearIcon.setVisible(true);
                      this.gearIcon.setScale(1);
                  }
                  if (this.input.setDefaultCursor) this.input.setDefaultCursor('none');
              }
          });
      }
  }

  openSettings() {
    this.tweens.killTweensOf(this.settingsContainer);
    this.settingsContainer.setAlpha(0);
    this.settingsContainer.setVisible(true);
    if (this.gearIcon) this.gearIcon.setVisible(false);
    if (this.input.setDefaultCursor) this.input.setDefaultCursor('none');

    this.tweens.add({
        targets: this.settingsContainer,
        alpha: 1,
        duration: 200,
        ease: 'Power2'
    });
  }
}

class MainMenu extends Phaser.Scene {
  constructor() {
    super({ key: 'MainMenu' });
  }

  preload() {
    // Add loading text and progress bar
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Scale factors for mobile responsiveness (relative to base 1280x720 logic or viewport)
    // Using viewport center is safe.

    // Loading Bar Background
    const progressBar = this.add.graphics();
    const progressBox = this.add.graphics();
    progressBox.fillStyle(0x222222, 0.8);
    // Centered, width 320, height 50
    progressBox.fillRect(width / 2 - 160, height / 2 - 25, 320, 50);

    const loadingText = this.add.text(width / 2, height / 2 + 50, 'Loading... 0%', {
      fontFamily: 'Comic Sans MS',
      fontSize: '24px',
      fill: '#ffffff'
    }).setOrigin(0.5, 0.5);

    this.load.on('progress', (value) => {
      // Update Text
      loadingText.setText(`Loading... ${Math.floor(value * 100)}%`);

      // Update Bar
      progressBar.clear();
      progressBar.fillStyle(0xffff00, 1);
      progressBar.fillRect(width / 2 - 150, height / 2 - 15, 300 * value, 30);
    });

    this.load.on('complete', () => {
      progressBar.destroy();
      progressBox.destroy();
      loadingText.destroy();
    });

    this.load.json('symbols', 'assets/symbols.json');
    this.load.json('map_sections', 'assets/map/map_sections.json'); // NEW: Preload map_sections.json
    this.load.video('intro-video', 'assets/video/HeIsRisen-Intro.mp4');
    this.load.atlas('level-complete-atlas', 'assets/video/level-complete.png', 'assets/video/level-complete.json');
    this.load.image('level-complete-stamp', 'assets/objects/level-complete-stamp.png');
    this.load.image('finger-cursor', 'assets/cursor/pointer-finger-pointer.png');

    // Audio assets
    this.load.audio('background-music', 'assets/audio/background-music.mp3');
    this.load.audio('collect', 'assets/audio/collect1.mp3');
    this.load.audio('success', 'assets/audio/success.wav');
    this.load.audio('error', 'assets/audio/error.wav');
    this.load.audio('ambient1', 'assets/audio/ambient1.mp3');
    this.load.audio('ambient2', 'assets/audio/ambient2.mp3');
    this.load.audio('ambient3', 'assets/audio/ambient3.mp3');
    this.load.audio('ambient4', 'assets/audio/ambient4.mp3');
    this.load.audio('ambient5', 'assets/audio/ambient5.mp3');
    this.load.audio('ambient6', 'assets/audio/ambient6.mp3');
    this.load.audio('ambient7', 'assets/audio/ambient7.mp3');
    this.load.audio('ambient8', 'assets/audio/ambient8.mp3');
    this.load.audio('ambient9', 'assets/audio/ambient9.mp3');
    this.load.audio('ambient10', 'assets/audio/ambient10.mp3');
    this.load.audio('fart', 'assets/audio/fart.mp3');
    this.load.audio('menu-click', 'assets/audio/menu-click.mp3');
    this.load.audio('drive1', 'assets/audio/drive1.mp3');
    this.load.audio('drive2', 'assets/audio/drive2.mp3');
    this.load.audio('level-complete-audio', 'assets/audio/level-complete.mp3');

    // Preload common UI and game assets here to avoid reloading in scenes
    this.load.image('new-map', 'assets/map/new-map.png');
    this.load.image('cog', 'assets/objects/cog.png');
    this.load.image('magnifying-glass', 'assets/cursor/magnifying-glass.png');
    this.load.image('egg-zit-button', 'assets/objects/egg-zit-button.png');
    this.load.image('eggs-ammin-haul', 'assets/objects/eggs-ammin-haul.png');
    this.load.image('score', 'assets/objects/score.png');
    this.load.image('eggzam-keyframe', 'assets/video/eggzam-keyframe.jpg');
    this.load.atlas('egg-cellent-button', 'assets/objects/egg-cellent.png', 'assets/objects/egg-cellent.json');
    this.load.atlas('eggs-tra-stinky-button', 'assets/objects/eggs-tra-stinky.png', 'assets/objects/eggs-tra-stinky.json');
    this.load.image('symbol-result-summary-diag', 'assets/objects/symbol-result-summary-diag.png');

    // Preload all 60 eggs
    for (let i = 1; i <= TOTAL_EGGS; i++) {
      this.load.image(`egg-${i}`, `assets/eggs/egg-${i}.png`);
    }

    this.load.on('filecomplete-json-symbols', (key, type, data) => {
      if (data && data.symbols) {
        const symbolBasePath = ''; // symbols.json paths are relative to assets/
        data.symbols.forEach(symbol => {
          // Sentinel: Validate symbol path to prevent traversal/malicious loading
          if (this.isValidSymbol(symbol)) {
            // Check if texture already exists to avoid warnings/errors
            if (!this.textures.exists(symbol.filename)) {
              this.load.image(symbol.filename, symbolBasePath + symbol.filename);
            }
          } else {
            console.warn(`Security: Skipped invalid symbol filename: ${symbol.filename}`);
          }
        });
      }
    });

    this.load.on('filecomplete-json-map_sections', (key, type, data) => {
      if (Array.isArray(data)) {
        data.forEach(section => {
             // Enqueue thumbnail explicitly
             this.load.image(`${section.name}-thumb`, `assets/map/sections/${section.background}`);
             // Enqueue the first fallback attempt (.jpg)
             this.load.image(`${section.name}-fallback`, `assets/map/sections/${section.background}`);

             // Preload video backgrounds
             this.load.video(`${section.name}-video`, `assets/video/${section.name}.mp4`);
        });
      }
    });
    this.load.on('loaderror', (file) => {
      // console.error(`MainMenu: Load error: Key='${file.key}', URL='${file.url}'`);
      if (file.key && file.key.endsWith('-fallback')) {
          const sectionName = file.key.replace('-fallback', '');
          // If the failing URL was a .jpg, queue a .png
          if (file.url.endsWith('.jpg')) {
              this.load.image(file.key, `assets/map/sections/${sectionName}.png`);
          }
          // If the failing URL was a .png, queue an .svg
          else if (file.url.endsWith('.png')) {
              this.load.svg(file.key, `assets/map/sections/${sectionName}.svg`);
          }
      }
    });
  }

  create() {
    try {
      this.input.setDefaultCursor('none');

      // Get scale factors based on game dimensions
      const scaleX = this.game.config.width / 1280;
      const scaleY = this.game.config.height / 720;
      const scale = Math.min(scaleX, scaleY);
      this.gameScale = scale;

      // NEW: Initialize all game variables
      this.registry.set('foundEggs', []);
      this.registry.set('stampedSections', []);
      this.registry.set('correctCategorizations', 0);
      this.registry.set('currentScore', 0);

      try {
          let highScoreVal = null;
          try { highScoreVal = localStorage.getItem('highScore'); } catch (e) { console.warn('localStorage error', e); }
          let loadedScore = highScoreVal !== null && highScoreVal !== '' ? Number(highScoreVal) : NaN;
          if (isNaN(loadedScore) || !isFinite(loadedScore) || loadedScore < 0) {
              loadedScore = 0;
          }
          this.registry.set('highScore', loadedScore);
      } catch (e) {
          console.warn('LocalStorage access failed:', e);
          this.registry.set('highScore', 0);
      }

      // Load and validate symbols and map sections
      if (!this.registry.has('eggData')) {
          initializeGameData(this.registry, this.cache);
      }

      // Debug: Log game dimensions and scale

      // Set camera bounds to match viewport
      this.cameras.main.setBounds(0, 0, this.game.config.width, this.game.config.height);
      requestAnimationFrame(() => {
          if (this.cameras && this.cameras.main) {
              try { this.cameras.main.setViewport(0, 0, this.game.config.width, this.game.config.height); } catch(e) {}
          }
      });
      this.cameras.main.setPosition(0, 0);

      // Debug: Log camera position

      // Intro Video - centered
      const introVideo = this.add.video(this.game.config.width / 2, this.game.config.height / 2, 'intro-video');
      this.introVideo = introVideo; // Store reference for resizing
      introVideo.setMute(true); // Start muted to allow autoplay
      introVideo.disableInteractive(); // Ensure video ignores input

      // Handle delayed video metadata loading and scaling on resize
      const applyVideoScale = () => {
          if (this.introVideo && this.introVideo.active && this.introVideo.width > 0) {
              if (Math.abs(this.introVideo.displayWidth - this.game.config.width) > 10) {
                  this.introVideo.setDisplaySize(this.game.config.width, this.game.config.height);
                  this.introVideo.setPosition(this.game.config.width / 2, this.game.config.height / 2);
              }
          }
      };

      if (this.introVideo && this.introVideo.active) {
          const checkVideoReady = () => {
              if (this.introVideo && this.introVideo.active) {
                  if (this.introVideo.width > 0) {
                      applyVideoScale();
                  } else {
                      this.time.delayedCall(100, checkVideoReady);
                  }
              }
          };
          this.introVideo.once('play', checkVideoReady);
          this.scale.on('resize', applyVideoScale, this);
          this.events.once('shutdown', () => {
               this.scale.off('resize', applyVideoScale, this);
          });
          // Fallback trigger if event misses
          this.time.delayedCall(100, checkVideoReady);
      }

      try {
        introVideo.play(true); // Loop
      } catch (e) {
        console.warn('Video autoplay synchronous error:', e);
      }

      // Remove static text overlays as they are likely in the video
      // this.add.text(640 * scale, 0, `He Is Risen!`, ...);
      // this.add.text(0, 522 * scale, `Hunt with P.A.L.`, ...);
      // this.add.text(0, 580 * scale, `for the Meaning of Easter`, ...);

      // Only show cursor on desktop
      if (!this.sys.game.device.os.desktop) {
        this.fingerCursor = null;
      } else {
        this.fingerCursor = this.add.image(0, 0, 'finger-cursor')
          .setOrigin(0, 0)
          .setAngle(0)
          .setDisplaySize(50 * scale, 75 * scale)
          .setDepth(111111); // Ensure cursor is on top of everything
      }

      // Handle both mouse and touch input, request fullscreen on first click
      const safeRequestFullscreen = (element) => {
        if (element.requestFullscreen) {
          element.requestFullscreen().catch(err => {});
        } else if (element.webkitRequestFullscreen) {
          element.webkitRequestFullscreen().catch(err => {});
        }
      };

      // NEW INTRO SEQUENCE LOGIC
      // 1. Silent Loop + "Tap anywhere to start"
      // 2. User Tap -> Unmute, Fullscreen, Wait 3s
      // 3. Show "Play Now" Button
      // 4. User Tap "Play Now" -> Start Game

    // Initialize volume registry early (Load from localStorage if available)
    const getSafeVol = (key) => {
      let val = null;
      try { val = localStorage.getItem(key); } catch (e) { console.warn('localStorage error', e); }
      let parsed = parseFloat(val);
      if (isNaN(parsed) || parsed < 0 || parsed > 1) {
          let backupVal = null;
          try { backupVal = localStorage.getItem(key + '_backup'); } catch (e) { console.warn('localStorage error', e); }
          parsed = parseFloat(backupVal);
          if (isNaN(parsed) || parsed < 0 || parsed > 1) {
              return 0.5;
          }
      }
      return parsed;
    };

    if (!this.registry.has('musicVolume')) this.registry.set('musicVolume', getSafeVol('musicVolume'));
    if (!this.registry.has('ambientVolume')) this.registry.set('ambientVolume', getSafeVol('ambientVolume'));
    if (!this.registry.has('sfxVolume')) this.registry.set('sfxVolume', getSafeVol('sfxVolume'));

      // Launch UI Scene immediately (hidden initially)
      if (!this.scene.get('UIScene').scene.isActive()) {
          this.scene.launch('UIScene');
      }

      // Initial Overlay Text
      const tapToStartText = this.add.text(this.game.config.width / 2, this.game.config.height / 2, 'Tap anywhere to start', {
          fontSize: '48px',
          fontFamily: 'Comic Sans MS',
          fill: '#ffffff',
          stroke: '#000000',
          strokeThickness: 6
      }).setOrigin(0.5).setDepth(11);

      // Pulse animation to make it obvious the game is waiting for user input
      this.tweens.add({
          targets: tapToStartText,
          alpha: 0.5,
          duration: 800,
          yoyo: true,
          repeat: -1,
          ease: 'Sine.easeInOut'
      });

      // "Play Now" / "Continue" Button Container (Initially Hidden)
      const buttonWidth = 400;
      const buttonHeight = 80;
      const btnX = this.game.config.width / 2;
      const btnY = 580 * scale;
      let hasSaveState = false;
      try { hasSaveState = localStorage.getItem('heIsRisenGameState') !== null; } catch (e) { console.warn('localStorage error', e); }

      const startBtnContainer = this.add.container(btnX, btnY).setVisible(false).setDepth(11);
      this.startBtnContainer = startBtnContainer;

      let btnTextString = hasSaveState ? 'CONTINUE THE HUNT!' : 'PLAY NOW';
      const mainBtnContainer = this.add.container(0, hasSaveState ? -50 : 0);

      const btnBg = this.add.graphics();
      btnBg.fillStyle(0xff0000, 1);
      btnBg.fillRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, buttonHeight / 2);
      btnBg.lineStyle(4, 0xffffff, 1);
      btnBg.strokeRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, buttonHeight / 2);
      mainBtnContainer.add(btnBg);

      const btnText = this.add.text(0, 0, btnTextString, {
        fontSize: hasSaveState ? `28px` : `40px`,
        fill: '#ffffff',
        fontStyle: 'bold',
        fontFamily: 'Comic Sans MS',
        stroke: '#000000',
        strokeThickness: 4
      }).setOrigin(0.5);
      mainBtnContainer.add(btnText);

      mainBtnContainer.setSize(buttonWidth, buttonHeight);
      // Massive hit area for easier tapping
      mainBtnContainer.setInteractive();
      startBtnContainer.add(mainBtnContainer);

      let newGameBtnContainer = null;
      if (hasSaveState) {
          newGameBtnContainer = this.add.container(0, 50);
          const newBtnBg = this.add.graphics();
          newBtnBg.fillStyle(0x0000ff, 1);
          newBtnBg.fillRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, buttonHeight / 2);
          newBtnBg.lineStyle(4, 0xffffff, 1);
          newBtnBg.strokeRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, buttonHeight / 2);
          newGameBtnContainer.add(newBtnBg);

          const newBtnText = this.add.text(0, 0, 'START NEW GAME', {
            fontSize: `28px`,
            fill: '#ffffff',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#000000',
            strokeThickness: 4
          }).setOrigin(0.5);
          newGameBtnContainer.add(newBtnText);

          newGameBtnContainer.setSize(buttonWidth, buttonHeight);
          newGameBtnContainer.setInteractive();
          startBtnContainer.add(newGameBtnContainer);
      }

      startBtnContainer.setScale(scale);

      // State Management
      let introState = 'waiting_for_interaction'; // waiting_for_interaction -> playing_intro -> ready_to_play

      const handleGlobalTap = () => {
          if (introState !== 'waiting_for_interaction') return;

          introState = 'playing_intro';
          tapToStartText.setVisible(false);

          // Resume Audio Context
          if (this.sound.context.state === 'suspended') {
              this.sound.context.resume();
          }

          // Unmute Video
          if (this.introVideo) {
              this.introVideo.setMute(false);
              const vol = this.registry.get('musicVolume');
              this.introVideo.setVolume(vol !== undefined ? vol : 0.5);
              // Ensure it's playing
              this.introVideo.setPaused(false);
              if (this.introVideo.isPaused()) this.introVideo.play(true);

              // Force play again after a short delay to handle fullscreen interruption
              this.time.delayedCall(200, () => {
                   if (this.introVideo && this.introVideo.active) {
                       this.introVideo.setPaused(false);
                       this.introVideo.play(true);
                   }
              });
          }

          // Fullscreen
          const canvas = this.game.canvas;
          const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
          if (isMobile) {
              safeRequestFullscreen(document.documentElement); // Use documentElement instead of canvas for better mobile support
              if (screen.orientation && screen.orientation.lock) {
                  screen.orientation.lock('landscape').catch(() => {});
              }
              // Hack to force address bar to hide on mobile Safari
              setTimeout(() => window.scrollTo(0, 1), 100);
          } else {
              safeRequestFullscreen(canvas);
          }

          // Show Play Button almost immediately
          this.time.delayedCall(100, () => {
              introState = 'ready_to_play';
              startBtnContainer.setVisible(true);
              startBtnContainer.setScale(0);

              // Kill any existing tweens to prevent conflicts
              this.tweens.killTweensOf(startBtnContainer);
              
              // Unmute Video (Bolt Fix: 50% relative volume)
              if (this.introVideo) {
                  this.introVideo.setMute(false);
                  const vol = this.registry.get('musicVolume');
                  this.introVideo.setVolume((vol !== undefined ? vol : 0.5) * 0.5);
              }
              // Pop in effect
              this.tweens.add({
                  targets: startBtnContainer,
                  scaleX: scale,
                  scaleY: scale,
                  duration: 500,
                  ease: 'Back.out',
                  onComplete: () => {
                      // Start pulsing after pop-in is complete
                      this.tweens.add({
                        targets: startBtnContainer,
                        scaleX: scale * 1.05,
                        scaleY: scale * 1.05,
                        duration: 800,
                        yoyo: true,
                        repeat: -1,
                        ease: 'Sine.easeInOut'
                      });
                  }
              });
          });
      };

      // Add one-time listener for the global tap
      this.input.once('pointerdown', handleGlobalTap);

      // Play Now Handler
      const startGame = (forceNew = false) => {
          if (introState !== 'ready_to_play') return;

          // Prevent multiple calls
          introState = 'starting';

          if (forceNew) {
              initializeGameData(this.registry, this.cache, true);
          }

          // Fade out video audio
          this.tweens.add({
              targets: this.introVideo,
              volume: 0,
              duration: 500,
              onComplete: () => {
                  if (this.introVideo) {
                      this.introVideo.stop();
                      this.introVideo.destroy();
                  }

                  // Start Background Music
                  if (!this.scene.get('MusicScene').scene.isActive()) {
                      this.scene.launch('MusicScene');
                  }

                  const musicScene = this.scene.get('MusicScene');
                  if (musicScene) {
                      musicScene.playSFX('drive1');
                  }
                  this.scene.start('MapScene');
              }
          });
      };

      mainBtnContainer.on('pointerdown', () => startGame(false));
      if (newGameBtnContainer) {
          newGameBtnContainer.on('pointerdown', () => {
                const confirmation = new Confirmation(this, 0, 0, 'Your current game will be reset,\nare you sure?', () => {
                    startGame(true);
                });
                this.add.existing(confirmation);
          });
      }

      // Explicitly add window listener for robust keyboard support on initial screen
      const globalKeyHandler = (e) => {
          if (e.code === 'Space' || e.code === 'Enter') {
              if (introState === 'waiting_for_interaction') {
                  handleGlobalTap();
              } else if (introState === 'ready_to_play') {
                  startGame(false);
              }
          }
      };
      window.addEventListener('keydown', globalKeyHandler);
      this.events.once('shutdown', () => {
          window.removeEventListener('keydown', globalKeyHandler);
      });
      
      // ROBUST AUTOPLAY STRATEGY for Video (Bolt Fix: Volume scaling)
      const musicVol = this.registry.get('musicVolume');
      introVideo.setVolume(musicVol * 0.5);

      const updateIntroVolume = (parent, key, data) => {
          if (key === 'musicVolume' && introVideo && introVideo.active) {
              introVideo.setVolume(data * 0.5);
          }
      };
      this.registry.events.on('changedata', updateIntroVolume);
      
      // Clean up on shutdown
      this.events.once('shutdown', () => {
          if (introVideo) {
              introVideo.stop();
              introVideo.destroy();
          }
      });

      // Ensure loading text is destroyed if it persists (safety check)
      // Note: loadingText is local to preload, so we can't access it here directly easily unless stored on this.
      // But preload logic destroys it on complete.

    } catch (error) {
       console.error("Critical error in MainMenu create:", error);
       // Manually trigger the global error handler
       window.dispatchEvent(new ErrorEvent('error', { message: error.message }));
    }
  }

  isValidSymbol(s) {
    // Sentinel: validate structure and prevent path traversal
    return s && typeof s === 'object' &&
           typeof s.filename === 'string' &&
           !s.filename.includes('..') &&
           /^[a-zA-Z0-9_\-\/]+\.(png|jpg|jpeg)$/i.test(s.filename);
  }

  update() {
    if (this.fingerCursor) {
      this.fingerCursor.setPosition(this.input.x, this.input.y);
    }
  }
}

class MapScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MapScene' });
  }

  preload() {
    this.load.image('new-map', 'assets/map/new-map.png');
    // Common assets like 'finger-cursor', 'eggs-ammin-haul', 'score' are preloaded in MainMenu
  }

  create() {
    this.input.setDefaultCursor('none');

    // Get scale factors relative to the viewport
    const scaleX = this.game.config.width / 1280;
    const scaleY = this.game.config.height / 720;
    const scale = Math.min(scaleX, scaleY);
    this.gameScale = scale;

    // Set camera bounds to match viewport
    this.cameras.main.setBounds(0, 0, this.game.config.width, this.game.config.height);
    requestAnimationFrame(() => {
        if (this.cameras && this.cameras.main) {
            try { this.cameras.main.setViewport(0, 0, this.game.config.width, this.game.config.height); } catch(e) {}
        }
    });
    this.cameras.main.setPosition(0, 0);

    // NEW: Retrieve existing eggData and sections from registry
    const eggData = this.registry.get('eggData');
    const sections = this.registry.get('sections');
    let mapSections = this.cache.json.get('map_sections');
    if (!Array.isArray(mapSections)) mapSections = [];
    if (!eggData || !sections) {
      console.error('MapScene: eggData or sections missing from registry');
      this.scene.start('MainMenu'); // Fallback to MainMenu
      return;
    }

    if (!this.scene.get('MusicScene').scene.isActive()) {
      this.scene.launch('MusicScene');
    }
    const musicScene = this.scene.get('MusicScene');
    if (musicScene) {
        musicScene.playSFX('drive2');
    }

    // Add map image, fill the viewport proportionally based on native size
    this.mapImage = this.add.image(this.game.config.width/2, this.game.config.height/2, 'new-map')
      .setOrigin(0.5, 0.5);
    const nativeW = this.mapImage.width || 1376;
    const nativeH = this.mapImage.height || 768;
    const mapScale = Math.max(this.game.config.width / nativeW, this.game.config.height / nativeH);
    this.mapImage.setScale(mapScale);

    // Create map thumbnails (videos/images)
    this.mapZones = [];
    this.stamps = [];

    // We will use the original zone dimensions to calculate the center
    mapSections.forEach(section => {
      const centerX = section.coords.x;
      const centerY = section.coords.y;

      const nativeW = this.mapImage ? (this.mapImage.width || 1376) : 1376;
      const nativeH = this.mapImage ? (this.mapImage.height || 768) : 768;
      const initMapScale = Math.max(this.game.config.width / nativeW, this.game.config.height / nativeH);

      const mapWidth = nativeW * initMapScale;
      const mapHeight = nativeH * initMapScale;
      const offsetX = (this.game.config.width - mapWidth) / 2;
      const offsetY = (this.game.config.height - mapHeight) / 2;

      const thumbX = offsetX + centerX * initMapScale;
      const thumbY = offsetY + centerY * initMapScale;

      // Create container for border and drop shadow
      const thumbContainer = this.add.container(thumbX, thumbY);

      const radius = 15;

      const shadow = this.add.graphics();
      shadow.fillStyle(0x000000, 0.6);
      shadow.fillRoundedRect(-section.coords.width / 2 + 4, -section.coords.height / 2 + 4, section.coords.width, section.coords.height, radius);

      const border = this.add.graphics();
      border.lineStyle(4, 0x8b4513, 1);
      border.fillStyle(0xffffff, 1);
      border.fillRoundedRect(-section.coords.width / 2 - 5, -section.coords.height / 2 - 5, section.coords.width + 10, section.coords.height + 10, radius + 2);
      border.strokeRoundedRect(-section.coords.width / 2 - 5, -section.coords.height / 2 - 5, section.coords.width + 10, section.coords.height + 10, radius + 2);

      const thumbImage = this.add.image(0, 0, `${section.name}-thumb`).setOrigin(0.5, 0.5);
      thumbImage.setDisplaySize(section.coords.width, section.coords.height);

      const maskGraphics = this.add.graphics();
      maskGraphics.fillStyle(0xffffff);
      maskGraphics.fillRoundedRect(-section.coords.width / 2, -section.coords.height / 2, section.coords.width, section.coords.height, radius);
      maskGraphics.setVisible(false); // Do not show the mask itself

      const mask = maskGraphics.createGeometryMask();
      thumbImage.setMask(mask);

      // Add invisible hit area graphics for reliable touch detection on mobile
      // Use an expanded hit area to make tapping on mobile much easier
      const hitArea = this.add.rectangle(0, 0, section.coords.width + 80, section.coords.height + 80, 0x000000, 0);

      // IMPORTANT: maskGraphics should NOT be added to the container's children array when used as a mask
      // because it is scaled dynamically by the container, and rendering it as a child breaks the mask visually
      thumbContainer.add([shadow, border, thumbImage, hitArea]);
      thumbContainer.setSize(section.coords.width + 80, section.coords.height + 80);

      // By omitting geometry arguments and relying on the `hitArea` rectangle we added above,
      // Phaser will natively compute the bounds from the container's display list components
      // correctly mapping the center of the click zone to the container origin (0,0) across all scales.
      thumbContainer.setInteractive();

      const thumbScale = (section.coords.width * initMapScale) / section.coords.width;
      thumbContainer.setScale(thumbScale);

      const thumb = thumbContainer;
      thumb.name = section.name;
      thumb.sectionData = section;
      thumb.maskGraphics = maskGraphics; // Store reference to update mask transforms

      // Update mask initially
      maskGraphics.setPosition(thumbX, thumbY);
      maskGraphics.setScale(thumbScale);

      // Save original scale for click interactions
      thumb.baseScaleX = thumb.scaleX;
      thumb.baseScaleY = thumb.scaleY;

      addButtonInteraction(this, thumb, 'drive1');

      thumb.on('pointerdown', () => {
        this.time.delayedCall(100, () => {
            this.scene.start('SectionHunt', { sectionName: section.name });
        });
      });

      this.mapZones.push(thumb);

      // Level Complete Stamp Logic
      const eggData = this.registry.get('eggData') || [];
      const sectionEggs = eggData.filter(e => e.section === section.name);
      const foundEggs = this.registry.get('foundEggs') || [];
      const isCompleted = sectionEggs.length > 0 && sectionEggs.every(e => foundEggs.some(found => (found === e.eggId) || (found && found.eggId === e.eggId)));

      let stampedSections = this.registry.get('stampedSections') || [];

      if (isCompleted) {
          if (!stampedSections.includes(section.name)) {
              // FIRST TIME COMPLETE: Play the sprite animation
              if (!this.anims.exists('level-complete-anim')) {
                  const frameNames = this.textures.get('level-complete-atlas').getFrameNames().filter(name => name !== '__BASE').sort();
                  this.anims.create({
                      key: 'level-complete-anim',
                      frames: frameNames.map(frame => ({ key: 'level-complete-atlas', frame: frame })),
                      frameRate: 30,
                      repeat: 0
                  });
              }

              const stampAnim = this.add.sprite(thumb.x, thumb.y, 'level-complete-atlas');
              stampAnim.setOrigin(0.5, 0.5);
              stampAnim.setDepth(2);
              stampAnim.disableInteractive();

              // IMPORTANT: Play the animation before scaling it so that it gets the dimensions of the first frame
              stampAnim.play('level-complete-anim');

              const updateStampSize = () => {
                  const offset = 0 * (this.bgScale || 1);
                  stampAnim.setPosition(thumb.x, thumb.y + offset);

                  // Use the height of the current frame now that it's playing
                  const intrinsicHeight = stampAnim.height || 720;
                  const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                  const calculatedScale = targetHeight / intrinsicHeight;
                  if (calculatedScale > 0 && isFinite(calculatedScale)) {
                      stampAnim.setScale(calculatedScale);
                  }
              };
              updateStampSize();

              if (!this.stamps) this.stamps = [];
              this.stamps.push({ video: stampAnim, thumb: thumb });

              // Play audio
              const sfxVol = this.registry.get('sfxVolume') !== undefined ? this.registry.get('sfxVolume') : 0.5;
              const soundManager = this.scene.get('MusicScene');
              if (soundManager) {
                  soundManager.playSFX('level-complete-audio', { volume: sfxVol });
              } else {
                  this.sound.play('level-complete-audio', { volume: sfxVol });
              }

              stampedSections.push(section.name);
              this.registry.set('stampedSections', stampedSections);

              // Swap to image when animation finishes to free memory
              stampAnim.on('animationcomplete', () => {
                  const stampImg = this.add.image(thumb.x, thumb.y, 'level-complete-stamp');
                  stampImg.setDepth(2);
                  stampImg.setOrigin(0.5, 0.5);

                  const offset = 0 * (this.bgScale || 1);
                  stampImg.setPosition(thumb.x, thumb.y + offset);

                  // Apply the identical scale multiplier that the thumbnail is using
                  // Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const intrinsicHeight = stampImg.height || 720;
                  const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                  const calculatedScale = targetHeight / intrinsicHeight;
                  if (calculatedScale > 0 && isFinite(calculatedScale)) {
                      stampImg.setScale(calculatedScale);
                  }
                  stampImg.disableInteractive();
                  // Replace in resize array so window resizing still works
                  const idx = this.stamps.findIndex(s => s.video === stampAnim);
                  if (idx !== -1) {
                      this.stamps[idx] = { video: stampImg, thumb: thumb };
                  }
                  stampAnim.destroy();
              });

          } else {
              // ALREADY COMPLETED: Show static image directly
              const stampImg = this.add.image(thumb.x, thumb.y, 'level-complete-stamp');
              stampImg.setOrigin(0.5, 0.5);
              stampImg.setDepth(2);
              stampImg.disableInteractive();
              const updateStampSize = () => {
                  const offset = 0 * (this.bgScale || 1);
                  stampImg.setPosition(thumb.x, thumb.y + offset);

                  // Scale the stamp so its height covers the thumbnail's height + 25%, maintaining its intrinsic aspect ratio
                  const intrinsicHeight = stampImg.height || 720;
                  const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                  const calculatedScale = targetHeight / intrinsicHeight;
                  if (calculatedScale > 0 && isFinite(calculatedScale)) {
                      stampImg.setScale(calculatedScale);
                  }
              };
              updateStampSize();

              if (!this.stamps) this.stamps = [];
              // We use "video: stampImg" so the generic resize loop works identically
              this.stamps.push({ video: stampImg, thumb: thumb });
          }
      }
      section.zone = thumb; // keep reference for resize
    });
    this.mapSections = mapSections;

    // UI elements
    this.eggsAmminHaul = this.add.image(0, 200 * scale, 'eggs-ammin-haul')
      .setOrigin(0, 0)
      .setDisplaySize(137 * scale, 150 * scale)
      .setInteractive();

    addButtonInteraction(this, this.eggsAmminHaul, 'menu-click');

    // Delayed transition
    this.eggsAmminHaul.on('pointerdown', () => {
        this.time.delayedCall(100, () => {
             this.scene.start('EggZamRoom');
        });
    });

    this.scoreImage = this.add.image(0, 0, 'score')
      .setOrigin(0, 0)
      .setDisplaySize(200 * scale, 200 * scale);

    const foundEggs = this.registry.get('foundEggs').length;
    const isDesktop = this.sys.game.device.os.desktop;
    const scoreY = isDesktop ? 125 * scale : 117 * scale;
    const scoreFontSize = isDesktop ? 32 : 42;
    this.scoreText = this.add.text(100 * scale, scoreY, `${foundEggs}/${TOTAL_EGGS}`, {
      fontSize: `${scoreFontSize * scale}px`,
      fill: '#000',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#fff',
      strokeThickness: 6 * scale
    }).setOrigin(0.5);

    // Cursor for desktop only
    if (!this.sys.game.device.os.desktop) {
      this.fingerCursor = null;
    } else {
      this.fingerCursor = this.add.image(0, 0, 'finger-cursor')
        .setOrigin(0, 0)
        .setAngle(0)
        .setDepth(111111) // Ensure cursor is on top of everything
        .setDisplaySize(50 * scale, 75 * scale);
    }
  }

  update() {
    if (this.fingerCursor) {
      this.fingerCursor.setPosition(this.input.x, this.input.y);
    }
  }
}

class SectionHunt extends Phaser.Scene {
  constructor() {
    super({ key: 'SectionHunt' });
  }

  init(data) {
    this.sectionName = data.sectionName;
  }

  preload() {
    // Media and Fallbacks are preloaded in MainMenu via map_sections.json.

    this.load.on('loaderror', (file) => {
      if (file.type === 'image' || file.type === 'video') {
        console.warn(`SectionHunt PRELOAD: Missing asset (expected if fallback occurs): Key='${file.key}', URL='${file.url}'`);
      }
    });
  }

  collectEgg(egg) {
    announceToScreenReader('Egg collected!');
    const foundEggs = this.registry.get('foundEggs');
    const eggDataArray = this.registry.get('eggData');
    const eggData = eggDataArray.find(e => e.eggId === egg.getData('eggId'));
    const eggInfo = {
      eggId: egg.getData('eggId'),
      symbolData: egg.getData('symbolDetails'),
      categorized: false
    };
    if (!foundEggs.some(e => e.eggId === eggInfo.eggId)) {
      const musicScene = this.scene.get('MusicScene');
      if (musicScene) {
          musicScene.playSFX('collect', { detune: Phaser.Math.Between(-200, 200) });
      }

      announceToScreenReader('Egg found!');

      if (navigator && navigator.vibrate) {
          navigator.vibrate(50);
      }

      // Get symbol texture if available
      let symbolTexture = null;
      if (egg.symbolSprite && egg.symbolSprite.active) {
          symbolTexture = egg.symbolSprite.texture.key;
      }

      // Decouple visual effect coordinates (e.g. magnifying glass lens center) from physical location
      const animX = egg.getData('animX') !== undefined ? egg.getData('animX') : egg.x;
      const animY = egg.getData('animY') !== undefined ? egg.getData('animY') : egg.y;

      this.showCollectionFeedback(animX, animY, egg.texture.key, symbolTexture);
      foundEggs.push(eggInfo);
      this.registry.set('foundEggs', foundEggs);
      if (eggData) {
        eggData.collected = true;
        this.registry.set('eggData', eggDataArray);
      }

      // Reset hint timer
      if (this.hintTimer) {
          this.hintTimer.reset({ delay: 90000, callback: this.showIdleHint, callbackScope: this, loop: true });
      }

      let currentScore = this.registry.get('currentScore');
      currentScore += 10;
      if (foundEggs.length === TOTAL_EGGS) {
        currentScore += 100;
      }
      this.registry.set('currentScore', currentScore);
      const highScore = this.registry.get('highScore');
      if (currentScore > highScore) {
        this.registry.set('highScore', currentScore);
        try { localStorage.setItem('highScore', currentScore); } catch (e) { console.warn('localStorage error', e); }
      }

      saveGameState(this.registry);

      this.checkLevelComplete();
    } else {
    }
  }

  checkLevelComplete(immediate = false) {
      const foundEggs = this.registry.get('foundEggs');
      const sections = this.registry.get('sections');
      const currentSection = sections.find(s => s.name === this.sectionName);
      const scale = this.gameScale;

      if (foundEggs.length === TOTAL_EGGS) {
          announceToScreenReader('All 60 Eggs Found! Transporting to the EggZam Room...');
          const clearText = this.add.text(this.game.config.width / 2, this.game.config.height / 2, "All 60 Eggs Found! Transporting to the EggZam Room...", {
              fontSize: `${48 * scale}px`,
              fontFamily: 'Comic Sans MS',
              fill: '#ffff00',
              backgroundColor: '#000000cc',
              padding: { x: 20 * scale, y: 20 * scale },
              stroke: '#000000',
              strokeThickness: 8 * scale,
              align: 'center',
              wordWrap: { width: 800 * scale, useAdvancedWrap: true }
          }).setOrigin(0.5).setDepth(35).setScrollFactor(0);

          if (this.hintTimer) this.hintTimer.remove();

          if (!immediate) {
              this.time.delayedCall(3000, () => this.scene.start('EggZamRoom'));
          } else {
              this.scene.start('EggZamRoom');
          }
          return;
      }

      if (currentSection) {
          const foundIds = foundEggs.map(e => e.eggId);
          const remainingCount = currentSection.eggs.filter(id => !foundIds.includes(id)).length;
          if (remainingCount === 0) {
              announceToScreenReader('Great Job Detective!! You found all the hidden eggs on this map, the others are hidden in other maps.');
              const clearText = this.add.text(this.game.config.width / 2, this.game.config.height / 2, "Great Job Detective!! You found all the hidden eggs on this map, the others are hidden in other maps.", {
                  fontSize: `${40 * scale}px`,
                  fontFamily: 'Comic Sans MS',
                  fill: '#ffff00',
                  backgroundColor: '#000000cc',
                  padding: { x: 20 * scale, y: 10 * scale },
                  stroke: '#000000',
                  strokeThickness: 6 * scale,
                  align: 'center',
                  wordWrap: { width: 800 * scale, useAdvancedWrap: true }
              }).setOrigin(0.5).setDepth(35).setScrollFactor(0);

              this.tweens.add({
                  targets: clearText,
                  alpha: 0,
                  delay: 5000,
                  duration: 1000,
                  onComplete: () => clearText.destroy()
              });

              if (this.hintTimer) {
                  this.hintTimer.remove();
              }
          }
      }
  }

  showCollectionFeedback(x, y, eggTexture, symbolTexture) {
    const scale = this.gameScale;

    if (!this.textures.exists('sparkle')) {
        const starObject = new Phaser.GameObjects.Star(this, 10, 10, 4, 2, 10, 0xffff00);
        const renderTexture = this.add.renderTexture(0, 0, 20, 20).setVisible(false);
        renderTexture.draw(starObject, 10, 10);
        renderTexture.saveTexture('sparkle');
        renderTexture.destroy();
        starObject.destroy();
    }

    const emitter = this.add.particles(x, y, 'sparkle', {
        speed: { min: 100 * scale, max: 300 * scale }, scale: { start: 1.5 * scale, end: 0 }, alpha: { start: 1, end: 0 },
        lifespan: 1000, gravityY: 300 * scale, quantity: 30, duration: 150
    }).setDepth(19);
    emitter.once('complete', () => emitter.destroy());

    // Egg Sprite
    const eggSprite = this.add.image(x, y, eggTexture).setDepth(20).setDisplaySize(50 * scale, 75 * scale);
    this.tweens.add({
        targets: eggSprite,
        y: y - (150 * scale),
        scaleX: eggSprite.scaleX * 2.0,
        scaleY: eggSprite.scaleY * 2.0,
        angle: 720,
        alpha: 0,
        duration: 1200,
        ease: 'Back.easeOut',
        onComplete: () => eggSprite.destroy()
    });

    // Symbol Sprite
    if (symbolTexture) {
        const symSprite = this.add.image(x, y, symbolTexture).setDepth(21).setDisplaySize(50 * scale, 75 * scale);
        this.tweens.add({
            targets: symSprite,
            y: y - (150 * scale),
            scaleX: symSprite.scaleX * 2.0,
            scaleY: symSprite.scaleY * 2.0,
            angle: 720,
            alpha: 0,
            duration: 1200,
            ease: 'Back.easeOut',
            onComplete: () => symSprite.destroy()
        });
    }

    const feedback = this.add.text(x, y - (40 * scale), 'Found!', {
        fontSize: `${32 * scale}px`,
        fontFamily: 'Comic Sans MS',
        fill: '#ffff00',
        stroke: '#000000',
        strokeThickness: 4 * scale
    }).setOrigin(0.5).setDepth(22);

    this.tweens.add({
        targets: feedback,
        y: y - (150 * scale),
        scaleX: 1.5,
        scaleY: 1.5,
        alpha: 0,
        duration: 1200,
        ease: 'Back.easeOut',
        onComplete: () => feedback.destroy()
    });
  }

  showIdleHint() {
    // Goal 1: Check if the user has touched/moved within the last 60 seconds
    const now = this.time.now;
    if (this.lastInteractionTime && (now - this.lastInteractionTime > 60000)) {
        // User is fully AFK, don't show the hint.
        return;
    }

    const foundEggs = this.registry.get('foundEggs');
    const sections = this.registry.get('sections');
    // For mobile, section lookup depends on if 'sections' structure is same.
    // m/main.js create sets registry sections: { name: section.name, eggs: sectionEggs }
    const currentSection = sections.find(s => s.name === this.sectionName);
    const scale = this.gameScale;

    if (!currentSection) return;

    const eggsInSection = currentSection.eggs; // Array of IDs in this section's cluster
    const foundIds = foundEggs.map(e => e.eggId);
    const remainingCount = eggsInSection.filter(id => !foundIds.includes(id)).length;

    if (remainingCount > 0) {
        const musicScene = this.scene.get('MusicScene');
        if (musicScene) musicScene.playSFX('menu-click');

        const hintText = this.add.text(this.game.config.width / 2, this.game.config.height * 0.9, `Hint: ${remainingCount} eggs left here!`, {
            fontSize: `${32 * scale}px`,
            fontFamily: 'Comic Sans MS',
            fill: '#ffffff',
            backgroundColor: '#00000088',
            padding: { x: 10 * scale, y: 5 * scale },
            stroke: '#000000',
            strokeThickness: 4 * scale
        }).setOrigin(0.5).setDepth(30).setScrollFactor(0);

        this.tweens.add({
            targets: hintText,
            alpha: 0,
            delay: 4000,
            duration: 1000,
            onComplete: () => hintText.destroy()
        });
    }
  }

  create() {
    this.input.setDefaultCursor('none');

    const scaleX = this.game.config.width / 1280;
    const scaleY = this.game.config.height / 720;
    const scale = Math.min(scaleX, scaleY);
    this.gameScale = scale;

    this.cameras.main.setBounds(0, 0, this.game.config.width, this.game.config.height);
    this.cameras.main.setViewport(0, 0, this.game.config.width, this.game.config.height);
    this.cameras.main.setPosition(0, 0);

    let useVideo = false;
    const videoKey = `${this.sectionName}-video`;

    if (this.cache.video.exists(videoKey)) {
        useVideo = true;
    }

    if (useVideo) {
        this.sectionImage = this.add.video(0, 0, videoKey)
            .setOrigin(0, 0)
            .setDisplaySize(this.game.config.width, this.game.config.height)
            .setDepth(0)
            .disableInteractive();

        this.sectionImage.setMute(false); // iOS quirk: keep muted attr false to avoid global context suspension
        const ambientVol = this.registry.has('ambientVolume') ? this.registry.get('ambientVolume') : 0.5;
        this.sectionImage.setVolume(ambientVol * 0.25);
        this.sectionImage.play(true);
        this.isUsingVideo = true;

        // Smart Audio Looping: Mute audio after first play, unmute every 5th loop
        // Use setVolume(0) instead of setMute(true) to prevent iOS global WebAudio suspension bugs
        this.sectionImage.loopCount = 0;
        this.sectionImage.on('loop', () => {
             this.sectionImage.loopCount++;
             if (this.sectionImage.loopCount % 5 !== 0) {
                 this.sectionImage.setVolume(0);
             } else {
                 const currentAmbientVol = this.registry.has('ambientVolume') ? this.registry.get('ambientVolume') : 0.5;
                 this.sectionImage.setVolume(currentAmbientVol * 0.25);
             }
        });

        const updateAmbientVolume = (parent, key, data) => {
             if (key === 'ambientVolume' && this.sectionImage && this.sectionImage.active && this.isUsingVideo) {
                 this.sectionImage.setVolume(data * 0.25);
             }
        };
        this.registry.events.on('changedata', updateAmbientVolume);
        this.events.once('shutdown', () => {
             this.registry.events.off('changedata', updateAmbientVolume);
        });

        this.sectionImage.on('error', () => {
             console.warn(`SectionHunt: Video ${videoKey} playback error. Falling back.`);
             this.sectionImage.destroy();
             this.isUsingVideo = false;
             this.createFallbackImage();
        });
    }

    if (!useVideo) {
        this.createFallbackImage();
    }
    this.setupEggsAndUI();
  }

  createFallbackImage() {
    let textureKey = `${this.sectionName}-fallback`;

    if (!this.textures.exists(textureKey)) {
        textureKey = 'placeholder-bg';
        if (!this.textures.exists('placeholder-bg')) {
            console.warn(`SectionHunt: Texture '${textureKey}' missing! Trying fallback...`);
            const graphics = this.make.graphics({x: 0, y: 0, add: false});
            graphics.fillStyle(0x444444);
            graphics.fillRect(0, 0, 1280, 720);
            graphics.lineStyle(4, 0xff0000);
            graphics.strokeRect(0, 0, 1280, 720);

            const text = this.make.text({
                x: 640,
                y: 360,
                text: `Missing Asset:\n${this.sectionName}`,
                origin: { x: 0.5, y: 0.5 },
                style: {
                    font: 'bold 40px Arial',
                    fill: '#ffffff',
                    align: 'center'
                }
            });

            graphics.generateTexture('placeholder-bg', 1280, 720);
            text.destroy();
            graphics.destroy();
        }
    }

    if (this.sys.settings.active) {
        this.sectionImage = this.add.image(0, 0, textureKey)
            .setOrigin(0, 0)
            .setDisplaySize(this.game.config.width, this.game.config.height)
            .setDepth(0);
    }
    this.isUsingVideo = false;
  }

  setupEggsAndUI() {
    const scale = this.gameScale;
    const eggData = this.registry.get('eggData') || [];
    const sectionEggs = eggData.filter(e => e.section === this.sectionName && !e.collected);
    this.eggs = this.add.group();

    sectionEggs.forEach(eggData => {
      const egg = this.add.image(eggData.x, eggData.y, `egg-${eggData.eggId}`)
        // .setInteractive() // Removed per Bolt Optimization
        .setDepth(5)
        .setDisplaySize(50 * scale, 75 * scale)
        .setAlpha(0);
      egg.setData('eggId', eggData.eggId);
      egg.setData('symbolDetails', eggData.symbol);
      if (eggData.symbol && eggData.symbol.filename) {
        const textureKey = eggData.symbol.filename;
        if (this.textures.exists(textureKey)) {
          const symbolSprite = this.add.image(eggData.x, eggData.y, textureKey)
            .setDepth(6)
            .setDisplaySize(50 * scale, 75 * scale)
            .setAlpha(0);
          egg.symbolSprite = symbolSprite;
        } else {
          console.warn(`SectionHunt: Texture '${textureKey}' not found for symbol '${eggData.symbol.name}'`);
          egg.symbolSprite = null;
        }
      } else {
        egg.symbolSprite = null;
      }
      // Note: We removed the individual click handler on egg to use global lens click logic
      this.eggs.add(egg);
    });

    this.eggZitButton = this.add.image(0, 200 * scale, 'egg-zit-button')
      .setOrigin(0, 0)
      .setDisplaySize(150 * scale, 150 * scale)
      .setInteractive()
      .on('pointerdown', () => {
        this.time.delayedCall(150, () => {
            this.scene.start('MapScene');
        });
      })
      .setDepth(4)
      .setScrollFactor(0);
    addButtonInteraction(this, this.eggZitButton, 'drive1');

    this.eggsAmminHaul = this.add.image(0, 350 * scale, 'eggs-ammin-haul')
      .setOrigin(0, 0)
      .setDisplaySize(137 * scale, 150 * scale)
      .setInteractive()
      .setDepth(4);

    addButtonInteraction(this, this.eggsAmminHaul, 'menu-click');

    // Delayed transition
    this.eggsAmminHaul.on('pointerdown', () => {
        this.time.delayedCall(100, () => {
             this.scene.start('EggZamRoom');
        });
    });

    const musicScene = this.scene.get('MusicScene');
    if (musicScene) {
        musicScene.playSFX('drive2');
    }
    this.scoreImage = this.add.image(0, 0, 'score')
      .setOrigin(0, 0)
      .setDisplaySize(200 * scale, 200 * scale)
      .setDepth(4)
      .setScrollFactor(0);

    const foundEggs = this.registry.get('foundEggs').length;
    const isDesktop = this.sys.game.device.os.desktop;
    const scoreY = isDesktop ? 125 * scale : 117 * scale;
    const scoreFontSize = isDesktop ? 32 : 42;
    this.scoreText = this.add.text(100 * scale, scoreY, `${foundEggs}/${TOTAL_EGGS}`, {
      fontSize: `${scoreFontSize * scale}px`,
      fill: '#000',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#fff',
      strokeThickness: 6 * scale
    }).setOrigin(0.5).setDepth(5);

    const diameter = 150 * scale;
    this.zoomedView = this.add.renderTexture(0, 0, diameter, diameter)
      .setDepth(6)
      .setScrollFactor(0)
      .setOrigin(0.5, 0.5); // Center origin for easier positioning
    this.maskGraphics = this.add.graphics()
      .setScrollFactor(0);
    // Draw circle centered at 0,0 relative to graphics object
    this.maskGraphics.fillCircle(0, 0, 75 * scale);
    this.zoomedView.setMask(this.maskGraphics.createGeometryMask());

    this.magnifyingGlass = this.add.image(0, 0, 'magnifying-glass')
      .setOrigin(1, 1) // Anchor at bottom-right (handle tip)
      .setDepth(7)
      .setScrollFactor(0);

    // Bolt Optimization: Render Stamp for single-pass drawing
    this.renderStamp = this.make.image({ x: 0, y: 0, key: this.sectionName, add: false });

    // Idle Hint Timer (90 seconds, with 60 second AFK check)
    this.lastInteractionTime = this.time.now;
    this.input.on('pointermove', () => {
        this.lastInteractionTime = this.time.now;
    });
    this.input.on('pointerdown', () => {
        this.lastInteractionTime = this.time.now;
    });

    this.hintTimer = this.time.addEvent({
        delay: 90000,
        callback: this.showIdleHint,
        callbackScope: this,
        loop: true
    });

    this.fingerCursor = this.add.image(0, 0, 'finger-cursor')
        .setOrigin(0, 0)
        .setAngle(0)
        .setDepth(111111)
        .setScrollFactor(0)
        .setVisible(false);

    // Check level complete immediately if returning to a completed map
    this.checkLevelComplete(true);

    // Pre-allocate array for buttons once
    this.uiButtons = [this.eggZitButton, this.eggsAmminHaul];

    // Global capture handler
    this.input.on('pointerdown', (pointer) => {
      // Calculate lens position based on pointer
      const scale = this.gameScale;

      // New offsets for reverted size (150x187.5 display size, 0.75x of doubled)
      // Visual lens center is approx (-97.5 * scale, -135 * scale) relative to handle tip
      const lensOffsetX = -97.5 * scale;
      const lensOffsetY = -135 * scale;

      const rawLensX = pointer.x + lensOffsetX;
      const rawLensY = pointer.y + lensOffsetY;

      const lensRadius = 75 * scale;
      const lensX = Phaser.Math.Clamp(rawLensX, lensRadius, this.game.config.width - lensRadius);
      const lensY = Phaser.Math.Clamp(rawLensY, lensRadius, this.game.config.height - lensRadius);
      const captureRadius = 80 * scale; // Slightly larger than visual radius (75)
      const captureRadiusSq = captureRadius * captureRadius;

      // Check all eggs
      // ⚡ Bolt Optimization: Replace forEach with fast for loop to prevent closure allocations on pointerdown
      const children = this.eggs.getChildren();
      // ⚡ Iterate backwards because destroying an object mutates the children array
      for (let i = children.length - 1; i >= 0; i--) {
        const egg = children[i];
        if (egg && egg.active && !egg.getData('collected')) { // collected check might be redundant if we destroy, but safe
           // Bolt Optimization: Squared distance check using POINTER position (where the finger is)
           // Tapping the screen harvests the egg under the finger.
           const distSq = Phaser.Math.Distance.Squared(pointer.x, pointer.y, egg.x, egg.y);

           // Increased capture radius logic for easier finding
           if (distSq < captureRadiusSq) {
               // Decouple the visual animation position from the physical interaction position
               egg.setData('animX', lensX);
               egg.setData('animY', lensY);

               this.collectEgg(egg);
               egg.destroy();
               if (egg.symbolSprite) egg.symbolSprite.destroy();
           }
        }
      }
    });
  }

  update() {
    const pointer = this.input.activePointer;
    const scale = this.gameScale;

    // Magnifying glass display size is 150*scale x 187.5*scale.
    // We shift it "Up and Left" relative to handle tip.

    const lensOffsetX = -97.5 * scale;
    const lensOffsetY = -135 * scale;

    const rawLensX = pointer.x + lensOffsetX;
    const rawLensY = pointer.y + lensOffsetY;

    // 1. Clamp physical lens position so the visual ring stays on screen
    const lensRadius = 75 * scale;
    const lensX = Phaser.Math.Clamp(rawLensX, lensRadius, this.game.config.width - lensRadius);
    const lensY = Phaser.Math.Clamp(rawLensY, lensRadius, this.game.config.height - lensRadius);

    // Ensure video size is correct once texture loads
    if (this.sectionImage && this.sectionImage.active && this.sectionImage.width > 0) {
        if (Math.abs(this.sectionImage.displayWidth - this.game.config.width) > 10) {
             this.sectionImage.setDisplaySize(this.game.config.width, this.game.config.height);
        }
    }

    // Update Zoomed View Position (centered on lens)
    this.zoomedView.setPosition(lensX, lensY);
    this.maskGraphics.setPosition(lensX, lensY);

    // Position the magnifying glass graphic to perfectly align its handle tip with the pointer,
    // and its visual lens ring with lensX/lensY.
    // The image's origin is (1, 1), so setting it to pointer.x, pointer.y locks the tip to the finger.
    // However, since lensX/lensY are now clamped, we must reverse-calculate the handle tip position
    // so the physical graphic perfectly aligns its visual lens ring with the clamped coordinates.
    const clampedTipX = lensX - lensOffsetX;
    const clampedTipY = lensY - lensOffsetY;
    this.magnifyingGlass.setPosition(clampedTipX, clampedTipY);

    const magnifierRadius = 75 * scale;
    const zoom = 2;
    const diameter = 150 * scale;
    const viewWidth = diameter / zoom;
    const viewHeight = diameter / zoom;

    // Crucial Change: The user requested the zoomed view to show what is visually under the FINGER (pointer.x, pointer.y),
    // because that's where they are pointing, even though the magnifying glass is visually offset so their hand doesn't block it.

    // Calculate the scale ratio of the active background to properly project pointer coordinates
    let baseScaleX = 1;
    let baseScaleY = 1;

    if (this.sectionImage && this.sectionImage.active) {
         if (this.renderStamp.texture.key !== this.sectionImage.texture.key) {
             this.renderStamp.setTexture(this.sectionImage.texture.key);
         }
         this.renderStamp.setFrame(this.sectionImage.frame.name);

         const actualBgWidth = this.renderStamp.width;
         const actualBgHeight = this.renderStamp.height;

         baseScaleX = this.sectionImage.displayWidth / actualBgWidth;
         baseScaleY = this.sectionImage.displayHeight / actualBgHeight;
    } else {
         if (this.renderStamp.texture.key !== this.sectionName) {
             this.renderStamp.setTexture(this.sectionName);
         }
         baseScaleX = this.bgScale || (this.game.config.width / this.renderStamp.width);
         baseScaleY = this.bgScale || (this.game.config.height / this.renderStamp.height);
    }

    this.zoomedView.clear();

    // 2. Apply zoom. The `zoomedView` RenderTexture expects coordinates and scales that represent the final pixels.
    this.renderStamp.setScale(baseScaleX * zoom, baseScaleY * zoom);
    this.renderStamp.setOrigin(0, 0);

    // To map the exact pixel under pointer.x, pointer.y to the center of the zoom window (radius):
    // The background is scaled up by `zoom` *relative to the screen coordinates*.
    // So the pixel at `pointer.x` on the screen becomes `pointer.x * zoom` on the scaled background.
    // We want `pointer.x * zoom` to land at the center of the RenderTexture, which is `viewWidth / 2 * zoom`.
    // Center of RenderTexture = (diameter / 2) = (viewWidth * zoom / 2) = radius.
    // The math is: drawX + (pointer.x * zoom) = radius  =>  drawX = radius - (pointer.x * zoom)
    const radius = diameter / 2;

    // Calculate the scaled dimensions of the background
    const scaledBgWidth = this.renderStamp.width * baseScaleX * zoom;
    const scaledBgHeight = this.renderStamp.height * baseScaleY * zoom;

    // 2. Clamp the internal projection so the edge of the renderStamp is never pulled inside the lens
    // The background is drawn at (drawX, drawY).
    // It cannot be drawn further right than 0 (which would show the left edge).
    // It cannot be drawn further left than (diameter - scaledBgWidth) (which would show the right edge).
    const minDrawX = Math.min(0, diameter - scaledBgWidth);
    const maxDrawX = 0;
    const minDrawY = Math.min(0, diameter - scaledBgHeight);
    const maxDrawY = 0;

    const rawDrawX = radius - (pointer.x * zoom);
    const rawDrawY = radius - (pointer.y * zoom);

    const drawX = Phaser.Math.Clamp(rawDrawX, minDrawX, maxDrawX);
    const drawY = Phaser.Math.Clamp(rawDrawY, minDrawY, maxDrawY);

    // Calculate clamped pointer offsets for drawing the eggs and symbols
    // correctly relative to the clamped background projection.
    // Normally, the egg projection is: radius + (egg.x - pointer.x) * zoom
    // Since drawX = rawDrawX = radius - (pointer.x * zoom) when unclamped,
    // this means pointer.x * zoom = radius - drawX.
    // So the egg projection is: drawX + (egg.x * zoom).
    // This maps seamlessly to the clamped drawX and drawY!

    this.zoomedView.draw(this.renderStamp, drawX, drawY);

    // Single pass for visibility update and drawing
    // ⚡ Bolt Optimization: Replace forEach with fast for loop in update loop
    const children = this.eggs.getChildren();
    const px = pointer.x;
    const py = pointer.y;
    const magnifierRadiusSq = radius * radius; // ⚡ Bolt Optimization: Hoisted standard magnifying glass coverage calculation
    for (let i = children.length - 1; i >= 0; i--) {
      const egg = children[i];
      if (egg && egg.active) {
          // Update visibility based on FINGER (pointer) visual position for the LENS
          // The hit area has expanded significantly, so the eggs should appear when hovered
          // ⚡ Bolt Optimization: Inline distance calculation to avoid function call overhead
          const dx = px - egg.x;
          const dy = py - egg.y;
          const distToPointerSq = dx * dx + dy * dy;

          const alpha = distToPointerSq < magnifierRadiusSq ? 1 : 0;
          egg.setAlpha(alpha);
          if (egg.symbolSprite) {
            egg.symbolSprite.setAlpha(alpha);
          }

          if (egg.visible && egg.alpha > 0) {
             // Draw Egg using renderStamp
             this.renderStamp.setTexture(egg.texture.key, egg.frame.name);
             this.renderStamp.setAngle(egg.angle);
             this.renderStamp.setFlipX(egg.flipX);
             this.renderStamp.setFlipY(egg.flipY);
             this.renderStamp.setOrigin(0.5, 0.5);
             this.renderStamp.setScale(egg.scaleX * zoom, egg.scaleY * zoom);

             // Offset logic: since the background is drawn at (drawX, drawY),
             // the egg (which is at egg.x on the unscaled screen) must be drawn at drawX + (egg.x * zoom).
             const eggDrawX = drawX + (egg.x * zoom);
             const eggDrawY = drawY + (egg.y * zoom);

             this.zoomedView.draw(this.renderStamp, eggDrawX, eggDrawY);

             // Draw Symbol using renderStamp
             if (egg.symbolSprite && egg.symbolSprite.active && egg.symbolSprite.visible) {
                 this.renderStamp.setTexture(egg.symbolSprite.texture.key, egg.symbolSprite.frame.name);
                 this.renderStamp.setAngle(egg.symbolSprite.angle);
                 this.renderStamp.setFlipX(egg.symbolSprite.flipX);
                 this.renderStamp.setFlipY(egg.symbolSprite.flipY);
                 this.renderStamp.setScale(egg.symbolSprite.scaleX * zoom, egg.symbolSprite.scaleY * zoom);

                 const symDrawX = drawX + (egg.symbolSprite.x * zoom);
                 const symDrawY = drawY + (egg.symbolSprite.y * zoom);
                 this.zoomedView.draw(this.renderStamp, symDrawX, symDrawY);
             }
          }
      }
    }

    // Handle Button Hover and Cursor Swap
    let isHoveringButton = false;

    // ⚡ Bolt Optimization: Replace forEach with fast for loop
    for (let i = 0, len = this.uiButtons.length; i < len; i++) {
        const btn = this.uiButtons[i];
        if (btn && btn.active) {
             // Store base scale if not already stored
             if (btn.baseScaleX === undefined) btn.baseScaleX = btn.scaleX;
             if (btn.baseScaleY === undefined) btn.baseScaleY = btn.scaleY;

                 // ⚡ Bolt Optimization: Avoid expensive getBounds() matrix calculations in 60fps update loop
                 // Since UI buttons are unrotated and have origin (0, 0), we can use simple AABB math
                 const left = btn.x;
                 const top = btn.y;
                 const right = left + btn.displayWidth;
                 const bottom = top + btn.displayHeight;

                 if (pointer.x >= left && pointer.x <= right && pointer.y >= top && pointer.y <= bottom) {
                 isHoveringButton = true;
                 if (!btn.isHovered) {
                     btn.isHovered = true;
                     // Use absolute scale based on baseScale
                     this.tweens.add({
                         targets: btn,
                         scaleX: btn.baseScaleX * 1.1,
                         scaleY: btn.baseScaleY * 1.1,
                         duration: 100,
                         ease: 'Sine.easeInOut'
                     });
                 }
             } else {
                 if (btn.isHovered) {
                     btn.isHovered = false;
                     // Return to base scale
                     this.tweens.add({
                         targets: btn,
                         scaleX: btn.baseScaleX,
                         scaleY: btn.baseScaleY,
                         duration: 100,
                         ease: 'Sine.easeInOut'
                     });
                 }
             }
        }
    }

    if (isHoveringButton) {
        if (this.magnifyingGlass) this.magnifyingGlass.setVisible(false);
        if (this.zoomedView) this.zoomedView.setVisible(false);
        if (this.maskGraphics) this.maskGraphics.setVisible(false);
    } else {
        if (this.magnifyingGlass) {
             this.magnifyingGlass.setVisible(true);
             this.magnifyingGlass.setDisplaySize(150 * scale, 187.5 * scale);
             // position is now handled smoothly at the top of update()
        }
        if (this.zoomedView) this.zoomedView.setVisible(true);
        if (this.maskGraphics) this.maskGraphics.setVisible(true);
    }
  }
}

class EggZamRoom extends Phaser.Scene {

  playGoodEggAnimation(eggImage, symbolImage, onCompleteCallback) {
    this.playVideo('eggzam-eggcellent', onCompleteCallback);

    const scale = this.gameScale;
    const isDesktop = this.sys.game.device.os.desktop;
    const assetScale = isDesktop ? scale : scale * 2;
    const startX = eggImage.x;
    const startY = eggImage.y;
    const targetY = startY - (80 * assetScale);

    const halo = this.add.image(startX, targetY - (40 * assetScale), 'halo').setDepth(2).setAlpha(0).setScale(0.5 * assetScale);

    // Sparkles Emitter
    const sparkles = this.add.particles(0, 0, 'sparkle', {
        x: startX,
        y: targetY,
        speed: { min: -100 * assetScale, max: 100 * assetScale },
        angle: { min: 0, max: 360 },
        scale: { start: 1 * assetScale, end: 0 },
        alpha: { start: 1, end: 0 },
        lifespan: 1000,
        frequency: 100,
        blendMode: 'ADD'
    }).setDepth(4);

    this.tweens.add({
        targets: [eggImage, symbolImage].filter(img => img),
        y: targetY,
        duration: 800,
        ease: 'Cubic.easeOut',
        onComplete: () => {
            this.tweens.add({
                targets: halo,
                alpha: 1,
                scaleX: 1.5 * assetScale,
                scaleY: 1.5 * assetScale,
                duration: 500,
                yoyo: true,
                repeat: 1
            });
            this.tweens.add({
                targets: [eggImage, symbolImage].filter(img => img),
                angle: 360,
                duration: 1000,
                ease: 'Sine.easeInOut',
                onComplete: () => {
                    sparkles.stop();
                    this.tweens.add({
                        targets: [eggImage, symbolImage].filter(img => img),
                        y: startY,
                        duration: 800,
                        ease: 'Cubic.easeIn',
                        onComplete: () => {
                            halo.destroy();
                            sparkles.destroy();
                        }
                    });
                }
            });
        }
    });
  }

  playBadEggAnimation(eggImage, symbolImage, onCompleteCallback) {
    this.playVideo('eggzam-stinky', onCompleteCallback);

    const scale = this.gameScale;
    const isDesktop = this.sys.game.device.os.desktop;
    const assetScale = isDesktop ? scale : scale * 2;
    const startX = eggImage.x;
    const startY = eggImage.y;

    const musicScene = this.scene.get('MusicScene');
    if (musicScene) {
        // Fart sound for eggs-tra stinky eggs
        const fartSound = this.sound.add('fart', { volume: this.registry.get('sfxVolume') ?? 0.5 });
        fartSound.play();
    }

    const gasParticles = this.add.particles(0, 0, 'green-gas', {
        x: startX,
        y: startY,
        speed: { min: 20 * assetScale, max: 100 * assetScale },
        angle: { min: 0, max: 360 },
        scale: { start: 1 * assetScale, end: 8 * assetScale }, // Huge scale to blur the edges
        alpha: { start: 0.9, end: 0 },
        lifespan: 3000,
        frequency: 30, // Faster emission
        blendMode: 'NORMAL', // Normal mode helps hide the underlying particles making it look like a dense cloud
        rotate: { min: -10, max: 10 },
        gravityY: -20 * assetScale, // Slowly float upwards
    }).setDepth(4);

    this.tweens.add({
        targets: [eggImage, symbolImage].filter(img => img),
        angle: { from: -15, to: 15 },
        duration: 100,
        yoyo: true,
        repeat: 5,
        onComplete: () => {
            this.tweens.add({
                targets: [eggImage, symbolImage].filter(img => img),
                x: this.cameras.main.width + (200 * assetScale),
                y: -100 * assetScale,
                angle: 720,
                duration: 800,
                ease: 'Back.in',
                onComplete: () => {
                    gasParticles.stop();
                    this.time.delayedCall(1000, () => {
                        gasParticles.destroy();
                    });
                }
            });
        }
    });
  }

  playIncorrectAnimation(onCompleteCallback) {
      this.playVideo('eggzam-incorrect', onCompleteCallback);
  }

  constructor() {
    super({ key: 'EggZamRoom' });
    this.displayedEggImage = null;
    this.displayedSymbolImage = null;
    this.explanationText = null;
    this.noEggsText = null;
    this.currentEgg = null;
    this.gameScale = 1;
    this.background = null;
    this.examiner = null;
    this.symbolResultDiag = null;
    this.eggZitButton = null;
    this.scoreImage = null;
    this.scoreText = null;
    this.correctText = null;
    this.leftBottleZone = null;
    this.rightBottleZone = null;
    this.fingerCursor = null;
    this.ambientTimer = null;
    this.currentVideo = null;
  }

  resetAmbientTimer() {
      if (this.ambientTimer) {
          this.ambientTimer.remove(false);
      }

      const playAmbient = () => {
          if (this.currentVideo && this.currentVideo.active) {
             this.resetAmbientTimer();
             return;
          }

          this.playVideo(this.registry.get('lastAmbient') === 1 ? 'eggzam-ambient-2' : 'eggzam-ambient-1', () => {
              this.registry.set('lastAmbient', this.registry.get('lastAmbient') === 1 ? 2 : 1);
              this.resetAmbientTimer();
          });
      };

      this.ambientTimer = this.time.delayedCall(10000, playAmbient, [], this);
  }

  stopCurrentVideo() {
      if (this.currentVideo) {
          this.currentVideo.destroy();
          this.currentVideo = null;

          if (this.actionButtons && !this.explanationText?.active) {
              this.actionButtons.forEach(btn => btn.setVisible(true));
          }
      }
  }

  playVideo(videoKey, onComplete) {
      this.stopCurrentVideo();
      if (!this.cache.video.exists(videoKey)) {
          console.warn(`Video ${videoKey} not found in cache. Skipping video and firing complete.`);
          if (onComplete) onComplete();
          return;
      }

      try {
          const width = this.game.config.width;
          const height = this.game.config.height;
          const scaleX = width / 1280;
          const scaleY = height / 720;
          const coverScale = Math.max(scaleX, scaleY);

          this.currentVideo = this.add.video(width/2, height/2, videoKey)
              .setDepth(1)
              .setOrigin(0.5, 0.5);

          this.currentVideo.once('play', () => {
              if (this.currentVideo && this.currentVideo.active) {
                  this.currentVideo.setDisplaySize(1168 * coverScale, 784 * coverScale);
              }
          });

          this.currentVideo.play();

          if (this.actionButtons && !videoKey.includes('ambient')) {
              this.actionButtons.forEach(btn => btn.setVisible(false));
          }

          this.currentVideo.on('complete', () => {
            this.stopCurrentVideo();
            if (onComplete) onComplete();
          });

          this.currentVideo.on('error', () => {
            this.stopCurrentVideo();
            if (onComplete) onComplete();
          });
      } catch (error) {
          console.error(`Error playing video ${videoKey}:`, error);
          this.stopCurrentVideo();
          if (onComplete) onComplete();
      }
  }

  preload() {
    // Assets are preloaded in MainMenu
    this.load.on('loaderror', (file) => {
      console.error(`EggZamRoom: Load error: Key='${file.key}', URL='${file.url}'`);
    });

    this.load.on('filecomplete', (key, type, data) => {
    });
  }

  create() {
    this.input.setDefaultCursor('none');

    // Background lazy-load core EggZam videos
    if (!this.registry.get('eggzamVideosLoaded')) {
        this.registry.set('eggzamVideosLoaded', true);
        this.load.video('eggzam-eggcellent', 'assets/video/eggzam-eggcellent.mp4');
        this.load.video('eggzam-stinky', 'assets/video/eggzam-stinky.mp4');
        this.load.video('eggzam-incorrect', 'assets/video/eggzam-incorrect-classification.mp4');
        this.load.start();
    }
    // Background lazy-load ambient EggZam videos
    if (!this.registry.get('eggzamAmbientVideosLoaded')) {
        this.registry.set('eggzamAmbientVideosLoaded', true);
        this.load.video('eggzam-ambient-1', 'assets/video/eggzam-ambient-1.mp4');
        this.load.video('eggzam-ambient-2', 'assets/video/eggzam-ambient-2.mp4');
        this.load.start();
    }

    if (!this.registry.has('lastAmbient')) {
        this.registry.set('lastAmbient', 1);
    }
    this.resetAmbientTimer();

    // Generate missing particle textures dynamically
    if (!this.textures.exists('halo')) {
        const haloGraphics = this.make.graphics({x:0, y:0, add:false});
        haloGraphics.fillStyle(0xffff00, 0.4);
        haloGraphics.fillCircle(50, 50, 50);
        haloGraphics.fillStyle(0xffff00, 0.8);
        haloGraphics.fillCircle(50, 50, 40);
        haloGraphics.generateTexture('halo', 100, 100);
    }

    if (!this.textures.exists('sparkle')) {
        // Use Phaser.GameObjects.Star and generate a texture from it safely
        const starObject = new Phaser.GameObjects.Star(this, 10, 10, 4, 2, 10, 0xffffff);
        const renderTexture = this.add.renderTexture(0, 0, 20, 20).setVisible(false);
        renderTexture.draw(starObject, 10, 10);
        renderTexture.saveTexture('sparkle');
        renderTexture.destroy();
        starObject.destroy();
    }

    if (!this.textures.exists('green-gas')) {
        const gasGraphics = this.make.graphics({x:0, y:0, add:false});
        // Create a softer, larger radial gradient-like gas puff by stacking low-opacity circles
        gasGraphics.fillStyle(0x55aa00, 0.1);
        gasGraphics.fillCircle(30, 30, 30);
        gasGraphics.fillStyle(0x449900, 0.2);
        gasGraphics.fillCircle(30, 30, 20);
        gasGraphics.fillStyle(0x338800, 0.3);
        gasGraphics.fillCircle(30, 30, 10);
        gasGraphics.generateTexture('green-gas', 60, 60);
    }

    const width = this.game.config.width;
    const height = this.game.config.height;
    const scaleX = width / 1280;
    const scaleY = height / 720;
    this.gameScale = Math.min(scaleX, scaleY);
    const uiScale = Math.min(scaleX, scaleY);
    const coverScale = Math.max(scaleX, scaleY);

    this.cameras.main.setBounds(0, 0, width, height);
    this.cameras.main.setViewport(0, 0, width, height);
    this.cameras.main.setPosition(0, 0);

    this.background = this.add.image(width/2, height/2, 'eggzam-keyframe')
      .setDepth(0)
      .setDisplaySize(1168 * coverScale, 784 * coverScale);

    const isDesktop = this.sys.game.device.os.desktop;
    const assetScale = isDesktop ? this.gameScale : this.gameScale * 1.75;

    // Use UI scale to keep UI elements proportionate and contained
    const offsetX = (width - 1280 * uiScale) / 2;
    const offsetY = (height - 720 * uiScale) / 2;

    // Store scale params for update/resize if needed
    this.uiParams = { offsetX, offsetY, uiScale, assetScale };

    this.symbolResultDiag = this.add.image(offsetX + 200 * uiScale, offsetY + 50 * uiScale, 'symbol-result-summary-diag')
      .setOrigin(0, 0)
      .setDepth(1)
      .setDisplaySize(900 * uiScale, 600 * uiScale)
      .setAlpha(0);

    this.eggZitButton = this.add.image(0, 200 * uiScale, 'egg-zit-button')
      .setOrigin(0, 0)
      .setDisplaySize(150 * uiScale, 131 * uiScale)
      .setInteractive()
      .on('pointerdown', () => {
          this.time.delayedCall(150, () => {
              this.scene.start('MapScene');
          });
      })
      .setDepth(4)
      .setScrollFactor(0);
    addButtonInteraction(this, this.eggZitButton, 'drive1');

    this.scoreImage = this.add.image(0, 0, 'score')
      .setOrigin(0, 0)
      .setDisplaySize(200 * uiScale, 200 * uiScale)
      .setDepth(4)
      .setScrollFactor(0);
    const foundEggsCount = this.registry.get('foundEggs').length;

    this.scoreText = this.add.text(40 * uiScale, 90 * uiScale, `${foundEggsCount}/${TOTAL_EGGS}`, {
      fontSize: `${42 * uiScale}px`,
      fill: '#000',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#fff',
      strokeThickness: 6 * uiScale
    }).setDepth(5);

    if (!this.registry.has('correctCategorizations')) {
      this.registry.set('correctCategorizations', 0);
    }

    this.correctText = this.add.text(100 * uiScale, 150 * uiScale, `Correct: ${this.registry.get('correctCategorizations')}`, {
      fontSize: `${32 * uiScale}px`,
      fill: '#000',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#fff',
      strokeThickness: 6 * uiScale
    }).setOrigin(0.5).setDepth(5);

    const showExplanation = (isCorrect, guessText) => {
        const data = this.currentEgg.symbolData;
        const eggId = this.currentEgg.eggId;
        const scale = this.gameScale;
        const isDesktop = this.sys.game.device.os.desktop;
        const assetScale = isDesktop ? scale : scale * 1.5;

        const executeExplanationPopup = () => {
            const musicScene = this.scene.get('MusicScene');
            if (isCorrect) {
                if (musicScene) {
                    musicScene.playSFX('success');
                }
                const correctCount = this.registry.get('correctCategorizations') + 1;
                this.registry.set('correctCategorizations', correctCount);
                this.correctText.setText(`Correct: ${correctCount}`);
                let currentScore = this.registry.get('currentScore');
                currentScore += 5;
                this.registry.set('currentScore', currentScore);
                const highScore = this.registry.get('highScore');
                if (currentScore > highScore) {
                  this.registry.set('highScore', currentScore);
                  try { localStorage.setItem('highScore', currentScore); } catch (e) { console.warn('localStorage error', e); }
                }
            } else {
                if (musicScene) {
                    musicScene.playSFX('error');
                }
            }

            this.currentEgg.categorized = true;
            saveGameState(this.registry);

            if (this.explanationText) this.explanationText.destroy();

            this.explanationText = this.add.container(width / 2, height / 2).setDepth(100);

        const bgWidth = Math.min(width * 0.95, 1280 * assetScale);
        const bgHeight = Math.min(height * 0.95, 720 * assetScale);

        const bg = this.add.graphics();
        bg.fillStyle(0xfff8dc, 1);
        bg.fillRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * assetScale);
        bg.lineStyle(8 * assetScale, 0x8b4513, 1);
        bg.strokeRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * assetScale);

        // Block clicks behind the popup
        bg.setInteractive(new Phaser.Geom.Rectangle(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight), Phaser.Geom.Rectangle.Contains);

        // Header Elements (Percentage based Y)
        const title = this.add.text(0, -bgHeight * 0.42, data.name || "Symbol", {
            fontSize: `${36 * assetScale}px`, fill: '#8b4513', fontStyle: 'bold', fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5);

        // Your Guess (Percentage based Y) - reduced whitespace and removed newline
        const guessDisplay = this.add.text(0, -bgHeight * 0.33, `Your Guess: ${guessText}`, {
            fontSize: `${24 * assetScale}px`, fill: '#333', fontStyle: 'bold', fontFamily: 'Comic Sans MS', align: 'center'
        }).setOrigin(0.5, 0.5);

        announceToScreenReader(isCorrect ? "Correct!" : "Incorrect!");

        // Result Text (Percentage based Y) - reduced whitespace
        const resultText = this.add.text(0, -bgHeight * 0.25, isCorrect ? "Correct!" : "Incorrect!", {
            fontSize: `${28 * assetScale}px`,
            fill: isCorrect ? '#008000' : '#d32f2f',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#fff',
            strokeThickness: 6 * assetScale
        }).setOrigin(0.5, 0.5);

        // Explanation Text (Percentage based Y) - moved up due to reduced whitespace
        const expText = this.add.text(0, -bgHeight * 0.04, data.explanation, {
            fontSize: `${28 * assetScale}px`, fill: '#000', fontFamily: 'Comic Sans MS',
            wordWrap: { width: bgWidth * 0.9, useAdvancedWrap: true }, align: 'center'
        }).setOrigin(0.5);

        // Scripture Link (Percentage based Y)
        const scriptureElements = [];
        const scriptures = data.scripture.split(',').map(s => s.trim());
        let totalWidth = 0;
        const tempText = this.add.text(0, 0, '', {
            fontSize: `${24 * assetScale}px`, fontStyle: 'italic', fontFamily: 'Comic Sans MS'
        });

        scriptures.forEach((scripture, index) => {
            tempText.setText(scripture);
            totalWidth += tempText.width;
            if (index < scriptures.length - 1) {
                tempText.setText(', ');
                totalWidth += tempText.width;
            }
        });

        let currentX = -totalWidth / 2;
        const scriptureY = bgHeight * 0.36; // scripture positioned at the bottom of the popup

        scriptures.forEach((scripture, index) => {
            const verseText = this.add.text(currentX, scriptureY, scripture, {
                fontSize: `${24 * assetScale}px`, fill: '#0000ee', fontStyle: 'italic', fontFamily: 'Comic Sans MS'
            }).setOrigin(0, 0.5).setInteractive();

            verseText.on('pointerdown', (p, x, y, event) => {
                event.stopPropagation();
                const link = parseScriptureLink(scripture);
                if (link) {
                    const iframeOverlay = document.createElement('div');
                    iframeOverlay.style.position = 'fixed';
                    iframeOverlay.style.top = '0';
                    iframeOverlay.style.left = '0';
                    iframeOverlay.style.width = '100vw';
                    iframeOverlay.style.height = '100vh';
                    iframeOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                    iframeOverlay.style.zIndex = '9999';
                    iframeOverlay.style.display = 'flex';
                    iframeOverlay.style.flexDirection = 'column';
                    iframeOverlay.style.alignItems = 'center';
                    iframeOverlay.style.justifyContent = 'center';

                    const iframe = document.createElement('iframe');
                    iframe.src = link;
                    iframe.style.width = '100%';
                    iframe.style.height = '100%';
                    iframe.style.border = '4px solid white';
                    iframe.style.borderRadius = '10px';
                    iframe.style.backgroundColor = 'white';

                    const closeBtn = document.createElement('button');
                    closeBtn.textContent = '\u2716';
                    closeBtn.style.position = 'absolute';
                    closeBtn.style.top = '10px';
                    closeBtn.style.right = '10px';
                    closeBtn.style.width = '60px';
                    closeBtn.style.height = '60px';
                    closeBtn.style.padding = '0';
                    closeBtn.style.fontSize = '32px';
                    closeBtn.style.fontWeight = 'bold';
                    closeBtn.style.color = 'white';
                    closeBtn.style.backgroundColor = '#ff0000';
                    closeBtn.style.border = '4px solid #8b4513';
                    closeBtn.style.borderRadius = '50%';
                    closeBtn.style.cursor = 'pointer';
                    closeBtn.style.fontFamily = '"Comic Sans MS", cursive, sans-serif';
                    closeBtn.style.display = 'flex';
                    closeBtn.style.alignItems = 'center';
                    closeBtn.style.justifyContent = 'center';

                    const closeIframe = () => {
                        iframeOverlay.remove();
                        window.removeEventListener('keydown', iframeKeyHandler);
                    };

                    closeBtn.onclick = closeIframe;

                    const iframeKeyHandler = (e) => {
                        if (e.code === 'Escape' || e.code === 'Enter') {
                            closeIframe();
                        }
                    };
                    window.addEventListener('keydown', iframeKeyHandler);

                    iframeOverlay.appendChild(closeBtn);
                    iframeOverlay.appendChild(iframe);
                    const targetContainer = document.fullscreenElement || document.webkitFullscreenElement || document.body;
                    targetContainer.appendChild(iframeOverlay);
                }
            });

            scriptureElements.push(verseText);
            currentX += verseText.width;

            if (index < scriptures.length - 1) {
                const commaText = this.add.text(currentX, scriptureY, ', ', {
                    fontSize: `${24 * assetScale}px`, fill: '#000', fontStyle: 'italic', fontFamily: 'Comic Sans MS'
                }).setOrigin(0, 0.5);
                scriptureElements.push(commaText);
                currentX += commaText.width;
            }
        });
        tempText.destroy();

        // Position elements in top corners, aligned equally with nearest borders
        // The dialog border is at x: -bgWidth/2 to +bgWidth/2, y: -bgHeight/2 to +bgHeight/2
        // We add an equal inset (e.g. 25px * assetScale) for top, left, and right
        const cornerInset = -10 * assetScale;
        const cornerY = -bgHeight/2 + cornerInset;
        
        // Egg aligned to Top-Left corner
        // Origin of image is 0.5, so we shift it down and right by half its size
        const eggSizeW = 80 * assetScale;
        const eggSizeH = 100 * assetScale;
        const eggX = -bgWidth/2 + cornerInset + eggSizeW/2;
        const eggImg = this.add.image(eggX, cornerY + eggSizeH/2, `egg-${eggId}`).setDisplaySize(eggSizeW, eggSizeH);

        // Symbol image if exists
        let symbolImgSmall = null;
        if (data && data.filename && this.textures.exists(data.filename)) {
            symbolImgSmall = this.add.image(eggX, cornerY + eggSizeH/2, data.filename).setDisplaySize(eggSizeW, eggSizeH);
        }

        // Massive Red X Close Button aligned to Top-Right corner
        // Matching the egg size for consistency
        const closeBtnSize = 80 * assetScale;
        const closeBtnX = bgWidth/2 - cornerInset - closeBtnSize/2;
        const closeBtnContainer = this.add.container(closeBtnX, cornerY + closeBtnSize/2);

        const closeBtnBg = this.add.graphics();
        closeBtnBg.fillStyle(0xff0000, 1);
        closeBtnBg.lineStyle(4 * assetScale, 0x8b4513, 1); // Brown stroke to match dialog
        // Draw a circle for the X button
        closeBtnBg.fillCircle(0, 0, closeBtnSize/2);
        closeBtnBg.strokeCircle(0, 0, closeBtnSize/2);

        const closeBtnText = this.add.text(0, 0, '\u2716', {
            fontSize: `${48 * assetScale}px`,
            fill: '#ffffff',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5, 0.5);

        closeBtnContainer.add([closeBtnBg, closeBtnText]);
        // Set interactive area for a circle
        closeBtnContainer.setSize(closeBtnSize, closeBtnSize);
        closeBtnContainer.setInteractive();
        
        // Add hand cursor manually as setInteractive config above doesn't support it directly in this shorthand
        closeBtnContainer.input.cursor = 'pointer';

        closeBtnContainer.baseScaleX = 1;
        closeBtnContainer.baseScaleY = 1;

        addButtonInteraction(this, closeBtnContainer, 'menu-click');

        const dismissPopup = () => {
            if (!this.explanationText) return;
            this.tweens.add({
                targets: this.explanationText, scaleX: 0, scaleY: 0, duration: 200, ease: 'Back.in',
                onComplete: () => {
                    this.explanationText.destroy();
                    this.explanationText = null;
                    if (!isCorrect) {
                        this.currentEgg = null;
                    }
                    this.displayRandomEggInfo();
                    window.removeEventListener('keydown', this.popupKeyHandler);
                }
            });
        };

        closeBtnContainer.on('pointerdown', () => {
            this.time.delayedCall(100, dismissPopup);
        });

        this.popupKeyHandler = (e) => {
            if (e.code === 'Escape' || e.code === 'Enter') {
                dismissPopup();
            }
        };
        window.addEventListener('keydown', this.popupKeyHandler);

        const elementsToAdd = [bg, title, guessDisplay, resultText, expText, ...scriptureElements, eggImg];
        if (symbolImgSmall) elementsToAdd.push(symbolImgSmall);
        elementsToAdd.push(closeBtnContainer);

        this.explanationText.add(elementsToAdd);

        this.explanationText.setScale(0);
        this.tweens.add({ targets: this.explanationText, scaleX: 1, scaleY: 1, duration: 300, ease: 'Back.out' });

        // Removed bg click dismiss
        };

        if (isCorrect) {
            if (data.category === 'Christian') {
                this.playGoodEggAnimation(this.displayedEggImage, this.displayedSymbolImage, executeExplanationPopup);
            } else if (data.category === 'Pagan') {
                this.playBadEggAnimation(this.displayedEggImage, this.displayedSymbolImage, executeExplanationPopup);
            } else {
                executeExplanationPopup();
            }
        } else {
            this.playIncorrectAnimation(executeExplanationPopup);
        }
    };

    const btnScale = uiScale * 0.4;
    const centerBottomX = offsetX + (1280 * uiScale) / 2;
    const centerBottomY = offsetY + (720 * uiScale) - (100 * uiScale);

    const buttonSpacing = 120 * uiScale;

    // Eggs-tra Stinky on the left, Egg-cellent on the right
    const stinkyBtn = this.add.sprite(centerBottomX - buttonSpacing, centerBottomY, 'eggs-tra-stinky-button', 'Symbol 10000')
        .setScale(btnScale)
        .setDepth(90)
        .setInteractive();

    stinkyBtn.on('pointerover', () => {
        stinkyBtn.setFrame('Symbol 10003');
    });

    stinkyBtn.on('pointerout', () => {
        stinkyBtn.setFrame('Symbol 10000');
    });

    stinkyBtn.on('pointerdown', () => {
      if (this.currentVideo && this.currentVideo.active && this.currentVideo.video.src.includes('ambient')) {
          this.stopCurrentVideo();
      }
      this.resetAmbientTimer();
      this.sound.play('menu-click', { volume: this.registry.get('sfxVolume') ?? 0.5 });
      if (this.currentEgg && !this.currentEgg.categorized && !this.explanationText?.active && !this.currentVideo) {
        showExplanation(this.currentEgg.symbolData.category === 'Pagan', 'Eggs-tra Stinky');
      }
    });

    const eggCellentBtn = this.add.sprite(centerBottomX + buttonSpacing, centerBottomY, 'egg-cellent-button')
        .setScale(btnScale)
        .setDepth(90)
        .setInteractive();

    eggCellentBtn.on('pointerover', () => {
        eggCellentBtn.setFrame('Eggcellent0004');
    });

    eggCellentBtn.on('pointerout', () => {
        eggCellentBtn.setFrame('Eggcellent0000');
    });

    eggCellentBtn.on('pointerdown', () => {
        if (this.currentVideo && this.currentVideo.active && this.currentVideo.video.src.includes('ambient')) {
            this.stopCurrentVideo();
        }
        this.resetAmbientTimer();
        this.sound.play('menu-click', { volume: this.registry.get('sfxVolume') ?? 0.5 });
        if (this.currentEgg && !this.currentEgg.categorized && !this.explanationText?.active && !this.currentVideo) {
            showExplanation(this.currentEgg.symbolData.category === 'Christian', 'Egg-cellent');
        }
    });

    this.actionButtons = [stinkyBtn, eggCellentBtn];

    this.displayRandomEggInfo();

    if (!this.sys.game.device.os.desktop) {
      this.fingerCursor = null;
    } else {
      this.fingerCursor = this.add.image(0, 0, 'finger-cursor')
        .setOrigin(0, 0)
        .setAngle(0)
        .setDisplaySize(50 * this.gameScale, 75 * this.gameScale)
        .setDepth(111111); // Ensure it renders above the popup modal (depth 100)
    }
  }

  displayRandomEggInfo() {
    const foundEggs = this.registry.get('foundEggs');
    const width = this.game.config.width;
    const height = this.game.config.height;

    if (this.currentEgg === null || this.currentEgg.categorized) {
      const uncategorizedEggs = foundEggs.filter(egg => !egg.categorized);
      if (uncategorizedEggs.length > 0) {
        this.currentEgg = Phaser.Utils.Array.GetRandom(uncategorizedEggs);
      } else {
        this.currentEgg = null;
        if (this.noEggsText) this.noEggsText.destroy();
        const ctaText = foundEggs.length < TOTAL_EGGS
            ? "All collected eggs categorized!\nReturn to the map to find more."
            : "All eggs categorized!\nHappy Easter!";
        // Position it higher so it isn't blocked by the larger mobile machine
        const isDesktop = this.sys.game.device.os.desktop;
        const textY = isDesktop ? 0.25 * height : 0.15 * height;
        this.noEggsText = this.add.text((0.36 * width), textY, ctaText, {
          fontSize: `${(isDesktop ? 28 : 40) * this.gameScale}px`,
          fill: '#000',
          fontStyle: 'bold',
          fontFamily: 'Comic Sans MS',
          stroke: '#fff',
          strokeThickness: 3 * this.gameScale,
          wordWrap: { width: 1200 * this.gameScale, useAdvancedWrap: true }
        }).setOrigin(0, 0).setDepth(10);

        if (foundEggs.length === TOTAL_EGGS) {
          // Summary Panel
          // Use an origin top-left style like the desktop, but responsive to mobile scaling
          const summaryContainer = this.add.container(0.36 * width, textY + 80 * this.gameScale).setDepth(100);

          const holyEggs = foundEggs.filter(e => e.symbolData && e.symbolData.category === 'Christian').length;
          const worldlyEggs = foundEggs.filter(e => e.symbolData && e.symbolData.category === 'Pagan').length;

          // Increase panel sizes for mobile readability
          const panelWidth = 500 * this.gameScale;
          const panelHeight = 320 * this.gameScale;

          const panelBg = this.add.graphics();
          panelBg.fillStyle(0xfff8dc, 1);
          panelBg.lineStyle(6 * this.gameScale, 0x8b4513, 1);
          panelBg.fillRoundedRect(0, 0, panelWidth, panelHeight, 20 * this.gameScale);
          panelBg.strokeRoundedRect(0, 0, panelWidth, panelHeight, 20 * this.gameScale);

          // User requested score and title to be different colors, sizes, and layout to prevent overlap
          const titleText = this.add.text(20 * this.gameScale, 40 * this.gameScale, 'Final EggZam!', {
              fontSize: `${(isDesktop ? 32 : 36) * this.gameScale}px`,
              fill: '#8b4513',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0, 0.5);

          const currentScore = this.registry.get('currentScore') || 0;
          // Use a carriage return and slightly smaller font on mobile, different color so they are distinct
          const scoreDisplay = isDesktop ? `Score: ${currentScore}` : `Score:\n${currentScore}`;
          const scoreTextLabel = this.add.text(panelWidth - 20 * this.gameScale, 40 * this.gameScale, scoreDisplay, {
              fontSize: `${(isDesktop ? 32 : 28) * this.gameScale}px`,
              fill: isDesktop ? '#8b4513' : '#d32f2f',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS',
              align: 'right'
          }).setOrigin(1, 0.5);

          const holyText = this.add.text(panelWidth / 2, 100 * this.gameScale, `Egg-cellent Eggs: ${holyEggs} / 30`, {
              fontSize: `${(isDesktop ? 24 : 30) * this.gameScale}px`,
              fill: '#008000',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5);

          const worldlyText = this.add.text(panelWidth / 2, 150 * this.gameScale, `Eggs-tra Stinky Eggs: ${worldlyEggs} / 30`, {
              fontSize: `${(isDesktop ? 24 : 30) * this.gameScale}px`,
              fill: '#d32f2f',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5);

          const totalText = this.add.text(panelWidth / 2, 200 * this.gameScale, `Total Categorized: 60/60`, {
              fontSize: `${(isDesktop ? 24 : 30) * this.gameScale}px`,
              fill: '#000000',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5);

          // PLAY AGAIN Button inside Summary Panel
          const playBtnContainer = this.add.container(panelWidth / 2, 260 * this.gameScale).setDepth(101);

          const playBtnWidth = 280 * this.gameScale;
          const playBtnHeight = 60 * this.gameScale;

          const playBtnBg = this.add.graphics();
          playBtnBg.fillStyle(0xffff00, 1);
          playBtnBg.lineStyle(4 * this.gameScale, 0x000000, 1);
          playBtnBg.fillRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 15 * this.gameScale);
          playBtnBg.strokeRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 15 * this.gameScale);

          const playBtnText = this.add.text(0, 0, 'PLAY AGAIN', {
              fontSize: `${(isDesktop ? 28 : 34) * this.gameScale}px`,
              fill: '#000',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5, 0.5);

          playBtnContainer.add([playBtnBg, playBtnText]);
          playBtnContainer.setSize(playBtnWidth, playBtnHeight);
          playBtnContainer.setInteractive();

          playBtnContainer.baseScaleX = 1;
          playBtnContainer.baseScaleY = 1;

          addButtonInteraction(this, playBtnContainer, 'menu-click');

          const triggerRestart = () => {
              this.time.delayedCall(150, () => {
                  if (this.input.setDefaultCursor) this.input.setDefaultCursor('none');
                  try { localStorage.removeItem('heIsRisenGameState'); } catch (e) { console.warn('localStorage error', e); }
                  initializeGameData(this.registry, this.cache, true);
                  this.scene.start('MapScene');
              });
          };

          playBtnContainer.on('pointerdown', triggerRestart);
          if (this.input.keyboard) {
              this.input.keyboard.once('keydown-SPACE', triggerRestart);
              this.input.keyboard.once('keydown-ENTER', triggerRestart);
          }

          summaryContainer.add([panelBg, titleText, scoreTextLabel, holyText, worldlyText, totalText, playBtnContainer]);
        }
        return;
      }
    }

    if (this.displayedEggImage) this.displayedEggImage.destroy();
    if (this.displayedSymbolImage) this.displayedSymbolImage.destroy();
    if (this.explanationText) this.explanationText.destroy();
    if (this.noEggsText) this.noEggsText.destroy();

    if (this.currentEgg) {
      const { eggId, symbolData } = this.currentEgg;
      const scale = this.gameScale;
      const uiParams = this.uiParams || { offsetX: 0, offsetY: 0, uiScale: scale, assetScale: scale };

      const offsetX = uiParams.offsetX;
      const offsetY = uiParams.offsetY;

      // Target coordinates inside the central egg chamber of the keyframe.
      const eggPosX = offsetX + (1280 * uiParams.uiScale) * 0.44 + (34 * uiParams.uiScale);
      const eggPosY = offsetY + (720 * uiParams.uiScale) * 0.42 + (80 * uiParams.uiScale);
      const symbolPosX = eggPosX;
      const symbolPosY = eggPosY;

      // Make egg as large as possible to fit chamber
      const eggScaleTarget = (240 * uiParams.uiScale) * 0.95;
      const eggHeightTarget = (300 * uiParams.uiScale) * 0.95;

      if (this.textures.exists(`egg-${eggId}`)) {
        this.displayedEggImage = this.add.image(eggPosX, eggPosY, `egg-${eggId}`)
          .setDisplaySize(eggScaleTarget, eggHeightTarget)
          .setAlpha(0.40)
          .setDepth(3);
      }
      if (symbolData && symbolData.filename && this.textures.exists(symbolData.filename)) {
        this.displayedSymbolImage = this.add.image(symbolPosX, symbolPosY, symbolData.filename)
          .setDisplaySize(eggScaleTarget, eggHeightTarget)
          .setAlpha(0.65)
          .setDepth(4);
      }
    }
  }

  update() {
    if (this.fingerCursor) {
      this.fingerCursor.setPosition(this.input.x, this.input.y);
    }
  }
}

function getViewportDimensions() {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  let width, height;
  if (isMobile) {
    width = window.innerWidth;
    height = window.innerHeight;

    // Force landscape dimensions if device is in portrait mode
    if (height > width) {
      if (width < 1000) {
        // Small screens (< 1000px): CSS rotates the view 90 degrees.
        // Phaser needs the swapped landscape dimensions.
        [width, height] = [height, width];
      }
      // Large screens (>= 1000px): Do nothing, let Phaser letterbox 16:9 naturally.
    }
  } else {
    width = window.innerWidth;
    height = document.documentElement.clientHeight;
  }
  return { width, height };
}

const { width, height } = getViewportDimensions();
const config = {
  type: Phaser.AUTO,
  transparent: true,
  width: width,
  height: height,
  disableContextMenu: true,
  audio: {
    disableWebAudio: false
  },
  fps: {
      target: 60,
      forceSetTimeOut: true
  },
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    parent: 'game-container',
  },
  input: {
    activePointers: 3 // Needed for reliable touch
  },
  scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene],
};

const game = new Phaser.Game(config);
window.game = game; // Expose for debugging/verification

// Fix iOS/mobile audio pausing and stuttering issues
game.events.on('ready', () => {
    // Disable automatic pausing to keep game running
    game.events.off('hidden');
    game.events.off('blur');
});

/**
 * Parses a scripture string (e.g., "John 3:16" or "1 Peter 2:4") into a URL.
 */
function parseScriptureLink(scriptureText) {
    if (!scriptureText) return null;

    // Basic mapping of common book names to 3-letter codes used in the target URL
    const bookMap = {
        "genesis": "GEN", "exodus": "EXO", "leviticus": "LEV", "numbers": "NUM", "deuteronomy": "DEU",
        "joshua": "JOS", "judges": "JDG", "ruth": "RUT", "1 samuel": "1SA", "2 samuel": "2SA",
        "1 kings": "1KI", "2 kings": "2KI", "1 chronicles": "1CH", "2 chronicles": "2CH",
        "ezra": "EZR", "nehemiah": "NEH", "esther": "EST", "job": "JOB", "psalms": "PSA", "psalm": "PSA",
        "proverbs": "PRO", "ecclesiastes": "ECC", "song of solomon": "SNG", "isaiah": "ISA",
        "jeremiah": "JER", "lamentations": "LAM", "ezekiel": "EZK", "daniel": "DAN", "hosea": "HOS",
        "joel": "JOL", "amos": "AMO", "obadiah": "OBA", "jonah": "JON", "micah": "MIC",
        "nahum": "NAM", "habakkuk": "HAB", "zephaniah": "ZEP", "haggai": "HAG", "zechariah": "ZEC",
        "malachi": "MAL", "matthew": "MAT", "mark": "MRK", "luke": "LUK", "john": "JHN",
        "acts": "ACT", "romans": "ROM", "1 corinthians": "1CO", "2 corinthians": "2CO",
        "galatians": "GAL", "ephesians": "EPH", "philippians": "PHP", "colossians": "COL",
        "1 thessalonians": "1TH", "2 thessalonians": "2TH", "1 timothy": "1TI", "2 timothy": "2TI",
        "titus": "TIT", "philemon": "PHM", "hebrews": "HEB", "james": "JAS", "1 peter": "1PE",
        "2 peter": "2PE", "1 john": "1JN", "2 john": "2JN", "3 john": "3JN", "jude": "JUD",
        "revelation": "REV"
    };

    // Regex to extract Book, Chapter, and Verse. Handles "1 Peter 2:4-5" or "John 3:16"
    const match = scriptureText.match(/^(\d?\s*[A-Za-z\s]+)\s+(\d+):([\d-]+)/);
    if (match) {
        const rawBook = match[1].trim().toLowerCase();
        const chapter = match[2];
        const verse = match[3];
        const bookCode = bookMap[rawBook];

        if (bookCode) {
            return `https://mt-sin.ai/365DBR/bible.html?book=${bookCode}&chapter=${chapter}&verse=${verse}`;
        }
    }
    return null;
}

/**
 * Adds a "press" animation to a game object on touch.
 * @param {Phaser.Scene} scene - The scene the object belongs to.
 * @param {Phaser.GameObjects.GameObject} button - The game object to animate.
 * @param {string} [soundKey='success'] - The key of the sound to play on click.
 */
function addButtonInteraction(scene, button, soundKey = 'success') {
  button.on('pointerdown', () => {
    // Try to play sound via MusicScene if available to ensure persistence
    const musicScene = scene.scene.get('MusicScene');
    if (musicScene && musicScene.scene.isActive()) {
      musicScene.playSFX(soundKey);
    } else if (soundKey && scene.sound.get(soundKey)) {
      scene.sound.play(soundKey, { volume: scene.registry.get('sfxVolume') ?? 0.5 });
    }

    if (navigator && navigator.vibrate) {
      navigator.vibrate(20);
    }

    if (button.baseScaleX === undefined || !scene.tweens.isTweening(button)) {
        // Capture ONLY if not tweening to avoid capturing a shrunken/grown state
        button.baseScaleX = button.scaleX;
        button.baseScaleY = button.scaleY;
    }

    scene.tweens.killTweensOf(button);
    scene.tweens.add({
      targets: button,
      scaleX: button.baseScaleX * 0.9,
      scaleY: button.baseScaleY * 0.9,
      duration: 50,
      ease: 'Power1'
    });
  });

  const restore = () => {
    if (button.baseScaleX !== undefined && button.baseScaleY !== undefined) {
      scene.tweens.killTweensOf(button);
      scene.tweens.add({
        targets: button,
        scaleX: button.baseScaleX,
        scaleY: button.baseScaleY,
        duration: 100,
        ease: 'Power1'
      });
    }
  };

  button.on('pointerup', restore);
  button.on('pointerout', restore);
}

function resizeGame() {
  const { width, height } = getViewportDimensions();
  game.scale.resize(width, height);
  const canvas = game.canvas;
  canvas.style.width = '100%';
  canvas.style.height = '100%';

  const scaleX = width / 1280;
  const scaleY = height / 720;
  const scale = Math.min(scaleX, scaleY);

  // ⚡ Bolt Optimization: Replace forEach with fast for loop to prevent closure allocations during resize
  const scenes = game.scene.getScenes(true);
  for (let s_idx = 0; s_idx < scenes.length; s_idx++) {
    const scene = scenes[s_idx];
    if (scene.gameScale) scene.gameScale = scale;
    if (scene.cameras && scene.cameras.main) {
      scene.cameras.main.setBounds(0, 0, width, height);
      requestAnimationFrame(() => {
          if (scene.cameras && scene.cameras.main) {
              try { scene.cameras.main.setViewport(0, 0, width, height); } catch(e) {}
          }
      });
      scene.cameras.main.setPosition(0, 0);
    }
    if (scene.scene.key === 'MainMenu') {
      if (scene.introVideo) {
        scene.introVideo.setPosition(width / 2, height / 2);
        requestAnimationFrame(() => {
            if (scene.introVideo && scene.introVideo.active) {
                try { scene.introVideo.setDisplaySize(width, height); } catch (e) {}
            }
        });
      }
      if (scene.startBtnContainer) {
        scene.startBtnContainer.setPosition(width / 2, 580 * scale);
        scene.startBtnContainer.setScale(scale);
        // Reset tween to match new scale to prevent jumps
        if (scene.tweens.isTweening(scene.startBtnContainer)) {
           scene.tweens.killTweensOf(scene.startBtnContainer);
           scene.tweens.add({
              targets: scene.startBtnContainer,
              scaleX: scale * 1.05,
              scaleY: scale * 1.05,
              duration: 800,
              yoyo: true,
              repeat: -1,
              ease: 'Sine.easeInOut'
            });
        }
      }
    }
    if (scene.scene.key === 'MapScene') {
      if (scene.mapImage) {
        const nativeW = scene.mapImage.width || 1376;
        const nativeH = scene.mapImage.height || 768;
        const mapScale = Math.max(width / nativeW, height / nativeH);
        scene.mapImage.setPosition(width/2, height/2);
        scene.mapImage.setScale(mapScale);
      }
      if (scene.mapSections) {
        // ⚡ Bolt Optimization: Replace forEach with fast for loop
        for (let m_idx = 0; m_idx < scene.mapSections.length; m_idx++) {
          const section = scene.mapSections[m_idx];
          if (section.zone) {
            const centerX = section.coords.x;
            const centerY = section.coords.y;

            const nativeW = scene.mapImage ? (scene.mapImage.width || 1376) : 1376;
            const nativeH = scene.mapImage ? (scene.mapImage.height || 768) : 768;
            const mapScale = Math.max(width / nativeW, height / nativeH);

            const mapWidth = nativeW * mapScale;
            const mapHeight = nativeH * mapScale;
            const offsetX = (width - mapWidth) / 2;
            const offsetY = (height - mapHeight) / 2;

            const thumbX = offsetX + centerX * mapScale;
            const thumbY = offsetY + centerY * mapScale;

            section.zone.setPosition(thumbX, thumbY);

            const targetW = section.coords.width * mapScale;
            const thumbScale = targetW / section.coords.width;
            section.zone.setScale(thumbScale);

            if (section.zone.maskGraphics) {
                section.zone.maskGraphics.setPosition(thumbX, thumbY);
                section.zone.maskGraphics.setScale(thumbScale);
            }

            section.zone.baseScaleX = section.zone.scaleX;
            section.zone.baseScaleY = section.zone.scaleY;
          }
        }

        if (scene.stamps) {
            // ⚡ Bolt Optimization: Replace forEach with fast for loop
            for (let st_idx = 0; st_idx < scene.stamps.length; st_idx++) {
                const item = scene.stamps[st_idx];
                if (item.video && item.video.active && item.thumb && item.thumb.active) {
                    const offsetY = 0;
                    item.video.setPosition(item.thumb.x, item.thumb.y + offsetY);

                    // Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const intrinsicHeight = item.video.height || 720;
                  const targetHeight = (item.thumb.height * item.thumb.scaleY) * 1.25;
                  item.video.setScale(targetHeight / intrinsicHeight);
                }
            }
        }
      }
      if (scene.eggsAmminHaul) {
        scene.eggsAmminHaul.setPosition(0, 200 * scale);
        scene.eggsAmminHaul.setDisplaySize(137 * scale, 150 * scale);
      }
      if (scene.scoreImage) {
        scene.scoreImage.setDisplaySize(200 * scale, 200 * scale);
      }
      if (scene.scoreText) {
        const isDesktop = scene.sys.game.device.os.desktop;
        const scoreY = isDesktop ? 125 * scale : 117 * scale;
        scene.scoreText.setPosition(100 * scale, scoreY);
        scene.scoreText.setStyle({
          fontSize: `${(isDesktop ? 32 : 42) * scale}px`,
          strokeThickness: 6 * scale
        });
        const foundEggsCount = scene.registry.get('foundEggs').length;
        scene.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
      }
      if (scene.fingerCursor) {
        scene.fingerCursor.setDisplaySize(50 * scale, 75 * scale);
      }
    }
    if (scene.scene.key === 'SectionHunt') {
      if (scene.sectionImage) {
        scene.sectionImage.setDisplaySize(width, height);
      }
      if (scene.eggs) {
        // ⚡ Bolt Optimization: Replace forEach with fast for loop
        const eggs = scene.eggs.getChildren();
        for (let e_idx = eggs.length - 1; e_idx >= 0; e_idx--) {
          const egg = eggs[e_idx];
          if (egg && egg.active) {
            egg.setDisplaySize(50 * scale, 75 * scale);
            if (egg.symbolSprite) {
              egg.symbolSprite.setDisplaySize(50 * scale, 75 * scale);
            }
          }
        }
      }
      if (scene.eggZitButton) {
        scene.eggZitButton.setPosition(0, 200 * scale);
        scene.eggZitButton.setDisplaySize(150 * scale, 150 * scale);
      }
      if (scene.eggsAmminHaul) {
        scene.eggsAmminHaul.setPosition(0, 350 * scale);
        scene.eggsAmminHaul.setDisplaySize(137 * scale, 150 * scale);
      }
      if (scene.scoreImage) {
        scene.scoreImage.setDisplaySize(200 * scale, 200 * scale);
      }
      if (scene.scoreText) {
        const isDesktop = scene.sys.game.device.os.desktop;
        const scoreY = isDesktop ? 125 * scale : 117 * scale;
        scene.scoreText.setPosition(100 * scale, scoreY);
        scene.scoreText.setStyle({
          fontSize: `${(isDesktop ? 32 : 42) * scale}px`,
          strokeThickness: 6 * scale
        });
        const foundEggsCount = scene.registry.get('foundEggs').length;
        scene.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
      }
      if (scene.zoomedView) {
        // Position set in update
        const diameter = 150 * scale;
        scene.zoomedView.setSize(diameter, diameter);
      }
      if (scene.maskGraphics) {
        scene.maskGraphics.clear();
        scene.maskGraphics.fillCircle(0, 0, 75 * scale);
      }
      if (scene.magnifyingGlass) {
        scene.magnifyingGlass.setDisplaySize(150 * scale, 187.5 * scale);
        scene.magnifyingGlass.setPosition(scene.input.x, scene.input.y);
      }
    }
    if (scene.scene.key === 'UIScene') {
      scene.resize({ width, height });
    }
    if (scene.scene.key === 'EggZamRoom') {
      scene.scene.restart(); // Simplest way to handle resizing complex UI layouts
    }
  }
}

game.events.on('ready', () => {
  resizeGame();

  // Wait a small tick after orientation change to get accurate window dimensions
  const debouncedResize = () => {
    setTimeout(resizeGame, 100);
  };
  window.addEventListener('resize', debouncedResize);
  window.addEventListener('orientationchange', debouncedResize);
});

// Auto-focus the game container for screen readers and keyboard accessibility
window.addEventListener('load', () => {
  const gameContainer = document.getElementById('game-container');
  if (gameContainer) gameContainer.focus();

  // Handle Safari CSS rotation input mapping for portrait phones
  const canvas = document.querySelector('canvas');
  if (!canvas) return;

  const handleTouch = (e) => {
    // Prevent infinite loops from intercepting our own synthetic dispatched events
    if (!e.isTrusted) return;

    // Only intercept if we are actively rotating via CSS in portrait mode on small screens
    const isPortrait = window.innerHeight > window.innerWidth;
    const isSmallScreen = Math.min(window.innerWidth, window.innerHeight) < 1000;

    // Check if the browser natively supports screen orientation lock (usually false on iOS Safari without fullscreen)
    let isLocked = false;
    try {
      if (screen.orientation && screen.orientation.type && screen.orientation.type.includes('landscape')) {
         isLocked = true;
      }
    } catch(err) {}

    if (isPortrait && isSmallScreen && !isLocked) {
      e.preventDefault();
      e.stopPropagation();

      const touches = Array.from(e.changedTouches).map(touch => {
        // Map portrait screen coordinates to rotated landscape canvas coordinates
        // Visual Rotation is: transform: rotate(90deg) translateY(-100%);
        // This means physical Top-Left (0,0) becomes Canvas Top-Right.
        // Screen X becomes Canvas Y
        // Screen Y becomes Canvas Inverse X

        const physicalX = touch.clientX;
        const physicalY = touch.clientY;
        const physicalWidth = window.innerWidth;

        const mappedX = physicalY;
        const mappedY = physicalWidth - physicalX;

        return new Touch({
          identifier: touch.identifier,
          target: canvas,
          clientX: mappedX,
          clientY: mappedY,
          screenX: mappedX,
          screenY: mappedY,
          pageX: mappedX,
          pageY: mappedY
        });
      });

      const syntheticEvent = new TouchEvent(e.type, {
        cancelable: true,
        bubbles: true,
        touches: e.type === 'touchend' ? [] : touches,
        targetTouches: e.type === 'touchend' ? [] : touches,
        changedTouches: touches
      });

      canvas.dispatchEvent(syntheticEvent);
    }
  };

  // Use capture phase to intercept before Phaser's default handlers
  gameContainer.addEventListener('touchstart', handleTouch, { capture: true, passive: false });
  gameContainer.addEventListener('touchmove', handleTouch, { capture: true, passive: false });
  gameContainer.addEventListener('touchend', handleTouch, { capture: true, passive: false });
  gameContainer.addEventListener('touchcancel', handleTouch, { capture: true, passive: false });
});
