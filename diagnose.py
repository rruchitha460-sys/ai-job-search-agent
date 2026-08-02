from matching.resume_reader import extract_resume_text
from ingestion.adzuna_client import search_jobs
from ingestion.greenhouse_client import search_greenhouse_jobs
from ingestion.lever_client import search_lever_jobs
from matching.embed import find_matches_in_jobs

jobs = search_jobs(query="machine learning engineer", location="Bangalore")
jobs += search_greenhouse_jobs(query="machine learning engineer", location_filter="Bangalore")
jobs += search_lever_jobs(query="machine learning engineer")

resume = extract_resume_text()
matches = find_matches_in_jobs(jobs, resume, top_k=len(jobs), max_distance=None)

print(f"Total jobs: {len(jobs)}")
for m in matches:
    print(f"{m['distance']:.4f}  {m['title']} — {m['company']}")