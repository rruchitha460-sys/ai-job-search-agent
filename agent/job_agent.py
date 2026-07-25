import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.adzuna_client import search_jobs
from storage.models import init_db, save_jobs
from matching.embed import find_matches
from matching.resume_reader import extract_resume_text

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL = "openrouter/free"


def explain_match(resume_text, job):
    prompt = f"""You are a career advisor. Given this resume and this job, write a short 2-3 sentence explanation of why this job is (or isn't) a good fit.

RESUME:
{resume_text[:1500]}

JOB TITLE: {job['title']}
COMPANY: {job['company']}
LOCATION: {job['location']}

Explanation:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()


def run_agent(query="machine learning engineer", location="Bangalore", top_k=5):
    print("Step 1: Fetching fresh jobs from Adzuna...")
    init_db()
    jobs = search_jobs(query=query, location=location)
    save_jobs(jobs, source="adzuna")

    print("\nStep 2: Matching jobs against your resume...")
    matches = find_matches(top_k=top_k)

    print("\nStep 3: Generating AI explanations for each match...\n")
    resume_text = extract_resume_text()

    for m in matches:
        explanation = explain_match(resume_text, m)
        print(f"{m['rank']}. {m['title']} — {m['company']} ({m['location']})")
        print(f"   Match score: {m['distance']:.4f}")
        print(f"   Why: {explanation}")
        print(f"   {m['url']}\n")


if __name__ == "__main__":
    run_agent()