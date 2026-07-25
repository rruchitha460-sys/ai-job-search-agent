import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.adzuna_client import search_jobs
from storage.models import init_db, save_jobs
from matching.embed import find_matches
from matching.resume_reader import extract_resume_text
from agent.job_agent import explain_match

st.set_page_config(page_title="AI Job Searcher Agent", page_icon="🧠", layout="centered")

st.title("🧠 AI Job Searcher Agent")
st.caption("Finds jobs matching your resume using semantic search + AI explanations")

with st.sidebar:
    st.header("Search Settings")
    query = st.text_input("Job title / keywords", value="machine learning engineer")
    location = st.text_input("Location", value="Bangalore")
    top_k = st.slider("Number of matches", min_value=1, max_value=10, value=5)
    run_button = st.button("🔍 Find Matching Jobs", type="primary")

if run_button:
    with st.spinner("Fetching fresh jobs from Adzuna..."):
        init_db()
        jobs = search_jobs(query=query, location=location)
        save_jobs(jobs, source="adzuna")

    with st.spinner("Matching jobs against your resume..."):
        matches = find_matches(top_k=top_k)
        resume_text = extract_resume_text()

    st.success(f"Found {len(matches)} matches!")

    for m in matches:
        with st.spinner(f"Generating explanation for {m['title']} at {m['company']}..."):
            explanation = explain_match(resume_text, m)

        with st.container(border=True):
            st.subheader(f"{m['rank']}. {m['title']} — {m['company']}")
            st.write(f"📍 {m['location']}  |  📊 Match score: {m['distance']:.4f} (lower = closer)")
            st.write(explanation)
            st.markdown(f"[View job posting]({m['url']})")
else:
    st.info("Set your search terms in the sidebar and click **Find Matching Jobs** to get started.")