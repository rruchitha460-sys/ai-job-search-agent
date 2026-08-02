import os
import sys
import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from matching.resume_reader import extract_resume_text

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "jobs.db")

# Default relevance threshold: matches with distance above this are dropped
# instead of being forced into the results just to fill top_k.
# Tune this against your own data — print raw distances for a deliberately
# mismatched search (e.g. resume vs "chef" jobs) to see where irrelevant
# results actually score, then set this just below that.
DEFAULT_MAX_DISTANCE = 1.7


# Load embedding model once (small, fast, runs locally)
try:
    import streamlit as st

    @st.cache_resource(show_spinner=False)
    def load_model():
        return SentenceTransformer("all-MiniLM-L6-v2")

    model = load_model()
except (ImportError, ModuleNotFoundError):
    model = SentenceTransformer("all-MiniLM-L6-v2")


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


def find_matches_in_jobs(jobs, resume_text, top_k=5, max_distance=DEFAULT_MAX_DISTANCE):
    """
    Match resume_text against ONLY the given list of job dicts
    (the current search's results) — fixes the old bug where matches
    were pulled from the entire historical database regardless of query.

    max_distance: matches with a distance above this are considered
    irrelevant and dropped, rather than forced into the results just
    to fill top_k. Pass max_distance=None to disable filtering entirely
    (e.g. for debugging/calibration — see __main__ below).
    """
    if not jobs:
        return []

    resume_embedding = model.encode([resume_text], convert_to_numpy=True)
    index = build_faiss_index_from_jobs(jobs)
    if index is None:
        return []

    # overfetch so filtering has room to work with, capped at what's available
    search_k = min(top_k * 3, len(jobs)) if max_distance is not None else len(jobs)
    distances, indices = index.search(resume_embedding, search_k)

    matches = []
    for dist, idx in zip(distances[0], indices[0]):
        if max_distance is not None and dist > max_distance:
            continue  # too weak — skip instead of forcing it in
        job = jobs[idx]
        matches.append({
            "rank": len(matches) + 1,
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "description": job.get("description"),
            "url": job.get("url"),
            "distance": float(dist),
        })
        if max_distance is not None and len(matches) >= top_k:
            break

    return matches


def find_matches(top_k=5, max_distance=DEFAULT_MAX_DISTANCE):
    """Legacy CLI helper: matches resume.pdf against the ENTIRE stored database.
    Kept only for standalone terminal testing (python matching/embed.py)."""
    resume_text = extract_resume_text()
    jobs_rows = get_all_jobs()
    jobs = [
        {"title": j[1], "company": j[2], "location": j[3], "description": j[4], "url": j[5]}
        for j in jobs_rows
    ]
    return find_matches_in_jobs(jobs, resume_text, top_k=top_k, max_distance=max_distance)


if __name__ == "__main__":
    # Calibration mode: run with no filtering so you can see the real
    # distance spread across your whole DB, then pick a sensible
    # DEFAULT_MAX_DISTANCE based on where irrelevant jobs start scoring.
    CALIBRATE = False  # set True temporarily to print all distances, unfiltered

    if CALIBRATE:
        resume_text = extract_resume_text()
        jobs_rows = get_all_jobs()
        jobs = [
            {"title": j[1], "company": j[2], "location": j[3], "description": j[4], "url": j[5]}
            for j in jobs_rows
        ]
        matches = find_matches_in_jobs(jobs, resume_text, top_k=len(jobs), max_distance=None)
        print("\nAll distances (unfiltered) — use this to pick DEFAULT_MAX_DISTANCE:\n")
        for m in matches:
            print(f"{m['distance']:.4f}  {m['title']} — {m['company']}")
    else:
        matches = find_matches(top_k=5)
        print("\nTop matching jobs for your resume:\n")
        for m in matches:
            print(f"{m['rank']}. {m['title']} — {m['company']} ({m['location']})")
            print(f"   Match score (lower = closer): {m['distance']:.4f}")
            print(f"   {m['url']}\n")