# File: app.py

from ui import render_ui
from agents import (
    analyze_resume,
    generate_questions,
    improve_resume_section,
    generate_jd_questions
)

if __name__ == "__main__":
    render_ui(analyze_resume, generate_questions, improve_resume_section, generate_jd_questions)
