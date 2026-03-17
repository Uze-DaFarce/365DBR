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
            categorized: true
        }));

        // Manipulate category for test scoring (30 holy, 30 pagan)
        simulatedFound.forEach((e, i) => {
            if (!e.symbolData) e.symbolData = {};
            e.symbolData.category = (i < 30) ? 'Christian' : 'Pagan';
        });

        game.registry.set('foundEggs', simulatedFound);
        game.registry.set('correctCategorizations', 60);

        // Jump to EggZamRoom
        const mapScene = game.scene.getScene('MapScene');
        // Wait for rendering to flush before transitioning to prevent WebGL artifacts
        setTimeout(() => {
            mapScene.scene.start('EggZamRoom');
        }, 500);
    }''')

    page.wait_for_timeout(2000)
    wait_for_scene(page, "EggZamRoom")

    page.wait_for_timeout(2000)
    # We are now in EggZamRoom with all eggs found. The summary panel should be visible.
    print("Verifying desktop summary components...")

    summary_data = page.evaluate('''() => {
        const game = window.game;
        const scene = game.scene.getScene('EggZamRoom');
        let textValues = [];
        const extractText = (container) => {
            if (container.type === "Text") textValues.push(container.text);
            if (container.list) container.list.forEach(extractText);
        };
        scene.children.list.forEach(extractText);
        return textValues;
    }''')

    print(f"Detected Desktop Text Nodes in EggZamRoom: {summary_data}")

    if "Final EggZamination!" not in summary_data:
        raise Exception("Failed to find summary title 'Final EggZamination!' on Desktop.")

    holy_text_found = any(["EggSelent (Holy) Eggs: 30 / 30" in txt for txt in summary_data])
    worldly_text_found = any(["Eggstra-Stinky (Worldly) Eggs: 30 / 30" in txt for txt in summary_data])
    total_text_found = any(["Total Categorized: 60/60" in txt for txt in summary_data])

    if not (holy_text_found and worldly_text_found and total_text_found):
        raise Exception("Failed to verify correct desktop scoring categories.")

    print("Desktop Endgame Validation Passed.")
    page.wait_for_timeout(1000)

    # Click "PLAY AGAIN" by evaluating the triggerRestart function attached to the button
    print("Triggering Restart...")
    page.evaluate('''() => {
        const game = window.game;
        const eggZamRoom = game.scene.getScene('EggZamRoom');
        // We know the global initializeGameData exists
        initializeGameData(eggZamRoom.registry, eggZamRoom.cache);

        // Wait for rendering to flush before transitioning to prevent WebGL artifacts
        setTimeout(() => {
            eggZamRoom.scene.start('MapScene');
        }, 500);
    }''')
    page.wait_for_timeout(500)

    page.wait_for_timeout(2000)
    wait_for_scene(page, "MapScene")
    print("Taking desktop reset screenshot...")
    page.wait_for_timeout(2000) # Ensure map rendering flush
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
            categorized: true
        }));

        simulatedFound.forEach((e, i) => {
            if (!e.symbolData) e.symbolData = {};
            e.symbolData.category = (i < 30) ? 'Christian' : 'Pagan';
        });

        game.registry.set('foundEggs', simulatedFound);
        game.registry.set('correctCategorizations', 60);

        const mapScene = game.scene.getScene('MapScene');
        mapScene.scene.start('EggZamRoom');
    }''')

    page.wait_for_timeout(2000)
    wait_for_scene(page, "EggZamRoom")
    page.wait_for_timeout(2000)
    print("Verifying mobile summary components...")

    mobile_summary_data = page.evaluate('''() => {
        const game = window.game;
        const scene = game.scene.getScene('EggZamRoom');
        let textValues = [];
        const extractText = (container) => {
            if (container.type === "Text") textValues.push(container.text);
            if (container.list) container.list.forEach(extractText);
        };
        scene.children.list.forEach(extractText);
        return textValues;
    }''')

    print(f"Detected Mobile Text Nodes in EggZamRoom: {mobile_summary_data}")

    if "Final EggZamination!" not in mobile_summary_data:
        raise Exception("Failed to find summary title 'Final EggZamination!' on Mobile.")

    holy_text_found = any(["EggSelent (Holy) Eggs: 30 / 30" in txt for txt in mobile_summary_data])
    worldly_text_found = any(["Eggstra-Stinky (Worldly) Eggs: 30 / 30" in txt for txt in mobile_summary_data])
    total_text_found = any(["Total Categorized: 60/60" in txt for txt in mobile_summary_data])

    if not (holy_text_found and worldly_text_found and total_text_found):
        raise Exception("Failed to verify correct mobile scoring categories.")

    print("Mobile Endgame Validation Passed.")
    page.wait_for_timeout(1000)

    print("Triggering mobile Restart...")
    page.evaluate('''() => {
        const game = window.game;
        const eggZamRoom = game.scene.getScene('EggZamRoom');
        initializeGameData(eggZamRoom.registry, eggZamRoom.cache);
        eggZamRoom.scene.start('MapScene');
    }''')

    page.wait_for_timeout(2000)
    wait_for_scene(page, "MapScene")
    print("Taking mobile reset screenshot...")
    page.wait_for_timeout(2000) # Ensure map rendering flush
    page.screenshot(path="verification/mobile_reset.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    with sync_playwright() as p:
        # Forcing hardware acceleration and removing problematic GL angle arguments
        # WebGL needs --use-gl=swiftshader or disable sandboxing if Xvfb headless
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--use-gl=swiftshader",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--disable-gpu-driver-bug-workarounds",
                "--no-sandbox"
            ]
        )

        # Desktop
        context_desktop = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page_desktop = context_desktop.new_page()
        page_desktop.on("console", lambda msg: print(f"Desktop Console: {msg.text}"))
        page_desktop.on("pageerror", lambda err: print(f"Desktop Error: {err}"))
        try:
            verify_desktop_game(page_desktop)
        finally:
            context_desktop.close()

        # Mobile
        context_mobile = browser.new_context(
            viewport={'width': 844, 'height': 390},
            is_mobile=True
        )
        page_mobile = context_mobile.new_page()
        page_mobile.on("console", lambda msg: print(f"Mobile Console: {msg.text}"))
        page_mobile.on("pageerror", lambda err: print(f"Mobile Error: {err}"))
        try:
            verify_mobile_game(page_mobile)
        finally:
            context_mobile.close()

        browser.close()
