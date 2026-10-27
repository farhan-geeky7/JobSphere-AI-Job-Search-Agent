import requests
import re
from html import unescape


API_URL = "https://himalayas.app/jobs/api/search"


def clean_html(text):
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def fetch_himalayas_jobs(
    keyword="",
    country="IN",
    page=1,
    employment_type=None,
    seniority=None,
    limit=20
):
    """
    Fetch real jobs from Himalayas public API.

    No API key required.
    """

    params = {
        "q": keyword,
        "country": country,
        "sort": "recent",
        "page": page,
    }

    if employment_type:
        params["employment_type"] = employment_type

    if seniority:
        params["seniority"] = seniority

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:
        print(f"Himalayas API error: {error}")
        return []

    except ValueError:
        print("Himalayas API returned invalid JSON.")
        return []

    jobs = data.get("jobs", [])

    results = []

    for job in jobs[:limit]:

        title = job.get("title", "")
        company = job.get("companyName", "")

        description = job.get("description", "")
        excerpt = job.get("excerpt", "")

        application_link = job.get(
            "applicationLink",
            ""
        )

        location_restrictions = job.get(
            "locationRestrictions",
            []
        )

        timezone_restrictions = job.get(
            "timezoneRestrictions",
            []
        )

        categories = job.get(
            "categories",
            []
        )

        job_data = {
            "id": job.get("guid", ""),

            "title": title,

            "company": company,

            "description": clean_html(
                description
            ),

            "excerpt": clean_html(
                excerpt
            ),

            "location": ", ".join(
                location_restrictions
            )
            if location_restrictions
            else "Remote / Worldwide",

            "location_restrictions":
                location_restrictions,

            "timezone_restrictions":
                timezone_restrictions,

            "categories": categories,

            "employment_type":
                job.get("employmentType", ""),

            "seniority":
                job.get("seniority", ""),

            "salary_min":
                job.get("minSalary"),

            "salary_max":
                job.get("maxSalary"),

            "salary_period":
                job.get("salaryPeriod", ""),

            "currency":
                job.get("currency", ""),

            "published_at":
                job.get("pubDate", ""),

            "expires_at":
                job.get("expiryDate", ""),

            "url":
                application_link,

            "application_url":
                application_link,

            "source":
                "Himalayas",

            "source_url":
                "https://himalayas.app",
        }

        results.append(job_data)

    return results


def search_himalayas_jobs(
    keyword,
    country="IN",
    pages=2
):
    """
    Search multiple pages and return
    combined real job listings.
    """

    all_jobs = []

    for page in range(1, pages + 1):

        jobs = fetch_himalayas_jobs(
            keyword=keyword,
            country=country,
            page=page
        )

        all_jobs.extend(jobs)

        if not jobs:
            break

    return all_jobs


if __name__ == "__main__":

    print("\n================================")
    print("HIMALAYAS REAL JOB SEARCH")
    print("================================")

    jobs = search_himalayas_jobs(
        keyword="machine learning",
        country="IN",
        pages=2
    )

    print(
        f"\nReal jobs found: {len(jobs)}\n"
    )

    for index, job in enumerate(
        jobs,
        start=1
    ):

        print(
            f"{index}. "
            f"{job['title']} "
            f"— "
            f"{job['company']}"
        )

        print(
            f"   Location: "
            f"{job['location']}"
        )

        print(
            f"   Type: "
            f"{job['employment_type']}"
        )

        print(
            f"   Apply: "
            f"{job['application_url']}"
        )

        print(
            f"   Source: "
            f"{job['source']}"
        )

        print()