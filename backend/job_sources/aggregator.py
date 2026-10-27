from job_sources.remoteok import fetch_remoteok_jobs
from job_sources.himalayas import search_himalayas_jobs


def normalize_himalayas_job(job):
    """
    Convert Himalayas job format into the common
    JobSphere job format used by the matcher.
    """

    categories = job.get("categories", [])

    if not isinstance(categories, list):
        categories = []

    tags = [
        str(category).strip()
        for category in categories
        if str(category).strip()
    ]

    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    currency = job.get("currency", "")

    salary = ""

    if salary_min is not None or salary_max is not None:

        minimum = (
            str(salary_min)
            if salary_min is not None
            else ""
        )

        maximum = (
            str(salary_max)
            if salary_max is not None
            else ""
        )

        salary = f"{minimum} - {maximum}"

        if currency:
            salary += f" {currency}"

    return {
        "id": job.get("id", ""),

        "source": "Himalayas",

        "title": job.get("title", ""),

        "company": job.get("company", ""),

        "location": job.get(
            "location",
            "Remote / Worldwide"
        ),

        "description": job.get(
            "description",
            ""
        ),

        "tags": tags,

        "salary": salary,

        "url": job.get(
            "url",
            ""
        ),

        "date": job.get(
            "published_at",
            ""
        ),

        "employment_type": job.get(
            "employment_type",
            ""
        ),

        "seniority": job.get(
            "seniority",
            ""
        ),

        "application_url": job.get(
            "application_url",
            job.get("url", "")
        ),

        "location_restrictions":
            job.get(
                "location_restrictions",
                []
            )
    }


def fetch_all_real_jobs(
    keyword="machine learning"
):
    """
    Fetch real jobs from all currently
    connected JobSphere sources.
    """

    all_jobs = []

    # ==========================================
    # REMOTE OK / EXISTING SOURCES
    # ==========================================

    try:

        remote_result = fetch_remoteok_jobs()

        if isinstance(remote_result, dict):

            remote_jobs = remote_result.get(
                "jobs",
                []
            )

            all_jobs.extend(
                remote_jobs
            )

    except Exception as error:

        print(
            f"Remote job source error: {error}"
        )


    # ==========================================
    # HIMALAYAS
    # ==========================================

    try:

        himalayas_jobs = search_himalayas_jobs(
            keyword=keyword,
            country="IN",
            pages=2
        )

        normalized_jobs = [
            normalize_himalayas_job(job)
            for job in himalayas_jobs
        ]

        all_jobs.extend(
            normalized_jobs
        )

    except Exception as error:

        print(
            f"Himalayas source error: {error}"
        )


    # ==========================================
    # REMOVE DUPLICATES
    # ==========================================

    unique_jobs = {}

    for job in all_jobs:

        title = str(
            job.get("title", "")
        ).strip().lower()

        company = str(
            job.get("company", "")
        ).strip().lower()

        url = str(
            job.get("url", "")
        ).strip().lower()

        key = (
            url
            or f"{title}|{company}"
        )

        if key:
            unique_jobs[key] = job


    final_jobs = list(
        unique_jobs.values()
    )


    return {
        "success": True,

        "source": "JobSphere Multi-Source",

        "sources": [
            "Remote OK",
            "Himalayas"
        ],

        "total_jobs": len(
            final_jobs
        ),

        "jobs": final_jobs
    }


if __name__ == "__main__":

    print()
    print("================================")
    print("JOBSPHERE REAL JOB AGGREGATOR")
    print("================================")

    result = fetch_all_real_jobs(
        keyword="machine learning"
    )

    print(
        f"\nTotal real jobs: "
        f"{result['total_jobs']}"
    )

    print(
        f"Sources: "
        f"{', '.join(result['sources'])}"
    )

    print()

    for index, job in enumerate(
        result["jobs"][:20],
        start=1
    ):

        print(
            f"{index}. "
            f"{job.get('title', '')}"
        )

        print(
            f"   Company: "
            f"{job.get('company', '')}"
        )

        print(
            f"   Location: "
            f"{job.get('location', '')}"
        )

        print(
            f"   Source: "
            f"{job.get('source', '')}"
        )

        print(
            f"   Apply: "
            f"{job.get('url', '')}"
        )

        print()