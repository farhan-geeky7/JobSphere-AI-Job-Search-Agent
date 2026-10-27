import re


# =========================================================
# CANONICAL SKILLS
# =========================================================

SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "React": ["react", "react.js", "reactjs"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Machine Learning": ["machine learning", "ml"],
    "Artificial Intelligence": ["artificial intelligence", "artificial-intelligence"],
    "Generative AI": ["generative ai", "generative artificial intelligence", "genai"],
    "REST API": ["rest api", "restful api"],
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo db"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Golang": ["golang", "go language"],
    "C++": ["c++"],
    "C#": ["c#", "c sharp"],
    ".NET": [".net", "dotnet"],
    "PHP": ["php"],
    "Ruby": ["ruby"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "TypeScript": ["typescript", "ts"],
    "Node.js": ["node.js", "nodejs"],
    "GraphQL": ["graphql"],
    "Git": ["git"],
    "GitHub": ["github"]
}


# =========================================================
# ROLE DEFINITIONS
# =========================================================

ROLE_DEFINITIONS = {
    "python": {
        "keywords": [
            "python developer", "python engineer",
            "python programmer", "python backend"
        ],
        "skills": ["Python"]
    },

    "java": {
        "keywords": [
            "java developer", "java engineer",
            "java programmer", "java backend"
        ],
        "skills": ["Java"]
    },

    "javascript": {
        "keywords": [
            "javascript developer",
            "javascript engineer",
            "javascript programmer"
        ],
        "skills": ["JavaScript"]
    },

    "frontend": {
        "keywords": [
            "frontend developer", "front end developer",
            "frontend engineer", "front end engineer",
            "web developer", "ui developer", "ui engineer"
        ],
        "skills": ["JavaScript", "React", "HTML", "CSS"]
    },

    "backend": {
        "keywords": [
            "backend developer", "back end developer",
            "backend engineer", "back end engineer",
            "api developer", "api engineer"
        ],
        "skills": [
            "Python", "Java", "FastAPI",
            "Django", "Flask", "REST API"
        ]
    },

    "fullstack": {
        "keywords": [
            "full stack developer", "full-stack developer",
            "full stack engineer", "full-stack engineer"
        ],
        "skills": [
            "Python", "JavaScript", "React", "REST API"
        ]
    },

    "machine_learning": {
        "keywords": [
            "machine learning engineer",
            "machine learning developer",
            "ml engineer", "ml developer",
            "machine learning scientist"
        ],
        "skills": ["Machine Learning", "Python"]
    },

    "ai": {
        "keywords": [
            "ai engineer", "ai developer",
            "ai agent engineer", "ai agent developer",
            "artificial intelligence engineer",
            "artificial intelligence developer",
            "generative ai engineer",
            "generative ai developer",
            "genai engineer", "genai developer"
        ],
        "skills": [
            "Artificial Intelligence",
            "Generative AI",
            "Machine Learning",
            "Python"
        ]
    },

    "data": {
        "keywords": [
            "data analyst", "data scientist",
            "data engineer", "business analyst"
        ],
        "skills": ["Python", "SQL"]
    },

    "devops": {
        "keywords": [
            "devops engineer", "devops developer",
            "cloud engineer", "site reliability engineer", "sre",
            "operations engineer",
            "operations engineer ii",
        ],
        "skills": [
            "AWS", "Azure", "Docker", "Kubernetes"
        ]
    }
}


NON_TECHNICAL_ROLE_WORDS = [
    "social comms",
    "social media",
    "marketing",
    "content writer",
    "content writing",
    "sales",
    "customer support",
    "customer service",
    "virtual assistant",
    "data annotator",
    "data annotation",
    "image evaluator",
    "video evaluator",
    "qa evaluator",
    "recruiter",
    "recruitment",
    "human resources"
]


INDIA_LOCATIONS = [
    "india", "delhi", "new delhi", "noida", "greater noida",
    "gurgaon", "gurugram", "ghaziabad", "patna", "bihar",
    "lucknow", "mumbai", "pune", "bangalore", "bengaluru",
    "hyderabad", "chennai", "kolkata", "jaipur", "ahmedabad",
    "chandigarh", "indore", "ranchi", "varanasi", "bhubaneswar"
]


# =========================================================
# BASIC HELPERS
# =========================================================

def normalize_text(text):
    return str(text or "").lower().strip()


def exact_match(value, text):
    value = normalize_text(value)
    text = normalize_text(text)

    if not value or not text:
        return False

    return re.search(
        r"(?<![a-z0-9])" + re.escape(value) + r"(?![a-z0-9])",
        text,
        re.IGNORECASE
    ) is not None


def get_job_title(job):
    return normalize_text(job.get("title", ""))


def get_job_description(job):
    return normalize_text(job.get("description", ""))


def get_job_location(job):
    return normalize_text(job.get("location", ""))


def get_job_tags_text(job):
    tags = job.get("tags", [])
    if isinstance(tags, list):
        return " ".join(str(x) for x in tags)
    return str(tags)


def find_skill_in_text(skill, text):
    for alias in SKILL_ALIASES.get(skill, [skill]):
        if exact_match(alias, text):
            return True
    return False


# =========================================================
# SKILL EXTRACTION
# =========================================================

def get_resume_core_skills(resume_skills):
    text = " ".join(str(x) for x in resume_skills)
    return [
        skill for skill in SKILL_ALIASES
        if find_skill_in_text(skill, text)
    ]


def detect_job_role(job):
    title = get_job_title(job)

    tags = normalize_text(
        get_job_tags_text(job)
    )

    title_tags = title + " " + tags

    # Prefer explicit title keywords.
    for role_name, data in ROLE_DEFINITIONS.items():
        for keyword in data["keywords"]:
            if keyword in title:
                return role_name

    # Then use role-identifying tags for multilingual titles.
    role_tag_patterns = {
        "fullstack": [
            "full stack",
            "full-stack"
        ],
        "frontend": [
            "frontend",
            "front end"
        ],
        "backend": [
            "backend",
            "back end"
        ],
        "devops": [
            "devops"
        ],
        "python": [
            "python"
        ],
        "java": [
            "java"
        ],
        "javascript": [
            "javascript"
        ],
        "machine_learning": [
            "machine learning"
        ],
        "ai": [
            "generative ai",
            "artificial intelligence"
        ],
        "data": [
            "data analyst",
            "data scientist",
            "data engineer"
        ]
    }

    for role_name, patterns in role_tag_patterns.items():
        for pattern in patterns:
            if exact_match(pattern, title_tags):
                return role_name

    return None


def get_job_required_skills(job):
    title_tags = (
        get_job_title(job)
        + " "
        + normalize_text(get_job_tags_text(job))
    )

    result = []

    # First use actual title/tag skills.
    for skill in SKILL_ALIASES:
        if find_skill_in_text(skill, title_tags):
            result.append(skill)

    # Then add primary role skills. This is important for
    # titles such as "AI Engineer", where "AI" itself is
    # deliberately not treated as a generic skill.
    role = detect_job_role(job)

    if role:
        for skill in ROLE_DEFINITIONS[role]["skills"]:
            if skill not in result:
                result.append(skill)

    return result


# =========================================================
# PREFERRED ROLE NORMALIZATION
# =========================================================

PREFERRED_ROLE_ALIASES = {
    "python developer": "python",
    "python engineer": "python",
    "python programmer": "python",
    "java developer": "java",
    "java engineer": "java",
    "java programmer": "java",
    "javascript developer": "javascript",
    "javascript engineer": "javascript",
    "frontend developer": "frontend",
    "front end developer": "frontend",
    "frontend engineer": "frontend",
    "front end engineer": "frontend",
    "backend developer": "backend",
    "back end developer": "backend",
    "backend engineer": "backend",
    "back end engineer": "backend",
    "full stack developer": "fullstack",
    "full-stack developer": "fullstack",
    "full stack engineer": "fullstack",
    "full-stack engineer": "fullstack",
    "machine learning": "machine_learning",
    "machine learning engineer": "machine_learning",
    "ml engineer": "machine_learning",
    "ai engineer": "ai",
    "ai developer": "ai",
    "artificial intelligence engineer": "ai",
    "generative ai engineer": "ai",
    "data analyst": "data",
    "data scientist": "data",
    "data engineer": "data",
    "devops engineer": "devops",
    "cloud engineer": "devops",
    "site reliability engineer": "devops"
}


def normalize_preferred_role(preferred_role):
    preferred = normalize_text(preferred_role)

    if not preferred:
        return ""

    if preferred in ROLE_DEFINITIONS:
        return preferred

    return PREFERRED_ROLE_ALIASES.get(
        preferred,
        ""
    )


# =========================================================
# ROLE MATCHING
# =========================================================

def check_role_match(resume_skills, job, preferred_role=""):
    resume = set(get_resume_core_skills(resume_skills))
    role = detect_job_role(job)

    preferred = normalize_preferred_role(
        preferred_role
    )

    # If the user selected a role, the job must
    # belong to that same role family.
    if preferred:
        if not role:
            return False

        if role != preferred:
            return False

    if not role:
        return False

    role_skills = set(
        ROLE_DEFINITIONS[role]["skills"]
    )

    matched = resume.intersection(role_skills)

    # AI/ML needs actual domain evidence.
    if role == "ai":
        return (
            "Artificial Intelligence" in matched
            or "Generative AI" in matched
            or "Machine Learning" in matched
        ) and (
            "Python" in matched
            or len(matched) >= 2
        )

    if role == "machine_learning":
        return (
            "Machine Learning" in matched
            and "Python" in matched
        ) or "Machine Learning" in matched

    return bool(matched)


# =========================================================
# EXPERIENCE
# =========================================================

def detect_required_experience(job):
    """Return the minimum explicitly stated years of experience.

    Handles common formats such as "3+ years of experience",
    "minimum 3 years", and "3-10 years of software engineering".
    Returns 0 when no clear requirement is found.
    """
    title = get_job_title(job)
    tags = get_job_tags_text(job)
    description = get_job_description(job)
    source_experience = str(job.get("experience", "") or "")

    # Capture the lower bound of an experience range (e.g. 3-10 years).
    range_patterns = [
        r"\b(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:software|ml|machine\s+learning|engineering|professional|relevant|work|industry|experience)",
        r"\b(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?\s*(?:years?|yrs?)\s+of\s+experience\b",
    ]
    single_patterns = [
        r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+of\s+(?:relevant\s+|professional\s+)?experience\b",
        r"\b(?:minimum|at least)\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
        r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:minimum|at least)\b",
        r"\bexperience\s*:\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
        r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+of\s+(?:software|ml|machine\s+learning|engineering|professional|relevant)\s+(?:engineering|experience|work)\b",
    ]

    # Prefer a structured experience field if the source provides one.
    texts_to_check = [source_experience, f"{title} {tags}", description]
    for text in texts_to_check:
        if not text.strip():
            continue
        values = []
        for pattern in range_patterns + single_patterns:
            for value in re.findall(pattern, text, re.IGNORECASE):
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
        if values:
            # For ranges, the regex captures the minimum (lower bound).
            return min(values) if any(
                re.search(pattern, text, re.IGNORECASE)
                for pattern in range_patterns
            ) else max(values)

    return 0


def detect_seniority(job):
    """
    Detect job seniority.

    Priority:
    1. Explicit seniority supplied by the job source.
    2. Job title as a fallback.

    Some sources, such as Himalayas, provide seniority as a
    list (for example ["Senior"]) rather than a string.
    """

    title = get_job_title(job)

    source_seniority = job.get("seniority", "")

    if isinstance(source_seniority, list):
        source_seniority = " ".join(
            str(item) for item in source_seniority
        )

    source_seniority = normalize_text(source_seniority)

    # Source-provided seniority has priority over title inference.
    if any(
        word in source_seniority
        for word in [
            "senior",
            "sr.",
            "lead",
            "principal",
            "staff",
            "architect",
            "director"
        ]
    ):
        return "senior"

    if any(
        word in source_seniority
        for word in [
            "junior",
            "jr.",
            "intern",
            "internship",
            "trainee",
            "graduate",
            "entry level",
            "entry-level",
            "fresher"
        ]
    ):
        return "junior"

    if any(
        word in source_seniority
        for word in [
            "mid-level",
            "mid level",
            "midlevel",
            "intermediate"
        ]
    ):
        return "mid"

    # Fallback: infer seniority from the job title.
    if any(
        word in title
        for word in [
            "senior",
            "sr.",
            "lead",
            "principal",
            "staff",
            "architect",
            "director"
        ]
    ):
        return "senior"

    if any(
        word in title
        for word in [
            "junior",
            "jr.",
            "intern",
            "internship",
            "trainee",
            "graduate",
            "entry level",
            "entry-level",
            "fresher"
        ]
    ):
        return "junior"

    return "mid"


# =========================================================
# LOCATION
# =========================================================

def is_remote_job(job):
    title = get_job_title(job)
    description = get_job_description(job)
    location = get_job_location(job)

    text = title + " " + description + " " + location

    return (
        "remote" in text
        or not location
    )


def normalize_candidate_location(location):
    text = normalize_text(location)

    if not text:
        return ""

    if any(
        x in text
        for x in ["india", "delhi", "noida", "patna", "bihar",
                  "mumbai", "pune", "bangalore", "bengaluru",
                  "hyderabad", "chennai", "kolkata", "jaipur",
                  "gurgaon", "gurugram", "ghaziabad"]
    ):
        return "india"

    return text


def job_is_location_eligible(job, candidate_location):
    candidate = normalize_candidate_location(
        candidate_location
    )

    job_location = get_job_location(job)
    description = get_job_description(job)

    job_text = job_location + " " + description

    if not job_location:
        return True

    # LATAM/US/Europe/etc. specific jobs should not be
    # recommended to an India-based candidate.
    foreign_regions = [
        "latam",
        "latin america",
        "los angeles",
        "california",
        "united states",
        "usa",
        "canada",
        "united kingdom",
        "uk",
        "south korea",
        "singapore",
        "australia",
        "europe"
    ]

    if candidate == "india":
        # Explicit foreign-region/country restrictions
        # override a generic "remote" label.
        for region in foreign_regions:
            if region in job_text:
                return False

        # A genuinely remote job with no foreign restriction
        # is eligible for an India-based candidate.
        if is_remote_job(job):
            return True

        # If it is an explicitly located non-Indian job,
        # don't recommend it.
        if not any(
            city in job_text
            for city in INDIA_LOCATIONS
        ):
            return False

        return True

    if not candidate:
        # Without candidate location, recommend only
        # remote/unspecified-location jobs.
        return False

    return candidate in job_text


# =========================================================
# ROLE / JOB QUALITY FILTERS
# =========================================================

def is_non_technical_role(job):
    title = get_job_title(job)
    return any(
        word in title
        for word in NON_TECHNICAL_ROLE_WORDS
    )


def has_generic_only_match(matched_skills, job):
    role = detect_job_role(job)

    if role:
        return False

    generic = {
        "Artificial Intelligence",
        "JavaScript",
        "Git",
        "GitHub",
        "SQL"
    }

    return bool(matched_skills) and all(
        skill in generic
        for skill in matched_skills
    )


# =========================================================
# RELEVANCE
# =========================================================

def calculate_relevance(
    matched_skills,
    job_skills,
    role_match,
    required_experience,
    experience_match,
    seniority,
    candidate_experience,
    job,
    candidate_location,
    preferred_role=""
):
    if not job_skills or not matched_skills:
        return False

    if is_non_technical_role(job):
        return False

    if not job_is_location_eligible(
        job,
        candidate_location
    ):
        return False

    if (
        required_experience > candidate_experience
    ):
        return False

    if (
        seniority == "senior"
        and candidate_experience < 2
    ):
        return False

    if has_generic_only_match(
        matched_skills,
        job
    ):
        return False

    role = detect_job_role(job)

    if role:
        if not role_match:
            return False

        primary = set(
            ROLE_DEFINITIONS[role]["skills"]
        )

        primary_matched = len(
            set(matched_skills).intersection(primary)
        )

        primary_total = len(primary)

        primary_ratio = (
            primary_matched / primary_total
            if primary_total
            else 0
        )

        # Strict roles need real coverage.
        if role in {
            "frontend",
            "backend",
            "fullstack",
            "data",
            "devops"
        }:
            return primary_ratio >= 0.50

        if role in {
            "ai",
            "machine_learning"
        }:
            return primary_matched >= 2

        # Language-specific title roles are valid when
        # the main language is present.
        if role in {
            "python",
            "java",
            "javascript"
        }:
            return primary_matched >= 1

        return False

    # If the user selected a preferred role, an unknown
    # job role cannot be safely treated as a match.
    if normalize_preferred_role(
        preferred_role
    ):
        return False

    # Unknown technical role: require at least two
    # meaningful matching skills.
    return len(matched_skills) >= 2


# =========================================================
# MATCH ONE JOB
# =========================================================

def match_resume_with_job(
    resume_skills,
    job,
    candidate_experience=0,
    candidate_location="",
    preferred_role=""
):
    resume_core = get_resume_core_skills(
        resume_skills
    )

    job_skills = get_job_required_skills(
        job
    )

    matched = [
        skill
        for skill in resume_core
        if skill in job_skills
    ]

    missing = [
        skill
        for skill in job_skills
        if skill not in matched
    ]

    role = detect_job_role(job)

    role_match = check_role_match(
        resume_skills,
        job,
        preferred_role
    )

    required_experience = detect_required_experience(
        job
    )

    experience_requirement_known = required_experience > 0
    experience_match = (
        candidate_experience >= required_experience
        if experience_requirement_known
        else None
    )

    seniority = detect_seniority(job)

    skill_score = (
        len(matched) / len(job_skills) * 60
        if job_skills
        else 0
    )

    role_score = 20 if role_match else 0

    # Do not award experience points when the source does not
    # provide a clear requirement; unknown is not the same as matched.
    experience_score = (
        20
        if experience_requirement_known and experience_match
        else 0
    )

    match_score = (
        skill_score
        + role_score
        + experience_score
    )

    relevant = calculate_relevance(
        matched,
        job_skills,
        role_match,
        required_experience,
        experience_match,
        seniority,
        candidate_experience,
        job,
        candidate_location,
        preferred_role
    )

    return {
        "job": job,
        "relevant": relevant,
        "matched_skills": matched,
        "missing_skills": missing,
        "job_skills": job_skills,
        "match_count": len(matched),
        "match_score": round(match_score, 2),
        "skill_score": round(skill_score, 2),
        "role_score": role_score,
        "experience_score": experience_score,
        "role_match": role_match,
        "experience_match": experience_match,
        "required_experience": required_experience,
        "experience_requirement_known": experience_requirement_known,
        "eligible": bool(relevant and experience_match is not False),
        "eligibility_status": (
            "Eligible"
            if relevant and experience_match is True
            else "Experience requirement not specified"
            if relevant and experience_match is None
            else "Does not meet requirements"
        ),
        "seniority": seniority
    }


# =========================================================
# MATCH ALL JOBS
# =========================================================

def match_resume_with_jobs(
    resume_skills,
    jobs,
    candidate_experience=0,
    candidate_location="",
    preferred_role=""
):
    results = []

    for job in jobs:
        result = match_resume_with_job(
            resume_skills,
            job,
            candidate_experience,
            candidate_location,
            preferred_role
        )

        if result["relevant"]:
            results.append(result)

    # Deduplicate.
    unique = {}

    for item in results:
        job = item["job"]

        key = (
            normalize_text(job.get("title", "")),
            normalize_text(job.get("company", "")),
            normalize_text(job.get("url", ""))
        )

        if key not in unique:
            unique[key] = item

    results = list(unique.values())

    # Highest score first.
    results.sort(
        key=lambda item: (
            item["match_score"],
            item["match_count"]
        ),
        reverse=True
    )

    return results
