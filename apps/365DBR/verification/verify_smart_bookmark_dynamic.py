import time
from playwright.sync_api import sync_playwright
import datetime

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # 1. Simulate "Today" State
        now = datetime.datetime.now()
        today_mmdd = f"{now.month:02d}{now.day:02d}"

        # Calculate Tomorrow (Should Save)
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_mmdd = f"{tomorrow.month:02d}{tomorrow.day:02d}"

        # Calculate Day After Tomorrow (Should NOT Save)
        future = now + datetime.timedelta(days=2)
        future_mmdd = f"{future.month:02d}{future.day:02d}"

        initial_state = f'{{"date":"{today_mmdd}","focal":"lsv","compare":"kjv","verseId":"INIT.1.1"}}'

        # Note: Must navigate first before setting localStorage
        page = context.new_page()
        print("Navigating to index.html...")
        page.goto("http://localhost:8000/index.html")

        # Set storage
        page.evaluate(f"localStorage.setItem('biblical_reading_state', '{initial_state}')")
        page.reload()
        time.sleep(2)

        try:
            # 2. Navigate to TOMORROW (Allowed Future)
            print(f"Navigating to Tomorrow ({tomorrow_mmdd})...")
            # Navigate using URL to be precise and avoid UI button issues
            page.goto(f"http://localhost:8000/index.html?startDate={tomorrow_mmdd}")
            time.sleep(2)

            saved_state = page.evaluate("localStorage.getItem('biblical_reading_state')")
            print(f"State after navigating to Tomorrow: {saved_state}")

            if f'"date":"{tomorrow_mmdd}"' in saved_state:
                print("SUCCESS: Date UPDATED for Tomorrow (Allowed).")
            else:
                print(f"FAILURE: Date NOT updated for Tomorrow. Expected {tomorrow_mmdd}.")

            # 3. Navigate to DAY AFTER TOMORROW (Blocked Future)
            print(f"Navigating to Day After Tomorrow ({future_mmdd})...")
            page.goto(f"http://localhost:8000/index.html?startDate={future_mmdd}")
            time.sleep(2)

            saved_state_2 = page.evaluate("localStorage.getItem('biblical_reading_state')")
            print(f"State after navigating to Future+2: {saved_state_2}")

            if f'"date":"{tomorrow_mmdd}"' in saved_state_2:
                print("SUCCESS: Date NOT updated for Future+2 (Blocked). Preserved Tomorrow.")
            elif f'"date":"{future_mmdd}"' in saved_state_2:
                print(f"FAILURE: Date UPDATED for Future+2! Should have been blocked.")
            else:
                 print(f"FAILURE: Unexpected state: {saved_state_2}")

            page.screenshot(path="verification/smart_bookmark_dynamic_test.png")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
