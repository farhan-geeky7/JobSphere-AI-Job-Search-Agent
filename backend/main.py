from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, HttpUrl

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from agent.application_agent import open_application_page
from agent.form_filler import fill_application_form



from models.user import UserProfile

from models.job import Job

from job_sources.remoteok import fetch_remoteok_jobs

from job_sources.aggregator import fetch_all_real_jobs

from job_sources.job_matcher import match_resume_with_jobs



from pypdf import PdfReader



import os

import re





app = FastAPI(

    title="JobSphere",

    description="AI Job Search and Application Agent",

    version="1.0.0"

)





app.mount(

    "/frontend",

    StaticFiles(directory="frontend", html=True),

    name="frontend"

)





app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)





os.makedirs("uploads", exist_ok=True)





 # =========================================================

 # SAMPLE JOBS

 # =========================================================



jobs = [

    Job(

        id=1,

        title="Python Developer",

        company="Tech Solutions",

        location="Noida",

        skills=["Python", "SQL", "Git"],

        experience_required=0

    ),

    Job(

        id=2,

        title="Customer Support Executive",

        company="BPO Solutions",

        location="Noida",

        skills=["Communication", "Customer Support", "English"],

        experience_required=0

    ),

    Job(

        id=3,

        title="Java Developer",

        company="Software Company",

        location="Delhi",

        skills=["Java", "SQL", "Git"],

        experience_required=1

    )

]





 # =========================================================

 # CV EXTRACTION

 # =========================================================



def extract_cv_text(file_path):

    reader = PdfReader(file_path)

    cv_text = ""



    for page in reader.pages:

        text = page.extract_text()



        if text:

            cv_text += text + "\n"



    return cv_text





 # =========================================================

 # SKILLS

 # =========================================================



SKILL_LIST = [

    "Python",

    "Java",

    "SQL",

    "JavaScript",

    "HTML",

    "CSS",

    "React",

    "FastAPI",

    "Django",

    "Flask",

    "AWS",

    "Azure",

    "Git",

    "GitHub",

    "Machine Learning",

    "Artificial Intelligence",

    "Generative AI",

    "REST API",

    "Docker",

    "Kubernetes",

    "MySQL",

    "MongoDB",

    "Communication",

    "Customer Support",

    "English"

]





def detect_skills(cv_text):

    detected = []

    text = cv_text.lower()



    for skill in SKILL_LIST:

        pattern = (

            r"(?<![a-z0-9])"

            + re.escape(skill.lower())

            + r"(?![a-z0-9])"

        )



        if re.search(pattern, text):

            detected.append(skill)



    return detected





 # =========================================================

 # EXPERIENCE

 # =========================================================



def detect_experience(cv_text):

    text = cv_text.lower()



    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:professional\s*)?experience",
        r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*work",
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*employment",
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*professional"
    ]



    values = []



    for pattern in patterns:

        for match in re.findall(

            pattern,

            text,

            re.IGNORECASE

        ):

            try:

                values.append(float(match))

            except (ValueError, TypeError):

                pass



    # Explicit fresher/entry-level wording

    if not values and re.search(

        r"\b(fresher|fresh graduate|recent graduate|entry[- ]level|0\s*(?:years?|yrs?))\b",

        text

    ):

        return 0



    return max(values) if values else 0





 # =========================================================

 # CANDIDATE LOCATION

 # =========================================================



INDIAN_LOCATIONS = [

    "india",

    "delhi",

    "new delhi",

    "noida",

    "greater noida",

    "gurgaon",

    "gurugram",

    "ghaziabad",

    "patna",

    "bihar",

    "lucknow",

    "mumbai",

    "pune",

    "bangalore",

    "bengaluru",

    "hyderabad",

    "chennai",

    "kolkata",

    "jaipur",

    "ahmedabad",

    "chandigarh",

    "indore",

    "bhubaneswar",

    "ranchi",

    "varanasi"

]





COUNTRY_WORDS = [

    "india",

    "united states",

    "usa",

    "canada",

    "uk",

    "united kingdom",

    "australia",

    "germany",

    "singapore",

    "south korea",

    "spain",

    "france"

]





def detect_candidate_location(cv_text):

    text = cv_text.lower()



    # Prefer explicit location/address lines.

    patterns = [

        r"(?:location|address|based in|residing in)\s*[:-]\s*([^\n]{2,80})",

        r"(?:city|place)\s*[:-]\s*([^\n]{2,60})"

    ]



    for pattern in patterns:

        match = re.search(

            pattern,

            text,

            re.IGNORECASE

        )



        if match:

            value = match.group(1).strip(" ,.-")



            if value:

                return value



    # Fall back to known Indian/country locations.

    for location in INDIAN_LOCATIONS:

        if re.search(

            r"(?<![a-z])"

            + re.escape(location)

            + r"(?![a-z])",

            text

        ):

            return location



    for country in COUNTRY_WORDS:

        if re.search(

            r"(?<![a-z])"

            + re.escape(country)

            + r"(?![a-z])",

            text

        ):

            return country



    return ""





 # =========================================================

 # PREFERRED ROLE

 # =========================================================



def detect_preferred_role(cv_text, skills):

    text = cv_text.lower()



    role_patterns = [

        (

            "machine learning",

            [

                "machine learning",

                "ml engineer",

                "ml developer"

            ]

        ),

        (

            "ai",

            [

                "artificial intelligence",

                "generative ai",

                "ai engineer",

                "ai developer"

            ]

        ),

        (

            "python",

            [

                "python developer",

                "python engineer"

            ]

        ),

        (

            "java",

            [

                "java developer",

                "java engineer"

            ]

        ),

        (

            "frontend",

            [

                "frontend developer",

                "front end developer",

                "frontend engineer"

            ]

        ),

        (

            "backend",

            [

                "backend developer",

                "back end developer",

                "backend engineer"

            ]

        ),

        (

            "fullstack",

            [

                "full stack developer",

                "full-stack developer",

                "full stack engineer"

            ]

        ),

        (

            "data",

            [

                "data analyst",

                "data scientist",

                "data engineer"

            ]

        ),

        (

            "devops",

            [

                "devops engineer",

                "cloud engineer",

                "site reliability engineer"

            ]

        )

    ]



    for role, keywords in role_patterns:

        for keyword in keywords:

            if keyword in text:

                return role



    # Skill-based fallback.

    skill_set = {

        skill.lower()

        for skill in skills

    }



    if "machine learning" in skill_set:

        return "machine_learning"



    if (

        "generative ai" in skill_set

        or "artificial intelligence" in skill_set

    ):

        return "ai"



    if "python" in skill_set:

        return "python"



    if "java" in skill_set:

        return "java"



    return ""





 # =========================================================

 # PERSONAL INFORMATION EXTRACTION

 # =========================================================



def detect_name(cv_text):

    lines = [

        line.strip()

        for line in cv_text.splitlines()

        if line.strip()

    ]



    # First try explicit name labels.

    for line in lines[:20]:

        match = re.search(

            r"^(?:name|full\s+name)\s*[:-]\s*(.+)$",

            line,

            re.IGNORECASE

        )



        if match:

            return match.group(1).strip()



    # Fallback: inspect first few lines for a likely name.

    for line in lines[:10]:

        lower_line = line.lower()



        if any(

            word in lower_line

            for word in [

                "resume",

                "curriculum vitae",

                "cv",

                "email",

                "phone",

                "mobile",

                "address",

                "linkedin",

                "github"

            ]

        ):

            continue



        words = line.split()



        if 2 <= len(words) <= 4:

            if all(

                re.match(

                    r"^[A-Za-z][A-Za-z.'-]\*$",

                    word

                )

                for word in words

            ):

                return line



    return ""





def detect_email(cv_text):

    match = re.search(

        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

        cv_text

    )



    return match.group(0) if match else ""





def detect_phone(cv_text):

    patterns = [

        r"(?<!\d)(?:\+?1[\s-]?)?[6-9]\d{9}(?!\d)",

        r"(?<!\d)(?:\+?1[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\d)"

    ]



    for pattern in patterns:

        match = re.search(pattern, cv_text)



        if match:

            return match.group(0).strip()



    return ""





 # =========================================================

 # FILE SAVE

 # =========================================================



async def save_upload(file):

    filename = os.path.basename(file.filename)



    file_path = os.path.join(

        "uploads",

        filename

    )



    with open(file_path, "wb") as buffer:

        buffer.write(await file.read())



    return filename, file_path





 # =========================================================

 # HOME

 # =========================================================



@app.get("/")
def home():
    return {
        "project": "JobSphere",
        "message": "JobSphere AI Agent is running"
    }
@app.get("/dashboard")
def dashboard():
    from fastapi.responses import FileResponse
    return FileResponse("frontend/index.html")




 # =========================================================

 # UPLOAD CV

 # =========================================================



@app.post("/upload-cv")

async def upload_cv(

    file: UploadFile = File(...)

):

    filename, file_path = await save_upload(file)



    cv_text = extract_cv_text(file_path)



    return {

        "message": "CV uploaded and text extracted successfully",

        "filename": filename,

        "path": file_path,

        "cv_text": cv_text

    }





 # =========================================================

 # ANALYZE CV

 # =========================================================



@app.post("/analyze-cv")

async def analyze_cv(

    file: UploadFile = File(...)

):

    filename, file_path = await save_upload(file)



    cv_text = extract_cv_text(file_path)



    skills = detect_skills(cv_text)

    experience = detect_experience(cv_text)

    location = detect_candidate_location(cv_text)

    preferred_role = detect_preferred_role(

        cv_text,

        skills

    )



    name = detect_name(cv_text)

    email = detect_email(cv_text)

    phone = detect_phone(cv_text)



    return {

        "message": "CV analyzed successfully",

        "filename": filename,



        "name": name,

        "email": email,

        "phone": phone,



        "skills": skills,

        "experience_years": experience,

        "candidate_location": location,

        "preferred_role": preferred_role,



        "cv_text": cv_text

    }





 # =========================================================

 # SAMPLE JOBS

 # =========================================================



@app.get("/jobs")

def get_jobs():

    return jobs





 # =========================================================

 # REAL JOBS

 # =========================================================



@app.get("/real-jobs")

def get_real_jobs():

    return fetch_all_real_jobs(

        keyword="machine learning"

    )





 # =========================================================

 # SEARCH STATUS

 # =========================================================



@app.get("/job-search-status")

def job_search_status():

    return {

        "agent": "JobSphere Job Search Agent",

        "status": "connected",

        "sources": [

            {

                "name": "Remote OK",

                "status": "connected",

                "endpoint": "/real-jobs"

            },

            {

                "name": "Himalayas",

                "status": "connected",

                "endpoint": "/real-jobs"

            }

        ]

    }





 # =========================================================

 # REAL JOBS + RESUME MATCHING

 # =========================================================



@app.post("/find-matching-real-jobs")

async def find_matching_real_jobs(

    file: UploadFile = File(...),

    preferred_role: str = Form(""),

    preferred_location: str = Form("")

):

    filename, file_path = await save_upload(file)



    cv_text = extract_cv_text(file_path)



    detected_skills = detect_skills(cv_text)

    experience_years = detect_experience(cv_text)



    resume_location = detect_candidate_location(cv_text)



    detected_role = detect_preferred_role(

        cv_text,

        detected_skills

    )



    # User-provided form values have priority.

    candidate_location = (

        preferred_location.strip()

        if preferred_location.strip()

        else resume_location

    )



    # Use the user's selected role when provided.

    # Otherwise use the role detected from the CV.

    candidate_role = (

        preferred_role.strip()

        if preferred_role.strip()

        else detected_role

    )



    real_jobs_result = fetch_all_real_jobs(

        keyword=(

            candidate_role

            or detected_role

            or "machine learning"

        )

    )



    if not real_jobs_result.get(

        "success",

        False

    ):

        return {

            "success": False,

            "message": "Unable to fetch real jobs.",

            "source": "JobSphere Multi-Source",

            "error": real_jobs_result.get(

                "error",

                "Unknown error"

            )

        }



    real_jobs = real_jobs_result.get(

        "jobs",

        []

    )



    matched_jobs = match_resume_with_jobs(

        detected_skills,

        real_jobs,

        experience_years,

        candidate_location,

        candidate_role

    )



    return {

        "success": True,

        "message": "Real jobs found and matched successfully",

        "filename": filename,

        "source": "JobSphere Multi-Source",

        "sources": real_jobs_result.get(

            "sources",

            []

        ),

        "total_jobs_found": len(real_jobs),

        "total_matching_jobs": len(matched_jobs),



        "detected_skills": detected_skills,

        "experience_years": experience_years,

        "candidate_location": candidate_location,

        "detected_role": detected_role,

        "preferred_role": candidate_role,



        "matches": matched_jobs

    }





 # =========================================================

 # OLD PROFILE MATCHING

 # =========================================================



@app.post("/match-jobs")

def match_jobs(

    profile: UserProfile

):

    matched_jobs = []



    profile_skills = [

        skill.lower()

        for skill in profile.skills

    ]



    for job in jobs:



        matched_skills = [

            skill

            for skill in job.skills

            if skill.lower() in profile_skills

        ]



        role_match = any(

            role.lower() in job.title.lower()

            for role in profile.preferred_roles

        )



        location_match = any(

            location.lower() == job.location.lower()

            for location in profile.preferred_locations

        )



        experience_match = (

            profile.experience_years

            >= job.experience_required

        )



        if matched_skills:



            skill_score = (

                len(matched_skills)

                / len(job.skills)

            ) * 60



            role_score = (

                20

                if role_match

                else 0

            )



            location_score = (

                10

                if location_match

                else 0

            )



            experience_score = (

                10

                if experience_match

                else 0

            )



            matched_jobs.append({

                "job": job,



                "matched_skills": matched_skills,



                "missing_skills": [

                    skill

                    for skill in job.skills

                    if skill not in matched_skills

                ],



                "match_count": len(

                    matched_skills

                ),



                "match_score": round(

                    skill_score

                    + role_score

                    + location_score

                    + experience_score,

                    2

                ),



                "skill_score": round(

                    skill_score,

                    2

                ),



                "role_score": role_score,

                "location_score": location_score,

                "experience_score": experience_score,



                "role_match": role_match,

                "location_match": location_match,

                "experience_match": experience_match

            })



    matched_jobs.sort(

        key=lambda x: x["match_score"],

        reverse=True

    )



    return {

        "message": "Job matching completed",

        "matches": matched_jobs

    }





 # =========================================================

 # OLD CV + SAMPLE JOB MATCHING

 # =========================================================



@app.post("/analyze-and-match-cv")

async def analyze_and_match_cv(

    file: UploadFile = File(...)

):

    filename, file_path = await save_upload(file)



    cv_text = extract_cv_text(file_path)



    detected_skills = detect_skills(cv_text)

    experience_years = detect_experience(cv_text)



    matched_jobs = []



    detected_skills_lower = [

        skill.lower()

        for skill in detected_skills

    ]



    for job in jobs:



        matched_skills = [

            skill

            for skill in job.skills

            if skill.lower()

            in detected_skills_lower

        ]



        if not matched_skills:

            continue



        role_match = False



        job_title_lower = job.title.lower()



        if "developer" in job_title_lower:



            for keyword in [

                "python",

                "java",

                "software",

                "developer"

            ]:



                if keyword in cv_text.lower():

                    role_match = True

                    break



        elif "customer support" in job_title_lower:



            for keyword in [

                "customer support",

                "customer service",

                "communication",

                "bpo"

            ]:



                if keyword in cv_text.lower():

                    role_match = True

                    break



        location_match = (

            job.location.lower()

            in cv_text.lower()

        )



        experience_match = (

            experience_years

            >= job.experience_required

        )



        skill_score = (

            len(matched_skills)

            / len(job.skills)

        ) * 60



        role_score = (

            20

            if role_match

            else 0

        )



        location_score = (

            10

            if location_match

            else 0

        )



        experience_score = (

            10

            if experience_match

            else 0

        )



        matched_jobs.append({

            "job": job,



            "matched_skills": matched_skills,



            "missing_skills": [

                skill

                for skill in job.skills

                if skill not in matched_skills

            ],



            "match_count": len(

                matched_skills

            ),



            "match_score": round(

                skill_score

                + role_score

                + location_score

                + experience_score,

                2

            ),



            "skill_score": round(

                skill_score,

                2

            ),



            "role_score": role_score,

            "location_score": location_score,

            "experience_score": experience_score,



            "role_match": role_match,

            "location_match": location_match,

            "experience_match": experience_match

        })



    matched_jobs.sort(

        key=lambda x: x["match_score"],

        reverse=True

    )



    return {

        "message": "CV analyzed and jobs matched successfully",

        "filename": filename,

        "detected_skills": detected_skills,

        "experience_years": experience_years,

        "matches": matched_jobs

    }

# =========================================================
# PREPARE APPLICATION
# =========================================================

class PrepareApplicationRequest(BaseModel):
    url: HttpUrl


@app.post("/prepare-application")
def prepare_application(request: PrepareApplicationRequest):
    """
    Open the selected application page and fill available fields using the
    existing CV-based form filler. The final Submit button is never clicked.
    """
    try:
        target_url = str(request.url)

        # This function opens a visible browser, analyzes the saved resume via
        # /analyze-cv, fills supported fields, attaches the resume when possible,
        # and leaves the page open briefly for the user to review.
        fill_application_form(target_url)

        return {
            "success": True,
            "message": (
                "Application page opened. Available fields were prepared "
                "for review; the final Submit button was not clicked."
            ),
            "url": target_url,
            "submitted": False
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Application preparation failed: {error}"
        )
