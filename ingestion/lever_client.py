import requests
import concurrent.futures

# Known company slugs on Lever's public postings API.
# Add more by checking: jobs.lever.co/<slug> on their careers page.
LEVER_COMPANIES = [
    "netflix",
    "palantir",
    "postman",
    "attentive",
    "voleon",
]


def fetch_lever_jobs(company_slug, query=""):
    """
    Fetch all public job postings for a single company from Lever.
    query: optional keyword to filter titles by (case-insensitive substring match).
    """
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for job in data:
            title = job.get("text", "")

            if query and query.lower() not in title.lower():
                continue

            categories = job.get("categories", {})
            location = categories.get("location", "")

            jobs.append({
                "title": title,
                "company": company_slug.replace("-", " ").title(),
                "location": location,
                "description": job.get("descriptionPlain", "") or job.get("description", ""),
                "url": job.get("hostedUrl", ""),
                "salary_min": None,
                "salary_max": None,
            })

        return jobs

    except requests.exceptions.RequestException:
        return []


def search_lever_jobs(query="", companies=None):
    """Search across multiple Lever-hosted companies for a keyword, in parallel."""
    companies = companies or LEVER_COMPANIES
    all_jobs = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(companies)) as executor:
        futures = [executor.submit(fetch_lever_jobs, company, query) for company in companies]
        for future in concurrent.futures.as_completed(futures):
            all_jobs.extend(future.result())

    return all_jobs


if __name__ == "__main__":
    results = search_lever_jobs(query="engineer")
    print(f"Found {len(results)} jobs across Lever companies\n")
    for j in results[:10]:
        print(f"- {j['title']} @ {j['company']} ({j['location']})")