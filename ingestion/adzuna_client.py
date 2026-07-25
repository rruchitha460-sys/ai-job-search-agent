import os
import requests
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage.models import init_db, save_jobs

# Load API keys from .env
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


def search_jobs(query="AI engineer", location="Bangalore", country="in", page=1, results_per_page=10):
    url = BASE_URL.format(country=country, page=page)

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "where": location,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    jobs = []

    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "url": job.get("redirect_url"),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
        })

    return jobs


if __name__ == "__main__":
    init_db()  # make sure table exists

    results = search_jobs(query="machine learning engineer", location="Bangalore")
    print(f"\nFound {len(results)} jobs from Adzuna\n")

    save_jobs(results, source="adzuna")