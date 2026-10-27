import requests
from playwright.sync_api import sync_playwright
from pathlib import Path


# =========================================================
# SETTINGS
# =========================================================

API_URL = "http://127.0.0.1:8000/analyze-cv"

FORM_URL = (
    "http://127.0.0.1:8000/"
    "frontend/test_application.html"
)

RESUME_PATH = (
    Path(__file__).parent.parent
    / "uploads"
    / "Farhan_resume.pdf"
)


# =========================================================
# GET PROFILE FROM CV ANALYZER
# =========================================================

def get_profile_from_cv():

    print("\n===== CV PROFILE ANALYSIS =====")

    if not RESUME_PATH.exists():
        print("Resume not found:")
        print(RESUME_PATH)
        return None

    try:

        with open(
            RESUME_PATH,
            "rb"
        ) as resume_file:

            response = requests.post(
                API_URL,
                files={
                    "file": (
                        RESUME_PATH.name,
                        resume_file,
                        "application/pdf"
                    )
                },
                timeout=60
            )

        response.raise_for_status()

        data = response.json()

        print("CV analyzed successfully.")

        return data

    except Exception as error:

        print("CV analysis failed:")
        print(error)

        return None


def extract_name_fallback(cv_text):
    """Try to find a likely candidate name near the top of extracted CV text."""
    if not isinstance(cv_text, str) or not cv_text.strip():
        return ""

    ignored_lines = {
        "resume", "curriculum vitae", "professional summary",
        "profile", "objective", "contact", "contact information",
        "education", "experience", "technical skills", "skills",
        "projects", "certifications", "work experience",
    }

    for raw_line in cv_text.splitlines()[:25]:
        line = " ".join(raw_line.strip().split())
        if not line or line.lower().strip(":- ") in ignored_lines:
            continue
        if "@" in line or any(ch.isdigit() for ch in line):
            continue
        words = line.split()
        if not 2 <= len(words) <= 4:
            continue
        # Accept ordinary name-like words; reject lines containing symbols/URLs.
        if all(
            word.replace(".", "").replace("'", "").replace("-", "").isalpha()
            for word in words
        ):
            candidate = " ".join(word.strip(".,:;") for word in words)
            if candidate and candidate.lower().strip() not in ignored_lines:
                return candidate
    return ""


# =========================================================
# FILL APPLICATION FORM
# =========================================================

def fill_application_form(url):

    profile = get_profile_from_cv()

    if not profile:
        print("\nUnable to continue.")
        return

    # The API's detect_name() can return an empty string for some CV layouts.
    # Try the API value first, then use the extracted CV text as a fallback.
    name = (profile.get("name") or profile.get("full_name") or "").strip()
    if not name:
        name = extract_name_fallback(profile.get("cv_text", ""))
    if not name:
        print("WARNING: CV se name detect nahi hua. Name field blank rahega; please enter it manually before submitting.")

    email = profile.get(
        "email",
        ""
    )

    phone = profile.get(
        "phone",
        ""
    )

    skills = profile.get(
        "skills",
        []
    )

    experience = profile.get(
        "experience_years",
        0
    )

    preferred_role = profile.get(
        "preferred_role",
        ""
    )

    candidate_location = profile.get(
        "candidate_location",
        ""
    )

    if isinstance(skills, str):
        skills_text = skills
    elif isinstance(skills, list):
        skills_text = ", ".join(str(skill) for skill in skills)
    else:
        skills_text = ""

    # -----------------------------------------------------
    # PROFILE SUMMARY
    # -----------------------------------------------------

    print("\n===== DETECTED PROFILE =====")

    print("Name:", name)
    print("Email:", email)
    print("Phone:", phone)
    print("Skills:", skills_text)
    print("Experience:", experience, "years")
    print("Location:", candidate_location)
    print("Preferred Role:", preferred_role)

    # -----------------------------------------------------
    # COVER LETTER
    # -----------------------------------------------------

    cover_letter = (
        "I am a motivated MCA graduate with knowledge of "
        f"{skills_text}. "
        "I am interested in this opportunity and eager "
        "to learn, contribute, and grow with the organization."
    )

    # -----------------------------------------------------
    # START BROWSER
    # -----------------------------------------------------

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto(url)

        print("\n===== FORM FILLER =====")

        # -------------------------------------------------
        # FULL NAME
        # -------------------------------------------------

        name_field = page.locator(
            'input[name="full_name"]'
        )

        if name_field.count() > 0 and name:
            name_field.fill(name)
            print("Name filled.")

        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        email_field = page.locator(
            'input[name="email"]'
        )

        if email_field.count() > 0 and email:
            email_field.fill(email)
            print("Email filled.")

        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        phone_field = page.locator(
            'input[name="phone"]'
        )

        if phone_field.count() > 0 and phone:
            phone_field.fill(phone)
            print("Phone filled.")

        # -------------------------------------------------
        # EXPERIENCE
        # -------------------------------------------------

        experience_field = page.locator(
            'input[name="experience"]'
        )

        if experience_field.count() > 0:
            experience_field.fill(
                f"{experience} years"
            )
            print("Experience filled.")

        # -------------------------------------------------
        # SKILLS
        # -------------------------------------------------

        skills_field = page.locator(
            'input[name="skills"]'
        )

        if skills_field.count() > 0 and skills_text:
            skills_field.fill(
                skills_text
            )
            print("Skills filled.")

        # -------------------------------------------------
        # COVER LETTER
        # -------------------------------------------------

        cover_letter_field = page.locator(
            'textarea[name="cover_letter"]'
        )

        if cover_letter_field.count() > 0:
            cover_letter_field.fill(
                cover_letter
            )
            print("Cover letter filled.")

        # -------------------------------------------------
        # PREFERRED ROLE
        # -------------------------------------------------

        role_dropdown = page.locator(
            'select[name="preferred_role"]'
        )

        if role_dropdown.count() > 0:

            options = role_dropdown.locator(
                "option"
            ).all_inner_texts()

            selected_role = ""

            for option in options:

                if (
                    preferred_role
                    and preferred_role.lower()
                    in option.lower()
                ):
                    selected_role = option
                    break

            # Try useful role aliases.
            if not selected_role:

                role_aliases = {
                    "machine learning": [
                        "Machine Learning",
                        "ML Engineer",
                        "Python Developer"
                    ],
                    "ai": [
                        "AI Engineer",
                        "Python Developer"
                    ],
                    "python": [
                        "Python Developer"
                    ],
                    "java": [
                        "Java Developer"
                    ],
                    "frontend": [
                        "Frontend Developer"
                    ],
                    "backend": [
                        "Backend Developer"
                    ],
                    "fullstack": [
                        "Full Stack Developer"
                    ],
                    "data": [
                        "Data Analyst",
                        "Data Scientist"
                    ],
                    "devops": [
                        "DevOps Engineer"
                    ]
                }

                aliases = role_aliases.get(
                    preferred_role.lower(),
                    []
                )

                for alias in aliases:

                    for option in options:

                        if alias.lower() == option.lower():
                            selected_role = option
                            break

                    if selected_role:
                        break

            if selected_role:

                role_dropdown.select_option(
                    label=selected_role
                )

                print(
                    "Preferred role selected:",
                    selected_role
                )

            else:

                print(
                    "Preferred role could not be "
                    "matched with available form options."
                )

        # -------------------------------------------------
        # RESUME UPLOAD
        # -------------------------------------------------

        resume_field = page.locator(
            'input[name="resume"]'
        )

        if (
            resume_field.count() > 0
            and RESUME_PATH.exists()
        ):

            resume_field.set_input_files(
                str(RESUME_PATH)
            )

            print(
                "Resume uploaded successfully."
            )

        # -------------------------------------------------
        # REVIEW
        # -------------------------------------------------

        print("\n===== REVIEW BEFORE SUBMIT =====")

        print("Name:", name)
        print("Email:", email)
        print("Phone:", phone)
        print("Role:", preferred_role)
        print("Experience:", experience, "years")
        print("Skills:", skills_text)
        print("Location:", candidate_location)
        print("Resume:", RESUME_PATH)

        print(
            "\nIMPORTANT:"
        )

        print(
            "Submit button will NOT be clicked."
        )

        print(
            "Review the application in the browser."
        )

        # -------------------------------------------------
        # KEEP BROWSER OPEN FOR REVIEW
        # -------------------------------------------------

        try:

            page.wait_for_timeout(
                300000
            )

        except Exception:

            print(
                "\nBrowser was closed manually."
            )

        finally:

            if not page.is_closed():

                browser.close()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    fill_application_form(
        FORM_URL
    )