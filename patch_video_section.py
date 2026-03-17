import re

with open("apps/HeIsRisen/main.js", "r") as f:
    content = f.read()

# 2. SectionHunt sectionVideo scaling
# Line ~1600
old_section_video1 = """      if (this.isUsingVideo && this.sectionVideo) {
          this.sectionVideo.setPosition(width/2, height/2);
          this.sectionVideo.setDisplaySize(1280 * scale, 720 * scale);
      }"""

new_section_video1 = """      if (this.isUsingVideo && this.sectionVideo) {
          this.sectionVideo.setPosition(width/2, height/2);
          if (this.sectionVideo.video && this.sectionVideo.video.videoWidth > 0 && scale > 0 && !isNaN(scale)) {
              this.sectionVideo.setDisplaySize(1280 * scale, 720 * scale);
          }
      }"""
content = content.replace(old_section_video1, new_section_video1)

# In update() for sectionVideo
old_section_video2 = """    // Robust scaling check for Video in SectionHunt
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
                 this.sectionVideo.setDisplaySize(1280 * targetScale, 720 * targetScale);"""

new_section_video2 = """    // Robust scaling check for Video in SectionHunt
    if (this.isUsingVideo && this.sectionVideo && this.sectionVideo.active) {
        if (this.sectionVideo.video && this.sectionVideo.video.videoWidth > 0) {
             // Check if scale matches Cover requirement
             const width = this.scale.width;
             const height = this.scale.height;
             const scaleX = width / 1280;
             const scaleY = height / 720;
             const targetScale = Math.max(scaleX, scaleY);
             const targetDisplayW = 1280 * targetScale;

             if (targetScale > 0 && !isNaN(targetScale) && Math.abs(this.sectionVideo.displayWidth - targetDisplayW) > 5) {
                 // console.log(`SectionHunt: Fixing video scale. Screen: ${width}x${height}, TargetW: ${targetDisplayW}`);
                 this.sectionVideo.setDisplaySize(1280 * targetScale, 720 * targetScale);"""
content = content.replace(old_section_video2, new_section_video2)

with open("apps/HeIsRisen/main.js", "w") as f:
    f.write(content)
