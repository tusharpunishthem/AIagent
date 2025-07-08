# File: ui.py

import streamlit as st
import matplotlib.pyplot as plt
import os
import tempfile

ROLES = [
    "Data Scientist", "Data Analyst", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "AI/ML Engineer", "GenAI Engineer",
    "Cloud Engineer", "LLM Developer", "DevOps Engineer"
]

def render_ui(analyze_fn, generate_fn, improve_fn, jd_fn):
    st.set_page_config(page_title="AI Recruitment Agent", layout="wide")
    st.title("🤖 AI‑Powered Recruitment Agent")
    st.sidebar.title("🔧 Configuration")

    theme = st.sidebar.color_picker("Theme color", "#0055ff")
    st.markdown(f"<style>body {{ --primary-color: {theme}; }}</style>", unsafe_allow_html=True)

    api_key = st.sidebar.text_input("🌐 OpenRouter API Key", type="password")
    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key

    tabs = st.tabs([
        "1. Resume Analysis",
        "2. Resume Q&A",
        "3. Resume Improvement",
        "4. Generate Interview Questions"
    ])

    # Tab 1: Resume Analysis (with JD)
    with tabs[0]:
        st.header("Resume Analysis")
        role = st.selectbox("Select Role", ROLES)
        cutoff = st.slider("Cutoff score (out of 100)", 0, 100, 60)
        jd_text = st.text_area("Paste Job Description (optional)", height=150)
        resume_pdf = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

        if st.button("Analyze Resume", key="analyze_resume_btn") and resume_pdf:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_resume:
                tmp_resume.write(resume_pdf.read())
                tmp_path = tmp_resume.name

            result = analyze_fn(tmp_path, role, cutoff, jd_text if jd_text.strip() else None)

            fig, ax = plt.subplots()
            ax.pie([result.score, 100 - result.score],
                   labels=[f"Score: {result.score:.1f}", ""],
                   colors=[theme, "#eee"])
            st.pyplot(fig)

            if result.score >= cutoff:
                st.success("🎉 Congrats! You may be the best fit for this role.")
            else:
                st.info("💡 Unfortunately, you weren't selected. Consider improving your resume.")

            st.markdown(f"**Strengths:** {', '.join(result.strengths)}")
            st.markdown(f"**Improvements:** {', '.join(result.improvements)}")
            st.markdown(f"**Weaknesses:** {', '.join(result.weaknesses)}")
        elif st.button("Missing PDF Upload", key="missing_resume_btn"):
            st.warning("Please upload your resume PDF.")

    # Tab 2: Resume Q&A
    with tabs[1]:
        st.header("Resume Q&A")
        role = st.selectbox("Role", ROLES, key="qna_role")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        count = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
        custom = st.text_area("Custom questions (one per line)")

        if st.button("Generate Q&A", key="qna_btn"):
            questions = generate_fn(role, difficulty, count, custom.strip().splitlines() or None)
            for q in questions:
                st.write(f"- {q}")

    # Tab 3: Resume Improvement
    with tabs[2]:
        st.header("Resume Improvement")
        section = st.selectbox("Section to improve", [
            "Key Skills", "Projects", "Experience",
            "Profile Summary", "Education", "Achievements", "Overall Structure"
        ])
        role_opt = st.selectbox("Target role (optional)", [""] + ROLES)
        text = st.text_area("Paste section text here")

        if st.button("Improve Section", key="improve_section_btn"):
            before = text
            after = improve_fn(text, section, role_opt)
            st.subheader("Before")
            st.write(before)
            st.subheader("After")
            st.write(after)

    # Tab 4: JD-Based Interview Question Generator
    with tabs[3]:
        st.header("Generate Interview Questions")
        jd_text = st.text_area("Paste Job Description here")
        jd_count = st.slider("Number of questions to generate", 1, 20, 10)

        if st.button("Generate from JD", key="generate_jd_btn") and jd_text.strip():
            questions = jd_fn(jd_text.strip(), jd_count)
            for q in questions:
                st.write(f"- {q}")
