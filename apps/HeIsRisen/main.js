// Define all scene classes first
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
        localStorage.setItem('heIsRisenGameState', JSON.stringify(state));
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

                    let loadedCorrect = (savedState.correctCategorizations !== null && savedState.correctCategorizations !== undefined && String(savedState.correctCategorizations).trim() !== '' && typeof savedState.correctCategorizations !== 'object') ? Number(savedState.correctCategorizations) : NaN;
                    if (isNaN(loadedCorrect) || !isFinite(loadedCorrect) || loadedCorrect < 0) loadedCorrect = 0;
                    registry.set('correctCategorizations', loadedCorrect);

                    let loadedScore = (savedState.currentScore !== null && savedState.currentScore !== undefined && String(savedState.currentScore).trim() !== '' && typeof savedState.currentScore !== 'object') ? Number(savedState.currentScore) : NaN;
                    if (isNaN(loadedScore) || !isFinite(loadedScore) || loadedScore < 0) loadedScore = 0;
                    registry.set('currentScore', loadedScore);

                    // Always ensure highScore is loaded/initialized correctly
                    try {
                        let highScoreVal = null;
                        try { highScoreVal = localStorage.getItem('highScore'); } catch (e) { console.warn('localStorage error', e); }
                        let loadedScore = (highScoreVal !== null && highScoreVal !== undefined && String(highScoreVal).trim() !== '' && typeof highScoreVal !== 'object') ? Number(highScoreVal) : NaN;
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
        const sections = mapSections.map(section => ({ name: section.name, eggs: [] }));

        let eggIndex = 0;
        const shuffledSymbols = Phaser.Utils.Array.Shuffle([...(symbolsData ? symbolsData.symbols : [])]);
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

        registry.set('sections', sections);
        registry.set('eggData', eggData);
    }

    if (!registry.has('sections')) registry.set('sections', []);
    if (!registry.has('eggData')) registry.set('eggData', []);
    registry.set('foundEggs', []);
    registry.set('stampedSections', []);
    registry.set('correctCategorizations', 0);
    registry.set('currentScore', 0);

    try {
        let highScoreVal = null;
        try { highScoreVal = localStorage.getItem('highScore'); } catch (e) { console.warn('localStorage error', e); }
        let loadedScore = (highScoreVal !== null && highScoreVal !== undefined && String(highScoreVal).trim() !== '' && typeof highScoreVal !== 'object') ? Number(highScoreVal) : NaN;
        if (isNaN(loadedScore) || !isFinite(loadedScore) || loadedScore < 0) {
            loadedScore = 0;
        }
        registry.set('highScore', loadedScore);
    } catch (e) {
        console.warn('LocalStorage access failed:', e);
        registry.set('highScore', 0);
    }

    saveGameState(registry);
}

class CursorScene extends Phaser.Scene {
  constructor() {
    super({ key: 'CursorScene', active: false });
  }

  create() {
    // If not loaded yet (e.g. boot), wait?
    // Assets are loaded in MainMenu. CursorScene starts active but MainMenu preloads.
    // If MainMenu hasn't loaded 'finger-cursor', this will fail.
    // Better to launch CursorScene FROM MainMenu after preload.
    this.fingerCursor = this.add.image(0, 0, 'finger-cursor')
        .setOrigin(0, 0)
        .setDepth(11111); // Always on top

    // ⚡ Bolt Optimization: Move static DOM operations and scaling out of update loop

    // Set initial size
    const initialScale = Math.min(this.scale.width / 1280, this.scale.height / 720);
    this.fingerCursor.setDisplaySize(50 * initialScale, 75 * initialScale);

    // Update size only on resize events
    const onResize = (gameSize) => {
      const scale = Math.min(gameSize.width / 1280, gameSize.height / 720);
      if (this.fingerCursor && this.fingerCursor.active) {
        this.fingerCursor.setDisplaySize(50 * scale, 75 * scale);
      }
    };
    this.scale.on('resize', onResize);
    this.events.once('shutdown', () => {
        this.scale.off('resize', onResize);
    });
  }

  update() {
    const pointer = this.input.activePointer;
    if (this.fingerCursor) {
        this.fingerCursor.setPosition(pointer.x, pointer.y);
    }
  }
}

class MusicScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MusicScene' });

    const getSafeVol = (key) => {
      let val = null;
      try { val = localStorage.getItem(key); } catch (e) { console.warn('localStorage error', e); }
      let parsed = (val !== null && val !== undefined && String(val).trim() !== '' && typeof val !== 'object') ? Number(val) : NaN;
      if (isNaN(parsed) || parsed < 0 || parsed > 1) {
          let backupVal = null;
          try { backupVal = localStorage.getItem(key + '_backup'); } catch (e) { console.warn('localStorage error', e); }
          parsed = (backupVal !== null && backupVal !== undefined && String(backupVal).trim() !== '' && typeof backupVal !== 'object') ? Number(backupVal) : NaN;
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
    // Simply play the sound. If not in cache, Phaser will warn internally,
    // but usually 'add' isn't needed for one-shot SFX if loaded.
    // If it's not added yet, we can try adding it, but play() usually handles it if the key exists.
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
        if (this.settingsContainer.visible) {
            this.closeSettings();
        } else {
            this.openSettings();
        }
    };
    this.input.keyboard.on('keydown-ESC', toggleSettings);
    this.input.keyboard.on('keydown-ENTER', () => this.closeSettings());

    this.scale.on('resize', this.resize, this);
    this.events.once('shutdown', () => {
        this.scale.off('resize', this.resize, this);
    });
  }

  resize(gameSize) {
      const width = gameSize.width;
      const height = gameSize.height;

      if (this.gearIcon) {
          this.gearIcon.x = 30;
          this.gearIcon.y = height - 30;
      }

      if (this.settingsContainer) {
          // Determine layout mode based on available height.
          // Need roughly 500px for a clean single column. Less than that -> 2 columns.
          const isTwoColumn = height < 500;
          const panelWidth = isTwoColumn ? Math.min(800, width - 40) : 500;
          const panelHeight = isTwoColumn ? Math.min(300, height - 40) : 500;
          const targetX = (width - panelWidth) / 2;
          const targetY = (height - panelHeight) / 2;
          const panelCenterX = targetX + panelWidth / 2;

          let controlYOffsets = isTwoColumn ? [120, 200, 120] : [150, 250, 350];
          let controlXOffsets = isTwoColumn ? [panelCenterX - 150, panelCenterX - 150, panelCenterX + 150] : [panelCenterX, panelCenterX, panelCenterX];
          let controlLabelIndex = 0;
          let controlArrowLeftIndex = 0;
          let controlArrowRightIndex = 0;
          let controlValueIndex = 0;

          this.settingsContainer.getAll().forEach(child => {
              // Re-size overlay
              if (child.type === 'Rectangle' && child.fillAlpha === 0.7) {
                  child.setSize(width, height);
              }
              // Re-center main panel
              else if (child.type === 'Rectangle' && child.fillColor === 0x333333) {
                  child.setPosition(width / 2, height / 2);
                  child.setSize(panelWidth, panelHeight);
                  // Update geometry for rounded rect if we resized it
                  child.geom.width = panelWidth;
                  child.geom.height = panelHeight;
                  child.updateDisplayOrigin();
              }
              // Re-center title
              else if (child.type === 'Text' && child.text === 'Audio Settings') {
                  child.setPosition(width / 2, targetY + 40);
              }
              // Re-center close button
              else if (child.type === 'Container' && child.list.length > 0 && child.list[0].type === 'Graphics' && child.width === 40) {
                  const closeX = targetX + panelWidth - 30;
                  const closeY = targetY + 30;
                  child.setPosition(closeX, closeY);
              }
              // Re-center "START NEW GAME" button container
              else if (child.type === 'Container' && child.list.length > 1 && child.list[1].type === 'Text' && child.list[1].text === 'START NEW GAME') {
                  const btnY = isTwoColumn ? targetY + panelHeight - 40 : targetY + 440;
                  child.setPosition(panelCenterX, btnY);
              }
              // Controls logic: Label, Left Arrow, Right Arrow, Value Text
              else if (child.type === 'Text' && ['Music', 'Ambient', 'SFX'].includes(child.text)) {
                  child.setPosition(controlXOffsets[controlLabelIndex], targetY + controlYOffsets[controlLabelIndex] - 30);
                  controlLabelIndex++;
              }
              // Number Value Text (matches 0-10 format, typically length 1 or 2 digits)
              else if (child.type === 'Text' && /^\d+$/.test(child.text)) {
                  child.setPosition(controlXOffsets[controlValueIndex], targetY + controlYOffsets[controlValueIndex]);
                  controlValueIndex++;
              }
              // Left Arrow Container
              else if (child.type === 'Container' && child.list.length > 0 && child.list[1] && child.list[1].type === 'Text' && child.list[1].text === '<') {
                  child.setPosition(controlXOffsets[controlArrowLeftIndex] - 50, targetY + controlYOffsets[controlArrowLeftIndex]);
                  controlArrowLeftIndex++;
              }
              // Right Arrow Container
              else if (child.type === 'Container' && child.list.length > 0 && child.list[1] && child.list[1].type === 'Text' && child.list[1].text === '>') {
                  child.setPosition(controlXOffsets[controlArrowRightIndex] + 50, targetY + controlYOffsets[controlArrowRightIndex]);
                  controlArrowRightIndex++;
              }
          });
      }
  }

  createGearIcon() {
    const x = 30;
    const y = this.cameras.main.height - 30;

    // Create a container to hold the background and the cog
    const gearContainer = this.add.container(x, y).setDepth(10);

    // Draw white circle with yellow border
    // Reduce circle to tightly wrap the 20x20 cog (radius 13 creates a 26px circle)
    const bg = this.add.graphics();
    bg.fillStyle(0xffffff, 1);
    bg.fillCircle(0, 0, 13);
    bg.lineStyle(3, 0xffd700, 1); // Yellow border
    bg.strokeCircle(0, 0, 13);

    // Add the cog icon scaled down to half size (20x20)
    const gearImg = this.add.image(0, 0, 'cog').setDisplaySize(20, 20);

    gearContainer.add([bg, gearImg]);

    // Add an invisible hit area graphic so setInteractive works perfectly
    // without relying on manual geometry params that break on scaling
    const hitAreaBg = this.add.graphics();
    hitAreaBg.fillStyle(0xffffff, 0.01);
    hitAreaBg.fillCircle(0, 0, 20);
    gearContainer.add(hitAreaBg);

    gearContainer.setSize(40, 40);
    gearContainer.setInteractive();

    gearContainer.baseScaleX = gearContainer.scaleX;
    gearContainer.baseScaleY = gearContainer.scaleY;

    addButtonInteraction(this, gearContainer, 'menu-click');

    gearContainer.on('pointerdown', () => {
        this.time.delayedCall(150, () => {
            this.openSettings();
            gearContainer.setScale(gearContainer.baseScaleX, gearContainer.baseScaleY); // Reset scale for next time
        });
    });

    addTooltip(this, gearContainer, 'Settings (Esc)');

    this.gearIcon = gearContainer;
  }

  createSettingsPanel() {
    const sw = this.cameras.main.width;
    const sh = this.cameras.main.height;
    const isTwoColumn = sh < 500;
    const width = isTwoColumn ? Math.min(800, sw - 40) : 500;
    const height = isTwoColumn ? Math.min(300, sh - 40) : 500;
    const x = (sw - width) / 2;
    const y = (sh - height) / 2;

    this.settingsContainer = this.add.container(0, 0).setVisible(false).setDepth(100);

    // Overlay
    const overlay = this.add.rectangle(0, 0, sw, sh, 0x000000, 0.7)
        .setOrigin(0)
        .setInteractive(); // Block clicks

    this.settingsContainer.add(overlay);

    // Panel
    const panel = this.add.rectangle(sw / 2, sh / 2, width, height, 0x333333)
        .setStrokeStyle(4, 0xffffff);
    this.settingsContainer.add(panel);

    // Title
    const title = this.add.text(sw / 2, y + 40, 'Audio Settings', {
        fontSize: '32px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff'
    }).setOrigin(0.5);
    this.settingsContainer.add(title);

    // Close Button
    const closeSize = 40;
    const closeX = x + width - 30;
    const closeY = y + 30;

    const closeBtn = this.add.container(closeX, closeY);
    const closeBg = this.add.graphics();
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
    closeBtn.setSize(closeSize, closeSize);
    closeBtn.setInteractive();

    closeBtn.baseScaleX = 1;
    closeBtn.baseScaleY = 1;

    addButtonInteraction(this, closeBtn, 'menu-click');

    closeBtn.on('pointerdown', () => {
        this.time.delayedCall(150, () => {
            this.closeSettings();
        });
    });
    this.settingsContainer.add(closeBtn);

    // Controls
    let controlYOffsets = isTwoColumn ? [120, 200, 120] : [150, 250, 350];
    const panelCenterX = x + width / 2;
    let controlXOffsets = isTwoColumn ? [panelCenterX - 150, panelCenterX - 150, panelCenterX + 150] : [panelCenterX, panelCenterX, panelCenterX];

    this.createNumberControl('Music', controlXOffsets[0], y + controlYOffsets[0], 'music');
    this.createNumberControl('Ambient', controlXOffsets[1], y + controlYOffsets[1], 'ambient');
    this.createNumberControl('SFX', controlXOffsets[2], y + controlYOffsets[2], 'sfx');

    // Start New Game Button
    const btnY = isTwoColumn ? y + height - 40 : y + 440;
    const resetBtnContainer = this.add.container(panelCenterX, btnY);
    const resetBg = this.add.graphics();
    resetBg.fillStyle(0xff4444, 1);
    resetBg.fillRoundedRect(-125, -25, 250, 50, 10);
    resetBg.lineStyle(2, 0xffffff, 1);
    resetBg.strokeRoundedRect(-125, -25, 250, 50, 10);

    const resetText = this.add.text(0, 0, 'START NEW GAME', {
        fontSize: '20px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff',
        fontStyle: 'bold'
    }).setOrigin(0.5);

    resetBtnContainer.add([resetBg, resetText]);
    resetBtnContainer.setSize(250, 50);
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

  createNumberControl(label, centerX, y, type) {
    const text = this.add.text(centerX, y - 30, label, {
        fontSize: '24px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff'
    }).setOrigin(0.5);
    this.settingsContainer.add(text);

    let currentVol = 0.5;
    if (this.registry.has(`${type}Volume`)) currentVol = this.registry.get(`${type}Volume`);

    // Convert 0.0-1.0 to 0-10
    let displayValue = Math.round(currentVol * 10);

    const valueText = this.add.text(centerX, y, displayValue.toString(), {
        fontSize: '32px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffff00',
        fontStyle: 'bold'
    }).setOrigin(0.5);
    this.settingsContainer.add(valueText);

    const updateVolume = (delta) => {
        displayValue = Phaser.Math.Clamp(displayValue + delta, 0, 10);
        valueText.setText(displayValue.toString());
        this.registry.set(`${type}Volume`, displayValue / 10);
    };

    // Left Arrow Container
    const leftArrowContainer = this.add.container(centerX - 50, y);
    const leftArrowText = this.add.text(0, 0, '<', {
        fontSize: '32px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff',
        fontStyle: 'bold'
    }).setOrigin(0.5);
    // Hit area background
    const leftHitArea = this.add.rectangle(0, 0, 40, 40, 0xffffff, 0.01);
    leftArrowContainer.add([leftHitArea, leftArrowText]);
    leftArrowContainer.setSize(40, 40);
    leftArrowContainer.setInteractive();
    addButtonInteraction(this, leftArrowContainer, 'menu-click');
    leftArrowContainer.on('pointerdown', () => updateVolume(-1));
    this.settingsContainer.add(leftArrowContainer);

    // Right Arrow Container
    const rightArrowContainer = this.add.container(centerX + 50, y);
    const rightArrowText = this.add.text(0, 0, '>', {
        fontSize: '32px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff',
        fontStyle: 'bold'
    }).setOrigin(0.5);
    const rightHitArea = this.add.rectangle(0, 0, 40, 40, 0xffffff, 0.01);
    rightArrowContainer.add([rightHitArea, rightArrowText]);
    rightArrowContainer.setSize(40, 40);
    rightArrowContainer.setInteractive();
    addButtonInteraction(this, rightArrowContainer, 'menu-click');
    rightArrowContainer.on('pointerdown', () => updateVolume(1));
    this.settingsContainer.add(rightArrowContainer);
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
            }
        });
    }
  }

  openSettings() {
    this.tweens.killTweensOf(this.settingsContainer);
    this.settingsContainer.setAlpha(0);
    this.settingsContainer.setVisible(true);
    if (this.gearIcon) this.gearIcon.setVisible(false);

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
    // Bolt Optimization: Centralized asset preloading to prevent gameplay stutter
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Loading Bar Background
    const progressBar = this.add.graphics();
    const progressBox = this.add.graphics();
    progressBox.fillStyle(0x222222, 0.8);
    progressBox.fillRect(width / 2 - 160, height / 2 - 25, 320, 50);

    // Loading Text
    const loadingText = this.add.text(width / 2, height / 2 + 50, 'Loading... 0%', {
        fontFamily: 'Comic Sans MS',
        fontSize: '24px',
        fill: '#ffffff'
    }).setOrigin(0.5);

    this.load.on('progress', (value) => {
        // Update Text
        loadingText.setText(`Loading... ${Math.floor(value * 100)}%`);

        // Update Bar
        progressBar.clear();
        progressBar.fillStyle(0xffff00, 1);
        progressBar.fillRect(width / 2 - 150, height / 2 - 15, 300 * value, 30);
    });

    this.load.json('symbols', 'assets/symbols.json');
    this.load.json('map_sections', 'assets/map/map_sections.json');
    this.load.video('intro-video', 'assets/video/HeIsRisen-Intro.mp4');
    this.load.atlas('level-complete-atlas', 'assets/video/level-complete.png', 'assets/video/level-complete.json');
    this.load.image('level-complete-stamp', 'assets/objects/level-complete-stamp.png');
    this.load.image('finger-cursor', 'assets/cursor/pointer-finger-pointer.png');

    // Preload common UI and game assets here to avoid reloading in scenes
    this.load.image('new-map', 'assets/map/new-map.png');
    this.load.image('cog', 'assets/objects/cog.png');
    this.load.image('eggs-ammin-haul', 'assets/objects/eggs-ammin-haul.png');
    this.load.image('score', 'assets/objects/score.png');
    this.load.image('magnifying-glass', 'assets/cursor/magnifying-glass.png');
    this.load.image('egg-zit-button', 'assets/objects/egg-zit-button.png');
    this.load.image('eggzam-keyframe', 'assets/video/eggzam-keyframe.jpg');
    this.load.atlas('egg-cellent-button', 'assets/objects/egg-cellent.png', 'assets/objects/egg-cellent.json');
    this.load.atlas('eggs-tra-stinky-button', 'assets/objects/eggs-tra-stinky.png', 'assets/objects/eggs-tra-stinky.json');
    this.load.image('symbol-result-summary-diag', 'assets/objects/symbol-result-summary-diag.png');

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

    this.load.on('filecomplete-json-map_sections', (key, type, data) => {
      if (Array.isArray(data)) {
        data.forEach(section => {
             // Enqueue thumbnail (.jpg) explicitly as thumb to avoid fallback errors
             this.load.image(`${section.name}-thumb`, `assets/map/sections/${section.background}`);
             // Keep the fallback key mapping to the same jpg, but thumb is cleaner for map.
             this.load.image(`${section.name}-fallback`, `assets/map/sections/${section.background}`);

             // Preload video backgrounds
             this.load.video(`${section.name}-video`, `assets/video/${section.name}.mp4`);
        });
      }
    });

    this.load.on('filecomplete-json-symbols', (key, type, data) => {
      // Preload all 60 eggs
      for (let i = 1; i <= TOTAL_EGGS; i++) {
        this.load.image(`egg-${i}`, `assets/eggs/egg-${i}.png`);
      }
      // Preload all symbols
      if (data && data.symbols) {
        data.symbols.forEach(symbol => {
          // Sentinel: Validate symbol path to prevent traversal/malicious loading
          if (this.isValidSymbol(symbol)) {
            this.load.image(symbol.filename, symbol.filename);
          } else {
            console.warn(`Security: Skipped invalid symbol filename: ${symbol.filename}`);
          }
        });
      }
    });

    this.load.on('complete', () => {
        progressBar.destroy();
        progressBox.destroy();
        loadingText.destroy();
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

    const width = this.scale.width;
    const height = this.scale.height;

    // Intro Video - centered
    const introVideo = this.add.video(width / 2, height / 2, 'intro-video');
    introVideo.setMute(true); // Start muted to allow autoplay
    introVideo.disableInteractive(); // Ensure video ignores input
    try {
        introVideo.play(true); // Loop
    } catch (e) {
        console.warn('Video autoplay synchronous error:', e);
    }
    this.introVideo = introVideo; // Store reference for resizing

    // Fit video to cover screen
    // Note: introVideo.width might be 0 initially if not fully loaded metadata
    // We should rely on resize or use displayWidth/displayHeight if set

    if (introVideo.width > 0) {
        const scaleX = width / introVideo.width;
        const scaleY = height / introVideo.height;
        const videoScale = Math.max(scaleX, scaleY);
        introVideo.setScale(videoScale);
    } else {
        // Fallback or wait for texture
        // We will rely on resize event which fires or we can force a resize check in update/timeout
    }

    // Initial Overlay Text "Click anywhere to start"
    const tapToStartText = this.add.text(width / 2, height / 2, 'Click anywhere to start', {
        fontSize: '48px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff',
        stroke: '#000000',
        strokeThickness: 6
    }).setOrigin(0.5).setDepth(100);
    this.tapToStartText = tapToStartText;

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
    const btnX = width / 2;
    const btnY = height * 0.8; // Position relative to height
    let hasSaveState = false;
    try { hasSaveState = localStorage.getItem('heIsRisenGameState') !== null; } catch (e) { console.warn('localStorage error', e); }

    const startBtnContainer = this.add.container(btnX, btnY).setVisible(false).setDepth(101);
    this.startBtnContainer = startBtnContainer;

    let btnTextString = hasSaveState ? 'CONTINUE THE HUNT!' : 'PLAY NOW';
    const mainBtnContainer = this.add.container(0, hasSaveState ? -50 : 0);

    const btnBg = this.add.graphics();
    btnBg.fillStyle(0xff0000, 1);
    btnBg.fillRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, 16);
    btnBg.lineStyle(4, 0xffffff, 1);
    btnBg.strokeRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, 16);
    mainBtnContainer.add(btnBg);

    const btnText = this.add.text(0, 0, btnTextString, {
      fontSize: hasSaveState ? `32px` : `40px`,
      fill: '#ffffff',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#000000',
      strokeThickness: 4
    }).setOrigin(0.5);
    mainBtnContainer.add(btnText);

    mainBtnContainer.setSize(buttonWidth, buttonHeight);
    mainBtnContainer.setInteractive();
    addButtonInteraction(this, mainBtnContainer, 'menu-click');
    startBtnContainer.add(mainBtnContainer);

    let newGameBtnContainer = null;
    if (hasSaveState) {
        newGameBtnContainer = this.add.container(0, 50);
        const newBtnBg = this.add.graphics();
        newBtnBg.fillStyle(0x0000ff, 1);
        newBtnBg.fillRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, 16);
        newBtnBg.lineStyle(4, 0xffffff, 1);
        newBtnBg.strokeRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, 16);
        newGameBtnContainer.add(newBtnBg);

        const newBtnText = this.add.text(0, 0, 'START NEW GAME', {
          fontSize: `32px`,
          fill: '#ffffff',
          fontStyle: 'bold',
          fontFamily: 'Comic Sans MS',
          stroke: '#000000',
          strokeThickness: 4
        }).setOrigin(0.5);
        newGameBtnContainer.add(newBtnText);

        newGameBtnContainer.setSize(buttonWidth, buttonHeight);
        newGameBtnContainer.setInteractive();
        addButtonInteraction(this, newGameBtnContainer, 'menu-click');
        startBtnContainer.add(newGameBtnContainer);
    }

    // Cursor handled by CursorScene

    // Initialize volume registry (Load from localStorage if available)
    const getSafeVol = (key) => {
      let val = null;
      try { val = localStorage.getItem(key); } catch (e) { console.warn('localStorage error', e); }
      let parsed = (val !== null && val !== undefined && String(val).trim() !== '' && typeof val !== 'object') ? Number(val) : NaN;
      if (isNaN(parsed) || parsed < 0 || parsed > 1) {
          let backupVal = null;
          try { backupVal = localStorage.getItem(key + '_backup'); } catch (e) { console.warn('localStorage error', e); }
          parsed = (backupVal !== null && backupVal !== undefined && String(backupVal).trim() !== '' && typeof backupVal !== 'object') ? Number(backupVal) : NaN;
          if (isNaN(parsed) || parsed < 0 || parsed > 1) {
              return 0.5;
          }
      }
      return parsed;
    };

    if (!this.registry.has('musicVolume')) this.registry.set('musicVolume', getSafeVol('musicVolume'));
    if (!this.registry.has('ambientVolume')) this.registry.set('ambientVolume', getSafeVol('ambientVolume'));
    if (!this.registry.has('sfxVolume')) this.registry.set('sfxVolume', getSafeVol('sfxVolume'));

    // Launch UI Scene
    if (!this.scene.get('UIScene').scene.isActive()) {
        this.scene.launch('UIScene');
    }

    // Launch Cursor Scene if not active (and assets loaded)
    if (!this.scene.get('CursorScene').scene.isActive()) {
        this.scene.launch('CursorScene');
        this.scene.bringToTop('CursorScene');
    }

    // Intro Logic State
    let introState = 'waiting'; // waiting -> playing -> ready

    // 1. Waiting: Loop Muted. On Click -> Playing
    const handleGlobalTap = () => {
        if (introState !== 'waiting') return;
        introState = 'playing';

        tapToStartText.setVisible(false);

        // Resume Audio
        if (this.sound.context.state === 'suspended') {
            this.sound.context.resume();
        }

        // Unmute and Restart Video
        if (introVideo) {
            introVideo.setMute(false);
            const vol = this.registry.get('musicVolume');
            introVideo.setVolume(vol);
            introVideo.play(true); // Restart loop with sound
        }

        // Request Fullscreen (Desktop logic)
        // Memory Directive: Bypass Phaser's internal scaling wrapper to prevent WebGL Framebuffer crash on desktop.
        const gameElement = document.getElementById('game');
        if (gameElement && gameElement.requestFullscreen) {
            gameElement.requestFullscreen().catch(err => {
                console.warn(`Fullscreen request failed: ${err.message}`);
            });
        }

        // Show Play Button almost immediately (short delay for visual transition)
        this.time.delayedCall(100, () => {
            introState = 'ready';
            startBtnContainer.setVisible(true);
            startBtnContainer.setScale(0);

            this.tweens.add({
                targets: startBtnContainer,
                scaleX: 1,
                scaleY: 1,
                duration: 500,
                ease: 'Back.out',
                onComplete: () => {
                    this.tweens.add({
                        targets: startBtnContainer,
                        scaleX: 1.05,
                        scaleY: 1.05,
                        duration: 800,
                        yoyo: true,
                        repeat: -1,
                        ease: 'Sine.easeInOut'
                    });
                }
            });
        });
    };

    this.input.once('pointerdown', handleGlobalTap);

    // 2. Play Button Logic
    const startGame = (forceNew = false) => {
        if (introState !== 'ready') return;

        // Prevent multiple calls
        introState = 'starting';

        if (forceNew) {
            initializeGameData(this.registry, this.cache, true);
        }

        this.tweens.add({
            targets: introVideo,
            volume: 0,
            duration: 500,
            onComplete: () => {
                if (introVideo) {
                    introVideo.stop();
                    introVideo.destroy();
                    this.introVideo = null;
                }
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
            if (introState === 'waiting') {
                handleGlobalTap();
            } else if (introState === 'ready') {
                startGame(false);
            }
        }
    };
    window.addEventListener('keydown', globalKeyHandler);
    this.events.once('shutdown', () => {
        window.removeEventListener('keydown', globalKeyHandler);
    });

    // Update intro volume if changed in settings
    const updateIntroVolume = (parent, key, data) => {
        if (key === 'musicVolume' && this.introVideo && this.introVideo.active) {
            this.introVideo.setVolume(data);
        }
    };
    this.registry.events.on('changedata', updateIntroVolume);
    this.events.once('shutdown', () => {
        this.registry.events.off('changedata', updateIntroVolume);
        if (this.introVideo) {
            this.introVideo.stop();
            this.introVideo.destroy();
        }
    });

    // Handle Resize
    this.scale.on('resize', this.resize, this);
    this.events.once('shutdown', () => {
        this.scale.off('resize', this.resize, this);
    });

    // Handle delayed video metadata loading
    if (this.introVideo && this.introVideo.active) {
        const checkVideoReady = () => {
            if (this.introVideo && this.introVideo.active) {
                if (this.introVideo.width > 0) {
                    this.resize(this.scale);
                } else {
                    // Poll occasionally until metadata is fully available (safer than a hardcoded 100ms)
                    this.time.delayedCall(100, checkVideoReady);
                }
            }
        };
        this.introVideo.once('play', checkVideoReady);
        // Fallback for Safari/iOS that might require interaction
        this.time.delayedCall(100, checkVideoReady);
    }

    const symbolsData = this.cache.json.get('symbols');
    if (symbolsData && symbolsData.symbols && Array.isArray(symbolsData.symbols)) {
        const validSymbols = symbolsData.symbols.filter(s => this.isValidSymbol(s));
        if (validSymbols.length !== symbolsData.symbols.length) {
            console.warn(`Security: Filtered ${symbolsData.symbols.length - validSymbols.length} invalid symbols.`);
            symbolsData.symbols = validSymbols;
        }
    }

    if (!this.registry.has('eggData')) {
        initializeGameData(this.registry, this.cache);
    }
  }

  resize(gameSize) {
      const width = gameSize.width;
      const height = gameSize.height;

      if (this.cameras && this.cameras.main) {
          // Use requestAnimationFrame to defer the viewport update until after the WebGL context
          // has completely re-allocated the framebuffers for the new window size.
          // This prevents the 'Framebuffer status: Incomplete Attachment' crash.
          requestAnimationFrame(() => {
              if (this.cameras && this.cameras.main) {
                  try { this.cameras.main.setViewport(0, 0, width, height); } catch (e) {}
              }
          });
      }

      if (this.introVideo && this.introVideo.active) {
          this.introVideo.setPosition(width/2, height/2);
          // Only scale if we have valid dimensions
          if (this.introVideo.width > 0 && this.introVideo.height > 0) {
              const scaleX = width / this.introVideo.width;
              const scaleY = height / this.introVideo.height;
              const videoScale = Math.max(scaleX, scaleY);
              this.introVideo.setScale(videoScale);
          }
      }

      if (this.tapToStartText) {
          this.tapToStartText.setPosition(width/2, height/2);
      }

      if (this.startBtnContainer) {
          this.startBtnContainer.setPosition(width/2, height * 0.8);
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
  }
}

class MapScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MapScene' });
  }

  create() {

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
        // We need a render texture to bake it into a reusable cache texture for particles
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

    // Scale logic
    const width = this.scale.width;
    const height = this.scale.height;

    // We want to fit the map 1280x720 into the screen while maintaining aspect ratio?
    // Or cover? The user requested "full screen maximized viewport".
    // For the map, "cover" makes sense to fill the screen.

    let mapSections = this.cache.json.get('map_sections');
    if (!Array.isArray(mapSections)) mapSections = [];

    if (!this.scene.get('MusicScene').scene.isActive()) {
      this.scene.launch('MusicScene');
    }
    const musicScene = this.scene.get('MusicScene');
    if (musicScene) {
      musicScene.playSFX('drive2');
    }

    this.mapImage = this.add.image(width/2, height/2, 'new-map');
    this.updateLayout(width, height);

    // Create map thumbnails (videos/images)
    this.mapZones = [];
    this.stamps = [];

    // We will use the original zone dimensions to calculate the center
    mapSections.forEach(section => {
      const centerX = section.coords.x;
      const centerY = section.coords.y;

      // Create container for border and drop shadow
      const thumbContainer = this.add.container(0, 0);

      // Rounded Rectangle mask for the image
      const radius = 15;

      // Shadow
      const shadow = this.add.graphics();
      shadow.fillStyle(0x000000, 0.6);
      shadow.fillRoundedRect(-section.coords.width / 2 + 4, -section.coords.height / 2 + 4, section.coords.width, section.coords.height, radius);

      // Border (white background with brown stroke)
      const border = this.add.graphics();
      border.lineStyle(4, 0x8b4513, 1); // Brown border
      border.fillStyle(0xffffff, 1);
      border.fillRoundedRect(-section.coords.width / 2 - 5, -section.coords.height / 2 - 5, section.coords.width + 10, section.coords.height + 10, radius + 2);
      border.strokeRoundedRect(-section.coords.width / 2 - 5, -section.coords.height / 2 - 5, section.coords.width + 10, section.coords.height + 10, radius + 2);

      // Add the static thumbnail image
      const thumbImage = this.add.image(0, 0, `${section.name}-thumb`).setOrigin(0.5, 0.5);
      thumbImage.setDisplaySize(section.coords.width, section.coords.height);

      // Create mask for the image to give it rounded corners
      const maskGraphics = this.add.graphics();
      maskGraphics.fillStyle(0xffffff);
      maskGraphics.fillRoundedRect(-section.coords.width / 2, -section.coords.height / 2, section.coords.width, section.coords.height, radius);
      maskGraphics.setVisible(false); // Do not show the mask itself

      const mask = maskGraphics.createGeometryMask();
      thumbImage.setMask(mask);

      // Add invisible hit area graphics for reliable click detection
      // Use an expanded hit area to make clicking slightly more forgiving
      const hitArea = this.add.rectangle(0, 0, section.coords.width + 40, section.coords.height + 40, 0x000000, 0);

      // IMPORTANT: maskGraphics should NOT be added to the container's children array when used as a mask
      // because it is scaled dynamically by the container, and rendering it as a child breaks the mask visually
      thumbContainer.add([shadow, border, thumbImage, hitArea]);
      thumbContainer.setSize(section.coords.width + 40, section.coords.height + 40);

      // By omitting geometry arguments and relying on the `hitArea` rectangle we added above,
      // Phaser will natively compute the bounds from the container's display list components
      // correctly mapping the center of the click zone to the container origin (0,0) across all scales.
      thumbContainer.setInteractive();

      const thumb = thumbContainer;
      thumb.name = section.name;
      thumb.sectionData = section;
      thumb.maskGraphics = maskGraphics; // Store reference to update mask transforms

      // The baseScale will be set in resizeGame()/updateLayout once dimensions are known,
      // but let's initialize it safely here just in case.
      thumb.baseScale = 1;

      // Update mask initially if position is already set
      // (though for main.js it gets set in updateLayout immediately after)

      thumb.on('pointerover', () => {
          this.tweens.add({
              targets: thumb,
              scaleX: thumb.baseScale * 1.1,
              scaleY: thumb.baseScale * 1.1,
              duration: 100,
              ease: 'Sine.easeInOut'
          });
      });

      thumb.on('pointerout', () => {
          this.tweens.add({
              targets: thumb,
              scaleX: thumb.baseScale,
              scaleY: thumb.baseScale,
              duration: 100,
              ease: 'Sine.easeInOut'
          });
      });

      thumb.on('pointerdown', () => {
        const musicScene = this.scene.get('MusicScene');
        if (musicScene) {
            musicScene.playSFX('drive1');
        }
        this.scene.start('SectionHunt', { sectionName: section.name });
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
              // instead of the entire atlas base dimension.
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
              // We use "video: stampAnim" so the generic resize loop works identically
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
    });

    this.eggsAmminHaul = this.add.image(0, 0, 'eggs-ammin-haul')
        .setOrigin(0, 0)
        .setInteractive()
        .setDepth(100); // Ensure it is above map zones
    addButtonInteraction(this, this.eggsAmminHaul, 'menu-click');
    addTooltip(this, this.eggsAmminHaul, 'View Collection');
    this.eggsAmminHaul.on('pointerdown', () => {
         this.time.delayedCall(100, () => {
             this.scene.start('EggZamRoom');
         });
    });

    this.scoreImage = this.add.image(0, 0, 'score').setOrigin(0, 0);
    const foundEggs = this.registry.get('foundEggs').length;
    this.scoreText = this.add.text(0, 0, `${foundEggs}/${TOTAL_EGGS}`, { fontSize: '42px', fill: '#000', fontStyle: 'bold', fontFamily: 'Comic Sans MS', stroke: '#fff', strokeThickness: 6 });

    // Initial Layout update
    this.updateLayout(width, height);

    this.scale.on('resize', this.resize, this);
    this.events.once('shutdown', () => {
        this.scale.off('resize', this.resize, this);
    });
  }

  resize(gameSize) {
      this.updateLayout(gameSize.width, gameSize.height);
  }

  updateLayout(width, height) {
      if (this.cameras && this.cameras.main) {
          requestAnimationFrame(() => {
              if (this.cameras && this.cameras.main) {
                  try { this.cameras.main.setViewport(0, 0, width, height); } catch (e) {}
              }
          });
      }

      // Calculate scale to COVER based on native map size, not forced 1280x720
      const nativeWidth = this.mapImage.width || 1376;
      const nativeHeight = this.mapImage.height || 768;
      const scaleX = width / nativeWidth;
      const scaleY = height / nativeHeight;
      const scale = Math.max(scaleX, scaleY);

      // Center map
      this.mapImage.setPosition(width/2, height/2);
      this.mapImage.setScale(scale);

      // Calculate offset for map centering based on the native resolution mapping.
      const mapWidth = nativeWidth * scale;
      const mapHeight = nativeHeight * scale;
      const offsetX = (width - mapWidth) / 2;
      const offsetY = (height - mapHeight) / 2;

      // Update Zones
      if (this.mapZones) {
          // ⚡ Bolt Optimization: Replace forEach with fast for loop to prevent closure allocations during layout update
          for (let m_idx = 0; m_idx < this.mapZones.length; m_idx++) {
              const thumb = this.mapZones[m_idx];
              const d = thumb.sectionData.coords;
              const centerX = d.x;
              const centerY = d.y;

              thumb.setPosition(offsetX + centerX * scale, offsetY + centerY * scale);

              // We use the custom width and height properties specified in map_sections.json
              // to accurately set the size of each thumbnail while maintaining proper ratio.
              const targetW = d.width * scale;
              const targetH = d.height * scale;

              // Container uses scale, not setDisplaySize
              const thumbScale = targetW / d.width;
              thumb.setScale(thumbScale);

              // Update mask transform to match the container
              if (thumb.maskGraphics) {
                  thumb.maskGraphics.setPosition(offsetX + centerX * scale, offsetY + centerY * scale);
                  thumb.maskGraphics.setScale(thumbScale);
              }

              // Update base scale for hover animations AFTER scaling
              thumb.baseScale = thumb.scaleX;
          }
      }

      if (this.stamps) {
          // ⚡ Bolt Optimization: Replace forEach with fast for loop to prevent closure allocations during layout update
          for (let st_idx = 0; st_idx < this.stamps.length; st_idx++) {
              const item = this.stamps[st_idx];
              if (item.video && item.video.active && item.thumb && item.thumb.active) {
                  const offsetY = 0;
                  item.video.setPosition(item.thumb.x, item.thumb.y + offsetY);

                  // Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const intrinsicHeight = item.video.height || 720;
                  const targetHeight = (item.thumb.height * item.thumb.scaleY) * 1.25;
                  const calculatedScale = targetHeight / intrinsicHeight;
                  if (calculatedScale > 0 && isFinite(calculatedScale)) {
                      item.video.setScale(calculatedScale);
                  }
              }
          }
      }

      // UI Elements - Scale with MIN to stay on screen and proportional
      const uiScale = Math.min(scaleX, scaleY);

      if (this.eggsAmminHaul) {
          this.eggsAmminHaul.setDisplaySize(137 * uiScale, 150 * uiScale);
          this.eggsAmminHaul.baseScaleX = this.eggsAmminHaul.scaleX;
          this.eggsAmminHaul.baseScaleY = this.eggsAmminHaul.scaleY;
          this.eggsAmminHaul.setPosition(0, 200 * uiScale);
      }

      if (this.scoreImage) {
          this.scoreImage.setScale(uiScale);
          this.scoreImage.setPosition(0, 0);
      }

      if (this.scoreText) {
          this.scoreText.setScale(uiScale);
          this.scoreText.setPosition(50 * uiScale, 98 * uiScale);
      }
  }

  update() {
  }
}

class SectionHunt extends Phaser.Scene {
  constructor() {
    super({ key: 'SectionHunt' });
  }

  init(data) {
    this.sectionName = data.sectionName;
  }

  collectEgg(egg) {
    announceToScreenReader('Egg collected!');
    const foundEggs = this.registry.get('foundEggs');
    const eggDataArray = this.registry.get('eggData');
    const eggData = {
      eggId: egg.getData('eggId'),
      symbolData: egg.getData('symbolDetails'),
      categorized: false
    };
    const globalEggData = eggDataArray.find(e => e.eggId === eggData.eggId);

    if (!foundEggs.some(e => e.eggId === eggData.eggId)) {
      const musicScene = this.scene.get('MusicScene');
      if (musicScene) {
          musicScene.playSFX('collect', { detune: Phaser.Math.Between(-200, 200) });
      }

      announceToScreenReader('Egg found!');

      if (navigator && navigator.vibrate) {
          navigator.vibrate(50);
      }

      let symbolTexture = null;
      if (egg.symbolSprite && egg.symbolSprite.active) {
          symbolTexture = egg.symbolSprite.texture.key;
      }

      this.showCollectionFeedback(egg.x, egg.y, egg.texture.key, symbolTexture);
      foundEggs.push(eggData);
      this.registry.set('foundEggs', foundEggs);

      if (globalEggData) {
          globalEggData.collected = true;
          this.registry.set('eggData', eggDataArray);
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

      this.updateScore();

      if (this.hintTimer) {
          this.hintTimer.reset({ delay: 90000, callback: this.showIdleHint, callbackScope: this, loop: true });
      }

      saveGameState(this.registry);

      this.checkLevelComplete();
    }
  }

  checkLevelComplete(immediate = false) {
      const foundEggs = this.registry.get('foundEggs');
      const sections = this.registry.get('sections');
      const currentSection = sections.find(s => s.name === this.sectionName);

      if (foundEggs.length === TOTAL_EGGS) {
          announceToScreenReader('All 60 Eggs Found! Transporting to the EggZam Room...');
          const clearText = this.add.text(this.scale.width / 2, this.scale.height / 2, "All 60 Eggs Found! Transporting to the EggZam Room...", {
              fontSize: '48px',
              fontFamily: 'Comic Sans MS',
              fill: '#ffff00',
              backgroundColor: '#000000cc',
              padding: { x: 20, y: 20 },
              stroke: '#000000',
              strokeThickness: 8,
              align: 'center',
              wordWrap: { width: 800, useAdvancedWrap: true }
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
              const clearText = this.add.text(this.scale.width / 2, this.scale.height / 2, "Great Job Detective!! You found all the hidden eggs on this map, the others are hidden in other maps.", {
                  fontSize: '40px',
                  fontFamily: 'Comic Sans MS',
                  fill: '#ffff00',
                  backgroundColor: '#000000cc',
                  padding: { x: 20, y: 10 },
                  stroke: '#000000',
                  strokeThickness: 6,
                  align: 'center',
                  wordWrap: { width: 800, useAdvancedWrap: true }
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
    if (!this.textures.exists('sparkle')) {
        const starObject = new Phaser.GameObjects.Star(this, 10, 10, 4, 2, 10, 0xffff00);
        const renderTexture = this.add.renderTexture(0, 0, 20, 20).setVisible(false);
        renderTexture.draw(starObject, 10, 10);
        renderTexture.saveTexture('sparkle');
        renderTexture.destroy();
        starObject.destroy();
    }

    // Flash white circle effect behind the egg
    const flash = this.add.circle(x, y, 10, 0xffffff, 0.8).setDepth(18);
    this.tweens.add({
        targets: flash,
        scale: 15,
        alpha: 0,
        duration: 600,
        ease: 'Cubic.easeOut',
        onComplete: () => flash.destroy()
    });

    const emitter = this.add.particles(x, y, 'sparkle', {
        speed: { min: 200, max: 500 }, scale: { start: 2, end: 0 }, alpha: { start: 1, end: 0 },
        lifespan: 1200, gravityY: 400, quantity: 45, duration: 250, blendMode: 'ADD'
    }).setDepth(19);
    emitter.once('complete', () => emitter.destroy());

    // Show Egg Sprite
    const eggSprite = this.add.image(x, y, eggTexture).setDepth(20).setDisplaySize(50, 75);

    // Animate the egg collection ("Juicy" squish and pop)
    this.tweens.add({
        targets: eggSprite,
        y: y - 180,
        scaleX: { value: eggSprite.scaleX * 2.5, duration: 400, ease: 'Back.easeOut' },
        scaleY: { value: eggSprite.scaleY * 2.5, duration: 400, ease: 'Back.easeOut' },
        angle: { value: 360, duration: 600, ease: 'Quad.easeOut' },
        alpha: { value: 0, delay: 600, duration: 400 },
        onComplete: () => eggSprite.destroy()
    });

    // Show Symbol Sprite if exists
    if (symbolTexture) {
        const symSprite = this.add.image(x, y, symbolTexture).setDepth(21).setDisplaySize(50, 75);
        this.tweens.add({
            targets: symSprite,
            y: y - 180,
            scaleX: { value: symSprite.scaleX * 2.5, duration: 400, ease: 'Back.easeOut' },
            scaleY: { value: symSprite.scaleY * 2.5, duration: 400, ease: 'Back.easeOut' },
            angle: { value: 360, duration: 600, ease: 'Quad.easeOut' },
            alpha: { value: 0, delay: 600, duration: 400 },
            onComplete: () => symSprite.destroy()
        });
    }

    const feedback = this.add.text(x, y - 40, 'Found!', {
        fontSize: '40px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff',
        stroke: '#ff9900',
        strokeThickness: 6,
        shadow: { offsetX: 2, offsetY: 2, color: '#000000', blur: 4, stroke: true, fill: true }
    }).setOrigin(0.5).setDepth(22);

    this.tweens.add({
        targets: feedback,
        y: y - 200,
        scaleX: { start: 0.5, to: 1.5 },
        scaleY: { start: 0.5, to: 1.5 },
        alpha: { value: 0, delay: 800, duration: 400 },
        duration: 1200,
        ease: 'Elastic.easeOut',
        easeParams: [1.5, 0.5],
        onComplete: () => feedback.destroy()
    });
  }

  showIdleHint() {
    // Goal 1: Check if the user has moved the mouse within the last 60 seconds
    const now = this.time.now;
    if (this.lastInteractionTime && (now - this.lastInteractionTime > 60000)) {
        // User is fully AFK, don't show the hint.
        return;
    }

    const foundEggs = this.registry.get('foundEggs');
    const sections = this.registry.get('sections');
    const currentSection = sections.find(s => s.name === this.sectionName);

    if (!currentSection) return;

    const eggsInSection = currentSection.eggs; // Array of IDs
    const foundIds = foundEggs.map(e => e.eggId);
    const remainingCount = eggsInSection.filter(id => !foundIds.includes(id)).length;

    if (remainingCount > 0) {
        const musicScene = this.scene.get('MusicScene');
        if (musicScene) musicScene.playSFX('menu-click');

        const hintText = this.add.text(this.scale.width / 2, this.scale.height * 0.8, `Hint: ${remainingCount} eggs left here!`, {
            fontSize: '32px',
            fontFamily: 'Comic Sans MS',
            fill: '#ffffff',
            backgroundColor: '#00000088',
            padding: { x: 10, y: 5 },
            stroke: '#000000',
            strokeThickness: 4
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

    // Background lazy-load core EggZam videos
    if (!this.registry.get('eggzamVideosLoaded')) {
        this.registry.set('eggzamVideosLoaded', true);
        this.load.video('eggzam-eggcellent', 'assets/video/eggzam-eggcellent.mp4');
        this.load.video('eggzam-stinky', 'assets/video/eggzam-stinky.mp4');
        this.load.video('eggzam-incorrect', 'assets/video/eggzam-incorrect-classification.mp4');
        this.load.start();
    }

    // Scale logic
    const width = this.scale.width;
    const height = this.scale.height;
    const scaleX = width / 1280;
    const scaleY = height / 720;
    const scale = Math.max(scaleX, scaleY); // Cover

    this.bgScale = scale;
    this.bgOffsetX = (width - 1280 * scale) / 2;
    this.bgOffsetY = (height - 720 * scale) / 2;

    this.cameras.main.setViewport(0, 0, width, height);

    // Load Thumbnail Background Immediately (acts as fallback and loading screen)
    // MapScene preloads these as '-thumb' keys
    const thumbKey = `${this.sectionName}-thumb`;
    if (this.textures.exists(thumbKey)) {
        this.sectionImage = this.add.image(width/2, height/2, thumbKey)
            .setDisplaySize(1280 * scale, 720 * scale)
            .setDepth(-1); // Underneath the video
    }

    // Check if video exists in cache
    const videoKey = `${this.sectionName}-video`;

    // Validate video existence
    let useVideo = false;
    if (this.cache.video.exists(videoKey)) {
        useVideo = true;
    }

    if (useVideo) {
        // Use Video Background
        this.sectionVideo = this.add.video(width/2, height/2, videoKey)
            .setDisplaySize(1280 * scale, 720 * scale)
            .setDepth(0);

        const applySectionVideoScale = () => {
             if (this.sectionVideo && this.sectionVideo.active && this.sectionVideo.width > 0) {
                 const w = this.scale.width;
                 const h = this.scale.height;
                 const sX = w / 1280;
                 const sY = h / 720;
                 const tScale = Math.max(sX, sY);

                 // Use a threshold to prevent jitter/unnecessary redraws
                 if (Math.abs(this.sectionVideo.displayWidth - (1280 * tScale)) > 5) {
                     this.sectionVideo.setDisplaySize(1280 * tScale, 720 * tScale);
                     this.sectionVideo.setPosition(w / 2, h / 2);

                     this.bgScale = tScale;
                     this.bgOffsetX = (w - 1280 * tScale) / 2;
                     this.bgOffsetY = (h - 720 * tScale) / 2;
                 }
             }
        };

        const checkSectionVideoReady = () => {
             if (this.sectionVideo && this.sectionVideo.active) {
                 if (this.sectionVideo.width > 0) {
                     applySectionVideoScale();
                 } else {
                     this.time.delayedCall(100, checkSectionVideoReady);
                 }
             }
        };

        this.sectionVideo.once('play', checkSectionVideoReady);
        // Fallback trigger if event misses
        this.time.delayedCall(100, checkSectionVideoReady);

        // Add a scale event listener to replace the update loop checks for resize
        this.scale.on('resize', applySectionVideoScale, this);
        this.events.once('shutdown', () => {
             this.scale.off('resize', applySectionVideoScale, this);
        });

        this.sectionVideo.play(true); // Loop
        this.sectionVideo.setMute(false); // iOS quirk: keep muted attr false to avoid global context suspension
        // Initialize volume from Ambient setting (reduced to 25% due to loud video mixing)
        const ambientVol = this.registry.has('ambientVolume') ? this.registry.get('ambientVolume') : 0.5;
        this.sectionVideo.setVolume(ambientVol * 0.25);
        this.sectionVideo.disableInteractive(); // Should not block clicks

        // Smart Audio Looping: Mute audio after first play, unmute every 5th loop
        // Use setVolume(0) instead of setMute(true) to prevent iOS global WebAudio suspension bugs
        this.sectionVideo.loopCount = 0;
        this.sectionVideo.on('loop', () => {
             this.sectionVideo.loopCount++;
             if (this.sectionVideo.loopCount % 5 !== 0) {
                 this.sectionVideo.setVolume(0);
             } else {
                 const currentAmbientVol = this.registry.has('ambientVolume') ? this.registry.get('ambientVolume') : 0.5;
                 this.sectionVideo.setVolume(currentAmbientVol * 0.25);
             }
        });

        // Listen for volume changes
        const updateAmbientVolume = (parent, key, data) => {
             if (key === 'ambientVolume' && this.sectionVideo && this.sectionVideo.active) {
                 this.sectionVideo.setVolume(data * 0.25);
             }
        };
        this.registry.events.on('changedata', updateAmbientVolume);
        this.events.once('shutdown', () => {
             this.registry.events.off('changedata', updateAmbientVolume);
        });

        // Video has started loading. We assume it works unless it errors.
        // We attach an error handler to fallback if playback fails later.
        this.isUsingVideo = true;

        this.sectionVideo.on('error', () => {
             console.warn(`SectionHunt: Video ${videoKey} playback error. Falling back to thumbnail.`);
             this.sectionVideo.destroy();
             this.isUsingVideo = false;
        });
    }

    // If no video, we simply rely on the this.sectionImage thumbnail already added at depth -1

    const eggDataArray = this.registry.get('eggData') || [];
    const sectionEggsData = eggDataArray.filter(e => e.section === this.sectionName && !e.collected);

    this.eggs = this.add.group();

    sectionEggsData.forEach(eggData => {
        // Calculate egg position relative to the SCALED background
        const scale = this.bgScale;
        const x = this.bgOffsetX + (eggData.x * scale);
        const y = this.bgOffsetY + (eggData.y * scale);

        const egg = this.add.image(x, y, `egg-${eggData.eggId}`)
          // ⚡ Bolt Optimization: Removing individual listeners to rely on global pointerdown
          .setDepth(5)
          .setDisplaySize(50, 75)
          .setAlpha(0); // Invisible until magnified

        egg.setData('eggId', eggData.eggId);
        const symbol = eggData.symbol;
        egg.setData('symbolDetails', symbol);

        if (symbol && symbol.filename && this.textures.exists(symbol.filename)) {
            const symbolSprite = this.add.image(x, y, symbol.filename)
              .setDepth(6)
              .setDisplaySize(50, 75)
              .setAlpha(0);
            egg.symbolSprite = symbolSprite;
        }
        // Note: We removed the individual click handler on egg to use global lens click logic
        this.eggs.add(egg);
    });

    // UI Elements (Scaled by MIN to fit)
    const uiScale = Math.min(scaleX, scaleY);

    this.eggZitButton = this.add.image(0, 200 * uiScale, 'egg-zit-button').setOrigin(0, 0).setDisplaySize(150 * uiScale, 150 * uiScale)
      .setInteractive()
      .setDepth(4).setScrollFactor(0);
    this.eggZitButton.on('pointerdown', () => {
        this.time.delayedCall(150, () => {
            this.scene.start('MapScene');
        });
    });
    addButtonInteraction(this, this.eggZitButton, 'drive1');
    addTooltip(this, this.eggZitButton, 'Back to Map');

    this.eggsAmminHaul = this.add.image(0, 350 * uiScale, 'eggs-ammin-haul').setOrigin(0, 0).setDisplaySize(137 * uiScale, 150 * uiScale)
      .setInteractive()
      .setDepth(4).setScrollFactor(0);
    this.eggsAmminHaul.on('pointerdown', () => {
        this.time.delayedCall(100, () => {
             this.scene.start('EggZamRoom');
        });
    });
    addButtonInteraction(this, this.eggsAmminHaul, 'menu-click');
    addTooltip(this, this.eggsAmminHaul, 'View Collection');

    const musicScene = this.scene.get('MusicScene');
    if (musicScene) {
        musicScene.playSFX('drive2');
    }

    this.scoreImage = this.add.image(0, 0, 'score').setOrigin(0, 0).setDisplaySize(200 * uiScale, 200 * uiScale).setDepth(4).setScrollFactor(0);
    const foundEggs = this.registry.get('foundEggs').length;
    this.scoreText = this.add.text(50 * uiScale, 98 * uiScale, `${foundEggs}/${TOTAL_EGGS}`, {
        fontSize: `${42 * uiScale}px`,
        fill: '#000',
        fontStyle: 'bold',
        fontFamily: 'Comic Sans MS',
        stroke: '#fff',
        strokeThickness: 6 * uiScale
    }).setDepth(5);

    // Fixed size Render Texture for Magnifier (Lens)
    const lensDiameter = 100;
    this.zoomedView = this.add.renderTexture(0, 0, lensDiameter, lensDiameter).setDepth(6).setScrollFactor(0);
    this.zoomedView.setOrigin(0.5, 0.5); // Center origin

    this.maskGraphics = this.add.graphics().fillCircle(0, 0, lensDiameter / 2).setScrollFactor(0);
    this.zoomedView.setMask(this.maskGraphics.createGeometryMask());

    this.magnifyingGlass = this.add.image(0, 0, 'magnifying-glass').setOrigin(0.25, 0.25).setDepth(7).setScrollFactor(0);

    // Render Stamp (reused for drawing video/bg/eggs into lens)
    // Key: if using video, we swap texture dynamically. If image, we set it here.
    const key = this.isUsingVideo ? 'placeholder-bg' : (this.sectionImage ? this.sectionImage.texture.key : this.sectionName);
    this.renderStamp = this.make.image({ x: 0, y: 0, key: key, add: false });

    // Stamp for eggs
    this.eggStamp = this.make.image({ x: 0, y: 0, key: 'egg-1', add: false });

    // Idle Hint Timer
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

    // Global click handler for egg collection within the lens
    this.input.on('pointerdown', (pointer) => {
        const captureRadiusSq = 50 * 50; // Lens capture radius

        // ⚡ Bolt Optimization: Use a fast for loop instead of forEach to prevent closure allocations
        const children = this.eggs.getChildren();
        // ⚡ Iterate backwards because destroying an object mutates the children array
        for (let i = children.length - 1; i >= 0; i--) {
            const egg = children[i];
            if (egg && egg.active) {
                // Check if egg is under the mouse (center of lens)
                const distSq = Phaser.Math.Distance.Squared(pointer.x, pointer.y, egg.x, egg.y);
                if (distSq < captureRadiusSq) {
                     this.collectEgg(egg);
                     egg.destroy();
                     if (egg.symbolSprite) egg.symbolSprite.destroy();
                     this.updateScore();
                }
            }
        }
    });

    this.scale.on('resize', this.resize, this);
    this.events.once('shutdown', () => {
        this.scale.off('resize', this.resize, this);
    });

    // Check level complete immediately if returning to a completed map
    this.checkLevelComplete(true);
  }

  updateScore() {
      // Defer to centralized changedata listener in MusicScene/Main
  }

  resize(gameSize) {
      const width = gameSize.width;
      const height = gameSize.height;

      if (this.cameras && this.cameras.main) {
          requestAnimationFrame(() => {
              if (this.cameras && this.cameras.main) {
                  try { this.cameras.main.setViewport(0, 0, width, height); } catch (e) {}
              }
          });
      }

      const scaleX = width / 1280;
      const scaleY = height / 720;
      // SWITCH TO FIT (Contain) to prevent cutting off bottom
      const scale = Math.min(scaleX, scaleY);

      this.bgScale = scale;
      this.bgOffsetX = (width - 1280 * scale) / 2;
      this.bgOffsetY = (height - 720 * scale) / 2;

      if (this.isUsingVideo && this.sectionVideo) {
          this.sectionVideo.setPosition(width/2, height/2);
          this.sectionVideo.setDisplaySize(1280 * scale, 720 * scale);
      } else if (this.sectionImage) {
          this.sectionImage.setPosition(width/2, height/2);
          this.sectionImage.setDisplaySize(1280 * scale, 720 * scale);
      }

      // UI Resize
      const uiScale = Math.min(scaleX, scaleY);
      this.eggZitButton.setPosition(0, 200 * uiScale).setDisplaySize(150 * uiScale, 150 * uiScale);
      this.eggZitButton.baseScaleX = this.eggZitButton.scaleX;
      this.eggZitButton.baseScaleY = this.eggZitButton.scaleY;
      this.eggsAmminHaul.setPosition(0, 350 * uiScale).setDisplaySize(137 * uiScale, 150 * uiScale);
      this.eggsAmminHaul.baseScaleX = this.eggsAmminHaul.scaleX;
      this.eggsAmminHaul.baseScaleY = this.eggsAmminHaul.scaleY;
      this.scoreImage.setDisplaySize(200 * uiScale, 200 * uiScale);
      this.scoreText.setPosition(50 * uiScale, 98 * uiScale).setFontSize(`${42 * uiScale}px`);
  }


  update() {
    const pointer = this.input.activePointer;

    // Magnifier logic
    // We want the lens (zoomedView) to follow the pointer.
    // Reverting offset to match original Desktop behavior (0.25, 0.2 origin with offset)
    // Magnifier logic
    // We want the lens (zoomedView) to follow the pointer exactly (Anchor).
    // We move the glass sprite relative to the pointer to align the visual loop.
    // Offset targets: X: -15 (Left), Y: -30 (Up).
    const glassOffsetX = -15;
    const glassOffsetY = -30;

    this.magnifyingGlass.setPosition(pointer.x + glassOffsetX, pointer.y + glassOffsetY);
    this.zoomedView.setPosition(pointer.x, pointer.y);
    this.maskGraphics.setPosition(pointer.x, pointer.y);

    // Zoom logic
    const zoom = 2;
    const lensDiameter = 100;
    const viewWidth = lensDiameter / zoom;
    const viewHeight = lensDiameter / zoom;

    // The "camera" of the render texture should be looking at the world coordinates
    // corresponding to the pointer's position.
    const scrollX = pointer.x - viewWidth / 2;
    const scrollY = pointer.y - viewHeight / 2;

    this.zoomedView.clear();

    // Draw Background/Video into ZoomedView
    // We use the renderStamp to draw the scaled background/video frame

    if (this.isUsingVideo && this.sectionVideo && this.sectionVideo.active) {
        // Swap texture to video frame
        this.renderStamp.setTexture(this.sectionVideo.texture.key, this.sectionVideo.frame.name);
    } else {
        // Use static image texture
        const key = this.sectionImage ? this.sectionImage.texture.key : this.sectionName;
        this.renderStamp.setTexture(key);
    }

    // Ensure stamp is scaled and positioned correctly relative to the "world"
    this.renderStamp.setOrigin(0, 0);

    // Calculate target scale directly without redundant matrix operations
    // Base scale = (1280 * this.bgScale) / renderStamp.width
    const targetScaleX = (1280 * this.bgScale / this.renderStamp.width) * zoom;
    const targetScaleY = (720 * this.bgScale / this.renderStamp.height) * zoom;
    this.renderStamp.setScale(targetScaleX, targetScaleY);

    // Position the stamp relative to the scroll position
    // If the background is at (bgOffsetX, bgOffsetY) in the world,
    // and we are looking at (scrollX, scrollY),
    // then the stamp should be drawn at (bgOffsetX - scrollX, bgOffsetY - scrollY) * zoom
    // inside the render texture.

    const drawX = (this.bgOffsetX - scrollX) * zoom;
    const drawY = (this.bgOffsetY - scrollY) * zoom;

    this.zoomedView.draw(this.renderStamp, drawX, drawY);

    // Draw Eggs
    // Visibility check: If egg is within the visual lens radius (pointer)
    const lensRadiusSq = (lensDiameter / 2) * (lensDiameter / 2);

    // ⚡ Bolt Optimization: Replace forEach with high-performance for loop in update loop
    const children = this.eggs.getChildren();
    const px = pointer.x;
    const py = pointer.y;
    for (let i = children.length - 1; i >= 0; i--) {
      const egg = children[i];
      if (egg && egg.active) {
        // Check distance to the POINTER (center of lens view)
        // ⚡ Bolt Optimization: Inline distance calculation to avoid function call overhead
        const dx = px - egg.x;
        const dy = py - egg.y;
        const distSq = dx * dx + dy * dy;
        const alpha = distSq < lensRadiusSq ? 1 : 0;

        egg.setAlpha(alpha);
        if (egg.symbolSprite) egg.symbolSprite.setAlpha(alpha);

        if (alpha > 0) {
            // Draw egg into render texture
            this.eggStamp.setTexture(egg.texture.key, egg.frame.name);
            this.eggStamp.setAngle(egg.angle);
            this.eggStamp.setFlipX(egg.flipX);
            this.eggStamp.setFlipY(egg.flipY);
            this.eggStamp.setOrigin(0.5, 0.5);

            // Scale egg by zoom factor
            this.eggStamp.setScale(egg.scaleX * zoom, egg.scaleY * zoom);

            // Calculate position in RT
            const eggDrawX = (egg.x - scrollX) * zoom;
            const eggDrawY = (egg.y - scrollY) * zoom;

            this.zoomedView.draw(this.eggStamp, eggDrawX, eggDrawY);

            if (egg.symbolSprite && egg.symbolSprite.active) {
                this.eggStamp.setTexture(egg.symbolSprite.texture.key, egg.symbolSprite.frame.name);
                this.eggStamp.setScale(egg.symbolSprite.scaleX * zoom, egg.symbolSprite.scaleY * zoom);
                const symDrawX = (egg.symbolSprite.x - scrollX) * zoom;
                const symDrawY = (egg.symbolSprite.y - scrollY) * zoom;
                this.zoomedView.draw(this.eggStamp, symDrawX, symDrawY);
            }
        }
      }
    }

    // Robust scaling check for Video in SectionHunt
    if (this.isUsingVideo && this.sectionVideo && this.sectionVideo.active) {
        if (this.sectionVideo.width > 0 && this.sectionVideo.height > 0) {
             // Check if scale matches Cover requirement
             const width = this.scale.width;
             const height = this.scale.height;
             const scaleX = width / 1280;
             const scaleY = height / 720;
             const targetScale = Math.max(scaleX, scaleY);
             const targetDisplayW = 1280 * targetScale;

             if (Math.abs(this.sectionVideo.displayWidth - targetDisplayW) > 5) {
                 this.sectionVideo.setDisplaySize(1280 * targetScale, 720 * targetScale);
                 this.sectionVideo.setPosition(width/2, height/2);

                 // Update globals used by lens
                 this.bgScale = targetScale;
                 this.bgOffsetX = (width - 1280 * targetScale) / 2;
                 this.bgOffsetY = (height - 720 * targetScale) / 2;
             }
        }
    }
  }
}

class EggZamRoom extends Phaser.Scene {

  playGoodEggAnimation(eggImage, symbolImage, onCompleteCallback) {
    this.playVideo('eggzam-eggcellent', onCompleteCallback);

    const scale = Math.min(this.sys.game.canvas.width / 1280, this.sys.game.canvas.height / 720);

    const startX = eggImage.x;
    const startY = eggImage.y;
    const targetY = startY - (100 * scale);
    
    const halo = this.add.image(startX, targetY, 'halo').setDepth(2).setAlpha(0).setScale(0.5 * scale);

    const sparkles = this.add.particles(0, 0, 'sparkle', {
        x: startX,
        y: targetY,
        speed: { min: -150 * scale, max: 150 * scale },
        angle: { min: 0, max: 360 },
        scale: { start: 1 * scale, end: 0 },
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
                scaleX: 2.0 * scale,
                scaleY: 2.0 * scale,
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
                            // callback is handled by playVideo completion
                        }
                    });
                }
            });
        }
    });
  }

  playBadEggAnimation(eggImage, symbolImage, onCompleteCallback) {
    this.playVideo('eggzam-stinky', onCompleteCallback);

    const scale = Math.min(this.sys.game.canvas.width / 1280, this.sys.game.canvas.height / 720);

    const startX = eggImage.x;
    const startY = eggImage.y;

    const musicScene = this.scene.get('MusicScene');
    if (musicScene) {
        const fartSound = this.sound.add('fart', { volume: this.registry.get('sfxVolume') ?? 0.5 });
        fartSound.play();
    }

    const gasParticles = this.add.particles(0, 0, 'green-gas', {
        x: startX,
        y: startY,
        speed: { min: 20 * scale, max: 100 * scale },
        angle: { min: 0, max: 360 },
        scale: { start: 1 * scale, end: 8 * scale },
        alpha: { start: 0.9, end: 0 },
        lifespan: 3000,
        frequency: 30, 
        blendMode: 'NORMAL', 
        rotate: { min: -10, max: 10 },
        gravityY: -20 * scale,
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
                x: this.cameras.main.width + (200 * scale),
                y: -100 * scale,
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
          const width = this.scale.width;
          const height = this.scale.height;
          const coverScale = Math.max(width / 1280, height / 720);
          
          this.currentVideo = this.add.video(width/2, height/2, videoKey)
              .setDepth(1)
              .setOrigin(0.5, 0.5);
              
          this.currentVideo.setVolume(this.registry.get('sfxVolume') ?? 0.5);

          // Phaser videos sometimes don't scale correctly until they are actively playing and populated
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
  create() {
    this.scene.bringToTop('CursorScene');
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

    // Scale logic
    const width = this.scale.width;
    const height = this.scale.height;
    const scaleX = width / 1280;
    const scaleY = height / 720;
    const scale = Math.min(scaleX, scaleY); // Fit logic for minigame usually better, but let's try cover or contained fit
    const uiScale = Math.min(scaleX, scaleY);

    // Position background centered (Cover logic for background)
    const coverScale = Math.max(scaleX, scaleY);
    this.add.image(width/2, height/2, 'eggzam-keyframe')
      .setDisplaySize(1168 * coverScale, 784 * coverScale)
      .setDepth(0);

    // We still use UI scale to keep UI elements proportionate and contained
    const offsetX = (width - 1280 * uiScale) / 2;
    const offsetY = (height - 720 * uiScale) / 2;

    this.add.image(offsetX + 200 * uiScale, offsetY + 50 * uiScale, 'symbol-result-summary-diag')
      .setOrigin(0, 0)
      .setDisplaySize(900 * uiScale, 600 * uiScale)
      .setDepth(1)
      .setAlpha(0);

    const eggZitButton = this.add.image(0, 200 * uiScale, 'egg-zit-button')
      .setOrigin(0, 0)
      .setDisplaySize(150 * uiScale, 131 * uiScale)
      .setInteractive()
      .on('pointerdown', () => {
          this.time.delayedCall(150, () => {
              this.scene.start('MapScene');
          });
      })
      .setDepth(4).setScrollFactor(0);
    addButtonInteraction(this, eggZitButton, 'drive1');
    addTooltip(this, eggZitButton, 'Back to Map');

    this.add.image(0, 0, 'score')
      .setOrigin(0, 0)
      .setDisplaySize(200 * uiScale, 200 * uiScale)
      .setDepth(4).setScrollFactor(0);

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
    }).setDepth(5).setOrigin(0.5);

    const showExplanation = (isCorrect, guessText) => {
        if (this.explanationText) this.explanationText.destroy();
        const data = this.currentEgg.symbolData;
        const eggId = this.currentEgg.eggId;

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

            this.explanationText = this.add.container(offsetX + 640 * uiScale, offsetY + 360 * uiScale).setDepth(100);

        const bgWidth = 1200 * uiScale;
        const bgHeight = 600 * uiScale;

        const bg = this.add.graphics();
        bg.fillStyle(0xfff8dc, 1);
        bg.fillRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * uiScale);
        bg.lineStyle(8 * uiScale, 0x8b4513, 1);
        bg.strokeRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * uiScale);

        // Block clicks behind the popup
        bg.setInteractive(new Phaser.Geom.Rectangle(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight), Phaser.Geom.Rectangle.Contains);

        // Header Elements (Percentage based Y)
        const title = this.add.text(0, -bgHeight * 0.42, data.name || "Symbol", {
            fontSize: `${48 * uiScale}px`, fill: '#8b4513', fontStyle: 'bold', fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5);

        // Your Guess (Percentage based Y) - reduced whitespace and removed newline
        const guessDisplay = this.add.text(0, -bgHeight * 0.33, `Your Guess: ${guessText}`, {
            fontSize: `${24 * uiScale}px`, fill: '#333', fontStyle: 'bold', fontFamily: 'Comic Sans MS', align: 'center'
        }).setOrigin(0.5, 0.5);

        announceToScreenReader(isCorrect ? "Correct!" : "Incorrect!");

        // Result Text (Percentage based Y) - reduced whitespace
        const resultText = this.add.text(0, -bgHeight * 0.25, isCorrect ? "Correct!" : "Incorrect!", {
            fontSize: `${28 * uiScale}px`,
            fill: isCorrect ? '#008000' : '#d32f2f',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#fff',
            strokeThickness: 6 * uiScale
        }).setOrigin(0.5, 0.5);

        // Explanation Text (Percentage based Y) - moved up due to reduced whitespace
        const expText = this.add.text(0, -bgHeight * 0.04, data.explanation, {
            fontSize: `${28 * uiScale}px`, fill: '#000', fontFamily: 'Comic Sans MS',
            wordWrap: { width: bgWidth * 0.9, useAdvancedWrap: true }, align: 'center'
        }).setOrigin(0.5);

        // Scripture Link (Percentage based Y)
        const scriptureElements = [];
        const scriptures = data.scripture.split(',').map(s => s.trim());
        let totalWidth = 0;
        const tempText = this.add.text(0, 0, '', {
            fontSize: `${24 * uiScale}px`, fontStyle: 'italic', fontFamily: 'Comic Sans MS'
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
                fontSize: `${24 * uiScale}px`, fill: '#0000ee', fontStyle: 'italic', fontFamily: 'Comic Sans MS'
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
                    // Override the global cursor: none !important to show custom finger cursor
                    iframeOverlay.style.setProperty('cursor', "url('assets/cursor/pointer-finger-pointer.png'), auto", 'important');

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
                    closeBtn.style.setProperty('cursor', "url('assets/cursor/pointer-finger-pointer.png'), auto", 'important');
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
                    fontSize: `${24 * uiScale}px`, fill: '#000', fontStyle: 'italic', fontFamily: 'Comic Sans MS'
                }).setOrigin(0, 0.5);
                scriptureElements.push(commaText);
                currentX += commaText.width;
            }
        });
        tempText.destroy();

        // Position elements in top corners, aligned equally with nearest borders
        // The dialog border is at x: -bgWidth/2 to +bgWidth/2, y: -bgHeight/2 to +bgHeight/2
        // We add an equal inset (e.g. 25px * uiScale) for top, left, and right
        const cornerInset = -10 * uiScale;
        const cornerY = -bgHeight/2 + cornerInset;
        
        // Egg aligned to Top-Left corner
        // Origin of image is 0.5, so we shift it down and right by half its size
        const eggSizeW = 80 * uiScale;
        const eggSizeH = 100 * uiScale;
        const eggX = -bgWidth/2 + cornerInset + eggSizeW/2;
        const eggImg = this.add.image(eggX, cornerY + eggSizeH/2, `egg-${eggId}`).setDisplaySize(eggSizeW, eggSizeH);

        // Symbol image if exists
        let symbolImgSmall = null;
        if (data && data.filename && this.textures.exists(data.filename)) {
            symbolImgSmall = this.add.image(eggX, cornerY + eggSizeH/2, data.filename).setDisplaySize(eggSizeW, eggSizeH);
        }

        // Massive Red X Close Button aligned to Top-Right corner
        // Matching the egg size for consistency
        const closeBtnSize = 80 * uiScale;
        const closeBtnX = bgWidth/2 - cornerInset - closeBtnSize/2;
        const closeBtnContainer = this.add.container(closeBtnX, cornerY + closeBtnSize/2);

        const closeBtnBg = this.add.graphics();
        closeBtnBg.fillStyle(0xff0000, 1);
        closeBtnBg.lineStyle(4 * uiScale, 0x8b4513, 1); // Brown stroke to match dialog
        // Draw a circle for the X button
        closeBtnBg.fillCircle(0, 0, closeBtnSize/2);
        closeBtnBg.strokeCircle(0, 0, closeBtnSize/2);

        const closeBtnText = this.add.text(0, 0, '\u2716', {
            fontSize: `${48 * uiScale}px`,
            fill: '#ffffff',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5, 0.5);

        closeBtnContainer.add([closeBtnBg, closeBtnText]);
        // Set interactive area for a circle
        closeBtnContainer.setSize(closeBtnSize, closeBtnSize);
        closeBtnContainer.setInteractive();

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
                    
                    if (this.actionButtons) {
                        this.actionButtons.forEach(btn => btn.setVisible(true));
                    }
                    
                    if (!isCorrect) {
                        this.currentEgg = null;
                    }
                    this.displayRandomEggInfo(offsetX, offsetY, uiScale);
                    
                    window.removeEventListener('keydown', this.popupKeyHandler);
                }
            });
        };

        closeBtnContainer.on('pointerdown', () => {
            if (this.currentVideo && this.currentVideo.active && this.currentVideo.video.src.includes('ambient')) {
                this.stopCurrentVideo(); // Interrupt ambient video
            }
            this.resetAmbientTimer();
            this.time.delayedCall(100, dismissPopup);
        });

        this.popupKeyHandler = (e) => {
            if (e.code === 'Escape' || e.code === 'Enter') {
                if (this.currentVideo && this.currentVideo.active && this.currentVideo.video.src.includes('ambient')) {
                    this.stopCurrentVideo(); // Interrupt ambient video
                }
                this.resetAmbientTimer();
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
        };

        if (isCorrect) {
            if (data.category === 'Christian') {
                this.playGoodEggAnimation(this.displayedEggImage, this.displayedSymbolImage, () => executeExplanationPopup());
            } else if (data.category === 'Pagan') {
                this.playBadEggAnimation(this.displayedEggImage, this.displayedSymbolImage, () => executeExplanationPopup());
            } else {
                executeExplanationPopup();
            }
        } else {
            this.playIncorrectAnimation(() => executeExplanationPopup());
        }
    };

    const btnScale = uiScale * 0.4;
    const centerBottomX = offsetX + (1280 * uiScale) / 2;
    const centerBottomY = offsetY + (720 * uiScale) - (100 * uiScale);
    
    const buttonSpacing = 120 * uiScale;

    // Swap positions: Eggs-tra Stinky on the left, Egg-cellent on the right, and closer together
    const stinkyBtn = this.add.sprite(centerBottomX - buttonSpacing, centerBottomY, 'eggs-tra-stinky-button', 'Symbol 10000')
        .setScale(btnScale)
        .setDepth(90)
        .setInteractive();
        
    stinkyBtn.on('pointerover', () => {
        // Check if animations exist, if not, fallback to frame setting manually.
        // It appears 'Symbol 10003' exists in JSON but the initial sprite creation might not have bound the default frame properly causing it to lock.
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

    addTooltip(this, stinkyBtn, 'Categorize as Eggs-tra Stinky');

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
    
    addTooltip(this, eggCellentBtn, 'Categorize as Egg-cellent');

    // Make sure we store them in visual order left-to-right for consistency later if needed
    this.actionButtons = [stinkyBtn, eggCellentBtn];

    this.displayRandomEggInfo(offsetX, offsetY, uiScale);

    // Store scale params for update/resize if needed (or just restart scene on resize)
    this.uiParams = { offsetX, offsetY, uiScale };

    const onResize = () => {
        this.scene.restart(); // Simplest way to handle resizing complex UI layouts
    };
    this.scale.on('resize', onResize);
    this.events.once('shutdown', () => {
        this.scale.off('resize', onResize);
    });
  }

  displayRandomEggInfo(offsetX, offsetY, scale) {
    const foundEggs = this.registry.get('foundEggs');

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
        this.noEggsText = this.add.text(offsetX + 420 * scale, offsetY + 220 * scale, ctaText, {
          fontSize: `${28 * scale}px`,
          fill: '#000',
          fontStyle: 'bold',
          fontFamily: 'Comic Sans MS',
          stroke: '#fff',
          strokeThickness: 3 * scale,
          align: 'center',
          wordWrap: { width: 480 * scale, useAdvancedWrap: true }
        }).setDepth(90).setOrigin(0, 0);

        if (foundEggs.length === TOTAL_EGGS) {
          // Summary Panel
          const summaryContainer = this.add.container(offsetX + 420 * scale, offsetY + 300 * scale).setDepth(90);

          const holyEggs = foundEggs.filter(e => e.symbolData && e.symbolData.category === 'Christian').length;
          const worldlyEggs = foundEggs.filter(e => e.symbolData && e.symbolData.category === 'Pagan').length;

          const panelWidth = 480 * scale;
          const panelHeight = 240 * scale;

          const panelBg = this.add.graphics();
          panelBg.fillStyle(0xfff8dc, 1);
          panelBg.lineStyle(6 * scale, 0x8b4513, 1);
          panelBg.fillRoundedRect(0, 0, panelWidth, panelHeight, 20 * scale);
          panelBg.strokeRoundedRect(0, 0, panelWidth, panelHeight, 20 * scale);

          const titleText = this.add.text(20 * scale, 30 * scale, 'Final EggZam!', {
              fontSize: `${32 * scale}px`,
              fill: '#8b4513',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0, 0.5);

          const currentScore = this.registry.get('currentScore') || 0;
          const scoreTextLabel = this.add.text(panelWidth - 20 * scale, 30 * scale, `Score: ${currentScore}`, {
              fontSize: `${32 * scale}px`,
              fill: '#8b4513',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS',
              align: 'right'
          }).setOrigin(1, 0.5);

          const holyText = this.add.text(panelWidth / 2, 75 * scale, `Egg-cellent Eggs: ${holyEggs} / 30`, {
              fontSize: `${24 * scale}px`,
              fill: '#008000',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5);

          const worldlyText = this.add.text(panelWidth / 2, 115 * scale, `Eggs-tra Stinky Eggs: ${worldlyEggs} / 30`, {
              fontSize: `${24 * scale}px`,
              fill: '#d32f2f',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5);

          const totalText = this.add.text(panelWidth / 2, 155 * scale, `Total Categorized: 60/60`, {
              fontSize: `${24 * scale}px`,
              fill: '#000000',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5);

          // PLAY AGAIN Button inside Summary Panel
          const playBtnContainer = this.add.container(panelWidth / 2 - 125 * scale, 180 * scale).setDepth(101);

          const playBtnWidth = 250 * scale;
          const playBtnHeight = 45 * scale;

          const playBtnBg = this.add.graphics();
          playBtnBg.fillStyle(0xffff00, 1);
          playBtnBg.lineStyle(4 * scale, 0x000000, 1);
          playBtnBg.fillRoundedRect(0, 0, playBtnWidth, playBtnHeight, 10 * scale);
          playBtnBg.strokeRoundedRect(0, 0, playBtnWidth, playBtnHeight, 10 * scale);

          const playBtnText = this.add.text(playBtnWidth / 2, playBtnHeight / 2, 'PLAY AGAIN', {
              fontSize: `${24 * scale}px`,
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
                  try { localStorage.removeItem('heIsRisenGameState'); } catch (e) { console.warn('localStorage error', e); }
                  initializeGameData(this.registry, this.cache, true);
                  this.scene.start('MapScene');
              });
          };

          playBtnContainer.on('pointerdown', triggerRestart);
          this.input.keyboard.once('keydown-SPACE', triggerRestart);
          this.input.keyboard.once('keydown-ENTER', triggerRestart);

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
      
      // Target coordinates inside the central egg chamber of the keyframe.
      // Based on visual inspection: Center-left.
      // Assuming original keyframe coords (1168x784), scaled down/up via coverScale.
      const eggPosX = offsetX + (1280 * scale) * 0.44 + (34 * scale); 
      const eggPosY = offsetY + (720 * scale) * 0.42 + (80 * scale);
      const symbolPosX = eggPosX;
      const symbolPosY = eggPosY;
      
      // Make egg as large as possible to fit chamber
      const eggScaleTarget = (240 * scale) * 0.85;
      const eggHeightTarget = (300 * scale) * 0.85;

      if (this.textures.exists(`egg-${eggId}`)) {
        this.displayedEggImage = this.add.image(eggPosX, eggPosY, `egg-${eggId}`)
          .setDisplaySize(eggScaleTarget, eggHeightTarget)
          .setAlpha(0.40) // Reduced opacity to 40%
          .setDepth(3);
      }
      if (symbolData && symbolData.filename && this.textures.exists(symbolData.filename)) {
        this.displayedSymbolImage = this.add.image(symbolPosX, symbolPosY, symbolData.filename)
          .setDisplaySize(eggScaleTarget, eggHeightTarget)
          .setAlpha(0.65) // Reduced opacity to 65%
          .setDepth(4); // Symbol sits above the egg
      }
    }
  }

  update() {
  }
}

/**
 * Adds a "pop" animation to a game object on hover.
 */
function addButtonInteraction(scene, button, soundKey = 'success') {
  button.on('pointerover', () => {
    if (!button.isHovered) {
        button.baseScaleX = button.scaleX;
        button.baseScaleY = button.scaleY;
    }
    button.isHovered = true;

    scene.tweens.killTweensOf(button);
    scene.tweens.add({
      targets: button,
      scaleX: button.baseScaleX * 1.1,
      scaleY: button.baseScaleY * 1.1,
      duration: 100,
      ease: 'Power1'
    });
  });

  button.on('pointerout', () => {
    button.isHovered = false;
    scene.tweens.killTweensOf(button);
    if (button.baseScaleX !== undefined && button.baseScaleY !== undefined) {
      scene.tweens.add({
        targets: button,
        scaleX: button.baseScaleX,
        scaleY: button.baseScaleY,
        duration: 100,
        ease: 'Power1'
      });
    }
  });

  button.on('pointerdown', () => {
    const musicScene = scene.scene.get('MusicScene');
    if (musicScene && musicScene.scene.isActive()) {
      musicScene.playSFX(soundKey);
    } else if (soundKey && scene.sound.get(soundKey)) {
      scene.sound.play(soundKey, { volume: scene.registry.get('sfxVolume') ?? 0.5 });
    }

    if (navigator && navigator.vibrate) {
      navigator.vibrate(20);
    }

    if (button.baseScaleX === undefined) {
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

  button.on('pointerup', () => {
    if (button.baseScaleX !== undefined && button.baseScaleY !== undefined) {
      scene.tweens.killTweensOf(button);
      scene.tweens.add({
        targets: button,
        scaleX: button.baseScaleX * 1.1,
        scaleY: button.baseScaleY * 1.1,
        duration: 100,
        ease: 'Power1'
      });
    }
  });
}

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
 * Adds a tooltip to a game object on hover.
 */
function addTooltip(scene, object, text) {
  let tooltipContainer = null;

  object.on('pointerover', (pointer) => {
    if (tooltipContainer) return;

    const padding = 8;
    const style = {
      fontSize: '16px',
      fontFamily: 'Comic Sans MS',
      fill: '#ffffff'
    };

    const textObj = scene.add.text(0, 0, text, style);
    const width = textObj.width + padding * 2;
    const height = textObj.height + padding * 2;

    const bg = scene.add.graphics();
    bg.fillStyle(0x000000, 0.8);
    bg.fillRoundedRect(-width/2, -height/2, width, height, 5);

    textObj.setOrigin(0.5, 0.5);

    // Position slightly above the pointer
    // Use pointer.x/y for screen coordinates since tooltip is fixed to screen
    tooltipContainer = scene.add.container(pointer.x, pointer.y - 30, [bg, textObj]);
    tooltipContainer.setDepth(1000);
    tooltipContainer.setScrollFactor(0);

    // Basic bounds check
    const cam = scene.cameras.main;
    if (tooltipContainer.x + width/2 > cam.width) {
        tooltipContainer.x = cam.width - width/2 - 5;
    }
    if (tooltipContainer.x - width/2 < 0) {
        tooltipContainer.x = width/2 + 5;
    }
    if (tooltipContainer.y - height/2 < 0) {
        tooltipContainer.y = pointer.y + 40; // Flip below
    }
  });

  object.on('pointermove', (pointer) => {
    if (tooltipContainer) {
        tooltipContainer.setPosition(pointer.x, pointer.y - 30);

        const height = tooltipContainer.getBounds().height;
        if (pointer.y - 30 - height/2 < 0) {
             tooltipContainer.y = pointer.y + 40;
        }
    }
  });

  object.on('pointerout', () => {
    if (tooltipContainer) {
      tooltipContainer.destroy();
      tooltipContainer = null;
    }
  });

  object.once('destroy', () => {
      if (tooltipContainer) {
          tooltipContainer.destroy();
          tooltipContainer = null;
      }
  });
}

// Game configuration
const config = {
  type: Phaser.AUTO,
  transparent: true,
  scale: {
      mode: Phaser.Scale.RESIZE, // Fill the window
      parent: 'game',
      width: '100%',
      height: '100%'
  },
  scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene, CursorScene],
  parent: 'game',
  backgroundColor: '#000000',
};

// Initialize the game
const game = new Phaser.Game(config);
window.game = game;

// Auto-focus the game container for screen readers and keyboard accessibility
window.addEventListener('load', () => {
    const gameContainer = document.getElementById('game');
    if (gameContainer) gameContainer.focus();
});
