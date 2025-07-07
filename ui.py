import streamlit as st
import matplotlib.pyplot as plt
import os

ROLES = [
    "Data Scientist", "Data Analyst", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "AI/ML Engineer", "GenAI Engineer",
    "Cloud Engineer", "LLM Developer", "DevOps Engineer"
]

def render_ui(analyze_fn, qna_fn, improve_fn):
    st.title("AI‑Powered Recruitment Agent")
    st.sidebar.title("🔧 Configuration")
    theme = st.sidebar.color_picker("Theme color", "#0055ff")
    st.markdown(f"<style>body {{ --primary-color: {theme}; }}</style>", unsafe_allow_html=True)
    openai_key = st.sidebar.text_input("OpenAI API Key", type="password")
    groq_key = st.sidebar.text_input("Groq API Key", type="password")
    if openai_key: os.environ["OPENAI_API_KEY"] = openai_key
    if groq_key: os.environ["GROQ_API_KEY"] = groq_key

    tab = st.tabs(["Resume Analysis", "Resume Q&A", "Resume Improvement", "Interview"]
                 )
    with tab[0]:
        st.header("1. Resume Analysis")
        role = st.selectbox("Select Role", ROLES)
        jd_pdf = st.file_uploader("Upload job description PDF", type=["pdf"])
        cutoff = st.slider("Cutoff score (out of 100)", 0, 100, 60)
        resume = st.file_uploader("Upload your resume PDF", type=["pdf"])
        if st.button("Analyze"):
            result = analyze_fn(resume, jd_pdf.read().decode("latin1"), cutoff) if jd_pdf else analyze_fn(resume, role, cutoff)
            fig, ax = plt.subplots()
            ax.pie([result.score, 100-result.score], labels=[f"Score: {result.score:.1f}", ""], colors=[theme, "#eee"])
            st.pyplot(fig)
            msg = "🎉 Congrats! You may be the best fit." if result.score >= cutoff else "💡 Unfortunately not selected – consider tweaking."
            st.success(msg)
            st.markdown("**Strengths:** " + ", ".join(result.strengths))
            st.markdown("**Improvements:** " + ", ".join(result.improvements))
            st.markdown("**Weaknesses:** " + ", ".join(result.weaknesses))

    with tab[1]:
        st.header("2. Resume Q&A")
        role = st.selectbox("Role", ROLES, key="qna_role")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        count = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
        custom = st.text_area("Custom questions (one per line)")
        if st.button("Generate Q&A"):
            qs = qna_fn(role, difficulty, int(count), custom.strip().splitlines())
            st.write("\n".join(qs))

    with tab[2]:
        st.header("3. Resume Improvement")
        section = st.selectbox("Section to improve", ["Key Skills","Projects","Experience","Profile Summary","Education","Achievements","Overall Structure"])
        role_opt = st.selectbox("Target role (optional)", [""]+ROLES)
        text = st.text_area("Paste that section text here")
        if st.button("Improve Section"):
            improved = improve_fn(text, section, role_opt or None)
            st.subheader("Before")
            st.write(text)
            st.subheader("After")
            st.write(improved)

    with tab[3]:
        st.header("4. Generate Interview Questions")
        role = st.selectbox("Target role", ROLES, key="interview_role")
        difficulty = st.selectbox("Difficulty level", ["Easy","Medium","Hard"], key="interview_diff")
        count = st.slider("Number of questions", 1, 20, 5)
        custom = st.text_area("Optional custom question prompts")
        if st.button("Generate Interview"):
            questions = qna_fn(role, difficulty, int(count), custom.strip().splitlines())
            st.write("\n".join(questions))
