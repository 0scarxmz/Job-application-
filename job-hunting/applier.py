import sys
import time
import json
from playwright.sync_api import sync_playwright

def main():
    print("Starting Playwright headed test...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # We need to navigate to the Garage job posting
        url = "https://www.ycombinator.com/companies/garage/jobs"
        print(f"Navigating to {url}")
        page.goto(url)
        
        # Give the page a moment to load and the user a moment to see it
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
        print("Page loaded. Looking for the 'Apply' button...", flush=True)
        # We will keep the browser open and wait for instructions via stdin
        while True:
            cmd = sys.stdin.readline().strip()
            if cmd == "quit":
                break
            elif cmd == "screenshot":
                page.screenshot(path="screenshot.png")
                print("Screenshot saved.", flush=True)
            elif cmd.startswith("eval"):
                code = cmd[4:].strip()
                try:
                    result = page.evaluate(code)
                    print(f"Result: {result}", flush=True)
                except Exception as e:
                    print(f"Error: {e}", flush=True)
            elif cmd.startswith("click"):
                selector = cmd[5:].strip()
                try:
                    page.click(selector)
                    print(f"Clicked {selector}", flush=True)
                except Exception as e:
                    print(f"Error: {e}", flush=True)
            elif cmd.startswith("fill"):
                # format: fill SELECTOR | TEXT
                parts = cmd[4:].strip().split("|", 1)
                if len(parts) == 2:
                    try:
                        page.fill(parts[0].strip(), parts[1].strip())
                        print(f"Filled {parts[0].strip()}", flush=True)
                    except Exception as e:
                        print(f"Error: {e}", flush=True)
            elif cmd.startswith("upload"):
                parts = cmd[6:].strip().split("|", 1)
                if len(parts) == 2:
                    try:
                        page.set_input_files(parts[0].strip(), parts[1].strip())
                        print(f"Uploaded {parts[1].strip()} to {parts[0].strip()}", flush=True)
                    except Exception as e:
                        print(f"Error: {e}", flush=True)
            elif cmd == "html":
                print(page.content(), flush=True)
            else:
                print("Unknown command. Supported: quit, screenshot, eval JS_CODE, click SELECTOR, fill SELECTOR | TEXT, html", flush=True)

        print("Closing browser...")
        browser.close()

if __name__ == "__main__":
    main()
