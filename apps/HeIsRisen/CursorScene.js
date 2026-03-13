class CursorScene extends Phaser.Scene {
  constructor() {
    super({ key: 'CursorScene', active: true }); // Active by default
  }

  create() {
    this.fingerCursor = this.add.image(0, 0, 'finger-cursor')
        .setOrigin(0, 0)
        .setDisplaySize(50, 75)
        .setDepth(9999); // Max depth

    // Ensure this scene renders on top
    this.scene.bringToTop();
  }

  update() {
    // Follow pointer from the active input manager
    // Note: input.x/y are relative to the scene's camera, but this scene matches window size.
    // However, we must ensure we get the global pointer position.
    const pointer = this.input.activePointer;
    this.fingerCursor.setPosition(pointer.x, pointer.y);

    // Optional: cursor feedback (scale down on click)
    if (pointer.isDown) {
        this.fingerCursor.setScale(0.9);
    } else {
        this.fingerCursor.setScale(1.0);
    }
  }
}
