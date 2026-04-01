from playwright.sync_api import sync_playwright
import time

RESUME_PATH = "/Users/sentional/JOB hunting/Untitled Resume - Resume.pdf"
JOB_URL = "https://job-boards.greenhouse.io/exiger/jobs/5751719004"

def click_custom_dropdown(iframe, field_id, value):
    """
    Custom dropdowns (Greenhouse): click the container to open,
    then click the option by visible text. Do NOT use fill() — it filters to 'No options'.
    """
    try:
        # Click the dropdown container/arrow to open the menu
        container = iframe.locator(f"#{field_id}")
        container.scroll_into_view_if_needed()
        container.click(timeout=5000)
        time.sleep(0.8)
        # Click the option matching the value text
        option = iframe.locator(f".select__option:has-text('{value}'), .choices__item:has-text('{value}'), li:has-text('{value}')").first
        option.click(timeout=5000)
        print(f"Selected dropdown {field_id} = '{value}'")
    except Exception as e:
        print(f"WARNING: click_custom_dropdown failed for {field_id}: {e}")
        # Fallback: try standard select
        try:
            iframe.locator(f"select#{field_id}").select_option(label=value, timeout=2000)
            print(f"  -> Used standard select fallback for {field_id}")
        except Exception as e2:
            print(f"  -> Fallback also failed: {e2}")


def main():
    with sync_playwright() as p:
        print(f"Starting Exiger application...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(JOB_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        print("Loaded Exiger careers page")

        iframe = page.frame_locator("#grnhse_iframe")

        # Click Apply if needed
        try:
            apply_button = iframe.locator('button[aria-label="Apply"], button:has-text("Apply")').first
            if apply_button.is_visible(timeout=3000):
                print("Clicking Apply button...")
                apply_button.click()
                time.sleep(3)
        except:
            print("Apply button not found or already on form")

        # Wait for form
        print("Waiting for form fields...")
        try:
            iframe.locator("#first_name").wait_for(state="visible", timeout=10000)
            print("Form is visible")
        except:
            print("Form not visible after timeout")
            page.screenshot(path="/Users/sentional/JOB hunting/exiger_error.png")
            browser.close()
            return

        # Basic Info
        iframe.locator("#first_name").fill("Oscar")
        iframe.locator("#last_name").fill("Reyes")
        iframe.locator("#email").fill("manzueta2199@gmail.com")
        
        # Phone Country
        click_custom_dropdown(iframe, "country", "United States")
        iframe.locator("#phone").fill("4848900615")
        print("Filled basic info")

        # Resume Upload
        try:
            file_input = iframe.locator('input[type="file"]#resume')
            if not file_input.is_visible():
                file_input = iframe.locator('input[type="file"]').first
            file_input.set_input_files(RESUME_PATH)
            print("Uploaded resume")
        except Exception as e:
            print(f"Failed to upload resume: {e}")

        # LinkedIn
        try:
            iframe.locator("#question_14984795004").fill("https://linkedin.com/in/oscar-reyes-manzueta-713a1a289")
            print("Filled LinkedIn")
        except: pass

        # Website
        try:
            iframe.locator("#question_14984796004").fill("https://oscar-s-portfolio-1094785770988.us-west1.run.app")
            print("Filled Website")
        except: pass

        # US Citizen?
        click_custom_dropdown(iframe, "question_14984797004", "Yes")
        # Authorized?
        click_custom_dropdown(iframe, "question_14984798004", "Yes")
        # Require sponsorship?
        click_custom_dropdown(iframe, "question_14984799004", "No")

        # Demographics
        click_custom_dropdown(iframe, "gender", "Male")
        click_custom_dropdown(iframe, "hispanic_ethnicity", "Yes")
        click_custom_dropdown(iframe, "veteran_status", "I am not a protected veteran")
        click_custom_dropdown(iframe, "disability_status", "No, I do not have a disability and have not had one in the past")

        # Submit
        print("Taking debug screenshot...")
        page.screenshot(path="/Users/sentional/JOB hunting/exiger_debug_presubmit.png")
        
        print("Clicking submit...")
        try:
            # Close any open dropdown first (press Escape)
            page.keyboard.press("Escape")
            time.sleep(0.5)
            submit_btn = iframe.locator('button[type="submit"]').first
            # Wait for it to be enabled (all required fields are valid)
            submit_btn.wait_for(state="visible", timeout=5000)
            for _ in range(10):  # retry up to 10 times
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
        
        # Take final screenshot
        page.screenshot(path="/Users/sentional/JOB hunting/exiger_result.png")
        print("Screenshot saved to exiger_result.png")

        browser.close()

if __name__ == "__main__":
    main()
