/* -= main.js =- */
// Define total eggs as a variable to avoid hardcoding
const TOTAL_EGGS = 60;

// Define all scene classes first

class MusicScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MusicScene' });
    this.musicVolume = localStorage.getItem('musicVolume') !== null ? parseFloat(localStorage.getItem('musicVolume')) : 0.5;
    this.ambientVolume = localStorage.getItem('ambientVolume') !== null ? parseFloat(localStorage.getItem('ambientVolume')) : 0.5;
    this.sfxVolume = localStorage.getItem('sfxVolume') !== null ? parseFloat(localStorage.getItem('sfxVolume')) : 0.5;
  }

  create() {
    // console.log('MusicScene: checking background music');
    const music = this.sound.get('background-music');
    if (!music) {
      this.sound.add('background-music', { loop: true, volume: this.musicVolume }).play();
      // console.log('MusicScene: Background music started');
    } else if (!music.isPlaying) {
      // Ensure volume is updated if restarting
      music.setVolume(this.musicVolume);
      music.play();
      // console.log('MusicScene: Background music resumed');
    }

    // Schedule ambient1 to play randomly every 1-3 minutes
    this.scheduleAmbientSound();

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
            localStorage.setItem(key, data);
        }
    });
  }

  scheduleAmbientSound() {
    const delay = Phaser.Math.Between(60000, 180000); // 1-3 minutes in ms
    // console.log(`MusicScene: Scheduling ambient1 in ${delay}ms`);
    this.time.delayedCall(delay, () => {
      this.sound.play('ambient1', { volume: this.ambientVolume });
      this.scheduleAmbientSound(); // Reschedule
    });
  }

  playSFX(key) {
    if (this.cache.audio.exists(key)) {
        this.sound.play(key, { volume: this.sfxVolume });
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
            this.settingsContainer.setVisible(false);
            if (this.gearIcon) this.gearIcon.setVisible(true);
            this.input.setDefaultCursor('none');
        } else {
            this.openSettings();
        }
    };
    const closeSettings = () => {
        if (this.settingsContainer && this.settingsContainer.visible) {
            this.settingsContainer.setVisible(false);
            if (this.gearIcon) this.gearIcon.setVisible(true);
            this.input.setDefaultCursor('none');
        }
    };
    if (this.input.keyboard) {
        this.input.keyboard.on('keydown-ESC', toggleSettings);
        this.input.keyboard.on('keydown-ENTER', closeSettings);
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
        this.gearIcon.setPosition(width - 30, 30);
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
    const x = this.cameras.main.width - 30;
    const y = 30;

    // Create a container to hold the background and the cog
    const gearContainer = this.add.container(x, y).setDepth(10); // Keep below cursor

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
    this.settingsContainer = this.add.container(0, 0).setVisible(false).setDepth(100);
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
                this.settingsContainer.setVisible(false);
                this.gearIcon.setVisible(true);
                this.input.setDefaultCursor('none');
                closeBtn.setScale(1); // Reset
            }
        });
    });
    this.settingsContainer.add(closeBtn);

    // Calculate layout for sliders
    // Space available below title (y + 80) to bottom (y + height - 20)
    const contentTop = y + 80;
    const contentHeight = height - 100;
    const spacing = contentHeight / 3;
    const trackWidth = Math.min(200, width - 60);

    this.createSlider('Music', contentTop + spacing * 0.5, screenWidth / 2, 'music', trackWidth);
    this.createSlider('Ambient', contentTop + spacing * 1.5, screenWidth / 2, 'ambient', trackWidth);
    this.createSlider('SFX', contentTop + spacing * 2.5, screenWidth / 2, 'sfx', trackWidth);
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

  openSettings() {
    this.settingsContainer.setVisible(true);
    this.gearIcon.setVisible(false);
    this.input.setDefaultCursor('default');
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
    this.load.video('level-complete', 'assets/video/level-complete.mp4');
    this.load.image('level-complete-stamp', 'assets/objects/level-complete-stamp.png');
    this.load.image('finger-cursor', 'assets/cursor/pointer-finger-pointer.png');

    // Audio assets
    this.load.audio('background-music', 'assets/audio/background-music.mp3');
    this.load.audio('collect', 'assets/audio/collect1.mp3');
    this.load.audio('success', 'assets/audio/success.wav');
    this.load.audio('error', 'assets/audio/error.wav');
    this.load.audio('ambient1', 'assets/audio/ambient1.mp3');
    this.load.audio('menu-click', 'assets/audio/menu-click.mp3');
    this.load.audio('drive1', 'assets/audio/drive1.mp3');
    this.load.audio('drive2', 'assets/audio/drive2.mp3');

    // Preload common UI and game assets here to avoid reloading in scenes
    this.load.image('new-map', 'assets/map/new-map.png');
    this.load.image('cog', 'assets/objects/cog.png');
    this.load.image('magnifying-glass', 'assets/cursor/magnifying-glass.png');
    this.load.image('egg-zit-button', 'assets/objects/egg-zit-button.png');
    this.load.image('eggs-ammin-haul', 'assets/objects/eggs-ammin-haul.png');
    this.load.image('score', 'assets/objects/score.png');
    this.load.image('egg-zam-room', 'assets/map/egg-zam-room.png');
    this.load.image('egg-zamminer', 'assets/objects/egg-zamminer.png');
    this.load.image('symbol-result-summary-diag', 'assets/objects/symbol-result-summary-diag.png');

    // Preload all 60 eggs
    for (let i = 1; i <= TOTAL_EGGS; i++) {
      this.load.image(`egg-${i}`, `assets/eggs/egg-${i}.png`);
    }

    this.load.on('filecomplete-json-symbols', (key, type, data) => {
      // console.log(`MainMenu: filecomplete-json-symbols: Key='${key}', Type='${type}'`);
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
        // console.log(`MainMenu: Queued ${data.symbols.length} symbol images for loading.`);
      }
    });

    this.load.on('filecomplete-json-map_sections', (key, type, data) => {
      // console.log(`MainMenu: filecomplete-json-map_sections: Key='${key}', Type='${type}'`);
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
      // console.log('MainMenu: Initializing game state');
      this.registry.set('foundEggs', []);
      this.registry.set('stampedSections', []);
      this.registry.set('correctCategorizations', 0);
      this.registry.set('currentScore', 0);

      try {
          this.registry.set('highScore', parseInt(localStorage.getItem('highScore')) || 0);
      } catch (e) {
          console.warn('LocalStorage access failed:', e);
          this.registry.set('highScore', 0);
      }
      // console.log('MainMenu: highScore:', this.registry.get('highScore'));

      // Load and validate symbols and map sections
      const symbolsData = this.cache.json.get('symbols');
      const mapSections = this.cache.json.get('map_sections');
      if (!symbolsData || !symbolsData.symbols || !Array.isArray(symbolsData.symbols)) {
        console.error('MainMenu: Invalid symbols data:', symbolsData);
        return;
      }

      // Sentinel: Filter invalid symbols before using them in game logic
      const validSymbols = symbolsData.symbols.filter(s => this.isValidSymbol(s));
      if (validSymbols.length !== symbolsData.symbols.length) {
          console.warn(`Security: Filtered ${symbolsData.symbols.length - validSymbols.length} invalid symbols.`);
          symbolsData.symbols = validSymbols;
      }

      if (symbolsData.symbols.length !== TOTAL_EGGS) {
        console.error(`MainMenu: Expected ${TOTAL_EGGS} symbols, found ${symbolsData.symbols.length}`);
      }
      if (!mapSections) { console.error('Map sections missing'); return; }
      if (mapSections.length !== 11) {
        console.warn(`MainMenu: Expected 11 sections, found ${mapSections.length || 0}`);
      }
      this.registry.set('symbols', symbolsData);

      // Randomly assign 3-8 eggs per section, totaling TOTAL_EGGS
      const eggCounts = [];
      let remainingEggs = TOTAL_EGGS;
      const numSections = mapSections.length;
      for (let i = 0; i < numSections - 1; i++) {
        const maxPossible = remainingEggs - ((numSections - 1 - i) * 3);
        const minPossible = remainingEggs - ((numSections - 1 - i) * 8);

        const maxEggs = Math.min(8, maxPossible);
        const minEggs = Math.max(3, minPossible);

        const count = Phaser.Math.Between(minEggs, maxEggs);
        eggCounts.push(count);
        remainingEggs -= count;
      }
      eggCounts.push(remainingEggs);

      // console.log('MainMenu: Egg distribution:', eggCounts);

      // Shuffle egg IDs and symbols
      const eggs = Phaser.Utils.Array.Shuffle(Array.from({ length: TOTAL_EGGS }, (_, i) => i + 1));
      const shuffledSymbols = Phaser.Utils.Array.Shuffle([...symbolsData.symbols]);

      // Create eggData and sections
      const eggData = [];
      let eggIndex = 0;
      const sections = mapSections.map((section, index) => {
        const sectionEggs = eggs.slice(eggIndex, eggIndex + eggCounts[index]);
        eggIndex += eggCounts[index];
        sectionEggs.forEach((eggId, idx) => {
          // Fix: Mobile viewport coordinates are absolute, don't divide by scale for the max bounds.
          // The visual lens has an offset of (-97.5, -135) relative to the physical touch pointer.
          // This means to reach an egg at (x, y), the user must touch at (x + 97.5, y + 135).
          // We must ensure that this required touch point never falls outside the screen bounds.
          // Therefore, the max bounds for an egg must be at least that far from the right/bottom edges.
          // We also must ensure that min bounds are respected relative to negative offsets.
          // The lens offset in Mobile is X: -97.5, Y: -135 (lens is UP and LEFT of pointer).
          // Meaning if an egg is at X=0, the user must touch at X=+97.5.
          // Conversely, if an egg is at X=width, the user must touch at X=width+97.5 (which is OFF SCREEN).
          // To ensure the required TOUCH is within [0, width], the EGG must be within [0 - 97.5, width - 97.5].
          // However, we also want the egg to be visible on screen.
          // So the EGG must be within [50, width - 150].

          // Phaser.Math.Between requires max >= min. If screen is very small, we might get negative ranges.
          // We clamp maxX and maxY to be at least minX and minY to avoid Phaser errors.
          // Wait, the lens offset is scaling based on the *current* scale (which can be very different based on device orientation).
          // And we must ensure the REQUIRED touch (egg.x - (-97.5 * scale)) is <= screen width.
          // required_touch_x = egg.x + 97.5 * scale <= width => egg.x <= width - 97.5 * scale
          // Let's add an extra safety margin. width - 150 * scale is good.
          // BUT what if width is VERY small?
          // Let's use strict bounds:
          const minX = 50 * scale;
          const maxX = Math.max(minX, this.game.config.width - (160 * scale));
          const minY = 50 * scale;
          const maxY = Math.max(minY, this.game.config.height - (200 * scale));

          const x = Phaser.Math.Between(minX, maxX);
          const y = Phaser.Math.Between(minY, maxY);

          eggData.push({
            eggId: eggId,
            section: section.name,
            x: x,
            y: y,
            symbol: shuffledSymbols[eggId - 1] || null,
            collected: false
          });
        });
        return { name: section.name, eggs: sectionEggs };
      });

      this.registry.set('eggData', eggData);
      this.registry.set('sections', sections);
      // console.log('MainMenu: Initialized eggData:', eggData);

      // Debug: Log game dimensions and scale
      // console.log(`MainMenu: Game dimensions - width: ${this.game.config.width}, height: ${this.game.config.height}, scale: ${scale}`);

      // Set camera bounds to match viewport
      this.cameras.main.setBounds(0, 0, this.game.config.width, this.game.config.height);
      this.cameras.main.setViewport(0, 0, this.game.config.width, this.game.config.height);
      this.cameras.main.setPosition(0, 0);

      // Debug: Log camera position
      // console.log(`MainMenu: Camera position - x: ${this.cameras.main.scrollX}, y: ${this.cameras.main.scrollY}`);

      // Intro Video - centered
      const introVideo = this.add.video(this.game.config.width / 2, this.game.config.height / 2, 'intro-video');
      this.introVideo = introVideo; // Store reference for resizing
      introVideo.setMute(true); // Start muted to allow autoplay
      introVideo.disableInteractive(); // Ensure video ignores input
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
          .setDepth(1000); // Ensure cursor is on top of everything
      }

      // Handle both mouse and touch input, request fullscreen on first click
      const safeRequestFullscreen = (element) => {
        if (element.requestFullscreen) {
          element.requestFullscreen().catch(err => {}); // console.log('Fullscreen failed:', err));
        } else if (element.webkitRequestFullscreen) {
          element.webkitRequestFullscreen().catch(err => {}); // console.log('Fullscreen failed:', err));
        }
      };

      // NEW INTRO SEQUENCE LOGIC
      // 1. Silent Loop + "Tap anywhere to start"
      // 2. User Tap -> Unmute, Fullscreen, Wait 3s
      // 3. Show "Play Now" Button
      // 4. User Tap "Play Now" -> Start Game

    // Initialize volume registry early (Load from localStorage if available)
    const savedMusic = localStorage.getItem('musicVolume');
    const savedAmbient = localStorage.getItem('ambientVolume');
    const savedSfx = localStorage.getItem('sfxVolume');

    if (!this.registry.has('musicVolume')) this.registry.set('musicVolume', savedMusic !== null ? parseFloat(savedMusic) : 0.5);
    if (!this.registry.has('ambientVolume')) this.registry.set('ambientVolume', savedAmbient !== null ? parseFloat(savedAmbient) : 0.5);
    if (!this.registry.has('sfxVolume')) this.registry.set('sfxVolume', savedSfx !== null ? parseFloat(savedSfx) : 0.5);

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
      }).setOrigin(0.5).setDepth(100);

      // "Play Now" Button Container (Initially Hidden)
      const buttonWidth = 400;
      const buttonHeight = 100;
      const btnX = this.game.config.width / 2;
      const btnY = 580 * scale;

      const startBtnContainer = this.add.container(btnX, btnY).setVisible(false).setDepth(101);
      this.startBtnContainer = startBtnContainer;

      const btnBg = this.add.graphics();
      btnBg.fillStyle(0xff0000, 1);
      btnBg.fillRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, buttonHeight / 2);
      btnBg.lineStyle(4, 0xffffff, 1);
      btnBg.strokeRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, buttonHeight / 2);
      startBtnContainer.add(btnBg);

      const btnText = this.add.text(0, 0, 'PLAY NOW', {
        fontSize: `40px`,
        fill: '#ffffff',
        fontStyle: 'bold',
        fontFamily: 'Comic Sans MS',
        stroke: '#000000',
        strokeThickness: 4
      }).setOrigin(0.5);
      startBtnContainer.add(btnText);

      startBtnContainer.setSize(buttonWidth, buttonHeight);
      // Massive hit area for easier tapping
      startBtnContainer.setInteractive(new Phaser.Geom.Rectangle(-buttonWidth, -buttonHeight * 2, buttonWidth * 2, buttonHeight * 4), Phaser.Geom.Rectangle.Contains);
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
      const startGame = () => {
          if (introState !== 'ready_to_play') return;

          // Prevent multiple calls
          introState = 'starting';

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

                  this.sound.play('drive1', { volume: 0.5 });
                  this.scene.start('MapScene');
              }
          });
      };

      startBtnContainer.on('pointerdown', startGame);

      // Explicitly add window listener for robust keyboard support on initial screen
      const globalKeyHandler = (e) => {
          if (e.code === 'Space' || e.code === 'Enter') {
              if (introState === 'waiting_for_interaction') {
                  handleGlobalTap();
              } else if (introState === 'ready_to_play') {
                  startGame();
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

    // Ensure video size is correct once texture loads
    if (this.introVideo && this.introVideo.active && this.introVideo.width > 0) {
        if (Math.abs(this.introVideo.displayWidth - this.game.config.width) > 10) {
            this.introVideo.setDisplaySize(this.game.config.width, this.game.config.height);
        }
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
    this.cameras.main.setViewport(0, 0, this.game.config.width, this.game.config.height);
    this.cameras.main.setPosition(0, 0);

    // NEW: Retrieve existing eggData and sections from registry
    const eggData = this.registry.get('eggData');
    const sections = this.registry.get('sections');
    const mapSections = this.cache.json.get('map_sections') || [];
    if (!eggData || !sections) {
      console.error('MapScene: eggData or sections missing from registry');
      this.scene.start('MainMenu'); // Fallback to MainMenu
      return;
    }
    // console.log('MapScene: Using existing eggData:', eggData);

    if (!this.scene.get('MusicScene').scene.isActive()) {
      this.scene.launch('MusicScene');
    }
    this.sound.play('drive2', { volume: 0.5 });

    // Add map image, fill the viewport proportionally based on native size
    this.mapImage = this.add.image(this.game.config.width/2, this.game.config.height/2, 'new-map')
      .setOrigin(0.5, 0.5);
    const nativeW = this.mapImage.width || 1376;
    const nativeH = this.mapImage.height || 768;
    const mapScale = Math.max(this.game.config.width / nativeW, this.game.config.height / nativeH);
    this.mapImage.setScale(mapScale);
    // console.log(`Map display size: ${this.mapImage.displayWidth}x${this.mapImage.displayHeight}, Position: (${this.mapImage.x}, ${this.mapImage.y})`);

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
              // FIRST TIME COMPLETE: Play the video
              const stampVideo = this.add.video(thumb.x, thumb.y, 'level-complete');
              stampVideo.setOrigin(0.5, 0.5);
              stampVideo.setDepth(2);
              stampVideo.disableInteractive();
              stampVideo.setBlendMode(Phaser.BlendModes.MULTIPLY);
              const updateStampSize = () => {
                  // Offset the video slightly up so it visually matches the stamp image
                  stampVideo.setPosition(thumb.x, thumb.y - 40 * thumb.scaleY);

                  // Scale the stamp so its height covers the thumbnail's height + 25%, maintaining its intrinsic aspect ratio
                  // We must wait for the video metadata to load to get its intrinsic height,
                  // but we can set a fallback or set scale immediately based on a standard 1080p/720p assumption if needed.
                  // Wait, Phaser Video objects have a default size of 256x256 before load.
                  // To be safe, we can apply the scale based on the thumbnail's physical displayHeight.
                  // Since video height might be 0 initially, we use a fallback of 720 (standard height).
                  const intrinsicHeight = stampVideo.height || 720;
                  const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                  const calculatedScale = targetHeight / intrinsicHeight;
                  stampVideo.setScale(calculatedScale);
              };
              updateStampSize();

              if (!this.stamps) this.stamps = [];
              this.stamps.push({ video: stampVideo, thumb: thumb });

              const sfxVol = this.registry.get('sfxVolume') !== undefined ? this.registry.get('sfxVolume') : 0.5;
              stampVideo.setVolume(sfxVol);
              stampVideo.play();

              stampedSections.push(section.name);
              this.registry.set('stampedSections', stampedSections);

              // Swap to image when video finishes to free memory
              stampVideo.on('complete', () => {
                  const stampImg = this.add.image(thumb.x, thumb.y, 'level-complete-stamp');
                  stampImg.setDepth(2);

                  // Apply the identical scale multiplier that the thumbnail is using
                  // Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const intrinsicHeight = stampImg.height || 720;
                  const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                  stampImg.setScale(targetHeight / intrinsicHeight);
                  stampImg.disableInteractive();
                  // Replace in resize array so window resizing still works
                  const idx = this.stamps.findIndex(s => s.video === stampVideo);
                  if (idx !== -1) {
                      this.stamps[idx] = { video: stampImg, thumb: thumb };
                  }
                  stampVideo.destroy();
              });

          } else {
              // ALREADY COMPLETED: Show static image directly
              const stampImg = this.add.image(thumb.x, thumb.y, 'level-complete-stamp');
              stampImg.setOrigin(0.5, 0.5);
              stampImg.setDepth(2);
              stampImg.disableInteractive();
                  const updateStampSize = () => {
                  stampImg.setPosition(thumb.x, thumb.y);

                  // Scale the stamp so its height covers the thumbnail's height + 25%, maintaining its intrinsic aspect ratio
                  const intrinsicHeight = stampImg.height || 720;
                  const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                  const calculatedScale = targetHeight / intrinsicHeight;
                  stampImg.setScale(calculatedScale);
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
    const foundEggs = this.registry.get('foundEggs');
    const eggDataArray = this.registry.get('eggData');
    const eggData = eggDataArray.find(e => e.eggId === egg.getData('eggId'));
    const eggInfo = {
      eggId: egg.getData('eggId'),
      symbolData: egg.getData('symbolDetails'),
      categorized: false
    };
    // console.log('SectionHunt: Collecting egg with symbolData:', eggInfo.symbolData);
    if (!foundEggs.some(e => e.eggId === eggInfo.eggId)) {
      this.sound.play('collect');

      // Get symbol texture if available
      let symbolTexture = null;
      if (egg.symbolSprite && egg.symbolSprite.active) {
          symbolTexture = egg.symbolSprite.texture.key;
      }

      this.showCollectionFeedback(egg.x, egg.y, egg.texture.key, symbolTexture);
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
        localStorage.setItem('highScore', currentScore);
      }
      // console.log(`SectionHunt: Collected egg-${eggInfo.eggId} with symbol:`, eggInfo.symbolData ? eggInfo.symbolData.name : 'none', `Score: ${currentScore}`);
      const foundEggsCount = foundEggs.length;
      if (this.scoreText) {
        this.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
      }

      this.checkLevelComplete();
    } else {
      // console.log(`SectionHunt: Egg-${eggInfo.eggId} already collected, skipping`);
    }
  }

  checkLevelComplete(immediate = false) {
      const foundEggs = this.registry.get('foundEggs');
      const sections = this.registry.get('sections');
      const currentSection = sections.find(s => s.name === this.sectionName);
      const scale = this.gameScale;

      if (foundEggs.length === TOTAL_EGGS) {
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

    // Egg Sprite
    const eggSprite = this.add.image(x, y, eggTexture).setDepth(20).setDisplaySize(50 * scale, 75 * scale);
    this.tweens.add({
        targets: eggSprite,
        y: y - (60 * scale),
        alpha: 0,
        duration: 1000,
        ease: 'Power1',
        onComplete: () => eggSprite.destroy()
    });

    // Symbol Sprite
    if (symbolTexture) {
        const symSprite = this.add.image(x, y, symbolTexture).setDepth(21).setDisplaySize(50 * scale, 75 * scale);
        this.tweens.add({
            targets: symSprite,
            y: y - (60 * scale),
            alpha: 0,
            duration: 1000,
            ease: 'Power1',
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
        y: y - (100 * scale),
        alpha: 0,
        duration: 1000,
        ease: 'Power1',
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

        this.sectionImage.setMute(false);
        const ambientVol = this.registry.has('ambientVolume') ? this.registry.get('ambientVolume') : 0.5;
        this.sectionImage.setVolume(ambientVol * 0.25);
        this.sectionImage.play(true);
        this.isUsingVideo = true;

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
    // console.log(`SectionHunt: Creating ${sectionEggs.length} uncollected eggs for ${this.sectionName}`);

    sectionEggs.forEach(eggData => {
      const egg = this.add.image(eggData.x, eggData.y, `egg-${eggData.eggId}`)
        .setInteractive()
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
          // console.log(`SectionHunt: Added symbol '${eggData.symbol.name}' (${textureKey}) to egg-${eggData.eggId}`);
        } else {
          console.warn(`SectionHunt: Texture '${textureKey}' not found for symbol '${eggData.symbol.name}'`);
          egg.symbolSprite = null;
        }
      } else {
        // console.log(`SectionHunt: No symbol for egg-${eggData.eggId}`);
        egg.symbolSprite = null;
      }
      egg.on('pointerdown', () => {
        // console.log(`SectionHunt: Click on egg-${eggData.eggId} at (${egg.x}, ${egg.y})`);
        const pointer = this.input.activePointer;
        if (egg.getBounds().contains(pointer.worldX, pointer.worldY)) {
          // console.log(`SectionHunt: Bounds check PASSED for egg-${eggData.eggId}`);
          // ⚡ Bolt Optimization: Use squared distance to avoid expensive Math.sqrt calls during pointerdown events
          const distSq = Phaser.Math.Distance.Squared(pointer.worldX, pointer.worldY, egg.x, egg.y);
          const threshold = 150 * scale;
          if (distSq < threshold * threshold) {
            // console.log(`SectionHunt: Distance check PASSED for egg-${eggData.eggId}, collecting!`);
            this.collectEgg(egg);
            egg.destroy();
            if (egg.symbolSprite) {
              egg.symbolSprite.destroy();
            }
          } else {
            // console.log(`SectionHunt: Distance check FAILED for egg-${eggData.eggId}. Dist: ${distance}`);
          }
        } else {
          // console.log(`SectionHunt: Bounds check FAILED for egg-${eggData.eggId}`);
        }
      });
      this.eggs.add(egg);
    });

    this.eggZitButton = this.add.image(0, 200 * scale, 'egg-zit-button')
      .setOrigin(0, 0)
      .setDisplaySize(150 * scale, 150 * scale)
      .setInteractive()
      .on('pointerdown', () => {
        // console.log('Click on eggZitButton');
        this.scene.start('MapScene');
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
        // console.log('Click on eggsAmminHaul');
        this.time.delayedCall(100, () => {
             this.scene.start('EggZamRoom');
        });
    });

    this.sound.play('drive2', { volume: 0.5 });
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
    this.lastFoundCount = foundEggs; // Bolt Optimization

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
        .setDepth(8)
        .setScrollFactor(0)
        .setVisible(false);

    // Check level complete immediately if returning to a completed map
    this.checkLevelComplete(true);

    // Global capture handler
    this.input.on('pointerdown', (pointer) => {
      // Calculate lens position based on pointer
      const scale = this.gameScale;

      // New offsets for reverted size (150x187.5 display size, 0.75x of doubled)
      // Visual lens center is approx (-97.5 * scale, -135 * scale) relative to handle tip
      const lensOffsetX = -97.5 * scale;
      const lensOffsetY = -135 * scale;

      const lensX = pointer.x + lensOffsetX;
      const lensY = pointer.y + lensOffsetY;
      const captureRadius = 80 * scale; // Slightly larger than visual radius (75)
      const captureRadiusSq = captureRadius * captureRadius;

      // Check all eggs
      this.eggs.getChildren().forEach(egg => {
        if (egg.active && !egg.getData('collected')) { // collected check might be redundant if we destroy, but safe
           // Bolt Optimization: Squared distance check using LENS position
           // Tapping the screen harvests the egg under the visual lens window.
           const distSq = Phaser.Math.Distance.Squared(lensX, lensY, egg.x, egg.y);

           // Increased capture radius logic for easier finding
           if (distSq < captureRadiusSq) {
               this.collectEgg(egg);
               egg.destroy();
               if (egg.symbolSprite) egg.symbolSprite.destroy();
           }
        }
      });
    });
  }

  update() {
    const pointer = this.input.activePointer;
    const scale = this.gameScale;

    // Magnifying glass display size is 150*scale x 187.5*scale.
    // We shift it "Up and Left" relative to handle tip.

    const lensOffsetX = -97.5 * scale;
    const lensOffsetY = -135 * scale;

    const lensX = pointer.x + lensOffsetX;
    const lensY = pointer.y + lensOffsetY;

    // Ensure video size is correct once texture loads
    if (this.sectionImage && this.sectionImage.active && this.sectionImage.width > 0) {
        if (Math.abs(this.sectionImage.displayWidth - this.game.config.width) > 10) {
             this.sectionImage.setDisplaySize(this.game.config.width, this.game.config.height);
        }
    }

    // Update Zoomed View Position (centered on lens)
    this.zoomedView.setPosition(lensX, lensY);
    this.maskGraphics.setPosition(lensX, lensY);

    const magnifierRadius = 75 * scale;
    const zoom = 2;
    const diameter = 150 * scale;
    const viewWidth = diameter / zoom;
    const viewHeight = diameter / zoom;

    // Crucial Change: The zoomed view should show what is visually under the LENS (lensX, lensY),
    // not directly under the finger (pointer).
    const scrollX = lensX - viewWidth / 2;
    const scrollY = lensY - viewHeight / 2;

    this.zoomedView.clear();

    // Draw background using renderStamp to avoid dirtying scene object
    if (this.sectionImage && this.sectionImage.active) {
         this.renderStamp.texture = this.sectionImage.texture;
         this.renderStamp.frame = this.sectionImage.frame;
    } else {
         this.renderStamp.setTexture(this.sectionName);
    }

    // Set explicit size before scaling
    this.renderStamp.setDisplaySize(this.game.config.width, this.game.config.height);

    // Scale by 2 for zoom
    this.renderStamp.setScale(this.renderStamp.scaleX * zoom, this.renderStamp.scaleY * zoom);

    // We already scaled the stamp by zoom. So we only offset by scrollX*zoom.
    this.renderStamp.setPosition(-scrollX * zoom, -scrollY * zoom);
    this.renderStamp.setOrigin(0, 0);

    this.zoomedView.draw(this.renderStamp, this.renderStamp.x, this.renderStamp.y);

    // Single pass for visibility update and drawing
    this.eggs.getChildren().forEach(egg => {
      if (egg && egg.active) {
          // Update visibility based on LENS visual position
          // If the egg is under the lens (visual), it should be visible in the zoomed view.

          // Bolt Optimization: Use squared distance to avoid sqrt calculation in loop
          const distToLensSq = Phaser.Math.Distance.Squared(lensX, lensY, egg.x, egg.y);
          const magnifierRadiusSq = magnifierRadius * magnifierRadius;

          const alpha = distToLensSq < magnifierRadiusSq ? 1 : 0;
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
             this.zoomedView.draw(this.renderStamp, (egg.x - scrollX) * zoom, (egg.y - scrollY) * zoom);

             // Draw Symbol using renderStamp
             if (egg.symbolSprite && egg.symbolSprite.active && egg.symbolSprite.visible) {
                 this.renderStamp.setTexture(egg.symbolSprite.texture.key, egg.symbolSprite.frame.name);
                 this.renderStamp.setAngle(egg.symbolSprite.angle);
                 this.renderStamp.setFlipX(egg.symbolSprite.flipX);
                 this.renderStamp.setFlipY(egg.symbolSprite.flipY);
                 this.renderStamp.setScale(egg.symbolSprite.scaleX * zoom, egg.symbolSprite.scaleY * zoom);
                 this.zoomedView.draw(this.renderStamp, (egg.symbolSprite.x - scrollX) * zoom, (egg.symbolSprite.y - scrollY) * zoom);
             }
          }
      }
    });

    // Handle Button Hover and Cursor Swap
    const buttons = [this.eggZitButton, this.eggsAmminHaul];
    let isHoveringButton = false;

    buttons.forEach(btn => {
        if (btn && btn.active) {
             // Store base scale if not already stored
             if (btn.baseScaleX === undefined) btn.baseScaleX = btn.scaleX;
             if (btn.baseScaleY === undefined) btn.baseScaleY = btn.scaleY;

             const bounds = btn.getBounds();
             if (bounds.contains(pointer.x, pointer.y)) {
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
    });

    if (isHoveringButton) {
        if (this.magnifyingGlass) this.magnifyingGlass.setVisible(false);
        if (this.zoomedView) this.zoomedView.setVisible(false);
        if (this.maskGraphics) this.maskGraphics.setVisible(false);

        if (this.fingerCursor) {
            this.fingerCursor.setVisible(true);
            this.fingerCursor.setDisplaySize(50 * scale, 75 * scale);
            this.fingerCursor.setPosition(pointer.x, pointer.y);
        }
    } else {
        if (this.magnifyingGlass) {
             this.magnifyingGlass.setVisible(true);
             this.magnifyingGlass.setDisplaySize(150 * scale, 187.5 * scale);
             this.magnifyingGlass.setPosition(pointer.x, pointer.y);
        }
        if (this.zoomedView) this.zoomedView.setVisible(true);
        if (this.maskGraphics) this.maskGraphics.setVisible(true);
        if (this.fingerCursor) this.fingerCursor.setVisible(false);
    }

    const foundEggsCount = this.registry.get('foundEggs').length;
    if (this.lastFoundCount !== foundEggsCount) {
        this.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
        this.lastFoundCount = foundEggsCount;
    }
  }
}

class EggZamRoom extends Phaser.Scene {
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
  }

  preload() {
    // Assets are preloaded in MainMenu
    this.load.on('loaderror', (file) => {
      console.error(`EggZamRoom: Load error: Key='${file.key}', URL='${file.url}'`);
    });

    this.load.on('filecomplete', (key, type, data) => {
      // console.log(`EggZamRoom: Successfully loaded asset: Key='${key}', Type='${type}'`);
    });
  }

  create() {
    this.input.setDefaultCursor('none');
    const width = this.game.config.width;
    const height = this.game.config.height;
    const scaleX = width / 1280;
    const scaleY = height / 720;
    this.gameScale = Math.min(scaleX, scaleY);

    this.cameras.main.setBounds(0, 0, width, height);
    this.cameras.main.setViewport(0, 0, width, height);
    this.cameras.main.setPosition(0, 0);

    this.background = this.add.image(0, 0, 'egg-zam-room')
      .setOrigin(0, 0)
      .setDepth(0)
      .setDisplaySize(width, height);

    const isDesktop = this.sys.game.device.os.desktop;
    const assetScale = isDesktop ? this.gameScale : this.gameScale * 1.75;

    const tanBoxCenterX = (640 / 1280) * width;
    const examinerWidth = 400 * assetScale;
    const examinerHeight = 500 * assetScale;
    const examinerX = tanBoxCenterX - (examinerWidth / 2);
    const floorY = isDesktop ? ((740 / 720) * height) : height + (100 * assetScale); // push further down on mobile
    const examinerY = floorY - examinerHeight;

    this.examiner = this.add.image(examinerX, examinerY, 'egg-zamminer')
      .setOrigin(0, 0)
      .setDepth(2)
      .setDisplaySize(examinerWidth, examinerHeight);

    const diagX = 0.55 * width;
    const diagY = 0.05 * height;
    this.symbolResultDiag = this.add.image(diagX, diagY, 'symbol-result-summary-diag')
      .setOrigin(0, 0)
      .setDepth(1)
      .setDisplaySize(900 * this.gameScale, 600 * this.gameScale)
      .setAlpha(0);

    this.eggZitButton = this.add.image(0, 200 * this.gameScale, 'egg-zit-button')
      .setOrigin(0, 0)
      .setDisplaySize(150 * this.gameScale, 131 * this.gameScale)
      .setInteractive()
      .on('pointerdown', () => this.scene.start('MapScene'))
      .setDepth(4)
      .setScrollFactor(0);
    addButtonInteraction(this, this.eggZitButton, 'drive1');

    this.scoreImage = this.add.image(0, 0, 'score')
      .setOrigin(0, 0)
      .setDisplaySize(200 * this.gameScale, 200 * this.gameScale)
      .setDepth(4)
      .setScrollFactor(0);
    const foundEggsCount = this.registry.get('foundEggs').length;
    const scoreY = isDesktop ? 125 * this.gameScale : 117 * this.gameScale;
    const correctY = isDesktop ? 150 * this.gameScale : 146 * this.gameScale;
    // Scale text up slightly more on mobile for readability
    const scoreFontSize = isDesktop ? 32 : 54;
    const correctFontSize = isDesktop ? 24 : 42;
    this.scoreText = this.add.text(100 * this.gameScale, scoreY, `${foundEggsCount}/${TOTAL_EGGS}`, {
      fontSize: `${scoreFontSize * this.gameScale}px`,
      fill: '#000',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#fff',
      strokeThickness: (isDesktop ? 6 : 8) * this.gameScale
    }).setOrigin(0.5).setDepth(5);
    this.lastFoundCount = foundEggsCount; // Bolt Optimization

    if (!this.registry.has('correctCategorizations')) {
      this.registry.set('correctCategorizations', 0);
    }
    this.correctText = this.add.text(100 * this.gameScale, correctY, `Correct: ${this.registry.get('correctCategorizations')}`, {
      fontSize: `${correctFontSize * this.gameScale}px`,
      fill: '#000',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#fff',
      strokeThickness: (isDesktop ? 6 : 8) * this.gameScale
    }).setOrigin(0.5).setDepth(5);

    const zoneWidth = 200 * assetScale;
    const zoneHeight = 400 * assetScale;
    const zoneY = examinerY + 100 * assetScale;

    this.leftBottleZone = this.add.zone(examinerX, zoneY, zoneWidth, zoneHeight)
      .setOrigin(0, 0)
      .setInteractive();

    this.rightBottleZone = this.add.zone(examinerX + zoneWidth, zoneY, zoneWidth, zoneHeight)
      .setOrigin(0, 0)
      .setInteractive();

    const showExplanation = (isCorrect, guessText) => {
        if (isCorrect) {
            this.sound.play('success');
            const correctCount = this.registry.get('correctCategorizations') + 1;
            this.registry.set('correctCategorizations', correctCount);
            this.correctText.setText(`Correct: ${correctCount}`);
            let currentScore = this.registry.get('currentScore');
            currentScore += 5;
            this.registry.set('currentScore', currentScore);
            const highScore = this.registry.get('highScore');
            if (currentScore > highScore) {
              this.registry.set('highScore', currentScore);
              localStorage.setItem('highScore', currentScore);
            }
            this.currentEgg.categorized = true;
        } else {
            this.sound.play('error');
        }

        if (this.explanationText) this.explanationText.destroy();
        const data = this.currentEgg.symbolData;
        const eggId = this.currentEgg.eggId;
        const scale = this.gameScale;
        const isDesktop = this.sys.game.device.os.desktop;
        const assetScale = isDesktop ? scale : scale * 1.5;

        this.explanationText = this.add.container(width / 2, height / 2).setDepth(100);

        const bgWidth = Math.min(width * 0.95, 800 * assetScale);
        const bgHeight = Math.min(height * 0.95, 600 * assetScale);

        const bg = this.add.graphics();
        bg.fillStyle(0xfff8dc, 0.95);
        bg.fillRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * assetScale);
        bg.lineStyle(8 * assetScale, 0x8b4513, 1);
        bg.strokeRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * assetScale);
        bg.setInteractive(new Phaser.Geom.Rectangle(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight), Phaser.Geom.Rectangle.Contains);

        // Header Elements
        const title = this.add.text(0, -bgHeight/2 + 60 * assetScale, data.name || "Symbol", {
            fontSize: `${48 * assetScale}px`, fill: '#8b4513', fontStyle: 'bold', fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5);

        const eggImg = this.add.image(-bgWidth/2 + 90 * assetScale, -bgHeight/2 + 90 * assetScale, `egg-${eggId}`).setDisplaySize(100 * assetScale, 125 * assetScale);
        const symbolImgSmall = this.add.image(-bgWidth/2 + 90 * assetScale, -bgHeight/2 + 90 * assetScale, data.filename).setDisplaySize(100 * assetScale, 125 * assetScale);

        const guessDisplay = this.add.text(bgWidth/2 - 40 * assetScale, -bgHeight/2 + 60 * assetScale, `Your Guess:\n${guessText}`, {
            fontSize: `${32 * assetScale}px`, fill: '#333', fontStyle: 'bold', fontFamily: 'Comic Sans MS', align: 'center'
        }).setOrigin(0.5, 0.5);

        // Result Text
        const resultText = this.add.text(bgWidth/2 - 40 * assetScale, -bgHeight/2 + 130 * assetScale, isCorrect ? "Correct!" : "Incorrect!", {
            fontSize: `${36 * assetScale}px`,
            fill: isCorrect ? '#008000' : '#d32f2f',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#fff',
            strokeThickness: 6 * assetScale
        }).setOrigin(0.5, 0.5);

        const expText = this.add.text(0, 0, data.explanation, {
            fontSize: `${28 * assetScale}px`, fill: '#000', fontFamily: 'Comic Sans MS',
            wordWrap: { width: bgWidth - 40 * assetScale, useAdvancedWrap: true }, align: 'center'
        }).setOrigin(0.5);

        const scriptText = this.add.text(0, bgHeight/2 - 120 * assetScale, data.scripture, {
            fontSize: `${24 * assetScale}px`, fill: '#0000ee', fontStyle: 'italic', fontFamily: 'Comic Sans MS',
            wordWrap: { width: bgWidth - 40 * assetScale, useAdvancedWrap: true }, align: 'center'
        }).setOrigin(0.5).setInteractive(); // Removed hand cursor for mobile, let touch handle it

        scriptText.on('pointerdown', (p, x, y, event) => {
            event.stopPropagation();
            const link = parseScriptureLink(data.scripture);
            if (link) window.open(link, '_blank');
        });

        const continueText = this.add.text(0, bgHeight/2 - 40 * assetScale, "[ Tap anywhere to continue ]", {
            fontSize: `${20 * assetScale}px`, fill: '#8b4513', fontStyle: 'bold', fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5);

        this.explanationText.add([bg, title, eggImg, symbolImgSmall, guessDisplay, resultText, expText, scriptText, continueText]);

        this.explanationText.setScale(0);
        this.tweens.add({ targets: this.explanationText, scaleX: 1, scaleY: 1, duration: 300, ease: 'Back.out' });

        bg.on('pointerdown', () => {
            this.tweens.add({
                targets: this.explanationText, scaleX: 0, scaleY: 0, duration: 200, ease: 'Back.in',
                onComplete: () => {
                    this.explanationText.destroy();
                    this.explanationText = null;
                    if (!isCorrect) {
                        this.currentEgg = null; // Un-set so it can be re-drawn
                    }
                    this.displayRandomEggInfo();
                }
            });
        });
    };

    this.leftBottleZone.on('pointerdown', () => {
      if (this.currentEgg && !this.currentEgg.categorized && !this.explanationText?.active) {
        showExplanation(this.currentEgg.symbolData.category === 'Christian', 'Christian');
      }
    });

    this.rightBottleZone.on('pointerdown', () => {
      if (this.currentEgg && !this.currentEgg.categorized && !this.explanationText?.active) {
        showExplanation(this.currentEgg.symbolData.category === 'Pagan', 'Worldly');
      }
    });

    this.displayRandomEggInfo();

    if (!this.sys.game.device.os.desktop) {
      this.fingerCursor = null;
    } else {
      this.fingerCursor = this.add.image(0, 0, 'finger-cursor')
        .setOrigin(0, 0)
        .setAngle(0)
        .setDisplaySize(50 * this.gameScale, 75 * this.gameScale)
        .setDepth(1000); // Ensure it renders above the popup modal (depth 100)
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
          wordWrap: { width: 480 * this.gameScale, useAdvancedWrap: true }
        }).setOrigin(0, 0).setDepth(10);

        if (foundEggs.length === TOTAL_EGGS) {
          // PLAY AGAIN Button
          const playBtnContainer = this.add.container((0.36 * width) + (125 * this.gameScale), textY + (100 * this.gameScale)).setDepth(100);

          const playBtnWidth = 250 * this.gameScale;
          const playBtnHeight = 60 * this.gameScale;

          const playBtnBg = this.add.graphics();
          playBtnBg.fillStyle(0xffff00, 1);
          playBtnBg.lineStyle(4 * this.gameScale, 0x000000, 1);
          playBtnBg.fillRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 15 * this.gameScale);
          playBtnBg.strokeRoundedRect(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight, 15 * this.gameScale);

          const playBtnText = this.add.text(0, 0, 'PLAY AGAIN', {
              fontSize: `${28 * this.gameScale}px`,
              fill: '#000',
              fontStyle: 'bold',
              fontFamily: 'Comic Sans MS'
          }).setOrigin(0.5, 0.5);

          playBtnContainer.add([playBtnBg, playBtnText]);

          playBtnContainer.setSize(playBtnWidth, playBtnHeight);
          playBtnContainer.setInteractive(new Phaser.Geom.Rectangle(-playBtnWidth/2, -playBtnHeight/2, playBtnWidth, playBtnHeight), Phaser.Geom.Rectangle.Contains);

          const triggerReload = () => {
              window.location.reload();
          };

          playBtnContainer.on('pointerdown', triggerReload);
          if (this.input.keyboard) {
              this.input.keyboard.once('keydown-SPACE', triggerReload);
              this.input.keyboard.once('keydown-ENTER', triggerReload);
          }
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
      const isDesktop = this.sys.game.device.os.desktop;
      const assetScale = isDesktop ? this.gameScale : this.gameScale * 2;

      const windowCenterX = 196 * assetScale;
      const windowBottomY = 190 * assetScale;
      const eggHeight = 125 * assetScale;
      const symbolHeight = 125 * assetScale;

      const eggPosX = this.examiner.x + windowCenterX;
      const eggPosY = this.examiner.y + windowBottomY - (eggHeight / 2);
      const symbolPosX = this.examiner.x + windowCenterX;
      const symbolPosY = this.examiner.y + windowBottomY - (symbolHeight / 2);

      if (this.textures.exists(`egg-${eggId}`)) {
        this.displayedEggImage = this.add.image(eggPosX, eggPosY, `egg-${eggId}`)
          .setOrigin(0.5, 0.5)
          .setDisplaySize(100 * assetScale, 125 * assetScale)
          .setDepth(3);
      }
      if (symbolData && symbolData.filename && this.textures.exists(symbolData.filename)) {
        this.displayedSymbolImage = this.add.image(symbolPosX, symbolPosY, symbolData.filename)
          .setOrigin(0.5, 0.5)
          .setDisplaySize(100 * assetScale, 125 * assetScale)
          .setDepth(3);
      }
    }
  }

  update() {
    const foundEggsCount = this.registry.get('foundEggs').length;
    if (this.scoreText && this.lastFoundCount !== foundEggsCount) {
      this.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
      this.lastFoundCount = foundEggsCount;
    }
    if (this.fingerCursor) {
      this.fingerCursor.setPosition(this.input.x, this.input.y);
    }
  }
}

function getViewportDimensions() {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  let width, height;
  if (isMobile) {
    width = screen.width;
    height = screen.height;
    if (width < height) {
      [width, height] = [height, width];
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
  width: width,
  height: height,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    parent: 'game-container',
  },
  scene: [MainMenu, MapScene, SectionHunt, EggZamRoom, MusicScene, UIScene],
  backgroundColor: '#000000',
};

const game = new Phaser.Game(config);
window.game = game; // Expose for debugging/verification


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
    const match = scriptureText.match(/^(\d?\s*[A-Za-z\s]+)\s+(\d+):(\d+)/);
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
        scene.sound.play(soundKey, { volume: 0.5 });
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

  game.scene.getScenes(true).forEach(scene => {
    if (scene.gameScale) scene.gameScale = scale;
    if (scene.cameras && scene.cameras.main) {
      scene.cameras.main.setBounds(0, 0, width, height);
      scene.cameras.main.setViewport(0, 0, width, height);
      scene.cameras.main.setPosition(0, 0);
    }
    if (scene.scene.key === 'MainMenu') {
      if (scene.introVideo) {
        scene.introVideo.setPosition(width / 2, height / 2);
        scene.introVideo.setDisplaySize(width, height);
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
        scene.mapSections.forEach(section => {
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
        });

        if (scene.stamps) {
            scene.stamps.forEach(item => {
                if (item.video && item.video.active && item.thumb && item.thumb.active) {
                    // Only apply the 40px upward offset to the stampVideo (Phaser.Video), not the final stampImg
                    const isVideo = item.video.type === 'Video';
                    const offsetY = isVideo ? -40 * item.thumb.scaleY : 0;
                    item.video.setPosition(item.thumb.x, item.thumb.y + offsetY);

                    // Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const intrinsicHeight = item.video.height || 720;
                  const targetHeight = (item.thumb.height * item.thumb.scaleY) * 1.25;
                  item.video.setScale(targetHeight / intrinsicHeight);
                }
            });
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
        scene.eggs.getChildren().forEach(egg => {
          if (egg && egg.active) {
            egg.setDisplaySize(50 * scale, 75 * scale);
            if (egg.symbolSprite) {
              egg.symbolSprite.setDisplaySize(50 * scale, 75 * scale);
            }
          }
        });
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
      const isDesktop = scene.sys.game.device.os.desktop;
      const assetScale = isDesktop ? scale : scale * 1.75;

      if (scene.background) scene.background.setDisplaySize(width, height);
      if (scene.examiner) {
        const tanBoxCenterX = (640 / 1280) * width;
        const examinerWidth = 400 * assetScale;
        const examinerHeight = 500 * assetScale;
        const examinerX = tanBoxCenterX - (examinerWidth / 2);
        const floorY = isDesktop ? ((740 / 720) * height) : height + (100 * assetScale);
        const examinerY = floorY - examinerHeight;
        scene.examiner.setPosition(examinerX, examinerY);
        scene.examiner.setDisplaySize(examinerWidth, examinerHeight);
      }
      if (scene.symbolResultDiag) {
        scene.symbolResultDiag.setPosition(0.55 * width, 0.05 * height);
        scene.symbolResultDiag.setDisplaySize(900 * scale, 600 * scale);
      }
      if (scene.eggZitButton) {
        scene.eggZitButton.setPosition(0, 200 * scale);
        scene.eggZitButton.setDisplaySize(150 * scale, 131 * scale);
      }
      if (scene.scoreImage) {
        scene.scoreImage.setDisplaySize(200 * scale, 200 * scale);
      }
      if (scene.scoreText) {
        const foundEggsCount = scene.registry.get('foundEggs').length;
        scene.scoreText.setText(`${foundEggsCount}/${TOTAL_EGGS}`);
        const scoreY = isDesktop ? 125 * scale : 117 * scale;
        scene.scoreText.setPosition(100 * scale, scoreY);
        scene.scoreText.setStyle({ fontSize: `${(isDesktop ? 32 : 54) * scale}px`, strokeThickness: (isDesktop ? 6 : 8) * scale });
      }
      if (scene.correctText) {
        const correctY = isDesktop ? 150 * scale : 146 * scale;
        scene.correctText.setPosition(100 * scale, correctY);
        scene.correctText.setStyle({ fontSize: `${(isDesktop ? 24 : 42) * scale}px`, strokeThickness: (isDesktop ? 6 : 8) * scale });
      }
      if (scene.leftBottleZone) {
        const examinerX = (640 / 1280) * width - (400 * assetScale / 2);
        const floorY = isDesktop ? ((740 / 720) * height) : height + (50 * assetScale);
        const examinerY = floorY - (500 * assetScale);
        scene.leftBottleZone.setPosition(examinerX, examinerY + (100 * assetScale));
        scene.leftBottleZone.setSize(200 * assetScale, 400 * assetScale);
      }
      if (scene.rightBottleZone) {
        const examinerX = (640 / 1280) * width - (400 * assetScale / 2);
        const floorY = isDesktop ? ((740 / 720) * height) : height + (50 * assetScale);
        const examinerY = floorY - (500 * assetScale);
        scene.rightBottleZone.setPosition(examinerX + (200 * assetScale), examinerY + (100 * assetScale));
        scene.rightBottleZone.setSize(200 * assetScale, 400 * assetScale);
      }
      if (scene.displayedEggImage) {
        const windowCenterX = 196 * assetScale;
        const windowBottomY = 190 * assetScale;
        const eggHeight = 125 * assetScale;
        scene.displayedEggImage.setPosition(scene.examiner.x + windowCenterX, scene.examiner.y + windowBottomY - (eggHeight / 2));
        scene.displayedEggImage.setDisplaySize(100 * assetScale, 125 * assetScale);
      }
      if (scene.displayedSymbolImage) {
        const windowCenterX = 196 * assetScale;
        const windowBottomY = 190 * assetScale;
        const symbolHeight = 125 * assetScale;
        scene.displayedSymbolImage.setPosition(scene.examiner.x + windowCenterX, scene.examiner.y + windowBottomY - (symbolHeight / 2));
        scene.displayedSymbolImage.setDisplaySize(100 * assetScale, 125 * assetScale);
      }
      if (scene.noEggsText) {
        const isDesktop = scene.sys.game.device.os.desktop;
        const textY = isDesktop ? 0.25 * height : 0.15 * height;
        scene.noEggsText.setPosition(0.36 * width, textY);
        scene.noEggsText.setStyle({ fontSize: `${(isDesktop ? 28 : 40) * scale}px`, strokeThickness: 3 * scale, wordWrap: { width: 480 * scale, useAdvancedWrap: true } });
      }
      if (scene.fingerCursor) scene.fingerCursor.setDisplaySize(50 * scale, 75 * scale);
    }
  });
}

game.events.on('ready', () => {
  resizeGame();
  window.addEventListener('resize', resizeGame);
  window.addEventListener('orientationchange', resizeGame);
});

// Auto-focus the game container for screen readers and keyboard accessibility
window.addEventListener('load', () => {
  const gameContainer = document.getElementById('game-container');
  if (gameContainer) gameContainer.focus();
});
