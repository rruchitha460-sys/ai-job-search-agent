import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import app_graph
from storage.models import init_db

st.set_page_config(page_title="Find Matches — AI Job Searcher Agent", page_icon="🔎", layout="wide")

# ---------- Shared CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.9rem; font-weight: 700; color: #F1F5F9; margin-bottom: 0.2rem;
    }
    .page-sub { color: #9CA3AF; font-size: 0.95rem; margin-bottom: 1.5rem; }

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

    .stat-card {
        background: #171B26; border: 1px solid #2D3646; border-radius: 14px;
        padding: 1rem 1.25rem; text-align: center;
    }
    .stat-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; font-weight: 700; color: #A5B4FC; }
    .stat-label { color: #9CA3AF; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }

    .job-card {
        background: linear-gradient(145deg, #1A2030 0%, #161B26 100%);
        border: 1px solid #2D3646; border-left: 4px solid #6366F1;
        border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1.1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .job-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(99,102,241,0.18); }
    .job-card.strong { border-left-color: #4ADE80; }
    .job-card.medium { border-left-color: #FACC15; }
    .job-card.weak   { border-left-color: #F87171; }

    .job-rank {
        display: inline-block; background: #262E40; color: #A5B4FC;
        font-weight: 700; font-size: 0.8rem; border-radius: 6px;
        padding: 0.1rem 0.5rem; margin-right: 0.5rem;
    }
    .job-title { font-size: 1.2rem; font-weight: 700; color: #F1F5F9; display: inline; }
    .job-meta { color: #9CA3AF; font-size: 0.88rem; margin: 0.35rem 0 0.6rem 0; }

    .score-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 600; font-size: 0.82rem; }
    .score-strong { background: #14532D; color: #4ADE80; }
    .score-medium { background: #713F12; color: #FACC15; }
    .score-weak { background: #7F1D1D; color: #F87171; }

    .job-explanation {
        margin-top: 0.8rem; line-height: 1.55; color: #D1D5DB;
        background: rgba(99,102,241,0.06); border-left: 2px solid #4338CA;
        padding: 0.6rem 0.9rem; border-radius: 0 8px 8px 0; font-size: 0.92rem;
    }
    .job-link a { color: #818CF8; text-decoration: none; font-weight: 600; font-size: 0.9rem; }
    .job-link a:hover { color: #A5B4FC; }

    .source-tag {
        display: inline-block; padding: 0.15rem 0.6rem; border-radius: 6px;
        font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.03em; margin-left: 0.5rem; vertical-align: middle;
    }
    .source-adzuna     { background: #1E3A5F; color: #7DD3FC; }
    .source-greenhouse { background: #14432A; color: #86EFAC; }
    .source-lever      { background: #4C1D3D; color: #F0ABFC; }
</style>
""", unsafe_allow_html=True)


def score_badge(distance):
    if distance < 1.25:
        return "Strong match", "score-strong", "strong", "🟢"
    elif distance < 1.45:
        return "Good match", "score-medium", "medium", "🟡"
    else:
        return "Weaker match", "score-weak", "weak", "🔴"


# ---------- Guard: must have a resume from page 1 ----------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_name" not in st.session_state:
    st.session_state.resume_name = None

if not st.session_state.resume_text:
    st.warning("No resume found yet — please upload your resume on the home page first.")
    if st.button("⬅ Go to home page"):
        st.switch_page("app.py")
    st.stop()

# ---------- Header ----------
st.markdown(f'<div class="page-title">🔎 Find Your Matches</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-sub">Using resume: <b>{st.session_state.resume_name}</b></div>', unsafe_allow_html=True)

with st.expander("↩ Upload a different resume"):
    if st.button("Go back to home page"):
        st.switch_page("app.py")

# ---------- Step 2: Search settings ----------
st.markdown('<div class="step-heading"><span class="step-badge">2</span> Search Settings</div>', unsafe_allow_html=True)

if "query_input" not in st.session_state:
    st.session_state.query_input = "machine learning engineer"
if "location_input" not in st.session_state:
    st.session_state.location_input = "Bangalore"

c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1.2])
with c1:
    query = st.text_input("Job title / keywords", key="query_input")
with c2:
    location = st.text_input("Location", key="location_input")
with c3:
    top_k = st.slider("Matches", min_value=1, max_value=10, value=5)
with c4:
    sort_by = st.selectbox("Sort by", ["Best match first", "Company (A-Z)"])
with c5:
    experience_label = st.selectbox(
        "Experience level",
        ["Fresher (0–2 yrs)", "Mid-level (2–5 yrs)", "Senior (5+ yrs)", "Any"],
    )

experience_map = {
    "Fresher (0–2 yrs)": "fresher",
    "Mid-level (2–5 yrs)": "mid",
    "Senior (5+ yrs)": "senior",
    "Any": "any",
}
target_level = experience_map[experience_label]

run_button = st.button("🚀 Find Matching Jobs", type="primary", use_container_width=True)

st.divider()

# ---------- Main logic ----------
if run_button:
    progress = st.progress(0, text="Running multi-agent search...")

    init_db()

    progress.progress(30, text="Sourcing + filtering + matching...")

    result = app_graph.invoke({
        "query": query,
        "location": location,
        "target_level": target_level,
        "resume_text": st.session_state.resume_text,
        "jobs": [],
        "matches": [],
        "errors": [],
    })

    progress.progress(80, text="Generating AI explanations...")

    matches = result["matches"][:top_k]

    if sort_by == "Company (A-Z)":
        matches = sorted(matches, key=lambda m: m["company"] or "")

    progress.empty()

    if result.get("errors"):
        st.caption(f"⚠ Some sources had issues: {', '.join(result['errors'])}")

    if not matches:
        st.warning(f"No jobs found for '{query}' in '{location}'. Try a different search.")
    else:
        st.success(f"Found {len(matches)} matches for **{query}** in **{location}**")

        # ---- Stats row ----
        strong_count = sum(1 for m in matches if m["distance"] < 1.25)
        avg_score = sum(m["distance"] for m in matches) / len(matches)

        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{len(matches)}</div><div class="stat-label">Matches found</div></div>', unsafe_allow_html=True)
        with cc2:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{strong_count}</div><div class="stat-label">Strong matches</div></div>', unsafe_allow_html=True)
        with cc3:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{avg_score:.2f}</div><div class="stat-label">Avg score</div></div>', unsafe_allow_html=True)

        st.write("")

        for m in matches:
            label, css_class, tier, dot = score_badge(m["distance"])
            source = m.get("source", "Adzuna")
            source_class = f"source-{source.lower()}"
            explanation = m.get("explanation") or "Explanation unavailable for this job."
            st.markdown(f"""
            <div class="job-card {tier}">
                <span class="job-rank">#{m['rank']}</span>
                <span class="job-title">{m['title']} — {m['company']}</span>
                <span class="source-tag {source_class}">{source}</span>
                <div class="job-meta">📍 {m['location']}</div>
                <span class="score-badge {css_class}">{dot} {label} · score {m['distance']:.2f}</span>
                <div class="job-explanation">💡 {explanation}</div>
                <div class="job-link" style="margin-top: 0.75rem;">
                    <a href="{m['url']}" target="_blank">View job posting →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Set your search terms above and click **Find Matching Jobs** to get started.")