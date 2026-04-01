---
name: job-hunting
description: Use this skill whenever the user wants to apply to a job online, automate filling out job applications, or streamline their job hunt. This skill provides explicit instructions on how to parse job forms, automatically fill them using the user's resume, and dynamically update the resume when encountering new or unexpected questions. Make sure to trigger this anytime the user mentions applying to a link, filling out an application, or automating a job submission.
---

# Job Hunting Automation

This skill automates the process of filling out and submitting online job applications. The goal is to act as a relentless assistant that handles the tedious data entry of job hunting.

---

## 🔴 MANDATORY RULES (Follow Every Time, No Exceptions)

### Rule 1: Always Read `resume.md` First
**BEFORE filling in ANY form field**, you MUST open and read `/Users/sentional/JOB hunting/resume.md` in full. This is your only source of truth. Do not guess, assume, or generate answers for fields that already exist in this file. Cross-reference every single field against `resume.md` before typing anything.

### Rule 2: STOP and Ask If Information Is Missing
If you encounter a form field that requires information **not already present in `resume.md`**:
1. **STOP the current task immediately.**
2. **Notify the user** using `notify_user` — ask them exactly what to put in that field.
3. **Wait for their answer.**
4. **Update `resume.md`** with the new answer in the appropriate section.
5. **Resume the application** from where you left off.

> ⚠️ Do NOT invent, guess, or generate fake answers for factual fields (e.g., GPA, graduation year, location). Only generate answers if the field is clearly an open-ended essay/behavioral question AND the user cannot provide info in time.

### Rule 3: Always Be Careful With Dropdown Arrows (Custom Selects)
Many ATS platforms (Greenhouse, Ashby, Workday, etc.) use **custom dropdown components** — they look like a box with a dropdown arrow (▼) but are NOT standard HTML `<select>` elements. Using `select_option()` or `fill()` on these will silently fail.

**You MUST handle custom dropdowns like this:**
1. **Click the dropdown container** (the visible box or arrow icon) to open the options menu.
2. **Wait** for the options list to appear in the DOM (use `wait_for` or a short sleep).
3. **Click the specific option text** you want from the list.
   - Example Playwright: `iframe.locator(".select-option:has-text('Yes')").first.click()`
   - Or use `page.get_by_text("Yes").click()` if the option is in the page context.
4. **Verify** the selection visually (take a screenshot if in debug mode).

Never use `select_option()` on custom div-based dropdowns — it won't work.

### Rule 4: Update This Skill With Every New User Directive
Every time the user gives you a new instruction or rule about how to apply to jobs, you MUST append it to this file immediately. The skill should always reflect the most up-to-date instructions. Do this before resuming the task.

### Rule 5: Verify Job Listings In A Real Browser Before Queueing Them
When searching for jobs, do not trust a raw link, search snippet, or memory alone. Use Playwright to open the live posting in a real browser before adding it to the queue or attempting an application.

The posting is only queue-worthy if the browser confirms one of these on the same date it is added:
1. An active application form is present.
2. A live ATS posting page is present with an apply/start application control.
3. The official company careers page clearly shows the role as open.

If the browser shows `job not found`, `no longer open`, `404`, expired status, or a broken redirect, do not add it as pending. Mark it skipped or leave it out of the queue.

---

## Core Directives

1. **Relentless Execution:**
   - Once you start an application, **DO NOT STOP** unless:
     - You hit a CAPTCHA you cannot solve.
     - You hit a security verification code (email/SMS) — notify the user.
     - **You are missing required information not in `resume.md`** — STOP and ask.
     - You successfully submit the application.

2. **Source of Truth (`resume.md`):**
   - The user's `resume.md` file at `/Users/sentional/JOB hunting/resume.md` is the **only** source of truth for all personal information, experience, demographics, links, and work authorization.
   - Read this file at the START of every application. Do not skip this step.

3. **Dynamic Resume Updating:**
   - If a behavioral/essay question is NOT in `resume.md`:
     1. Generate a professional, high-quality answer using the STAR method.
     2. Append the Q&A to the `## Additional Q&A` section of `resume.md`.
     3. Fill the form field with the generated answer.

---

## Workflow

When asked to apply to a job (usually provided as a URL):

1. **Read `resume.md` first** — mandatory before doing anything else.

2. **If Searching For Jobs, Verify The Listing First:**
   - Use Playwright to open the live posting in the browser before queueing it.
   - Prefer official company careers pages and official ATS pages such as Greenhouse, Lever, Ashby, Workday, SmartRecruiters, RippleMatch, or Handshake.
   - Treat third-party aggregators only as breadcrumbs. Never trust them as the final source of truth unless they lead to a verified official posting.
   - Only mark a role `⏸️ Pending` after the browser confirms it is currently live.
   - Keep the active queue clean: when a role becomes `✅ Submitted` or `⏭️ Skipped`, remove it from any pending-only list so stale links do not remain in the working queue.

3. **Navigate to the Application:**
   - Use Playwright (headed mode for CAPTCHAs, headless for silent runs).
   - Navigate to the provided job URL and wait for full page load.

4. **Form Parsing & Filling:**
   - Inspect the DOM to identify all form fields.
   - Cross-reference `resume.md` for every field value before filling.
   - **Handling Custom Dropdowns (▼):** These are NOT standard `<select>` elements.
     1. Click the dropdown container to open the list.
     2. Wait for options to appear.
     3. Click the target option by text.
   - For file uploads (resume PDF), locate `/Users/sentional/JOB hunting/Untitled Resume - Resume.pdf` and use `set_input_files()`.
   - Wait after resume upload (at least 3 seconds) before submitting, to avoid race conditions.

5. **Handling Missing Information:**
   - STOP, notify user, get the answer, update `resume.md`, then continue.

6. **Submission:**
   - Click "Next", "Continue", or "Submit Application" as needed.
   - Do NOT ask permission to proceed between pages.
   - After submit, wait 5-10 seconds and take a screenshot for verification.

7. **Stopping Conditions:**
   - **SUCCESS:** "Thank you for applying" or confirmation page → notify user.
   - **CAPTCHA / BLOCKER:** Notify user, ask them to clear it.
   - **Security Code (email/SMS):** Notify user, ask for the code.
   - **Missing required info:** Notify user, wait for answer, then continue.

8. **Tracker Logging:**
   - Upon successful submission, open `job_applications.csv` (create if missing with headers: `Date, Company, Job Title, URL, Status`).
   - Append: current date, company name, job title, URL, status = "Applied".
   - Also update `jobs_tracker.md` if it exists.

---

## Writing Style & Professionalism

When generating answers for behavioral/essay questions:
- Highly professional, concise, and impact-driven.
- Keep answers short by default: usually 2 to 4 sentences unless the prompt clearly asks for more detail.
- Use plain, natural language that does not sound overproduced or overly polished.
- Use the STAR method lightly when helpful, not as a rigid long-form structure.
- Reflect Oscar's actual experience: vibe-coding projects with React/Next.js/TypeScript/Python, no formal job experience, self-taught.
- Don't oversell — keep it realistic for an entry-level intern with strong personal projects.
- Default to `RISE` as the main project example when a prompt asks about a project Oscar is proud of, a project highlight, or a build he wants to discuss.
- Do not switch to side projects, portfolio work, or invented project variants unless the prompt clearly requires a different example.
- Never describe personal projects as work experience, employment, company experience, or team experience. If the user has no formal job history, say so plainly and refer only to `project experience` or `personal projects`.

---

## User Directives

- Use Playwright for job application automation in this workspace.
- If any required answer is missing or unclear, stop and ask the user before proceeding.
- After the user provides a new answer, add it to `/Users/sentional/JOB hunting/resume.md` in the appropriate section before continuing so future applications can reuse it.
- When building a target list, classify jobs using the user's difficulty system:
  - `Easy`: startup-leaning roles with the highest hiring probability for the user's profile, especially frontend/full-stack roles aligned with React/Next.js/TypeScript.
  - `Medium`: non-FAANG companies and mid-tier roles that are still realistic for the user's profile and are not unusually high-paying.
  - `Hard`: FAANG/MANGO-level companies, unusually high-bar roles, hardware/C++-heavy roles, or roles paying over roughly $40/hour.
- Prioritize only `Easy` and `Medium` roles unless the user explicitly asks to include `Hard` roles.
- If a role is marked `Hard`, deprioritize it, skip it in the active queue, and move on to the next `Easy` or `Medium` role unless the user explicitly asks to revisit it.
- If a role is already in the tracked queue and the user explicitly says to continue because it is easy to apply, proceed with the application even if the role would otherwise fall into the `Hard` bucket.
- If an application would require entering false or misleading factual information to proceed, skip that role instead of guessing or lying.
- If a role is blocked on new required factual questions and the user says to continue to the next one, leave the blocked role unsubmitted, keep moving through the queue, and revisit it later only if the user wants to.
- For questions asking whether the user is related to anyone at the company or on the board, answer `No`; if the form requires free text, enter `N/A`.
- For questions about prior formal job experience, answer `No` unless the user later adds real employment history to `resume.md`.
- For salary requirement questions, default to a flexible answer such as `Negotiable` or `Open to the company's standard intern compensation`, unless the user later gives a specific numeric minimum.
- When a form has multiple truthful options, choose the most favorable truthful answer that still matches the user's actual status. For future/expected degree questions, use the planned transfer path in `resume.md`; for current-enrollment or current-experience questions, answer with the current truth and skip the role if the form only works by misrepresenting it.
- When a form requires a numeric hourly expectation, prefer `25`; if the role's posted pay band is lower or a lower number is the only realistic option, `20` is acceptable.
- When searching for jobs to add to the queue, verify each listing in Playwright first instead of trusting raw links or memory. Use official ATS/careers pages as the source of truth, and only keep truly live roles in the pending queue.
- Focus on internship roles for students. Do not queue or apply to full-time, new-grad, or experienced-hire roles unless the user explicitly asks for them.
- Focus on real software engineering experience: prioritize software engineer, full-stack, frontend, web development, and closely related internship titles. Avoid adjacent non-SWE roles such as product analyst, digital intern, generic business intern, or ML-only roles unless the user explicitly wants them.
- Prioritize fresh postings. Only search and queue jobs that were posted within the last 48 hours. Strongly prefer same-day or 1-day-old listings, and treat anything older than 2 days as stale unless the user explicitly asks for it.
- When searching, assume older posts are more likely to be full or ghosted. If a job looks old, crowded, expired, or otherwise stale, do not add it to the active queue.
- Default search order: `Easy` internships first, then a small number of realistic `Medium` internships if the easy pool is thin.
- Do not queue or apply to `Hard` roles by default, even if the application looks quick. Only proceed on a `Hard` role when the user explicitly opts in for that specific role.
- When presenting fresh search results, freshness is not enough by itself. Exclude any role that appears `Hard`, prestige-heavy, high-pay, hardware-heavy, or otherwise high-bar. If difficulty is uncertain, do not surface the role until it is verified as `Easy` or `Medium`.
- Treat unusually high-pay, prestige-heavy, hardware-heavy, C++-heavy, or LeetCode-style high-bar roles as poor first-experience targets and skip them unless the user explicitly asks to revisit them.
- Do not apply twice to duplicate-looking roles at the same company without explicit user approval. If the company, title, location, and internship program are substantially the same, treat the second posting as a duplicate even if it has a different requisition ID or team name. Pause and ask before submitting a second application to the same company.
- Keep generated descriptions and essay answers shorter so they feel natural and not obviously AI-written.
- Use `RISE` as the default proud project answer unless the user explicitly says otherwise.
- Be especially careful with any field about work history or experience: the user has no formal work experience, so do not imply prior employment.
