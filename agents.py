# File: agents.py

import os
import fitz  # PyMuPDF
import tiktoken
import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOpenAI as OpenRouterChatModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-small-3.2-24b-instruct:free")
TOKEN_LIMIT = int(os.getenv("TOKEN_LIMIT", 6000))
print("OPENROUTER_API_KEY:", OPENROUTER_API_KEY[:10] if OPENROUTER_API_KEY else "Not found")

# Initialize OpenRouter LLM
chat = OpenRouterChatModel(
    model=OPENROUTER_MODEL,
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=OPENROUTER_API_KEY or os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
    max_tokens=1024
)

def count_tokens(text):
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def truncate_text(text, max_tokens=1800):
    tokens = text.split()
    return ' '.join(tokens[:max_tokens])

def safe_extract_text(file_path):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"[ERROR] Failed to extract text: {e}"

def analyze_resume(file_path, role, cutoff=60, jd_text=None):
    resume_text = safe_extract_text(file_path)

    msg = (
        f"You are a recruitment expert. Evaluate this resume for the role of '{role}'.\n"
    )
    if jd_text:
        msg += f"Consider this Job Description as context:\n{jd_text}\n"
    msg += (
        "Give a score out of 100 and explain using bullet points.\n\n"
        f"Resume:\n{resume_text}"
    )

    if count_tokens(msg) > TOKEN_LIMIT:
        st.warning("Resume too long. Truncating to fit within token limits.")
        msg = truncate_text(msg)

    response = chat.invoke([HumanMessage(content=msg)])
    return type("Result", (), {
        "score": extract_score(response.content),
        "strengths": extract_bullets(response.content, "strength"),
        "weaknesses": extract_bullets(response.content, "weakness"),
        "improvements": extract_bullets(response.content, "improv")
    })()

def extract_score(text):
    import re
    match = re.search(r"(\b\d{1,3}\b)[ ]?(/100)?", text)
    score = float(match.group(1)) if match else 60.0
    return min(max(score, 0), 100)

def extract_bullets(text, keyword):
    lines = text.lower().split("\n")
    return [line.strip("-•* \t") for line in lines if keyword in line and len(line.strip()) > 5][:5]

def generate_questions(role, difficulty, count, custom_lines=None):
    prompt = (
        f"You are an interviewer. Generate {count} {difficulty.lower()}-level technical and behavioral "
        f"interview questions for the role '{role}'."
    )
    if custom_lines:
        prompt += "\nAlso include questions related to:\n" + "\n".join(custom_lines)

    if count_tokens(prompt) > TOKEN_LIMIT:
        st.warning("Prompt too long. Truncating to fit within token limits.")
        prompt = truncate_text(prompt)

    response = chat.invoke([HumanMessage(content=prompt)])
    return response.content.strip().split("\n")

def improve_resume_section(section_text, section_name, role=None):
    prompt = (
        f"You are an expert resume writer. Improve the following {section_name} section"
        f"{' for the role of ' + role if role else ''}. Make it concise and impactful:\n\n{section_text}"
    )

    if count_tokens(prompt) > TOKEN_LIMIT:
        st.warning("Section too long. Truncating.")
        prompt = truncate_text(prompt)

    response = chat.invoke([HumanMessage(content=prompt)])
    return response.content.strip()

def generate_jd_questions(jd_text, count=10):
    prompt = (
        f"Based on the following Job Description, generate {count} interview questions (technical and behavioral):\n\n"
        f"{jd_text}"
    )

    if count_tokens(prompt) > TOKEN_LIMIT:
        st.warning("Job description too long. Truncating.")
        prompt = truncate_text(prompt)

    response = chat.invoke([HumanMessage(content=prompt)])
    return response.content.strip().split("\n")
