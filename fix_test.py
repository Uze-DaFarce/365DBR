import re

with open("apps/HeIsRisen/tests/test_stinky_eggs.py", "r") as f:
    content = f.read()

content = content.replace("""            page.wait_for_function("() => window.game.scene.getScene('MainMenu').scene.isActive()")
            page.evaluate("window.game.scene.scenes[0].scene.start('EggZamRoom')")
            time.sleep(2)""", """            time.sleep(5) # Just wait

            # Start MapScene directly
            page.evaluate("window.game.scene.scenes[0].scene.start('MapScene')")
            time.sleep(2)""")

with open("apps/HeIsRisen/tests/test_stinky_eggs.py", "w") as f:
    f.write(content)
