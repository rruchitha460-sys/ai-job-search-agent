import os
import sys
import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matching.resume_reader import extract_resume_text

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "jobs.db")

# Load embedding model once (small, fast, runs locally)
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, company, location, description, url FROM jobs")
    rows = cursor.fetchall()
    conn.close()
    return rows


def build_faiss_index():
    jobs = get_all_jobs()
    if not jobs:
        print("No jobs found in database. Run adzuna_client.py first.")
        return None, None

    descriptions = [job[4] or "" for job in jobs]  # job[4] = description
    embeddings = model.encode(descriptions, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index, jobs


def find_matches(top_k=5):
    resume_text = extract_resume_text()
    resume_embedding = model.encode([resume_text], convert_to_numpy=True)

    index, jobs = build_faiss_index()
    if index is None:
        return []

    distances, indices = index.search(resume_embedding, top_k)

    matches = []
    for rank, idx in enumerate(indices[0]):
        job = jobs[idx]
        matches.append({
            "rank": rank + 1,
            "title": job[1],
            "company": job[2],
            "location": job[3],
            "url": job[5],
            "distance": float(distances[0][rank]),
        })

    return matches


if __name__ == "__main__":
    matches = find_matches(top_k=5)

    print("\nTop matching jobs for your resume:\n")
    for m in matches:
        print(f"{m['rank']}. {m['title']} — {m['company']} ({m['location']})")
        print(f"   Match score (lower = closer): {m['distance']:.4f}")
        print(f"   {m['url']}\n")