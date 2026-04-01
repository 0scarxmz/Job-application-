from playwright.sync_api import sync_playwright
import time

RESUME_PATH = "/Users/sentional/JOB hunting/Untitled Resume - Resume.pdf"
JOB_URL = "https://job-boards.greenhouse.io/exiger/jobs/5751719004"

def main():
    with sync_playwright() as p:
        print(f"Starting Exiger application debug...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(JOB_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        iframe_locator = page.frame_locator("#grnhse_iframe")
        
        # Click Apply
        try:
            apply_button = iframe_locator.locator('button[aria-label="Apply"], button:has-text("Apply")').first
            if apply_button.is_visible():
                print("Clicking Apply button...")
                apply_button.click()
                # Wait for form to appear
                print("Waiting for form...")
                time.sleep(5)
        except Exception as e:
            print(f"Error clicking Apply: {e}")
        
        print(f"Frames after clicking: {len(page.frames)}")
        for i, frame in enumerate(page.frames):
            print(f"Frame {i}: Name='{frame.name}', URL='{frame.url}'")
            if "greenhouse.io" in frame.url:
                with open(f"/Users/sentional/JOB hunting/exiger_iframe_debug_{i}.html", "w") as f:
                    f.write(frame.content())
                print(f"Dumped frame {i}")
        
        browser.close()

if __name__ == "__main__":
    main()
