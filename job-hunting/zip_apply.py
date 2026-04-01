from playwright.sync_api import sync_playwright

RESUME_PATH = "/Users/sentional/JOB hunting/Untitled Resume - Resume.pdf"
JOB_URL = "https://jobs.ashbyhq.com/zip/d404b517-9b02-4206-b49e-5c2986603baa/application"

def fill_react_input(page, selector, value):
    """Fill a React-controlled input by triggering synthetic events."""
    el = page.locator(selector).first
    el.click()
    el.fill(value)
    el.evaluate("el => el.dispatchEvent(new Event('input', {bubbles:true}))")
    el.evaluate("el => el.dispatchEvent(new Event('change', {bubbles:true}))")

def click_button_with_text(page, text, exact=True):
    """Click the first button or radio option matching the given text."""
    try:
        page.get_by_text(text, exact=exact).first.click(timeout=3000)
        print(f"  Clicked: '{text}'")
        page.wait_for_timeout(300)
        return True
    except:
        pass
    # Fallback: loop all buttons
    for btn in page.locator('button').all():
        try:
            if (exact and btn.inner_text(timeout=300).strip() == text) or \
               (not exact and text.lower() in btn.inner_text(timeout=300).lower()):
                btn.click()
                print(f"  Clicked (fallback): '{text}'")
                page.wait_for_timeout(300)
                return True
        except:
            pass
    print(f"  WARNING: Could not find '{text}'")
    return False

def main():
    with sync_playwright() as p:
        print("Starting Zip application...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(JOB_URL)
        page.wait_for_load_state("networkidle")
        print("Loaded Zip Ashby form")

        # --- RESUME UPLOAD ---
        page.evaluate("""
            const resumeInput = document.getElementById('_systemfield_resume');
            if (resumeInput) {
                resumeInput.style.display = 'block';
                resumeInput.style.opacity = '1';
                resumeInput.style.position = 'relative';
                resumeInput.style.visibility = 'visible';
                resumeInput.style.zIndex = '9999';
            }
        """)
        page.locator('#_systemfield_resume').set_input_files(RESUME_PATH)
        # Wait for Ashby to finish uploading (10 seconds to be absolutely safe)
        print("Waiting 10 seconds for resume upload to complete on Ashby's end...")
        page.wait_for_timeout(10000)
        print("Resume upload complete")

        # Core contact fields
        fill_react_input(page, '[name="_systemfield_name"]', 'Oscar Reyes')
        fill_react_input(page, '[name="_systemfield_email"]', 'manzueta2199@gmail.com')
        fill_react_input(page, '[name="cbfc2c7b-104c-416e-a680-34ea932124e7"]', '4848900615')
        print("Filled name, email, phone")

        # LinkedIn
        fill_react_input(page, '[name="180746a2-599b-48d3-9fc4-505b2279d086"]', 'https://linkedin.com/in/oscar-reyes-manzueta-713a1a289')
        print("Filled LinkedIn")

        # Education
        fill_react_input(page, '[name="5a7e6c02-0a55-4810-a419-d0a99e71d92e"]', 'Reading Area Community College')
        fill_react_input(page, '[name="9bdc5825-ce09-49c4-8bcd-99a8c5e55b20"]', 'Computer Science / Information Technology')
        print("Filled college and major")

        # Expected graduation date (combobox — type and pick)
        try:
            grad_field = page.locator('[placeholder="Start typing..."]').first
            grad_field.click()
            grad_field.type('2027', delay=80)
            page.wait_for_timeout(500)
            page.get_by_text('Spring 2027', exact=False).first.click(timeout=2000)
            print("Selected graduation date: Spring 2027")
        except:
            try:
                page.get_by_text('2027', exact=False).first.click(timeout=2000)
                print("Selected graduation date: 2027")
            except:
                print("WARNING: Could not set graduation date")

        # SMS Consent — Yes
        print("Answering SMS consent...")
        click_button_with_text(page, 'Yes - I consent to receiving text messages')

        # Office willingness — Yes
        print("Answering office willingness...")
        click_button_with_text(page, 'Yes I am willing to come into the office')

        # How did you hear about Zip? — LinkedIn
        print("Selecting referral source...")
        click_button_with_text(page, 'LinkedIn', exact=True)

        # US Work Authorization — Yes
        print("Answering work authorization...")
        click_button_with_text(page, 'Yes', exact=True)

        # Sponsorship — No
        print("Answering sponsorship...")
        click_button_with_text(page, 'No', exact=True)

        # Submit with retries to handle Ashby's async file upload delays
        print("Attempting to submit...")
        submitted_successfully = False
        for attempt in range(10):
            page.wait_for_timeout(1000)
            
            # Click submit
            clicked = False
            for btn in page.locator('button').all():
                try:
                    txt = btn.inner_text(timeout=300).strip()
                    if 'Submit' in txt:
                        btn.click(force=True)
                        clicked = True
                        print(f"  Attempt {attempt+1}: Clicked Submit Application")
                        break
                except:
                    pass
            if not clicked:
                page.evaluate("document.querySelector('button[type=submit]') && document.querySelector('button[type=submit]').click()")
                print(f"  Attempt {attempt+1}: Submitted via JS fallback")
                
            page.wait_for_timeout(3000)
            
            # Check for success
            if "success" in page.content().lower() and "submitted" in page.content().lower():
                print("✅ Success banner detected!")
                submitted_successfully = True
                break
                
            print("  Still waiting for submission to go through...")
                
        if not submitted_successfully:
            print("❌ Failed to detect successful submission after retries.")

        # Wait and screenshot
        page.wait_for_timeout(3000)
        page.screenshot(path="/Users/sentional/JOB hunting/zip_result.png")
        print("Screenshot saved to zip_result.png")

        input("Press Enter to close the browser...")
        browser.close()

if __name__ == "__main__":
    main()
