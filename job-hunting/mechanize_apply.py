from playwright.sync_api import sync_playwright

RESUME_PATH = "/Users/sentional/JOB hunting/Untitled Resume - Resume.pdf"

def fill_react_input(page, selector, value):
    """Fill a React-controlled input, triggering its onChange handler."""
    el = page.locator(selector).first
    el.click()
    el.fill(value)
    el.evaluate("el => el.dispatchEvent(new Event('input', {bubbles:true}))")
    el.evaluate("el => el.dispatchEvent(new Event('change', {bubbles:true}))")

def main():
    with sync_playwright() as p:
        print("Starting Playwright headed test...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://jobs.ashbyhq.com/mechanize/d148d54f-6db7-4c28-9699-0304596f554e")
        page.wait_for_load_state("networkidle")
        print("Navigated to Mechanize Ashby page")

        # Click 'Apply for this Job' to reveal the form
        try:
            page.click('text="Apply for this Job"', timeout=5000)
            page.wait_for_timeout(1500)
            print("Clicked Apply for this Job")
        except:
            print("Apply button not found, form may already be visible")

        # --- RESUME UPLOAD ---
        # Ashby hides the file input via CSS - we reveal it first
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
        page.wait_for_timeout(1000)
        print("Uploaded resume")

        # Fill name and email - page.fill() properly triggers React events
        fill_react_input(page, '[name="_systemfield_name"]', 'Oscar Reyes')
        fill_react_input(page, '[name="_systemfield_email"]', 'manzueta2199@gmail.com')
        print("Filled contact info")

        # Fill GitHub link
        fill_react_input(page, '[name="340652e6-73ac-411d-b5ca-5bb514690a2e"]', 'https://github.com/0scarxmz')

        # Fill 100-word essay
        essay = "I used to believe that building complex, full-stack applications required a massive team and months of specialized backend development. However, my experience building RISE, a complete AI creator platform, changed my mind empirically. By leveraging modern BaaS solutions like Supabase alongside Next.js and serverless APIs, I discovered that a single developer can architect secure authentication, complex media storage, and real-time database workflows in mere weeks. The empirical data of my deployment velocity proved that architectural complexity has shifted from writing boilerplate backend code to effectively composing managed cloud services, drastically democratizing software development for small ambitious teams."
        fill_react_input(page, '[name="73e68f0c-ce52-4802-8db0-69771ea2178c"]', essay)
        print("Filled custom text answers via React-compatible events")

        # Click Yes on Yes/No toggle questions
        # Ashby embeds Yes/No as styled buttons, not labels
        page.wait_for_timeout(500)
        yes_count = 0
        for btn in page.locator('button').all():
            try:
                txt = btn.inner_text(timeout=300).strip()
                if txt == 'Yes':
                    btn.click()
                    yes_count += 1
                    page.wait_for_timeout(200)
            except:
                pass
        print(f"Clicked Yes on {yes_count} questions")

        # Submit the form
        page.wait_for_timeout(500)
        submitted = False
        for btn in page.locator('button').all():
            try:
                if 'Submit' in btn.inner_text(timeout=300):
                    btn.click()
                    submitted = True
                    print("Clicked Submit Application!")
                    break
            except:
                pass
        if not submitted:
            page.evaluate("document.querySelector('button[type=submit]') && document.querySelector('button[type=submit]').click()")
            print("Submitted via JS fallback")

        # Wait for result and take screenshot
        page.wait_for_timeout(5000)
        page.screenshot(path="/Users/sentional/JOB hunting/application_result.png")
        print("Screenshot saved to application_result.png")

        input("Press Enter to close the browser...")
        browser.close()

if __name__ == "__main__":
    main()
