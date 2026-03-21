import re

def fix_stamp_pop(file):
    with open(file, 'r') as f:
        content = f.read()

    # Restore the blend mode for the video ONLY
    if "stampVideo.setBlendMode(Phaser.BlendModes.MULTIPLY)" not in content:
        content = content.replace("stampVideo.disableInteractive();", "stampVideo.disableInteractive();\n              stampVideo.setBlendMode(Phaser.BlendModes.MULTIPLY);")

    # Fix the visual jump regression in the 'complete' callback where the video is swapped for an image
    bad_scale_regex = r"stampImg\.setScale\(thumb\.scaleX\);"
    good_scale = """// Cover thumbnail height + 25%, maintaining intrinsic stamp ratio
                  const intrinsicHeight = stampImg.height || 720;
                  const targetHeight = thumb.displayHeight * 1.25;
                  stampImg.setScale(targetHeight / intrinsicHeight);"""

    # We only want to replace the bad scale that's INSIDE the complete callback,
    # but since we already updated the main stampImg scale to be the height math,
    # let's just make sure all instances of `stampImg.setScale(thumb.scaleX)` are replaced.
    content = re.sub(bad_scale_regex, good_scale, content)

    with open(file, 'w') as f:
        f.write(content)

fix_stamp_pop('main.js')
fix_stamp_pop('m/main.js')
