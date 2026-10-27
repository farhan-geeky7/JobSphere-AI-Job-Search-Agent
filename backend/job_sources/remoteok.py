import requests
import re


# =========================================================
# API ENDPOINTS
# =========================================================

REMOTE_OK_API = "https://remoteok.com/api"

REMOTIVE_API = "https://remotive.com/api/remote-jobs"

HIMALAYAS_API = "https://himalayas.app/jobs/api"


# =========================================================
# COMMON SETTINGS
# =========================================================

HEADERS = {
    "User-Agent": "JobSphere/1.0"
}

REQUEST_TIMEOUT = 15


# =========================================================
# TEXT HELPERS
# =========================================================

def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


def html_to_text(value):
    if not value:
        return ""

    text = re.sub(
        r"<[^>]+>",
        " ",
        str(value)
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize_key(value):
    if not value:
        return ""

    value = str(value).lower().strip()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value
    )

    return re.sub(
        r"\s+",
        " ",
        value
    ).strip()


# =========================================================
# REMOTE OK
# =========================================================

def fetch_remoteok_source():
    """
    Fetch jobs from Remote OK.
    """

    try:

        response = requests.get(
            REMOTE_OK_API,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        jobs = []

        if not isinstance(data, list):
            return {
                "success": False,
                "jobs": [],
                "error": "Remote OK returned invalid data."
            }

        for item in data:

            if not isinstance(item, dict):
                continue

            # Remote OK API contains a legal notice
            # object as the first element.
            if not item.get("position"):
                continue

            title = clean_text(
                item.get("position")
            )

            company = clean_text(
                item.get("company")
            )

            location = clean_text(
                item.get("location")
            )

            description = clean_text(
                item.get("description")
            )

            tags = item.get(
                "tags",
                []
            )

            if not isinstance(tags, list):
                tags = [tags]

            tags = [
                clean_text(tag)
                for tag in tags
                if clean_text(tag)
            ]

            salary = clean_text(
                item.get("salary")
            )

            url = clean_text(
                item.get("url")
            )

            date = clean_text(
                item.get("date")
            )

            jobs.append({
                "source": "Remote OK",
                "title": title,
                "company": company,
                "location": location or "Remote",
                "description": description,
                "tags": tags,
                "salary": salary,
                "url": url,
                "date": date
            })

        return {
            "success": True,
            "jobs": jobs,
            "error": None
        }

    except Exception as e:

        return {
            "success": False,
            "jobs": [],
            "error": str(e)
        }


# =========================================================
# REMOTIVE
# =========================================================

def fetch_remotive_source():

    try:

        params = {
            "limit": 50
        }

        response = requests.get(
            REMOTIVE_API,
            params=params,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        raw_jobs = data.get(
            "jobs",
            []
        )

        jobs = []

        for item in raw_jobs:

            if not isinstance(item, dict):
                continue

            title = clean_text(
                item.get("title")
            )

            company = clean_text(
                item.get("company_name")
            )

            candidate_location = clean_text(
                item.get(
                    "candidate_required_location"
                )
            )

            description = clean_text(
                item.get("description")
            )

            category = clean_text(
                item.get("category")
            )

            job_type = clean_text(
                item.get("job_type")
            )

            salary = clean_text(
                item.get("salary")
            )

            url = clean_text(
                item.get("url")
            )

            date = clean_text(
                item.get("publication_date")
            )

            tags = []

            if category:
                tags.append(category)

            if job_type:
                tags.append(job_type)

            # The matcher can use these tags to
            # identify role categories.
            tags_text = html_to_text(
                description
            )

            if tags_text:

                title_lower = title.lower()

                role_words = [
                    "python",
                    "java",
                    "javascript",
                    "react",
                    "frontend",
                    "backend",
                    "full stack",
                    "full-stack",
                    "machine learning",
                    "artificial intelligence",
                    "generative ai",
                    "devops",
                    "cloud",
                    "data engineer",
                    "data scientist",
                    "data analyst",
                    "software engineer"
                ]

                for word in role_words:

                    if (
                        word in tags_text.lower()
                        and word not in tags
                    ):
                        tags.append(word)

            jobs.append({
                "source": "Remotive",
                "title": title,
                "company": company,
                "location": (
                    candidate_location
                    or "Remote"
                ),
                "description": description,
                "tags": tags,
                "salary": salary,
                "url": url,
                "date": date
            })

        return {
            "success": True,
            "jobs": jobs,
            "error": None
        }

    except Exception as e:

        return {
            "success": False,
            "jobs": [],
            "error": str(e)
        }


# =========================================================
# HIMALAYAS
# =========================================================

def fetch_himalayas_source():

    try:

        params = {
            "limit": 20
        }

        response = requests.get(
            HIMALAYAS_API,
            params=params,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        raw_jobs = data.get(
            "jobs",
            []
        )

        jobs = []

        for item in raw_jobs:

            if not isinstance(item, dict):
                continue

            title = clean_text(
                item.get("title")
            )

            company = clean_text(
                item.get("companyName")
            )

            description = clean_text(
                item.get("description")
            )

            excerpt = clean_text(
                item.get("excerpt")
            )

            location_restrictions = item.get(
                "locationRestrictions",
                []
            )

            if not isinstance(
                location_restrictions,
                list
            ):
                location_restrictions = [
                    location_restrictions
                ]

            location_restrictions = [
                clean_text(x)
                for x in location_restrictions
                if clean_text(x)
            ]

            if location_restrictions:

                location = ", ".join(
                    location_restrictions
                )

            else:

                location = "Worldwide Remote"

            categories = item.get(
                "categories",
                []
            )

            parent_categories = item.get(
                "parentCategories",
                []
            )

            if not isinstance(categories, list):
                categories = [categories]

            if not isinstance(
                parent_categories,
                list
            ):
                parent_categories = [
                    parent_categories
                ]

            tags = []

            for tag in (
                categories
                + parent_categories
            ):

                tag = clean_text(tag)

                if tag:
                    tags.append(tag)

            salary = ""

            min_salary = item.get(
                "minSalary"
            )

            max_salary = item.get(
                "maxSalary"
            )

            currency = clean_text(
                item.get("currency")
            )

            salary_period = clean_text(
                item.get("salaryPeriod")
            )

            if (
                min_salary is not None
                and max_salary is not None
            ):

                salary = (
                    f"{currency} "
                    f"{min_salary:,} - "
                    f"{max_salary:,}"
                )

                if salary_period:
                    salary += (
                        f" / {salary_period}"
                    )

            elif min_salary is not None:

                salary = (
                    f"{currency} "
                    f"{min_salary:,}+"
                )

            url = clean_text(
                item.get("applicationLink")
            )

            date = clean_text(
                item.get("pubDate")
            )

            combined_description = (
                description
                or excerpt
            )

            jobs.append({
                "source": "Himalayas",
                "title": title,
                "company": company,
                "location": location,
                "description": combined_description,
                "tags": tags,
                "salary": salary,
                "url": url,
                "date": date
            })

        return {
            "success": True,
            "jobs": jobs,
            "error": None
        }

    except Exception as e:

        return {
            "success": False,
            "jobs": [],
            "error": str(e)
        }


# =========================================================
# DEDUPLICATION
# =========================================================

def deduplicate_jobs(jobs):

    unique_jobs = []

    seen_urls = set()

    seen_job_keys = set()

    for job in jobs:

        url = clean_text(
            job.get("url")
        )

        title = normalize_key(
            job.get("title")
        )

        company = normalize_key(
            job.get("company")
        )

        job_key = (
            title,
            company
        )

        # Prefer URL-based duplicate detection.
        if url:

            if url in seen_urls:
                continue

            seen_urls.add(url)

        # Also prevent same title/company
        # from appearing multiple times.
        if job_key in seen_job_keys:

            if not url:
                continue

        seen_job_keys.add(
            job_key
        )

        unique_jobs.append(job)

    return unique_jobs


# =========================================================
# MULTI-SOURCE JOB FETCHER
# =========================================================

def fetch_remoteok_jobs():

    """
    Existing function name is intentionally kept.

    main.py already imports:

        fetch_remoteok_jobs

    So we can expand the job engine without
    changing main.py or job_matcher.py.
    """

    sources = []

    all_jobs = []


    # -----------------------------------------------------
    # Remote OK
    # -----------------------------------------------------

    remoteok_result = (
        fetch_remoteok_source()
    )

    sources.append({
        "name": "Remote OK",
        "success": remoteok_result["success"],
        "jobs": len(
            remoteok_result["jobs"]
        ),
        "error": remoteok_result["error"]
    })

    all_jobs.extend(
        remoteok_result["jobs"]
    )


    # -----------------------------------------------------
    # Remotive
    # -----------------------------------------------------

    remotive_result = (
        fetch_remotive_source()
    )

    sources.append({
        "name": "Remotive",
        "success": remotive_result["success"],
        "jobs": len(
            remotive_result["jobs"]
        ),
        "error": remotive_result["error"]
    })

    all_jobs.extend(
        remotive_result["jobs"]
    )


    # -----------------------------------------------------
    # Himalayas
    # -----------------------------------------------------

    himalayas_result = (
        fetch_himalayas_source()
    )

    sources.append({
        "name": "Himalayas",
        "success": himalayas_result["success"],
        "jobs": len(
            himalayas_result["jobs"]
        ),
        "error": himalayas_result["error"]
    })

    all_jobs.extend(
        himalayas_result["jobs"]
    )


    # -----------------------------------------------------
    # Deduplicate
    # -----------------------------------------------------

    unique_jobs = deduplicate_jobs(
        all_jobs
    )


    successful_sources = [
        source
        for source in sources
        if source["success"]
    ]


    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    if not successful_sources:

        errors = [
            source["error"]
            for source in sources
            if source["error"]
        ]

        return {
            "success": False,
            "source": "Multi-source",
            "sources": sources,
            "jobs": [],
            "error": (
                "All job sources failed. "
                + " | ".join(errors)
            )
        }


    return {
        "success": True,
        "source": "Multi-source",
        "sources": sources,
        "jobs": unique_jobs,
        "error": None
    }