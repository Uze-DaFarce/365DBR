import os
import subprocess
import time
import io
import sys

def ensure_dependencies():
    missing = []
    try:
        from PIL import Image
    except ImportError:
        missing.append('pillow')
    try:
        import playwright
    except ImportError:
        missing.append('playwright')
    try:
        import pytest
    except ImportError:
        missing.append('pytest')

    if missing:
        print(f"Installing missing test dependencies: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

        if 'playwright' in missing:
            print("Installing Playwright browsers...")
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

        # Need to reload modules if we just installed them
        import importlib
        import site
        importlib.invalidate_caches()

ensure_dependencies()
from PIL import Image

def start_server(app_dir):
    """Starts a local http-server in the specified directory."""
    server_process = subprocess.Popen(
        ["npx", "http-server", "-p", "8080", "-c-1"],
        cwd=app_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)  # wait for server to start
    return server_process

def is_screen_blank(screenshot_bytes, tolerance_threshold=0.98):
    """
    Analyzes an image to determine if it's mostly a single solid color (like a black screen).
    Returns True if the image is blank/solid, False otherwise.
    """
    try:
        img = Image.open(io.BytesIO(screenshot_bytes))
        img = img.convert("RGB")

        # Get all colors and their counts
        colors = img.getcolors(img.size[0] * img.size[1])
        if not colors:
             return False # Image has more than maxcolors

        # Find the most frequent color
        most_frequent_count = max(count for count, color in colors)
        total_pixels = img.size[0] * img.size[1]

        ratio = most_frequent_count / total_pixels
        return ratio > tolerance_threshold
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return True # Default to failing if we can't read the image

def assert_not_blank_screen(page, error_msg="Screen is blank or solid colored"):
    """
    Takes a screenshot and raises an AssertionError if the screen is mostly a single solid color.
    """
    # Force a render cycle to prevent capturing a partial frame
    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")

    # Take screenshot in memory
    screenshot_bytes = page.screenshot(type="jpeg")

    if is_screen_blank(screenshot_bytes):
        raise AssertionError(f"Visual Test Failed: {error_msg}")

    print("Visual Check: Screen is not blank.")

def get_random_map_section(page):
    """
    Retrieves a random available map section from the game registry.
    """
    import random
    sections_data = page.evaluate("""
        () => {
            const registry = window.game.scene.scenes[0].registry;
            const sections = registry.get('sections');
            return sections.map(s => s.name);
        }
    """)
    if not sections_data:
        raise Exception("No sections found in registry.")

    selected = random.choice(sections_data)
    print(f"Randomly selected map section: {selected}")
    return selected

def init_global_bypasses(page):
    """
    Injects global scripts to bypass autoplay policies or user interaction requirements.
    It also dismisses device mismatch popups automatically.
    """
    page.add_init_script("""
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' || e.code === 'Enter') {
                // Let Phaser handle it via its own listener
            }
        });

        // Auto-dismiss the device mismatch prompts to prevent blocking tests
        const checkPrompt = setInterval(() => {
            if (window.game && window.game.scene && window.game.scene.scenes.length > 0) {
                const mainScene = window.game.scene.getScene('MainMenu');
                if (mainScene && mainScene.registry) {
                    mainScene.registry.set('mobilePromptShown', true);
                    mainScene.registry.set('desktopPromptShown', true);
                    clearInterval(checkPrompt);
                }
            }
        }, 100);
    """)

def wait_for_phaser_init(page):
    page.wait_for_function("() => window.game && window.game.scene && window.game.scene.scenes.length > 0")

def wait_for_active_scene(page, scene_name):
    page.wait_for_function(f"() => window.game.scene.getScene('{scene_name}').scene.isActive()")
