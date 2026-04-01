from playwright.sync_api import sync_playwright

RESUME_PATH = "/Users/sentional/JOB hunting/Untitled Resume - Resume.pdf"
JOB_URL = "https://jobs.ashbyhq.com/gigaml/aa903645-854f-4404-9d49-8a96f0dcc2cc/application"

def fill_react_input(page, selector, value):
    """Fill a React-controlled input by triggering the synthetic events."""
    el = page.locator(selector).first
    el.click()
    el.fill(value)
    el.evaluate("el => el.dispatchEvent(new Event('input', {bubbles:true}))")
    el.evaluate("el => el.dispatchEvent(new Event('change', {bubbles:true}))")

def main():
    with sync_playwright() as p:
        print("Starting GigaML application...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(JOB_URL)
        page.wait_for_load_state("networkidle")
        print("Loaded GigaML Ashby form")

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
        page.wait_for_timeout(1000)
        print("Uploaded resume")

        # Fill name and email
        fill_react_input(page, '[name="_systemfield_name"]', 'Oscar Reyes')
        fill_react_input(page, '[name="_systemfield_email"]', 'manzueta2199@gmail.com')
        print("Filled contact info")

        # Fill the open-ended essay
        essay = (
            "I am a bilingual (English/Spanish) CS student with hands-on full-stack "
            "experience, having built RISE — a complete AI creator monetization platform "
            "using Next.js, Supabase, and Stripe. I am passionate about machine learning "
            "infrastructure and excited to contribute to GigaML's mission of scaling AI "
            "systems. I am a fast learner, work well in small teams, and thrive in "
            "high-velocity startup environments."
        )
        fill_react_input(page, '[name="80819a7e-5472-4d7f-bf8e-cc006d8a798a"]', essay)
        print("Filled essay")

        # Click Yes on Yes/No toggle questions
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
        print(f"Clicked Yes on {yes_count} toggle questions")

        # "Are you able to work in-person in San Francisco, CA?"
        # Oscar is in Reading, PA so select the relocation option
        page.wait_for_timeout(300)
        relocation_selected = False
        try:
            # Try get_by_text which does partial match across any element type
            page.get_by_text('open to relocation', exact=False).first.click(timeout=3000)
            relocation_selected = True
            print("Selected relocation option via get_by_text")
        except:
            pass
        if not relocation_selected:
            # Fallback: find any clickable element containing 'relocation'
            for el in page.locator('[role="button"], button, div[tabindex]').all():
                try:
                    if 'relocation' in el.inner_text(timeout=300).lower():
                        el.click()
                        relocation_selected = True
                        print("Selected relocation via fallback")
                        break
                except:
                    pass
        if not relocation_selected:
            print("WARNING: Could not find relocation option")

        # Submit
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

        # Wait and screenshot
        page.wait_for_timeout(5000)
        page.screenshot(path="/Users/sentional/JOB hunting/gigaml_result.png")
        print("Screenshot saved to gigaml_result.png")

        input("Press Enter to close the browser...")
        browser.close()

if __name__ == "__main__":
    main()
