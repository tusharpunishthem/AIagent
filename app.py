import streamlit as st
from agents import analyze_resume, generate_questions, improve_resume_section
from ui import render_ui

if __name__ == "__main__":
    render_ui(analyze_resume, generate_questions, improve_resume_section)
