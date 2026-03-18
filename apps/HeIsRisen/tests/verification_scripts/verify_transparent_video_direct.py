import os
from playwright.sync_api import Page, sync_playwright

def verify_feature(page: Page):
    print("Navigating to index.html...")
    # Navigate to the page
    page.goto("http://localhost:8000/apps/HeIsRisen/index.html")

    print("Waiting for game to initialize...")

    # We will inject a custom scene to just play the video over a colorful background
    # Wait for the game instance to be ready, bypassing whatever scene is running
    page.wait_for_function("""
        () => {
            if (typeof window.game === 'undefined' || !window.game.scene) return false;

            // Only inject once
            if (!window.VideoTestInjected) {
                window.VideoTestInjected = true;

                // Stop all existing scenes to clear the way
                const scenes = window.game.scene.scenes;
                scenes.forEach(s => {
                    if (s.sys.isActive() || s.sys.isSleeping() || s.sys.isPaused()) {
                        window.game.scene.stop(s.scene.key);
                    }
                });

                // Create a temporary scene specifically to play the video over a red background
                const tempScene = window.game.scene.add('VideoTestScene', {
                    create: function() {
                        window.videoTestPlaying = false;
                        // Bright red background
                        this.add.rectangle(400, 300, 800, 600, 0xff0000);

                        // Load the video directly from cache or URL if necessary
                        if (this.cache.video.has('level-complete')) {
                            const video = this.add.video(400, 300, 'level-complete');
                            video.setLoop(true);
                            video.play();

                            video.on('play', () => {
                                window.videoTestPlaying = true;
                            });
                        } else {
                            // If the video wasn't preloaded, load it now
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
                }, true); // Start it immediately
            }

            return window.videoTestPlaying === true;
        }
    """, timeout=60000)

    print("Test Scene playing video. Capturing screenshot...")
    page.wait_for_timeout(3000) # Let it play out a few frames

    screenshot_path = os.path.abspath("/home/jules/verification/video_transparency_test.png")
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Record video
        video_dir = os.path.abspath("/home/jules/verification/video_direct")
        context = browser.new_context(record_video_dir=video_dir)
        page = context.new_page()
        try:
            verify_feature(page)
        finally:
            context.close()
            browser.close()
