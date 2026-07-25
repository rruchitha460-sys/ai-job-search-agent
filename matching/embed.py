import os
import sys
import sqlite3
import numpy as np
import faiss
import streamlit as st
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matching.resume_reader import extract_resume_text

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "jobs.db")

# Load embedding model once (small, fast, runs locally)
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()


def get_all_jobs():
    """Fetch every job ever stored (used only for standalone/CLI testing)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, company, location, description, url FROM jobs")
    rows = cursor.fetchall()
    conn.close()
    return rows


def build_faiss_index_from_jobs(jobs):
    """
    Build a FAISS index from an explicit list of job dicts
    (e.g. just the jobs fetched in the current search), NOT the whole DB.
    Each job dict must have a 'description' key.
    """
    if not jobs:
        return None

    descriptions = [job.get("description") or "" for job in jobs]
    embeddings = model.encode(descriptions, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index


def find_matches_in_jobs(jobs, resume_text, top_k=5):
    """
    Match resume_text against ONLY the given list of job dicts
    (the current search's results) — fixes the old bug where matches
    were pulled from the entire historical database regardless of query.
    """
    if not jobs:
        return []

    top_k = min(top_k, len(jobs))

    resume_embedding = model.encode([resume_text], convert_to_numpy=True)
    index = build_faiss_index_from_jobs(jobs)
    if index is None:
        return []

    distances, indices = index.search(resume_embedding, top_k)

    matches = []
    for rank, idx in enumerate(indices[0]):
        job = jobs[idx]
        matches.append({
            "rank": rank + 1,
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "description": job.get("description"),
            "url": job.get("url"),
            "distance": float(distances[0][rank]),
        })

    return matches


def find_matches(top_k=5):
    """Legacy CLI helper: matches resume.pdf against the ENTIRE stored database.
    Kept only for standalone terminal testing (python matching/embed.py)."""
    resume_text = extract_resume_text()
    jobs_rows = get_all_jobs()
    jobs = [
        {"title": j[1], "company": j[2], "location": j[3], "description": j[4], "url": j[5]}
        for j in jobs_rows
    ]
    return find_matches_in_jobs(jobs, resume_text, top_k=top_k)


if __name__ == "__main__":
    matches = find_matches(top_k=5)

    print("\nTop matching jobs for your resume:\n")
    for m in matches:
        print(f"{m['rank']}. {m['title']} — {m['company']} ({m['location']})")
        print(f"   Match score (lower = closer): {m['distance']:.4f}")
        print(f"   {m['url']}\n")