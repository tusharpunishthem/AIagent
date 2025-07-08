import streamlit as st
import matplotlib.pyplot as plt
import os

ROLES = [
    "Data Scientist", "Data Analyst", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "AI/ML Engineer", "GenAI Engineer",
    "Cloud Engineer", "LLM Developer", "DevOps Engineer"
]

def render_ui(analyze_fn, qna_fn, improve_fn):
    st.set_page_config(page_title="AI Recruitment Agent", layout="wide")
    st.title("🤖 AI‑Powered Recruitment Agent")
    st.sidebar.title("🔧 Configuration")
    theme = st.sidebar.color_picker("Theme color", "#0055ff")
    st.markdown(f"<style>:root {{ --primary-color: {theme}; }}</style>", unsafe_allow_html=True)
    openai_key = st.sidebar.text_input("OpenAI API Key", type="password")
    groq_key = st.sidebar.text_input("Groq API Key", type="password")
    if openai_key: os.environ["OPENAI_API_KEY"] = openai_key
    if groq_key: os.environ["GROQ_API_KEY"] = groq_key

    tabs = st.tabs(["Resume Analysis", "Resume Q&A", "Resume Improvement", "Interview"])

    with tabs[0]:
        st.header("1. Resume Analysis")
        role = st.selectbox("Select Role", ROLES)
        jd_pdf = st.text_area("Paste the job description")
        cutoff = st.slider("Cutoff score", 0, 100, 60)
        resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        if st.button("Analyze Resume"):
            if resume:
                result = analyze_fn(resume, jd_pdf or role, cutoff)
                fig, ax = plt.subplots()
                ax.pie([result.score, 100 - result.score], labels=[f"{result.score:.1f}", ""], colors=[theme, "#eee"])
                st.pyplot(fig)
                st.success("🎯 Analysis complete!")
                st.markdown("**Strengths:** " + ", ".join(result.strengths))
                st.markdown("**Improvements:** " + ", ".join(result.improvements))
                st.markdown("**Weaknesses:** " + ", ".join(result.weaknesses))
            else:
                st.warning("Please upload a resume.")

    with tabs[1]:
        st.header("2. Resume Q&A")
        role = st.selectbox("Role", ROLES, key="qna_role")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        count = st.number_input("How many questions?", min_value=1, max_value=20, value=5)
        custom_qs = st.text_area("Custom questions (optional, one per line)")
        if st.button("Generate Questions"):
            questions = qna_fn(role, difficulty, int(count), custom_qs.strip().splitlines())
            st.write("\n".join(questions))

    with tabs[2]:
        st.header("3. Resume Improvement")
        section = st.selectbox("Section", ["Profile Summary", "Experience", "Skills", "Projects", "Education"])
        role_input = st.selectbox("Target Role (optional)", [""] + ROLES)
        section_text = st.text_area("Paste resume section text")
        if st.button("Improve Section"):
            result = improve_fn(section_text, section, role_input if role_input else None)
            st.subheader("🔍 Improved Section")
            st.write(result)

    with tabs[3]:
        st.header("4. Interview Questions")
        role = st.selectbox("Target Role", ROLES, key="interview_role")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        count = st.slider("Number of questions", 1, 20, 5)
        custom = st.text_area("Custom prompts (optional)")
        if st.button("Generate Interview Questions"):
            questions = qna_fn(role, difficulty, int(count), custom.strip().splitlines())
            st.write("\n".join(questions))
