import os
from playwright.sync_api import Page, sync_playwright

def verify_feature(page: Page):
    print("Navigating to mobile index.html...")
    page.goto("http://localhost:8000/apps/HeIsRisen/m/index.html")

    print("Waiting for game to initialize...")
    page.wait_for_function("""
        () => {
            if (typeof window.game === 'undefined' || !window.game.scene) return false;

            if (!window.VideoTestInjected) {
                window.VideoTestInjected = true;

                const scenes = window.game.scene.scenes;
                scenes.forEach(s => {
                    if (s.sys.isActive() || s.sys.isSleeping() || s.sys.isPaused()) {
                        window.game.scene.stop(s.scene.key);
                    }
                });

                const tempScene = window.game.scene.add('VideoTestScene', {
                    create: function() {
                        window.videoTestPlaying = false;
                        // Bright blue background
                        this.add.rectangle(400, 300, 1000, 1000, 0x0000ff);

                        // We do NOT use blend modes here, just standard rendering
                        if (this.cache.video.has('level-complete')) {
                            const video = this.add.video(400, 300, 'level-complete');
                            video.setLoop(true);
                            video.play();

                            video.on('play', () => {
                                window.videoTestPlaying = true;
                            });
                        } else {
                            this.load.video('test-vid', 'assets/video/level-complete.webm');
                            this.load.once('complete', () => {
                                const video = this.add.video(400, 300, 'test-vid');
                                video.setLoop(true);
                                video.play();
                                video.on('play', () => {
                                    window.videoTestPlaying = true;
                                });
                            });
                            this.load.start();
                        }
                    }
                }, true);
            }

            return window.videoTestPlaying === true;
        }
    """, timeout=60000)

    print("Test Scene playing video. Capturing screenshot...")
    page.wait_for_timeout(3000)

    screenshot_path = os.path.abspath("/home/jules/verification/video_transparency_test_mobile_fixed.png")
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        video_dir = os.path.abspath("/home/jules/verification/video_direct_mobile_fixed")
        context = browser.new_context(
            record_video_dir=video_dir,
            viewport={'width': 844, 'height': 390}
        )
        page = context.new_page()
        try:
            verify_feature(page)
        finally:
            context.close()
            browser.close()
