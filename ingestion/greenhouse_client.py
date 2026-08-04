import requests
import concurrent.futures

# Known company slugs on Greenhouse's public Job Board API.
# Add more by checking: boards.greenhouse.io/<slug> on their careers page.
GREENHOUSE_COMPANIES = [
    "anthropic",
    "databricks",
    "notion",
    "stripe",
    "airbnb",
    "coinbase",
    "robinhood",
    "doordash",
]


def fetch_greenhouse_jobs(company_slug, query="", location_filter=""):
    """
    Fetch all public job postings for a single company from Greenhouse.
    query: optional keyword to filter titles by (case-insensitive substring match,
           since Greenhouse's API doesn't support server-side search).
    location_filter: optional keyword to filter by location (case-insensitive
           substring match, e.g. "Bangalore"). Greenhouse's API doesn't support
           server-side location filtering either, so this is done client-side
           after fetching. Note: many Greenhouse companies simply don't have
           postings for a given location — an empty result here is often
           correct, not a bug.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for job in data.get("jobs", []):
            title = job.get("title", "")

            # Simple keyword filter since Greenhouse has no search param
            if query and query.lower() not in title.lower():
                continue

            location = job.get("location", {}).get("name", "")

            # Client-side location filter — Greenhouse has no location param either
            if location_filter and location_filter.lower() not in location.lower():
                continue

            jobs.append({
                "title": title,
                "company": company_slug.replace("-", " ").title(),
                "location": location,
                "description": job.get("content", ""),  # HTML content
                "url": job.get("absolute_url", ""),
                "salary_min": None,
                "salary_max": None,
            })

        return jobs

    except requests.exceptions.RequestException:
        return []


def search_greenhouse_jobs(query="", location_filter="", companies=None):
    """Search across multiple Greenhouse-hosted companies for a keyword,
    optionally filtered by location. Fetches all companies in parallel —
    sequential fetching of 8 companies was the main cause of slow search."""
    companies = companies or GREENHOUSE_COMPANIES
    all_jobs = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(companies)) as executor:
        futures = [
            executor.submit(fetch_greenhouse_jobs, company, query, location_filter)
            for company in companies
        ]
        for future in concurrent.futures.as_completed(futures):
            all_jobs.extend(future.result())

    return all_jobs


if __name__ == "__main__":
    # Test 1: no location filter, to see the full raw spread
    results = search_greenhouse_jobs(query="machine learning")
    print(f"Found {len(results)} jobs across Greenhouse companies (no location filter)\n")
    for j in results[:10]:
        print(f"- {j['title']} @ {j['company']} ({j['location']})")

    # Test 2: with location filter, to see how many survive
    print("\n---\n")
    filtered = search_greenhouse_jobs(query="machine learning", location_filter="Bangalore")
    print(f"Found {len(filtered)} jobs matching location 'Bangalore'\n")
    for j in filtered[:10]:
        print(f"- {j['title']} @ {j['company']} ({j['location']})")