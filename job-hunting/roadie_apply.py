from playwright.sync_api import sync_playwright
import time

RESUME_PATH = "/Users/sentional/JOB hunting/Untitled Resume - Resume.pdf"
JOB_URL = "https://job-boards.greenhouse.io/roadie/jobs/8431926002"

def click_custom_dropdown(iframe, field_id, value):
    """
    Greenhouse custom dropdowns: click container to open, then click option by text.
    Do NOT use fill() — it filters to 'No options'.
    """
    try:
        container = iframe.locator(f"#{field_id}")
        container.scroll_into_view_if_needed()
        container.click(timeout=5000)
        time.sleep(0.8)
        option = iframe.locator(f"li:has-text('{value}'), .select__option:has-text('{value}'), .choices__item:has-text('{value}')").first
        option.click(timeout=5000)
        print(f"Selected dropdown {field_id} = '{value}'")
    except Exception as e:
        print(f"WARNING: click_custom_dropdown failed for {field_id}: {e}")
        try:
            iframe.locator(f"select#{field_id}").select_option(label=value, timeout=2000)
            print(f"  -> Used standard select fallback for {field_id}")
        except Exception as e2:
            print(f"  -> Fallback also failed: {e2}")

def main():
    with sync_playwright() as p:
        print("Starting Roadie application...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(JOB_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        print("Loaded Roadie careers page")

        iframe = page.frame_locator("#grnhse_iframe")

        # Wait for form
        print("Waiting for form fields...")
        try:
            iframe.locator("#first_name").wait_for(state="visible", timeout=15000)
            print("Form is visible")
        except:
            print("Form not visible — trying to click Apply button first")
            try:
                apply_btn = iframe.locator('a:has-text("Apply"), button:has-text("Apply")').first
                apply_btn.click(timeout=5000)
                time.sleep(2)
                iframe.locator("#first_name").wait_for(state="visible", timeout=10000)
            except Exception as e:
                print(f"Could not get to form: {e}")
                page.screenshot(path="/Users/sentional/JOB hunting/roadie_error.png")
                browser.close()
                return

        # Basic Info
        iframe.locator("#first_name").fill("Oscar")
        iframe.locator("#last_name").fill("Reyes")
        try:
            iframe.locator("#preferred_name").fill("Oscar")
        except: pass
        iframe.locator("#email").fill("manzueta2199@gmail.com")

        # Country dropdown
        click_custom_dropdown(iframe, "country", "United States")
        time.sleep(0.5)

        # Phone
        iframe.locator("#phone").fill("4848900615")
        print("Filled basic info")

        # Location (City) — autocomplete search field
        try:
            location_input = iframe.locator("#candidate-location, input[id*='location'], input[placeholder*='ity']").first
            location_input.click(timeout=3000)
            location_input.fill("Reading, PA")
            time.sleep(1.5)
            # Click first suggestion
            suggestion = iframe.locator("li[role='option'], .pac-item, [class*='suggestion']").first
            suggestion.click(timeout=3000)
            print("Filled location")
        except Exception as e:
            print(f"WARNING: Location field failed: {e}")

        # Resume Upload
        try:
            file_input = iframe.locator('input[type="file"]').first
            file_input.set_input_files(RESUME_PATH)
            time.sleep(3)
            print("Uploaded resume")
        except Exception as e:
            print(f"Failed to upload resume: {e}")

        # LinkedIn
        try:
            iframe.locator("#question_35423328002").fill("https://linkedin.com/in/oscar-reyes-manzueta-713a1a289")
            print("Filled LinkedIn")
        except: pass

        # Referral Source (required)
        try:
            iframe.locator("#question_35423329002").fill("LinkedIn")
            print("Filled referral source")
        except Exception as e:
            print(f"Referral source failed: {e}")

        # State dropdown — Pennsylvania
        click_custom_dropdown(iframe, "question_35423330002", "Pennsylvania")
        time.sleep(0.5)

        # Demographics
        click_custom_dropdown(iframe, "gender", "Male")
        click_custom_dropdown(iframe, "hispanic_ethnicity", "Yes")
        click_custom_dropdown(iframe, "veteran_status", "I am not a protected veteran")
        click_custom_dropdown(iframe, "disability_status", "No, I do not have a disability and have not had one in the past")

        # Debug screenshot
        print("Taking debug screenshot...")
        page.screenshot(path="/Users/sentional/JOB hunting/roadie_debug_presubmit.png")

        # Submit
        print("Clicking submit...")
        try:
            page.keyboard.press("Escape")
            time.sleep(0.5)
            submit_btn = iframe.locator('button[type="submit"]').first
            submit_btn.wait_for(state="visible", timeout=5000)
            for _ in range(10):
                is_disabled = submit_btn.get_attribute("disabled")
                if is_disabled is None:
                    break
                time.sleep(0.5)
            submit_btn.click(timeout=5000)
            print("Clicked submit button")
        except Exception as e:
            print(f"Submit click failed: {e}")

        print("Waiting for submission result...")
        time.sleep(10)

        page.screenshot(path="/Users/sentional/JOB hunting/roadie_result.png")
        print("Screenshot saved to roadie_result.png")

        browser.close()

if __name__ == "__main__":
    main()
