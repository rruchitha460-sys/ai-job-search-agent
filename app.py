import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.adzuna_client import search_jobs
from storage.models import init_db, save_jobs
from matching.embed import find_matches_in_jobs
from matching.resume_reader import extract_resume_text
from agent.job_agent import explain_match

st.set_page_config(page_title="AI Job Searcher Agent", page_icon="🧠", layout="wide")

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; margin-bottom: 0; }
    .sub-header { color: #9CA3AF; font-size: 1rem; margin-bottom: 1.5rem; }
    .job-card {
        background: #1E2530; border: 1px solid #2D3646; border-radius: 12px;
        padding: 1.25rem 1.5rem; margin-bottom: 1rem;
    }
    .job-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.1rem; }
    .job-meta { color: #9CA3AF; font-size: 0.9rem; margin-bottom: 0.75rem; }
    .score-badge {
        display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem;
    }
    .score-strong { background: #14532D; color: #4ADE80; }
    .score-medium { background: #713F12; color: #FACC15; }
    .score-weak { background: #7F1D1D; color: #F87171; }
    .job-explanation { margin-top: 0.75rem; line-height: 1.5; color: #E5E7EB; }
    .job-link a { color: #60A5FA; text-decoration: none; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


def score_badge(distance):
    if distance < 1.25:
        return "Strong match", "score-strong"
    elif distance < 1.45:
        return "Good match", "score-medium"
    else:
        return "Weaker match", "score-weak"


# ---------- Session state ----------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_name" not in st.session_state:
    st.session_state.resume_name = None

# ---------- Header ----------
st.markdown('<p class="main-header">🧠 AI Job Searcher Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Finds jobs matching your resume using semantic search + AI explanations</p>', unsafe_allow_html=True)

# ---------- Step 1: Resume upload (required first) ----------
with st.sidebar:
    st.header("Step 1: Your Resume")
    uploaded_resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded_resume is not None:
        st.session_state.resume_text = extract_resume_text(uploaded_resume)
        st.session_state.resume_name = uploaded_resume.name
        st.success(f"Loaded: {uploaded_resume.name}")

    st.divider()

    st.header("Step 2: Search Settings")
    if "query_input" not in st.session_state:
        st.session_state.query_input = "machine learning engineer"
    if "location_input" not in st.session_state:
        st.session_state.location_input = "Bangalore"

    query = st.text_input("Job title / keywords", key="query_input")
    location = st.text_input("Location", key="location_input")
    top_k = st.slider("Number of matches", min_value=1, max_value=10, value=5)
    sort_by = st.radio("Sort by", ["Best match first", "Company (A-Z)"])

    resume_ready = st.session_state.resume_text is not None
    run_button = st.button(
        "Find Matching Jobs",
        type="primary",
        use_container_width=True,
        disabled=not resume_ready,
    )
    if not resume_ready:
        st.caption("⬆️ Upload your resume above to enable search")

# ---------- Main logic ----------
if run_button and st.session_state.resume_text:
    progress = st.progress(0, text="Fetching fresh jobs from Adzuna...")

    init_db()
    raw_jobs = search_jobs(query=query, location=location)
    save_jobs(raw_jobs, source="adzuna")  # still stored for history/records

    progress.progress(33, text="Matching THIS search's jobs against your resume...")

    # IMPORTANT: match only against jobs from the current search,
    # not the entire historical database
    matches = find_matches_in_jobs(raw_jobs, st.session_state.resume_text, top_k=top_k)

    progress.progress(66, text="Generating AI explanations...")

    if sort_by == "Company (A-Z)":
        matches = sorted(matches, key=lambda m: m["company"] or "")

    explanations = []
    for i, m in enumerate(matches):
        explanations.append(explain_match(st.session_state.resume_text, m))
        progress.progress(66 + int(34 * (i + 1) / max(len(matches), 1)), text=f"Explaining match {i+1}/{len(matches)}...")

    progress.empty()

    if not matches:
        st.warning(f"No jobs found for '{query}' in '{location}'. Try a different search.")
    else:
        st.success(f"Found {len(matches)} matches for **{query}** in **{location}**")

        for m, explanation in zip(matches, explanations):
            label, css_class = score_badge(m["distance"])
            st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{m['rank']}. {m['title']} — {m['company']}</div>
                <div class="job-meta">📍 {m['location']}</div>
                <span class="score-badge {css_class}">{label} · score {m['distance']:.2f}</span>
                <div class="job-explanation">{explanation}</div>
                <div class="job-link" style="margin-top: 0.75rem;">
                    <a href="{m['url']}" target="_blank">View job posting →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif not resume_ready:
    st.info("👋 Start by uploading your resume in the sidebar — then set your search terms and click **Find Matching Jobs**.")
else:
    st.info("Set your search terms in the sidebar and click **Find Matching Jobs** to get started.")