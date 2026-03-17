import re

with open("apps/HeIsRisen/main.js", "r") as f:
    content = f.read()

# Replace stampVideo fallback size
# The problem is `stampVideo` is created then `stampVideo.play()`. But it doesn't have dimensions yet.
# When `stampVideo` doesn't have dimensions, `intrinsicHeight` defaults to 720.
# BUT `stampVideo.setScale` is called. If `stampVideo.videoHeight` is 0, the scale happens, but Phaser internal Framebuffer allocates a 0x0 size for the WebGL texture!
# So we need to protect ANY setScale or setDisplaySize on a video object if it doesn't have a width > 0.

# 1. MapScene stampVideo scaling
old_stamp_scale1 = """              const updateStampSize = () => {
                  stampVideo.setPosition(thumb.x, thumb.y - 40 * thumb.scaleY);
                  const intrinsicHeight = stampVideo.video.videoHeight || stampVideo.height || 720;
                  const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                  const calculatedScale = targetHeight / intrinsicHeight;
                  stampVideo.setScale(calculatedScale);
              };"""

new_stamp_scale1 = """              const updateStampSize = () => {
                  stampVideo.setPosition(thumb.x, thumb.y - 40 * thumb.scaleY);
                  const videoHasDims = stampVideo.video && stampVideo.video.videoHeight > 0;
                  if (videoHasDims) {
                      const intrinsicHeight = stampVideo.video.videoHeight;
                      const targetHeight = (thumb.height * thumb.scaleY) * 1.25;
                      const calculatedScale = targetHeight / intrinsicHeight;
                      if (calculatedScale > 0 && !isNaN(calculatedScale)) stampVideo.setScale(calculatedScale);
                  }
              };"""
content = content.replace(old_stamp_scale1, new_stamp_scale1)

old_stamp_scale2 = """                  // Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const intrinsicHeight = item.video.height || 720;
                  const targetHeight = (item.thumb.height * item.thumb.scaleY) * 1.25;
                  item.video.setScale(targetHeight / intrinsicHeight);
              }"""

new_stamp_scale2 = """                  // Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const hasDims = item.video.type === 'Video' ? (item.video.video && item.video.video.videoHeight > 0) : (item.video.height > 0);
                  if (hasDims) {
                      const intrinsicHeight = item.video.type === 'Video' ? item.video.video.videoHeight : item.video.height;
                      const targetHeight = (item.thumb.height * item.thumb.scaleY) * 1.25;
                      const calcScale = targetHeight / intrinsicHeight;
                      if (calcScale > 0 && !isNaN(calcScale)) item.video.setScale(calcScale);
                  }
              }"""
content = content.replace(old_stamp_scale2, new_stamp_scale2)

with open("apps/HeIsRisen/main.js", "w") as f:
    f.write(content)
