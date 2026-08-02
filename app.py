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

# ---------- Session state ----------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_name" not in st.session_state:
    st.session_state.resume_name = None

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
        <span class="pill">⚡ Live job data</span>
    </div>
</div>
""", unsafe_allow_html=True)

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

# ---------- Resume upload -> redirect ----------
st.markdown('<div class="upload-band">', unsafe_allow_html=True)
st.markdown('<div class="upload-title">Ready to find your matches?</div>', unsafe_allow_html=True)
st.markdown('<div class="upload-sub">Upload your resume to continue to search settings and results.</div>', unsafe_allow_html=True)

uploaded_resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")

if uploaded_resume is not None:
    st.session_state.resume_text = extract_resume_text(uploaded_resume)
    st.session_state.resume_name = uploaded_resume.name
    st.success(f"✅ Loaded: {uploaded_resume.name} — taking you to search →")
    st.switch_page("pages/1_Find_Matches.py")

st.markdown('</div>', unsafe_allow_html=True)