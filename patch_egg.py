import re

with open('apps/HeIsRisen/m/main.js', 'r') as f:
    content = f.read()

# Replace the egg position and alpha
old_pos = r"""      const offsetX = \(width - \(1168 \* coverScale\)\) / 2;
      const offsetY = \(height - \(784 \* coverScale\)\) / 2;

      // Calculate relative to the keyframe bounds so it aligns with the chamber
      const eggPosX = offsetX \+ \(1168 \* coverScale\) \* 0\.493;
      const eggPosY = offsetY \+ \(784 \* coverScale\) \* 0\.50;
      const symbolPosX = eggPosX;
      const symbolPosY = eggPosY;

      // Scale them to match the new background design
      const eggScaleTarget = \(240 \* coverScale\) \* 0\.85;
      const eggHeightTarget = \(300 \* coverScale\) \* 0\.85;

      if \(this\.textures\.exists\(`egg-\$\{eggId\}`\)\) \{
        this\.displayedEggImage = this\.add\.image\(eggPosX, eggPosY, `egg-\$\{eggId\}`\)
          \.setOrigin\(0\.5, 0\.5\)
          \.setDisplaySize\(eggScaleTarget, eggHeightTarget\)
          \.setDepth\(3\);
      \}
      if \(symbolData && symbolData\.filename && this\.textures\.exists\(symbolData\.filename\)\) \{
        this\.displayedSymbolImage = this\.add\.image\(symbolPosX, symbolPosY, symbolData\.filename\)
          \.setOrigin\(0\.5, 0\.5\)
          \.setDisplaySize\(eggScaleTarget, eggHeightTarget\)
          \.setDepth\(3\);
      \}"""

new_pos = """      const offsetX = (width - (1168 * coverScale)) / 2;
      const offsetY = (height - (784 * coverScale)) / 2;

      // Calculate relative to the keyframe bounds so it aligns with the chamber
      const eggPosX = offsetX + (1168 * coverScale) * 0.493 - (16 * coverScale);
      const eggPosY = offsetY + (784 * coverScale) * 0.50 + (10 * coverScale);
      const symbolPosX = eggPosX;
      const symbolPosY = eggPosY;

      // Scale them to match the new background design
      const eggScaleTarget = (240 * coverScale) * 0.85;
      const eggHeightTarget = (300 * coverScale) * 0.85;

      if (this.textures.exists(`egg-${eggId}`)) {
        this.displayedEggImage = this.add.image(eggPosX, eggPosY, `egg-${eggId}`)
          .setOrigin(0.5, 0.5)
          .setDisplaySize(eggScaleTarget, eggHeightTarget)
          .setAlpha(0)
          .setDepth(3);
      }
      if (symbolData && symbolData.filename && this.textures.exists(symbolData.filename)) {
        this.displayedSymbolImage = this.add.image(symbolPosX, symbolPosY, symbolData.filename)
          .setOrigin(0.5, 0.5)
          .setDisplaySize(eggScaleTarget, eggHeightTarget)
          .setAlpha(0)
          .setDepth(3);
      }

      this.tweens.add({
        targets: [this.displayedEggImage, this.displayedSymbolImage].filter(Boolean),
        alpha: 1,
        duration: 500
      });"""

content = re.sub(old_pos, new_pos, content)

with open('apps/HeIsRisen/m/main.js', 'w') as f:
    f.write(content)
