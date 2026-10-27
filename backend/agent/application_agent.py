# ============================================================
# JOBSPHERE - APPLICATION AGENT
# ============================================================
#
# Purpose:
# 1. Open a job/application page.
# 2. Analyze the page and application form.
# 3. Detect login and human-verification/security pages.
# 4. Detect standard application fields.
# 5. Never bypass CAPTCHA/Cloudflare/security controls.
# 6. Never click the final application Submit button.
#
# Usage:
#   python agent\application_agent.py "<JOB_URL>"
#
# Example:
#   python agent\application_agent.py "http://127.0.0.1:8000/frontend/test_application.html"
#
# ============================================================

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import sys
import json
import time


DEFAULT_WAIT_SECONDS = 20


# ============================================================
# DETECTION WORDS
# ============================================================

SUBMIT_WORDS = [
    "submit application",
    "submit",
    "apply now",
    "send application",
    "finish application",
    "complete application",
]

LOGIN_WORDS = [
    "sign in",
    "login",
    "log in",
    "create account",
    "register",
]

HUMAN_VERIFICATION_WORDS = [
    "captcha",
    "verify you are human",
    "verify you're human",
    "verification required",
    "human verification",
    "security check",
    "checking your browser",
    "just a moment",
    "cloudflare",
    "turnstile",
    "not a bot",
    "i'm not a robot",
    "im not a robot",
]

FIELD_PATTERNS = {
    "full_name": [
        "full_name",
        "fullname",
        "name",
        "first_name",
        "firstname",
    ],
    "email": [
        "email",
        "email_address",
        "emailaddress",
    ],
    "phone": [
        "phone",
        "phone_number",
        "mobile",
        "mobile_number",
        "telephone",
    ],
    "experience": [
        "experience",
        "years_experience",
        "work_experience",
        "years_of_experience",
    ],
    "skills": [
        "skills",
        "technical_skills",
        "skill",
    ],
    "location": [
        "location",
        "city",
        "address",
        "current_location",
    ],
    "cover_letter": [
        "cover_letter",
        "coverletter",
        "cover",
        "message",
        "additional_information",
    ],
    "resume": [
        "resume",
        "cv",
        "curriculum_vitae",
    ],
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def normalize_text(value):
    if not value:
        return ""

    return " ".join(
        str(value).lower().split()
    )


def get_attribute(element, attribute):
    try:
        value = element.get_attribute(attribute)

        if value:
            return value.strip()

    except Exception:
        pass

    return ""


# ============================================================
# HUMAN VERIFICATION DETECTION
# ============================================================

def detect_human_verification(page, title, body_text):
    """
    Detect common human-verification/security pages.

    Important:
    This function only DETECTS verification.
    It does not attempt to solve, bypass, or automate it.
    """

    title_text = normalize_text(title)
    body_text = normalize_text(body_text)

    # --------------------------------------------------------
    # Text indicators
    # --------------------------------------------------------

    for word in HUMAN_VERIFICATION_WORDS:

        if word in title_text or word in body_text:

            return True, word

    # --------------------------------------------------------
    # Cloudflare Turnstile response field
    # --------------------------------------------------------

    try:

        turnstile_count = page.locator(
            "input[name='cf-turnstile-response']"
        ).count()

        if turnstile_count > 0:

            return (
                True,
                "Cloudflare Turnstile detected"
            )

    except Exception:
        pass

    # --------------------------------------------------------
    # Cloudflare challenge selectors
    # --------------------------------------------------------

    challenge_selectors = [
        "#cf-chl-widget",
        "[name='cf-turnstile-response']",
        ".cf-turnstile",
        "iframe[src*='challenges.cloudflare.com']",
        "iframe[title*='Cloudflare']",
    ]

    for selector in challenge_selectors:

        try:

            count = page.locator(
                selector
            ).count()

            if count > 0:

                return (
                    True,
                    f"Security verification element detected: {selector}"
                )

        except Exception:
            pass

    return False, ""


# ============================================================
# PAGE ANALYZER
# ============================================================

def analyze_page(page):

    print()
    print("=" * 60)
    print("JOBSPHERE APPLICATION PAGE ANALYSIS")
    print("=" * 60)

    title = page.title()
    current_url = page.url

    print()
    print("PAGE TITLE:")
    print(title)

    print()
    print("CURRENT URL:")
    print(current_url)

    # --------------------------------------------------------
    # BODY TEXT
    # --------------------------------------------------------

    try:

        body_text = normalize_text(
            page.locator("body").inner_text()
        )

    except Exception:

        body_text = ""

    # --------------------------------------------------------
    # LOGIN DETECTION
    # --------------------------------------------------------

    login_detected = False

    for word in LOGIN_WORDS:

        if word in body_text:

            login_detected = True
            break

    # --------------------------------------------------------
    # HUMAN VERIFICATION DETECTION
    # --------------------------------------------------------

    human_verification_required, verification_reason = (
        detect_human_verification(
            page,
            title,
            body_text
        )
    )

    # --------------------------------------------------------
    # FORM DETECTION
    # --------------------------------------------------------

    forms = page.locator("form")

    try:

        form_count = forms.count()

    except Exception:

        form_count = 0

    print()
    print("FORMS FOUND:")
    print(form_count)

    # --------------------------------------------------------
    # INPUT / SELECT / TEXTAREA DETECTION
    # --------------------------------------------------------

    inputs = page.locator(
        "input, textarea, select"
    )

    try:

        input_count = inputs.count()

    except Exception:

        input_count = 0

    print()
    print("FORM ELEMENTS FOUND:")
    print(input_count)

    detected_fields = []

    for index in range(input_count):

        element = inputs.nth(index)

        try:

            tag_name = element.evaluate(
                "(el) => el.tagName.toLowerCase()"
            )

        except Exception:

            tag_name = ""

        field_type = get_attribute(
            element,
            "type"
        )

        name = get_attribute(
            element,
            "name"
        )

        element_id = get_attribute(
            element,
            "id"
        )

        placeholder = get_attribute(
            element,
            "placeholder"
        )

        aria_label = get_attribute(
            element,
            "aria-label"
        )

        field_data = {
            "index": index,
            "tag": tag_name,
            "type": field_type,
            "name": name,
            "id": element_id,
            "placeholder": placeholder,
            "aria_label": aria_label,
        }

        detected_fields.append(
            field_data
        )

    # --------------------------------------------------------
    # PRINT DETECTED FIELDS
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("DETECTED FORM FIELDS")
    print("-" * 60)

    for field in detected_fields:

        print()
        print(
            f"[{field['index']}] "
            f"{field['tag']} "
            f"type={field['type']}"
        )

        if field["name"]:
            print(
                f"    name: {field['name']}"
            )

        if field["id"]:
            print(
                f"    id: {field['id']}"
            )

        if field["placeholder"]:
            print(
                f"    placeholder: {field['placeholder']}"
            )

    # --------------------------------------------------------
    # CLASSIFY APPLICATION FIELDS
    # --------------------------------------------------------

    classified_fields = {}

    for field in detected_fields:

        values_to_check = [
            field["name"],
            field["id"],
            field["placeholder"],
            field["aria_label"],
        ]

        combined = normalize_text(
            " ".join(
                value
                for value in values_to_check
                if value
            )
        )

        for field_name, patterns in FIELD_PATTERNS.items():

            for pattern in patterns:

                if normalize_text(pattern) in combined:

                    if field_name not in classified_fields:

                        classified_fields[field_name] = field

                    break

    # --------------------------------------------------------
    # SUBMIT BUTTON DETECTION
    # --------------------------------------------------------

    buttons = page.locator(
        "button, input[type='submit']"
    )

    try:

        button_count = buttons.count()

    except Exception:

        button_count = 0

    submit_buttons = []

    for index in range(button_count):

        button = buttons.nth(index)

        try:

            text = normalize_text(
                button.inner_text()
            )

        except Exception:

            text = ""

        button_value = get_attribute(
            button,
            "value"
        )

        button_aria = get_attribute(
            button,
            "aria-label"
        )

        combined = normalize_text(
            f"{text} {button_value} {button_aria}"
        )

        is_submit = False

        for word in SUBMIT_WORDS:

            if word in combined:

                is_submit = True
                break

        if is_submit:

            submit_buttons.append({
                "index": index,
                "text": text,
                "value": button_value,
                "aria_label": button_aria,
            })

    # --------------------------------------------------------
    # RESULT OBJECT
    # --------------------------------------------------------

    result = {
        "url": current_url,
        "title": title,
        "forms_found": form_count,
        "form_elements_found": input_count,
        "login_detected": login_detected,
        "human_verification_required": human_verification_required,
        "verification_reason": verification_reason,
        "fields": detected_fields,
        "classified_fields": classified_fields,
        "submit_buttons": submit_buttons,
    }

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("APPLICATION AGENT SUMMARY")
    print("=" * 60)

    print()
    print(
        "Login detected:",
        "YES" if login_detected else "NO"
    )

    print(
        "Human verification:",
        "REQUIRED"
        if human_verification_required
        else "NOT REQUIRED"
    )

    if human_verification_required:

        print(
            "Verification reason:",
            verification_reason
        )

    print(
        "Submit button detected:",
        "YES" if submit_buttons else "NO"
    )

    print()
    print("Classified fields:")

    if classified_fields:

        for field_name, field in classified_fields.items():

            field_identifier = (
                field.get("name")
                or field.get("id")
                or field.get("placeholder")
                or "unknown"
            )

            print(
                f"  ✓ {field_name} -> {field_identifier}"
            )

    else:

        print(
            "  No standard application fields detected."
        )

    return result


# ============================================================
# OPEN APPLICATION PAGE
# ============================================================

def open_application_page(
    url,
    wait_seconds=DEFAULT_WAIT_SECONDS
):

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 900
            }
        )

        page = context.new_page()

        print()
        print("=" * 60)
        print("JOBSPHERE APPLICATION AGENT")
        print("=" * 60)

        print()
        print("Opening application page...")

        try:

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

        except PlaywrightTimeoutError:

            print()
            print(
                "Page loading timed out, "
                "but the page may still be usable."
            )

        except Exception as error:

            print()
            print("Unable to open page.")
            print("Error:", error)

            browser.close()

            return None

        print()
        print("Page opened successfully.")

        # ----------------------------------------------------
        # Wait for dynamic content
        # ----------------------------------------------------

        try:

            page.wait_for_load_state(
                "networkidle",
                timeout=15000
            )

        except Exception:

            pass

        time.sleep(2)

        # ----------------------------------------------------
        # Analyze page
        # ----------------------------------------------------

        result = analyze_page(page)

        # ----------------------------------------------------
        # USER ACTION SECTION
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("USER ACTION REQUIRED")
        print("=" * 60)

        if result["human_verification_required"]:

            print()
            print(
                "⚠ HUMAN VERIFICATION REQUIRED"
            )

            print()
            print(
                "The website requires human verification "
                "before JobSphere can analyze the application page."
            )

            print()
            print(
                "Reason:",
                result["verification_reason"]
            )

            print()
            print(
                "Please complete the verification manually "
                "in the browser if the website permits it."
            )

            print()
            print(
                "JobSphere will NOT bypass or automate "
                "this security verification."
            )

        elif result["login_detected"]:

            print()
            print(
                "Login/sign-in appears to be required."
            )

            print()
            print(
                "Please login manually in the browser."
            )

        else:

            print()
            print(
                "No login or human-verification requirement "
                "was detected."
            )

        print()
        print(
            "JobSphere will NOT automatically bypass "
            "login, CAPTCHA, Cloudflare, or other "
            "security controls."
        )

        print()
        print(
            "JobSphere will NOT click the final "
            "application Submit button."
        )

        # ----------------------------------------------------
        # Keep browser open for manual review
        # ----------------------------------------------------

        print()
        print(
            f"Browser will remain open for "
            f"{wait_seconds} seconds."
        )

        print(
            "Review the page manually."
        )

        print()

        try:

            time.sleep(wait_seconds)

        except KeyboardInterrupt:

            print()
            print(
                "Browser closing..."
            )

        # ----------------------------------------------------
        # Save analysis
        # ----------------------------------------------------

        try:

            with open(
                "application_page_analysis.json",
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    result,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            print()
            print(
                "Analysis saved to:"
            )

            print(
                "application_page_analysis.json"
            )

        except Exception as error:

            print()
            print(
                "Could not save analysis:",
                error
            )

        # ----------------------------------------------------
        # Close browser
        # ----------------------------------------------------

        browser.close()

        print()
        print(
            "Browser closed."
        )

        return result


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print()
        print("=" * 60)
        print("JOBSPHERE APPLICATION AGENT")
        print("=" * 60)

        print()
        print("Usage:")

        print(
            'python agent\\application_agent.py "<JOB_URL>"'
        )

        print()
        print("Example:")

        print(
            'python agent\\application_agent.py '
            '"http://127.0.0.1:8000/frontend/test_application.html"'
        )

        sys.exit(1)

    job_url = sys.argv[1]

    open_application_page(
        job_url
    )
