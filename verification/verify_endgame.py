import os
from playwright.sync_api import Page, expect, sync_playwright

def wait_for_scene(page: Page, scene_key: str, timeout: int = 10000):
    """Wait for a specific Phaser scene to become active."""
    print(f"Waiting for scene {scene_key}...")
    page.wait_for_function(
        f'''() => {{
            const game = window.game;
            if (!game) return false;
            const scene = game.scene.getScene("{scene_key}");
            return scene && scene.scene.isActive();
        }}''',
        timeout=timeout
    )
    print(f"Scene {scene_key} is active.")

def verify_desktop_game(page: Page):
    print("Navigating to desktop game...")
    page.goto("http://localhost:8000/apps/HeIsRisen/index.html")
    page.wait_for_timeout(2000)

    # Make sure MainMenu is active
    wait_for_scene(page, "MainMenu")

    # Click to start intro
    print("Clicking to start intro...")
    page.mouse.click(640, 360)
    page.wait_for_timeout(1000)

    # The PLAY NOW button scales up. Let's just evaluate JS to start MapScene.
    print("Starting MapScene via JS...")
    page.evaluate('''() => {
        const game = window.game;
        const introVideo = game.scene.getScene('MainMenu').introVideo;
        if(introVideo) {
            introVideo.stop();
            introVideo.destroy();
        }
        game.scene.getScene('MainMenu').scene.start('MapScene');
    }''')
    page.wait_for_timeout(1000)

    wait_for_scene(page, "MapScene")

    # Force the endgame
    print("Forcing endgame...")
    page.evaluate('''() => {
        const game = window.game;
        const totalEggs = 60;
        const eggData = game.registry.get('eggData');
        const simulatedFound = eggData.map(e => ({
            eggId: e.eggId,
            symbolData: e.symbol,
            categorized: false
        }));

        // Manipulate category for test scoring (30 holy, 30 pagan)
        simulatedFound.forEach((e, i) => {
            if (!e.symbolData) e.symbolData = {};
            e.symbolData.category = (i < 30) ? 'Christian' : 'Pagan';
        });

        game.registry.set('foundEggs', simulatedFound);

        // Jump to EggZamRoom
        const mapScene = game.scene.getScene('MapScene');
        mapScene.scene.start('EggZamRoom');
    }''')

    page.wait_for_timeout(2000)
    wait_for_scene(page, "EggZamRoom")

    # We are now in EggZamRoom with all eggs found. The summary panel should be visible.
    print("Taking desktop summary screenshot...")
    page.screenshot(path="verification/desktop_summary.png")
    page.wait_for_timeout(1000)

    # Click "PLAY AGAIN" by evaluating the triggerRestart function attached to the button
    print("Triggering Restart...")
    page.evaluate('''() => {
        const game = window.game;
        const eggZamRoom = game.scene.getScene('EggZamRoom');
        // We know the global initializeGameData exists
        initializeGameData(eggZamRoom.registry, eggZamRoom.scene.systems.cache);
        eggZamRoom.scene.start('MapScene');
    }''')

    page.wait_for_timeout(2000)
    wait_for_scene(page, "MapScene")
    print("Taking desktop reset screenshot...")
    page.screenshot(path="verification/desktop_reset.png")
    page.wait_for_timeout(1000)

def verify_mobile_game(page: Page):
    print("Navigating to mobile game...")
    page.goto("http://localhost:8000/apps/HeIsRisen/m/index.html")
    page.wait_for_timeout(2000)

    wait_for_scene(page, "MainMenu")

    print("Clicking to start mobile intro...")
    page.mouse.click(200, 400)
    page.wait_for_timeout(1000)

    print("Starting MapScene via JS...")
    page.evaluate('''() => {
        const game = window.game;
        const introVideo = game.scene.getScene('MainMenu').introVideo;
        if(introVideo) {
            introVideo.stop();
            introVideo.destroy();
        }
        game.scene.getScene('MainMenu').scene.start('MapScene');
    }''')
    page.wait_for_timeout(1000)

    wait_for_scene(page, "MapScene")

    print("Forcing endgame...")
    page.evaluate('''() => {
        const game = window.game;
        const totalEggs = 60;
        const eggData = game.registry.get('eggData');
        const simulatedFound = eggData.map(e => ({
            eggId: e.eggId,
            symbolData: e.symbol,
            categorized: false
        }));

        simulatedFound.forEach((e, i) => {
            if (!e.symbolData) e.symbolData = {};
            e.symbolData.category = (i < 30) ? 'Christian' : 'Pagan';
        });

        game.registry.set('foundEggs', simulatedFound);

        const mapScene = game.scene.getScene('MapScene');
        mapScene.scene.start('EggZamRoom');
    }''')

    page.wait_for_timeout(2000)
    wait_for_scene(page, "EggZamRoom")
    print("Taking mobile summary screenshot...")
    page.screenshot(path="verification/mobile_summary.png")
    page.wait_for_timeout(1000)

    print("Triggering mobile Restart...")
    page.evaluate('''() => {
        const game = window.game;
        const eggZamRoom = game.scene.getScene('EggZamRoom');
        initializeGameData(eggZamRoom.registry, eggZamRoom.scene.systems.cache);
        eggZamRoom.scene.start('MapScene');
    }''')

    page.wait_for_timeout(2000)
    wait_for_scene(page, "MapScene")
    print("Taking mobile reset screenshot...")
    page.screenshot(path="verification/mobile_reset.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Desktop
        context_desktop = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir="verification/video"
        )
        page_desktop = context_desktop.new_page()
        try:
            verify_desktop_game(page_desktop)
        finally:
            context_desktop.close()

        # Mobile
        context_mobile = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            record_video_dir="verification/video"
        )
        page_mobile = context_mobile.new_page()
        try:
            verify_mobile_game(page_mobile)
        finally:
            context_mobile.close()

        browser.close()
