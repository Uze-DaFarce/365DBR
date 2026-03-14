// Define all scene classes first
const TOTAL_EGGS = 60;

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
        .setDepth(10000); // Always on top
  }

  update() {
    const pointer = this.input.activePointer;
    if (this.fingerCursor) {
        this.fingerCursor.setPosition(pointer.x, pointer.y);
        // Ensure size is maintained (scale with window?)
        // Simple fixed size or ratio
        const scale = Math.min(this.scale.width / 1280, this.scale.height / 720);
        this.fingerCursor.setDisplaySize(50 * scale, 75 * scale);

        // Hide system cursor explicitly here just in case
        this.input.setDefaultCursor('none');
    }
  }
}

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
    // Simply play the sound. If not in cache, Phaser will warn internally,
    // but usually 'add' isn't needed for one-shot SFX if loaded.
    // If it's not added yet, we can try adding it, but play() usually handles it if the key exists.
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
        if (this.settingsContainer.visible) {
            this.settingsContainer.setVisible(false);
            this.gearIcon.setVisible(true);
            this.gearIcon.setScale(1);
            this.input.setDefaultCursor('none');
        } else {
            this.openSettings();
        }
    };
    const closeSettings = () => {
        if (this.settingsContainer.visible) {
            this.settingsContainer.setVisible(false);
            this.gearIcon.setVisible(true);
            this.gearIcon.setScale(1);
            this.input.setDefaultCursor('none');
        }
    };
    this.input.keyboard.on('keydown-ESC', toggleSettings);
    this.input.keyboard.on('keydown-ENTER', closeSettings);

    this.scale.on('resize', this.resize, this);
  }

  resize(gameSize) {
      const width = gameSize.width;
      const height = gameSize.height;

      if (this.gearIcon) {
          this.gearIcon.x = width - 30;
          this.gearIcon.y = 30;
      }

      if (this.settingsContainer) {
          // Re-center settings panel
          this.settingsContainer.getAll().forEach(child => {
              // Update overlay
              if (child.width === this.cameras.main.width && child.height === this.cameras.main.height) {
                  child.setSize(width, height);
              }
          });
      }
  }

  createGearIcon() {
    const x = this.cameras.main.width - 30;
    const y = 30;

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
    gearContainer.setInteractive(new Phaser.Geom.Circle(0, 0, 20), Phaser.Geom.Circle.Contains);
    gearContainer.input.cursor = 'pointer';

    gearContainer.baseScaleX = gearContainer.scaleX;
    gearContainer.baseScaleY = gearContainer.scaleY;

    gearContainer.on('pointerover', () => this.tweens.add({
        targets: gearContainer, scaleX: gearContainer.baseScaleX * 1.2, scaleY: gearContainer.baseScaleY * 1.2, duration: 100, ease: 'Sine.easeInOut'
    }));

    gearContainer.on('pointerout', () => this.tweens.add({
        targets: gearContainer, scaleX: gearContainer.baseScaleX, scaleY: gearContainer.baseScaleY, duration: 100, ease: 'Sine.easeInOut'
    }));

    gearContainer.on('pointerdown', () => {
        const musicScene = this.scene.get('MusicScene');
        if (musicScene && musicScene.scene.isActive()) {
            musicScene.playSFX('menu-click');
        }

        this.tweens.add({
            targets: gearContainer,
            scaleX: gearContainer.baseScaleX * 0.9,
            scaleY: gearContainer.baseScaleY * 0.9,
            duration: 50,
            ease: 'Power1',
            onComplete: () => {
                this.time.delayedCall(50, () => {
                    this.openSettings();
                    gearContainer.setScale(gearContainer.baseScaleX, gearContainer.baseScaleY); // Reset scale for next time
                });
            }
        });
    });

    addTooltip(this, gearContainer, 'Settings (Esc)');

    this.gearIcon = gearContainer;
  }

  createSettingsPanel() {
    const width = 500;
    const height = 500;
    const x = (this.cameras.main.width - width) / 2;
    const y = (this.cameras.main.height - height) / 2;

    this.settingsContainer = this.add.container(0, 0).setVisible(false).setDepth(100);

    // Overlay
    const overlay = this.add.rectangle(0, 0, this.cameras.main.width, this.cameras.main.height, 0x000000, 0.7)
        .setOrigin(0)
        .setInteractive(); // Block clicks

    this.settingsContainer.add(overlay);

    // Panel
    const panel = this.add.rectangle(this.cameras.main.width / 2, this.cameras.main.height / 2, width, height, 0x333333)
        .setStrokeStyle(4, 0xffffff);
    this.settingsContainer.add(panel);

    // Title
    const title = this.add.text(this.cameras.main.width / 2, y + 50, 'Audio Settings', {
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
    closeBtn.setInteractive(new Phaser.Geom.Circle(0, 0, closeSize / 2), Phaser.Geom.Circle.Contains);

    // Hover effects
    closeBtn.on('pointerover', () => {
        this.input.setDefaultCursor('pointer');
        this.tweens.add({
            targets: closeBtn,
            scaleX: 1.1,
            scaleY: 1.1,
            duration: 100,
            ease: 'Sine.easeInOut'
        });
    });

    closeBtn.on('pointerout', () => {
        this.input.setDefaultCursor('default');
        this.tweens.add({
            targets: closeBtn,
            scaleX: 1.0,
            scaleY: 1.0,
            duration: 100,
            ease: 'Sine.easeInOut'
        });
    });

    closeBtn.on('pointerdown', () => {
        this.settingsContainer.setVisible(false);
        this.gearIcon.setVisible(true);
        this.gearIcon.setScale(1);
        this.input.setDefaultCursor('none');
    });
    this.settingsContainer.add(closeBtn);

    // Sliders
    this.createSlider('Music', y + 150, 'music');
    this.createSlider('Ambient', y + 250, 'ambient');
    this.createSlider('SFX', y + 350, 'sfx');
  }

  createSlider(label, y, type) {
    const centerX = this.cameras.main.width / 2;
    const startX = centerX - 100;
    const endX = centerX + 100;

    const text = this.add.text(centerX, y - 30, label, {
        fontSize: '24px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffffff'
    }).setOrigin(0.5);
    this.settingsContainer.add(text);

    // Invisible hit area for easier clicking on track (increased height to 60)
    const trackHitArea = this.add.rectangle(centerX, y + 10, 200, 60, 0x888888, 0).setInteractive({ cursor: 'pointer' });
    this.settingsContainer.add(trackHitArea);
    this.settingsContainer.add(this.add.rectangle(centerX, y + 10, 200, 4, 0x888888));

    // Handle
    let currentVol = 0.5;
    if (this.registry.has(`${type}Volume`)) currentVol = this.registry.get(`${type}Volume`);

    // Wrap handle in a container to enlarge hit area (30 radius) like mobile
    const handleContainer = this.add.container(startX + (currentVol * 200), y + 10);
    handleContainer.setSize(60, 60);
    handleContainer.setInteractive(new Phaser.Geom.Circle(0, 0, 30), Phaser.Geom.Circle.Contains);
    this.input.setDraggable(handleContainer);

    const visualHandle = this.add.circle(0, 0, 12, 0xffffff);
    handleContainer.add(visualHandle);

    this.settingsContainer.add(handleContainer);

    const updateVolume = (x) => {
        const clampedX = Phaser.Math.Clamp(x, startX, endX);
        handleContainer.x = clampedX;
        this.registry.set(`${type}Volume`, (clampedX - startX) / 200);
    };

    handleContainer.on('drag', (p, x) => updateVolume(x));
    trackHitArea.on('pointerdown', (p) => updateVolume(p.worldX));

    handleContainer.on('pointerover', () => { handleContainer.setScale(1.3); this.input.setDefaultCursor('pointer'); });
    handleContainer.on('pointerout', () => { handleContainer.setScale(1); this.input.setDefaultCursor('default'); });
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
    this.load.video('level-complete', 'assets/video/level-complete.mp4');
    this.load.image('level-complete-stamp', 'assets/objects/level-complete-stamp.png');
    this.load.image('finger-cursor', 'assets/cursor/pointer-finger-pointer.png');

    // Preload common UI and game assets here to avoid reloading in scenes
    this.load.image('new-map', 'assets/map/new-map.png');
    this.load.image('cog', 'assets/objects/cog.png');
    this.load.image('eggs-ammin-haul', 'assets/objects/eggs-ammin-haul.png');
    this.load.image('score', 'assets/objects/score.png');
    this.load.image('magnifying-glass', 'assets/cursor/magnifying-glass.png');
    this.load.image('egg-zit-button', 'assets/objects/egg-zit-button.png');
    this.load.image('egg-zam-room', 'assets/map/egg-zam-room.png');
    this.load.image('egg-zamminer', 'assets/objects/egg-zamminer.png');
    this.load.image('symbol-result-summary-diag', 'assets/objects/symbol-result-summary-diag.png');

    // Audio assets
    this.load.audio('background-music', 'assets/audio/background-music.mp3');
    this.load.audio('collect', 'assets/audio/collect1.mp3');
    this.load.audio('success', 'assets/audio/success.wav');
    this.load.audio('error', 'assets/audio/error.wav');
    this.load.audio('ambient1', 'assets/audio/ambient1.mp3');
    this.load.audio('menu-click', 'assets/audio/menu-click.mp3');
    this.load.audio('drive1', 'assets/audio/drive1.mp3');
    this.load.audio('drive2', 'assets/audio/drive2.mp3');

    this.load.on('filecomplete-json-map_sections', (key, type, data) => {
      // console.log(`MainMenu: filecomplete-json-map_sections: Key='${key}', Type='${type}'`);
      if (Array.isArray(data)) {
        data.forEach(section => {
             // Enqueue thumbnail (.jpg) explicitly as thumb to avoid fallback errors
             this.load.image(`${section.name}-thumb`, `assets/map/sections/${section.background}`);
             // Keep the fallback key mapping to the same jpg, but thumb is cleaner for map.
             this.load.image(`${section.name}-fallback`, `assets/map/sections/${section.background}`);

             // Preload video backgrounds
             this.load.video(`${section.name}-video`, `assets/video/${section.name}.mp4`);
        });
        // console.log(`MainMenu: Queued ${data.length} section backgrounds and Videos for loading.`);
      }
    });

    this.load.on('filecomplete-json-symbols', (key, type, data) => {
      // console.log(`MainMenu: filecomplete-json-symbols: Key='${key}', Type='${type}'`);
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
    this.input.setDefaultCursor('none');

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

    // "Play Now" Button Container (Initially Hidden)
    const buttonWidth = 400;
    const buttonHeight = 100;
    const btnX = width / 2;
    const btnY = height * 0.8; // Position relative to height

    const startBtnContainer = this.add.container(btnX, btnY).setVisible(false).setDepth(101);
    this.startBtnContainer = startBtnContainer;

    const btnBg = this.add.graphics();
    btnBg.fillStyle(0xff0000, 1);
    btnBg.fillRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, 16);
    btnBg.lineStyle(4, 0xffffff, 1);
    btnBg.strokeRoundedRect(-buttonWidth / 2, -buttonHeight / 2, buttonWidth, buttonHeight, 16);
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
    startBtnContainer.setInteractive(new Phaser.Geom.Rectangle(-buttonWidth, -buttonHeight, buttonWidth * 2, buttonHeight * 2), Phaser.Geom.Rectangle.Contains);

    // Cursor handled by CursorScene

    // Initialize volume registry (Load from localStorage if available)
    const savedMusic = localStorage.getItem('musicVolume');
    const savedAmbient = localStorage.getItem('ambientVolume');
    const savedSfx = localStorage.getItem('sfxVolume');

    if (!this.registry.has('musicVolume')) this.registry.set('musicVolume', savedMusic !== null ? parseFloat(savedMusic) : 0.5);
    if (!this.registry.has('ambientVolume')) this.registry.set('ambientVolume', savedAmbient !== null ? parseFloat(savedAmbient) : 0.5);
    if (!this.registry.has('sfxVolume')) this.registry.set('sfxVolume', savedSfx !== null ? parseFloat(savedSfx) : 0.5);

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
        if (this.scale.fullscreen.available) {
            this.scale.startFullscreen();
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
    const startGame = () => {
        if (introState !== 'ready') return;

        // Prevent multiple calls
        introState = 'starting';

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
                    this.sound.play('drive1', { volume: 0.5 });
                }
                this.scene.start('MapScene');
            }
        });
    };

    startBtnContainer.on('pointerdown', startGame);

    // Explicitly add window listener for robust keyboard support on initial screen
    const globalKeyHandler = (e) => {
        if (e.code === 'Space' || e.code === 'Enter') {
            if (introState === 'waiting') {
                handleGlobalTap();
            } else if (introState === 'ready') {
                startGame();
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

    // Safety: Check video dimensions after a short delay to ensure metadata loaded
    this.time.delayedCall(100, () => {
        if (this.introVideo && this.introVideo.active) {
            // Force resize logic
            this.resize(this.scale);
        }
    });

    const symbolsData = this.cache.json.get('symbols');
    if (symbolsData) {
      if (symbolsData.symbols && Array.isArray(symbolsData.symbols)) {
        const validSymbols = symbolsData.symbols.filter(s => this.isValidSymbol(s));
        this.registry.set('symbols', symbolsData);
      }
    }

    const mapSections = this.cache.json.get('map_sections');
    if (mapSections && !this.registry.has('eggData')) {
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

        this.registry.set('sections', sections);
        this.registry.set('eggData', eggData);
    }

    if (!this.registry.has('foundEggs')) {
      this.registry.set('foundEggs', []);
      this.registry.set('stampedSections', []);
    }
  }

  resize(gameSize) {
      const width = gameSize.width;
      const height = gameSize.height;

      if (this.cameras && this.cameras.main) {
          this.cameras.main.setViewport(0, 0, width, height);
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
    // Fallback scaling check: if video loaded late and width was 0
    if (this.introVideo && this.introVideo.active) {
       // Ensure centered
       if (this.introVideo.x !== this.scale.width / 2 || this.introVideo.y !== this.scale.height / 2) {
           this.introVideo.setPosition(this.scale.width / 2, this.scale.height / 2);
       }

       // Ensure scaled if dimensions valid
       if (this.introVideo.width > 0 && this.introVideo.height > 0) {
           const width = this.scale.width;
           const height = this.scale.height;
           const scaleX = width / this.introVideo.width;
           const scaleY = height / this.introVideo.height;
           const desiredScale = Math.max(scaleX, scaleY);

           // If current scale is default (1) but desired is different, apply it
           // Use a small epsilon to avoid float jitter
           if (Math.abs(this.introVideo.scaleX - desiredScale) > 0.01) {
               console.log(`MainMenu: Applying delayed scale. Video: ${this.introVideo.width}x${this.introVideo.height}, Screen: ${width}x${height}, Scale: ${desiredScale}`);
               this.introVideo.setScale(desiredScale);
           }
       }
    }
  }
}

class MapScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MapScene' });
  }

  create() {
    this.input.setDefaultCursor('none');

    // Scale logic
    const width = this.scale.width;
    const height = this.scale.height;

    // We want to fit the map 1280x720 into the screen while maintaining aspect ratio?
    // Or cover? The user requested "full screen maximized viewport".
    // For the map, "cover" makes sense to fill the screen.

    const mapSections = this.cache.json.get('map_sections');

    if (!this.scene.get('MusicScene').scene.isActive()) {
      this.scene.launch('MusicScene');
    }
    this.sound.play('drive2', { volume: 0.5 });

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
          this.input.setDefaultCursor('pointer');
          this.tweens.add({
              targets: thumb,
              scaleX: thumb.baseScale * 1.1,
              scaleY: thumb.baseScale * 1.1,
              duration: 100,
              ease: 'Sine.easeInOut'
          });
      });

      thumb.on('pointerout', () => {
          this.input.setDefaultCursor('default');
          this.tweens.add({
              targets: thumb,
              scaleX: thumb.baseScale,
              scaleY: thumb.baseScale,
              duration: 100,
              ease: 'Sine.easeInOut'
          });
      });

      thumb.on('pointerdown', () => {
        this.sound.play('drive1', { volume: 0.5 });
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
  }

  resize(gameSize) {
      this.updateLayout(gameSize.width, gameSize.height);
  }

  updateLayout(width, height) {
      if (this.cameras && this.cameras.main) {
          this.cameras.main.setViewport(0, 0, width, height);
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
          this.mapZones.forEach(thumb => {
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
          });
      }

      if (this.stamps) {
          this.stamps.forEach(item => {
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
    const foundEggs = this.registry.get('foundEggs');
    const eggDataArray = this.registry.get('eggData');
    const eggData = {
      eggId: egg.getData('eggId'),
      symbolData: egg.getData('symbolDetails'),
      categorized: false
    };
    const globalEggData = eggDataArray.find(e => e.eggId === eggData.eggId);

    if (!foundEggs.some(e => e.eggId === eggData.eggId)) {
      this.sound.play('collect');

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

      this.updateScore();

      if (this.hintTimer) {
          this.hintTimer.reset({ delay: 90000, callback: this.showIdleHint, callbackScope: this, loop: true });
      }

      this.checkLevelComplete();
    }
  }

  checkLevelComplete(immediate = false) {
      const foundEggs = this.registry.get('foundEggs');
      const sections = this.registry.get('sections');
      const currentSection = sections.find(s => s.name === this.sectionName);

      if (foundEggs.length === TOTAL_EGGS) {
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
    // Show Egg Sprite
    const eggSprite = this.add.image(x, y, eggTexture).setDepth(20).setDisplaySize(50, 75);
    this.tweens.add({
        targets: eggSprite,
        y: y - 60,
        alpha: 0,
        duration: 1000,
        ease: 'Power1',
        onComplete: () => eggSprite.destroy()
    });

    // Show Symbol Sprite if exists
    if (symbolTexture) {
        const symSprite = this.add.image(x, y, symbolTexture).setDepth(21).setDisplaySize(50, 75);
        this.tweens.add({
            targets: symSprite,
            y: y - 60,
            alpha: 0,
            duration: 1000,
            ease: 'Power1',
            onComplete: () => symSprite.destroy()
        });
    }

    const feedback = this.add.text(x, y - 40, 'Found!', {
        fontSize: '32px',
        fontFamily: 'Comic Sans MS',
        fill: '#ffff00',
        stroke: '#000000',
        strokeThickness: 4
    }).setOrigin(0.5).setDepth(22);

    this.tweens.add({
        targets: feedback,
        y: y - 100,
        alpha: 0,
        duration: 1000,
        ease: 'Power1',
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
    this.input.setDefaultCursor('none');

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

    // Check if video exists in cache
    const videoKey = `${this.sectionName}-video`;

    // Validate video existence AND content
    let useVideo = false;
    if (this.cache.video.exists(videoKey)) {
        const videoData = this.cache.video.get(videoKey);
        // If blob URL or standard, we hope it loaded. MainMenu preloads it.
        // If load failed, it might still be in cache but broken?
        // We'll try to add it. If it has 0 duration/width after play attempt, we fallback?
        // Actually, checking if the texture exists might be safer if Phaser generated one.
        useVideo = true;
    }

    if (useVideo) {
        // Use Video Background
        this.sectionVideo = this.add.video(width/2, height/2, videoKey)
            .setDisplaySize(1280 * scale, 720 * scale)
            .setDepth(0);

        this.sectionVideo.play(true); // Loop
        this.sectionVideo.setMute(false); // Enable background video audio
        // Initialize volume from Ambient setting (reduced to 25% due to loud video mixing)
        const ambientVol = this.registry.has('ambientVolume') ? this.registry.get('ambientVolume') : 0.5;
        this.sectionVideo.setVolume(ambientVol * 0.25);
        this.sectionVideo.disableInteractive(); // Should not block clicks

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
             console.warn(`SectionHunt: Video ${videoKey} playback error. Falling back.`);
             this.sectionVideo.destroy();
             this.isUsingVideo = false;
             this.createFallbackImage();
        });
    }

    if (!useVideo) {
        this.createFallbackImage();
    }

    const eggDataArray = this.registry.get('eggData') || [];
    const sectionEggsData = eggDataArray.filter(e => e.section === this.sectionName && !e.collected);

    this.eggs = this.add.group();

    sectionEggsData.forEach(eggData => {
        // Calculate egg position relative to the SCALED background
        const scale = this.bgScale;
        const x = this.bgOffsetX + (eggData.x * scale);
        const y = this.bgOffsetY + (eggData.y * scale);

        const egg = this.add.image(x, y, `egg-${eggData.eggId}`)
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
    this.eggZitButton.on('pointerdown', () => this.scene.start('MapScene'));
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

    this.sound.play('drive2', { volume: 0.5 });

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

    this.lastFoundCount = foundEggs;

    // Fixed size Render Texture for Magnifier (Lens)
    const lensDiameter = 100;
    this.zoomedView = this.add.renderTexture(0, 0, lensDiameter, lensDiameter).setDepth(6).setScrollFactor(0);
    this.zoomedView.setOrigin(0.5, 0.5); // Center origin

    this.maskGraphics = this.add.graphics().fillCircle(0, 0, lensDiameter / 2).setScrollFactor(0);
    this.zoomedView.setMask(this.maskGraphics.createGeometryMask());

    this.magnifyingGlass = this.add.image(0, 0, 'magnifying-glass').setOrigin(0.25, 0.2).setDepth(7).setScrollFactor(0);

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
        // If clicking UI, ignore
        if (pointer.y < 200 * uiScale && pointer.x < 200 * uiScale) return; // Approximate UI blocking

        const captureRadiusSq = 50 * 50; // Lens capture radius

        this.eggs.getChildren().forEach(egg => {
            if (egg.active) {
                // Check if egg is under the mouse (center of lens)
                const distSq = Phaser.Math.Distance.Squared(pointer.x, pointer.y, egg.x, egg.y);
                if (distSq < captureRadiusSq) {
                     this.collectEgg(egg);
                     egg.destroy();
                     if (egg.symbolSprite) egg.symbolSprite.destroy();
                     this.updateScore();
                }
            }
        });
    });

    this.scale.on('resize', this.resize, this);

    // Check level complete immediately if returning to a completed map
    this.checkLevelComplete(true);
  }

  updateScore() {
      const foundEggs = this.registry.get('foundEggs').length;
      if (this.scoreText) this.scoreText.setText(`${foundEggs}/${TOTAL_EGGS}`);
  }

  resize(gameSize) {
      const width = gameSize.width;
      const height = gameSize.height;

      if (this.cameras && this.cameras.main) {
          this.cameras.main.setViewport(0, 0, width, height);
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

             // Add text to the texture
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

    // Ensure scene is still active before adding
    if (this.sys.settings.active) {
        this.sectionImage = this.add.image(this.cameras.main.centerX, this.cameras.main.centerY, textureKey)
            .setDisplaySize(1280 * this.bgScale, 720 * this.bgScale)
            .setDepth(0);
    }
    this.isUsingVideo = false;
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
    this.renderStamp.setDisplaySize(1280 * this.bgScale, 720 * this.bgScale);

    // Position the stamp relative to the scroll position
    // If the background is at (bgOffsetX, bgOffsetY) in the world,
    // and we are looking at (scrollX, scrollY),
    // then the stamp should be drawn at (bgOffsetX - scrollX, bgOffsetY - scrollY) * zoom
    // inside the render texture.

    const drawX = (this.bgOffsetX - scrollX) * zoom;
    const drawY = (this.bgOffsetY - scrollY) * zoom;

    this.renderStamp.setScale((1280 * this.bgScale / this.renderStamp.width) * zoom, (720 * this.bgScale / this.renderStamp.height) * zoom);

    this.zoomedView.draw(this.renderStamp, drawX, drawY);

    // Draw Eggs
    // Visibility check: If egg is within the visual lens radius (pointer)
    const lensRadiusSq = (lensDiameter / 2) * (lensDiameter / 2);

    this.eggs.getChildren().forEach(egg => {
      if (egg && egg.active) {
        // Check distance to the POINTER (center of lens view)
        const distSq = Phaser.Math.Distance.Squared(pointer.x, pointer.y, egg.x, egg.y);
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
    });

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
                 // console.log(`SectionHunt: Fixing video scale. Screen: ${width}x${height}, TargetW: ${targetDisplayW}`);
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
  constructor() {
    super({ key: 'EggZamRoom' });
    this.displayedEggImage = null;
    this.displayedSymbolImage = null;
    this.explanationText = null;
    this.noEggsText = null;
    this.currentEgg = null;
  }

  create() {
    this.input.setDefaultCursor('none');

    // Scale logic
    const width = this.scale.width;
    const height = this.scale.height;
    const scaleX = width / 1280;
    const scaleY = height / 720;
    const scale = Math.min(scaleX, scaleY); // Fit logic for minigame usually better, but let's try cover or contained fit
    // Background is 1280x720. Let's FIT.
    const bgScale = Math.min(scaleX, scaleY);

    // Position background centered
    this.add.image(width/2, height/2, 'egg-zam-room')
      .setDisplaySize(1280 * bgScale, 720 * bgScale)
      .setDepth(0);

    const examiner = this.add.image(0, 0, 'egg-zamminer').setOrigin(0, 0).setDepth(2);
    // Original pos: 390, 250. Size? Default.
    // Let's assume original design was 1280x720 fixed.
    // We scale everything by 'scale' (min) to ensure UI fits on screen.
    // But we need to center the "game area" in the viewport.

    const uiScale = Math.min(scaleX, scaleY);
    const offsetX = (width - 1280 * uiScale) / 2;
    const offsetY = (height - 720 * uiScale) / 2;

    // Examiner
    examiner.setPosition(offsetX + 390 * uiScale, offsetY + 250 * uiScale);
    examiner.setScale(uiScale);

    this.examiner = examiner; // Store for relative positioning

    this.add.image(offsetX + 200 * uiScale, offsetY + 50 * uiScale, 'symbol-result-summary-diag')
      .setOrigin(0, 0)
      .setDisplaySize(900 * uiScale, 600 * uiScale)
      .setDepth(1)
      .setAlpha(0);

    const eggZitButton = this.add.image(0, 200 * uiScale, 'egg-zit-button')
      .setOrigin(0, 0)
      .setDisplaySize(150 * uiScale, 131 * uiScale)
      .setInteractive()
      .on('pointerdown', () => this.scene.start('MapScene'))
      .setDepth(4).setScrollFactor(0);
    addButtonInteraction(this, eggZitButton, 'drive1');
    addTooltip(this, eggZitButton, 'Back to Map');

    this.add.image(0, 0, 'score')
      .setOrigin(0, 0)
      .setDisplaySize(200 * uiScale, 200 * uiScale)
      .setDepth(4).setScrollFactor(0);

    const foundEggsCount = this.registry.get('foundEggs').length;
    this.scoreText = this.add.text(50 * uiScale, 98 * uiScale, `${foundEggsCount}/${TOTAL_EGGS}`, {
      fontSize: `${42 * uiScale}px`,
      fill: '#000',
      fontStyle: 'bold',
      fontFamily: 'Comic Sans MS',
      stroke: '#fff',
      strokeThickness: 6 * uiScale
    }).setDepth(5);
    this.lastFoundCount = foundEggsCount;

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

    // Create hover graphics for highlighting bottles
    this.hoverGraphics = this.add.graphics().setDepth(10);

    // Zones need to be positioned relative to the SCALED examiner/room
    // Original: 450, 300, 100x200
    const leftBottleZone = this.add.zone(offsetX + 450 * uiScale, offsetY + 300 * uiScale, 100 * uiScale, 200 * uiScale).setOrigin(0, 0).setInteractive();
    // Original: 750, 300, 100x200
    const rightBottleZone = this.add.zone(offsetX + 750 * uiScale, offsetY + 300 * uiScale, 100 * uiScale, 200 * uiScale).setOrigin(0, 0).setInteractive();

    const addZoneHover = (zone) => {
        zone.on('pointerover', () => {
            this.hoverGraphics.clear();
            this.hoverGraphics.lineStyle(4, 0xffff00, 1);
            this.hoverGraphics.strokeRect(zone.x, zone.y, zone.width, zone.height);
            this.hoverGraphics.fillStyle(0xffff00, 0.2);
            this.hoverGraphics.fillRect(zone.x, zone.y, zone.width, zone.height);
        });

        zone.on('pointerout', () => {
            this.hoverGraphics.clear();
        });
    };

    addZoneHover(leftBottleZone);
    addZoneHover(rightBottleZone);

    const showExplanation = (isCorrect, guessText) => {
        if (isCorrect) {
            this.sound.play('success');
            const correctCount = this.registry.get('correctCategorizations') + 1;
            this.registry.set('correctCategorizations', correctCount);
            this.correctText.setText(`Correct: ${correctCount}`);
            this.currentEgg.categorized = true;
        } else {
            this.sound.play('error');
        }

        if (this.explanationText) this.explanationText.destroy();
        const data = this.currentEgg.symbolData;
        const eggId = this.currentEgg.eggId;

        this.explanationText = this.add.container(offsetX + 640 * uiScale, offsetY + 360 * uiScale).setDepth(100);

        const bgWidth = 800 * uiScale;
        const bgHeight = 600 * uiScale;

        const bg = this.add.graphics();
        bg.fillStyle(0xfff8dc, 0.95);
        bg.fillRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * uiScale);
        bg.lineStyle(8 * uiScale, 0x8b4513, 1);
        bg.strokeRoundedRect(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight, 20 * uiScale);
        bg.setInteractive(new Phaser.Geom.Rectangle(-bgWidth/2, -bgHeight/2, bgWidth, bgHeight), Phaser.Geom.Rectangle.Contains);

        // Header Elements
        const title = this.add.text(0, -bgHeight/2 + 60 * uiScale, data.name || "Symbol", {
            fontSize: `${48 * uiScale}px`, fill: '#8b4513', fontStyle: 'bold', fontFamily: 'Comic Sans MS'
        }).setOrigin(0.5);

        const eggImg = this.add.image(-bgWidth/2 + 90 * uiScale, -bgHeight/2 + 90 * uiScale, `egg-${eggId}`).setDisplaySize(100 * uiScale, 125 * uiScale);
        const symbolImgSmall = this.add.image(-bgWidth/2 + 90 * uiScale, -bgHeight/2 + 90 * uiScale, data.filename).setDisplaySize(100 * uiScale, 125 * uiScale);

        const guessDisplay = this.add.text(bgWidth/2 - 40 * uiScale, -bgHeight/2 + 60 * uiScale, `Your Guess:\n${guessText}`, {
            fontSize: `${32 * uiScale}px`, fill: '#333', fontStyle: 'bold', fontFamily: 'Comic Sans MS', align: 'center'
        }).setOrigin(0.5, 0.5);

        // Result Text (Correct/Incorrect) moved under the guess
        const resultText = this.add.text(bgWidth/2 - 40 * uiScale, -bgHeight/2 + 130 * uiScale, isCorrect ? "Correct!" : "Incorrect!", {
            fontSize: `${36 * uiScale}px`,
            fill: isCorrect ? '#008000' : '#d32f2f',
            fontStyle: 'bold',
            fontFamily: 'Comic Sans MS',
            stroke: '#fff',
            strokeThickness: 6 * uiScale
        }).setOrigin(0.5, 0.5);

        const expText = this.add.text(0, 0, data.explanation, {
            fontSize: `${28 * uiScale}px`, fill: '#000', fontFamily: 'Comic Sans MS',
            wordWrap: { width: bgWidth - 80 * uiScale, useAdvancedWrap: true }, align: 'center'
        }).setOrigin(0.5);

        const scriptText = this.add.text(0, bgHeight/2 - 120 * uiScale, data.scripture, {
            fontSize: `${24 * uiScale}px`, fill: '#0000ee', fontStyle: 'italic', fontFamily: 'Comic Sans MS',
            wordWrap: { width: bgWidth - 80 * uiScale, useAdvancedWrap: true }, align: 'center'
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });

        scriptText.on('pointerdown', (p, x, y, event) => {
            event.stopPropagation();
            const link = parseScriptureLink(data.scripture);
            if (link) window.open(link, '_blank', 'noopener,noreferrer');
        });

        const continueText = this.add.text(0, bgHeight/2 - 40 * uiScale, "[ Click anywhere to continue ]", {
            fontSize: `${20 * uiScale}px`, fill: '#8b4513', fontStyle: 'bold', fontFamily: 'Comic Sans MS'
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
                    this.displayRandomEggInfo(offsetX, offsetY, uiScale);
                }
            });
        });
    };

    leftBottleZone.on('pointerdown', () => {
      if (this.currentEgg && !this.currentEgg.categorized && !this.explanationText?.active) {
        showExplanation(this.currentEgg.symbolData.category === 'Christian', 'Christian');
      }
    });

    rightBottleZone.on('pointerdown', () => {
      if (this.currentEgg && !this.currentEgg.categorized && !this.explanationText?.active) {
        showExplanation(this.currentEgg.symbolData.category === 'Pagan', 'Worldly');
      }
    });

    this.displayRandomEggInfo(offsetX, offsetY, uiScale);

    // Store scale params for update/resize if needed (or just restart scene on resize)
    this.uiParams = { offsetX, offsetY, uiScale };

    this.scale.on('resize', () => {
        this.scene.restart(); // Simplest way to handle resizing complex UI layouts
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
        this.noEggsText = this.add.text(offsetX + 420 * scale, offsetY + 220 * scale, "All eggs have been categorized!", {
          fontSize: `${28 * scale}px`,
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
              fontSize: `${28 * scale}px`,
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

        return;
      }
    }

    if (this.displayedEggImage) this.displayedEggImage.destroy();
    if (this.displayedSymbolImage) this.displayedSymbolImage.destroy();
    if (this.explanationText) this.explanationText.destroy();
    if (this.noEggsText) this.noEggsText.destroy();

    if (this.currentEgg) {
      const { eggId, symbolData } = this.currentEgg;
      const eggPosX = offsetX + 630 * scale;
      const eggPosY = offsetY + 350 * scale;
      const symbolPosX = eggPosX;
      const symbolPosY = eggPosY;

      if (this.textures.exists(`egg-${eggId}`)) {
        this.displayedEggImage = this.add.image(eggPosX, eggPosY, `egg-${eggId}`)
          .setDisplaySize(100 * scale, 125 * scale)
          .setDepth(3);
      }
      if (symbolData && symbolData.filename && this.textures.exists(symbolData.filename)) {
        this.displayedSymbolImage = this.add.image(symbolPosX, symbolPosY, symbolData.filename)
          .setDisplaySize(100 * scale, 125 * scale)
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
