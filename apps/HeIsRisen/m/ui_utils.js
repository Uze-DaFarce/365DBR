export function createConfirmModal(scene, message, onConfirm, onCancel) {
    const width = scene.cameras.main.width;
    const height = scene.cameras.main.height;

    const container = scene.add.container(width / 2, height / 2).setDepth(2000);

    // Dim background overlay
    const overlay = scene.add.rectangle(0, 0, width, height, 0x000000, 0.7);
    overlay.setInteractive(); // Blocks clicks to underlying UI

    // Modal background
    const modalBg = scene.add.graphics();
    modalBg.fillStyle(0x333333, 1);
    modalBg.fillRoundedRect(-150, -100, 300, 200, 16);
    modalBg.lineStyle(4, 0xffffff, 1);
    modalBg.strokeRoundedRect(-150, -100, 300, 200, 16);

    const messageText = scene.add.text(0, -40, message, {
        fontSize: '20px',
        fill: '#ffffff',
        fontFamily: 'Comic Sans MS',
        align: 'center',
        wordWrap: { width: 260 }
    }).setOrigin(0.5);

    // Yes Button
    const yesBtn = scene.add.container(-60, 40);
    const yesBg = scene.add.graphics();
    yesBg.fillStyle(0xff0000, 1);
    yesBg.fillRoundedRect(-40, -20, 80, 40, 8);
    const yesText = scene.add.text(0, 0, 'YES', { fontSize: '18px', fill: '#ffffff', fontFamily: 'Comic Sans MS', fontStyle: 'bold' }).setOrigin(0.5);
    yesBtn.add([yesBg, yesText]);
    yesBtn.setSize(80, 40);
    yesBtn.setInteractive(new Phaser.Geom.Rectangle(-40, -20, 80, 40), Phaser.Geom.Rectangle.Contains);

    // No Button
    const noBtn = scene.add.container(60, 40);
    const noBg = scene.add.graphics();
    noBg.fillStyle(0x555555, 1);
    noBg.fillRoundedRect(-40, -20, 80, 40, 8);
    const noText = scene.add.text(0, 0, 'NO', { fontSize: '18px', fill: '#ffffff', fontFamily: 'Comic Sans MS', fontStyle: 'bold' }).setOrigin(0.5);
    noBtn.add([noBg, noText]);
    noBtn.setSize(80, 40);
    noBtn.setInteractive(new Phaser.Geom.Rectangle(-40, -20, 80, 40), Phaser.Geom.Rectangle.Contains);

    container.add([overlay, modalBg, messageText, yesBtn, noBtn]);

    yesBtn.on('pointerdown', () => {
        container.destroy();
        if (onConfirm) onConfirm();
    });

    noBtn.on('pointerdown', () => {
        container.destroy();
        if (onCancel) onCancel();
    });

    return container;
}
