import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from matching.resume_reader import extract_resume_text

st.set_page_config(page_title="AI Job Searcher Agent", page_icon="🧠", layout="wide")

# ---------- Shared CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
<<<<<<< HEAD
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .hero {
        background: linear-gradient(120deg, #1E1B4B 0%, #312E81 40%, #1E293B 100%);
        border-radius: 18px;
        padding: 2.5rem 2.75rem;
        margin-bottom: 2rem;
        border: 1px solid #3730A3;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: "";
        position: absolute; top: -80px; right: -80px;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(129,140,248,0.35) 0%, rgba(129,140,248,0) 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem; font-weight: 700; color: #F1F5F9; margin: 0;
    }
    .hero-sub { color: #C7D2FE; font-size: 1.1rem; margin-top: 0.5rem; max-width: 640px; }
    .pill-row { margin-top: 1.25rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .pill {
        background: rgba(129,140,248,0.15);
        border: 1px solid rgba(129,140,248,0.4);
        color: #C7D2FE; padding: 0.3rem 0.85rem; border-radius: 999px;
        font-size: 0.85rem; font-weight: 500;
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem; font-weight: 700; color: #F1F5F9;
        margin: 1.5rem 0 1rem 0;
    }

    .step-card {
        background: #171B26; border: 1px solid #2D3646; border-radius: 14px;
        padding: 1.25rem 1.4rem; height: 100%;
    }
    .step-num {
        display: inline-flex; align-items: center; justify-content: center;
        width: 30px; height: 30px; border-radius: 50%;
        background: #6366F1; color: white; font-weight: 700; font-size: 0.95rem;
        margin-bottom: 0.6rem;
    }
    .step-title { color: #F1F5F9; font-weight: 700; font-size: 1.02rem; margin-bottom: 0.3rem; }
    .step-desc { color: #9CA3AF; font-size: 0.88rem; line-height: 1.5; }

    .feature-card {
        background: linear-gradient(145deg, #1A2030 0%, #161B26 100%);
        border: 1px solid #2D3646; border-radius: 14px;
        padding: 1.1rem 1.3rem; height: 100%;
    }
    .feature-icon { font-size: 1.4rem; }
    .feature-title { color: #E5E7EB; font-weight: 700; font-size: 0.98rem; margin: 0.4rem 0 0.25rem 0; }
    .feature-desc { color: #9CA3AF; font-size: 0.85rem; line-height: 1.45; }

    .upload-band {
        background: linear-gradient(120deg, #1E1B4B 0%, #1E293B 100%);
        border: 1px solid #3730A3; border-radius: 18px;
        padding: 2rem 2.25rem; margin-top: 2rem; text-align: center;
    }
    .upload-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem; font-weight: 700; color: #F1F5F9;
    }
    .upload-sub { color: #C7D2FE; font-size: 0.95rem; margin-top: 0.3rem; margin-bottom: 1.25rem; }
</style>
""", unsafe_allow_html=True)

=======

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Hero header */
    .hero {
        background: linear-gradient(120deg, #1E1B4B 0%, #312E81 40%, #1E293B 100%);
        border-radius: 18px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.75rem;
        border: 1px solid #3730A3;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(129,140,248,0.35) 0%, rgba(129,140,248,0) 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: #F1F5F9;
        margin: 0;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .hero-sub {
        color: #C7D2FE;
        font-size: 1rem;
        margin-top: 0.4rem;
    }
    .pill-row { margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .pill {
        background: rgba(129,140,248,0.15);
        border: 1px solid rgba(129,140,248,0.4);
        color: #C7D2FE;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* Sidebar step badges */
    .step-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 24px; height: 24px; border-radius: 50%;
        background: #6366F1; color: white; font-weight: 700; font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .step-heading {
        display: flex; align-items: center; margin-bottom: 0.25rem;
        font-weight: 700; font-size: 1.05rem; color: #E5E7EB;
    }

    /* Stat cards */
    .stat-card {
        background: #171B26;
        border: 1px solid #2D3646;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        text-align: center;
    }
    .stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #A5B4FC;
    }
    .stat-label {
        color: #9CA3AF;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Job cards */
    .job-card {
        background: linear-gradient(145deg, #1A2030 0%, #161B26 100%);
        border: 1px solid #2D3646;
        border-left: 4px solid #6366F1;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .job-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(99,102,241,0.18);
    }
    .job-card.strong { border-left-color: #4ADE80; }
    .job-card.medium { border-left-color: #FACC15; }
    .job-card.weak   { border-left-color: #F87171; }

    .job-rank {
        display: inline-block;
        background: #262E40;
        color: #A5B4FC;
        font-weight: 700;
        font-size: 0.8rem;
        border-radius: 6px;
        padding: 0.1rem 0.5rem;
        margin-right: 0.5rem;
    }
    .job-title { font-size: 1.2rem; font-weight: 700; color: #F1F5F9; display: inline; }
    .job-meta { color: #9CA3AF; font-size: 0.88rem; margin: 0.35rem 0 0.6rem 0; }

    .score-badge {
        display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px;
        font-weight: 600; font-size: 0.82rem;
    }
    .score-strong { background: #14532D; color: #4ADE80; }
    .score-medium { background: #713F12; color: #FACC15; }
    .score-weak { background: #7F1D1D; color: #F87171; }

    .job-explanation {
        margin-top: 0.8rem; line-height: 1.55; color: #D1D5DB;
        background: rgba(99,102,241,0.06);
        border-left: 2px solid #4338CA;
        padding: 0.6rem 0.9rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.92rem;
    }
    .job-link a {
        color: #818CF8; text-decoration: none; font-weight: 600;
        font-size: 0.9rem;
    }
    .job-link a:hover { color: #A5B4FC; }
</style>
""", unsafe_allow_html=True)


def score_badge(distance):
    if distance < 1.25:
        return "Strong match", "score-strong", "strong", "🟢"
    elif distance < 1.45:
        return "Good match", "score-medium", "medium", "🟡"
    else:
        return "Weaker match", "score-weak", "weak", "🔴"


>>>>>>> d2058ee38e442381ecc451af8b9ba627081b59c3
# ---------- Session state ----------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_name" not in st.session_state:
    st.session_state.resume_name = None

<<<<<<< HEAD
# ---------- Hero ----------
st.markdown("""
<div class="hero">
    <p class="hero-title">🧠 AI Job Searcher Agent</p>
    <p class="hero-sub">
        An AI agent that reads your resume, searches live job postings, and ranks them by how well
        they actually match you — with a plain-language explanation for every match, not just a keyword score.
    </p>
    <div class="pill-row">
        <span class="pill">🔎 Semantic matching, not keyword matching</span>
        <span class="pill">🤖 AI-generated explanations</span>
=======
# ---------- Hero header ----------
st.markdown("""
<div class="hero">
    <p class="hero-title">🧠 AI Job Searcher Agent</p>
    <p class="hero-sub">Finds jobs matching your resume using semantic search + AI-generated explanations</p>
    <div class="pill-row">
        <span class="pill">🔎 Semantic matching</span>
        <span class="pill">🤖 AI explanations</span>
>>>>>>> d2058ee38e442381ecc451af8b9ba627081b59c3
        <span class="pill">⚡ Live job data</span>
    </div>
</div>
""", unsafe_allow_html=True)

<<<<<<< HEAD
# ---------- What it does ----------
st.markdown('<div class="section-title">What this agent does</div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">Understands your resume</div>
        <div class="feature-desc">Extracts your skills and experience from the PDF you upload — no manual keyword entry.</div>
    </div>
    """, unsafe_allow_html=True)
with f2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧬</div>
        <div class="feature-title">Matches by meaning</div>
        <div class="feature-desc">Uses semantic embeddings to rank jobs by real fit, not just whether words overlap.</div>
    </div>
    """, unsafe_allow_html=True)
with f3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💡</div>
        <div class="feature-title">Explains every match</div>
        <div class="feature-desc">Each result comes with a short AI explanation of why it fits your background.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- How to use ----------
st.markdown('<div class="section-title">How to use it</div>', unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("""
    <div class="step-card">
        <div class="step-num">1</div>
        <div class="step-title">Upload your resume</div>
        <div class="step-desc">Drop your resume as a PDF below. This is what the agent matches jobs against.</div>
    </div>
    """, unsafe_allow_html=True)
with s2:
    st.markdown("""
    <div class="step-card">
        <div class="step-num">2</div>
        <div class="step-title">Set your search</div>
        <div class="step-desc">On the next page, enter a job title, location, and how many matches you want.</div>
    </div>
    """, unsafe_allow_html=True)
with s3:
    st.markdown("""
    <div class="step-card">
        <div class="step-num">3</div>
        <div class="step-title">Get ranked matches</div>
        <div class="step-desc">See live job postings ranked by fit, each with an AI explanation and a link to apply.</div>
    </div>
    """, unsafe_allow_html=True)
=======
# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="step-heading"><span class="step-badge">1</span> Your Resume</div>', unsafe_allow_html=True)
    uploaded_resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")

    if uploaded_resume is not None:
        st.session_state.resume_text = extract_resume_text(uploaded_resume)
        st.session_state.resume_name = uploaded_resume.name
        st.success(f"✅ Loaded: {uploaded_resume.name}")
>>>>>>> d2058ee38e442381ecc451af8b9ba627081b59c3

# ---------- Resume upload -> redirect ----------
st.markdown('<div class="upload-band">', unsafe_allow_html=True)
st.markdown('<div class="upload-title">Ready to find your matches?</div>', unsafe_allow_html=True)
st.markdown('<div class="upload-sub">Upload your resume to continue to search settings and results.</div>', unsafe_allow_html=True)

<<<<<<< HEAD
uploaded_resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")
=======
    st.markdown('<div class="step-heading"><span class="step-badge">2</span> Search Settings</div>', unsafe_allow_html=True)
    if "query_input" not in st.session_state:
        st.session_state.query_input = "machine learning engineer"
    if "location_input" not in st.session_state:
        st.session_state.location_input = "Bangalore"
>>>>>>> d2058ee38e442381ecc451af8b9ba627081b59c3

if uploaded_resume is not None:
    st.session_state.resume_text = extract_resume_text(uploaded_resume)
    st.session_state.resume_name = uploaded_resume.name
    st.success(f"✅ Loaded: {uploaded_resume.name} — taking you to search →")
    st.switch_page("pages/1_Find_Matches.py")

<<<<<<< HEAD
st.markdown('</div>', unsafe_allow_html=True)
=======
    resume_ready = st.session_state.resume_text is not None
    run_button = st.button(
        "🚀 Find Matching Jobs",
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

        # ---- Stats row ----
        strong_count = sum(1 for m in matches if m["distance"] < 1.25)
        avg_score = sum(m["distance"] for m in matches) / len(matches)
        top_company = matches[0]["company"] or "—"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{len(matches)}</div><div class="stat-label">Matches found</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{strong_count}</div><div class="stat-label">Strong matches</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{avg_score:.2f}</div><div class="stat-label">Avg score</div></div>', unsafe_allow_html=True)

        st.write("")

        for m, explanation in zip(matches, explanations):
            label, css_class, tier, dot = score_badge(m["distance"])
            st.markdown(f"""
            <div class="job-card {tier}">
                <span class="job-rank">#{m['rank']}</span>
                <span class="job-title">{m['title']} — {m['company']}</span>
                <div class="job-meta">📍 {m['location']}</div>
                <span class="score-badge {css_class}">{dot} {label} · score {m['distance']:.2f}</span>
                <div class="job-explanation">💡 {explanation}</div>
                <div class="job-link" style="margin-top: 0.75rem;">
                    <a href="{m['url']}" target="_blank">View job posting →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif not resume_ready:
    st.info("👋 Start by uploading your resume in the sidebar — then set your search terms and click **Find Matching Jobs**.")
else:
    st.info("Set your search terms in the sidebar and click **Find Matching Jobs** to get started.")
>>>>>>> d2058ee38e442381ecc451af8b9ba627081b59c3
