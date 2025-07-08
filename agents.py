import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from pydantic import BaseModel
from typing import Optional, List

load_dotenv()

API_BACKEND = os.getenv("API_BACKEND", "openai")  # "openai" or "groq"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class ResumeAnalysisResult(BaseModel):
    score: float
    strengths: List[str]
    improvements: List[str]
    weaknesses: List[str]

def get_chat_model():
    return ChatOpenAI(api_key=OPENAI_API_KEY)

def embed_docs(uploaded_file):
    temp_path = "/tmp/resume.pdf"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    loader = PyPDFLoader(temp_path)
    docs = loader.load()
    embedder = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    store = FAISS.from_documents(docs, embedder)
    return store

def analyze_resume(resume_file, role_desc: str, cutoff: float) -> ResumeAnalysisResult:
    store = embed_docs(resume_file)
    chat = get_chat_model()
    msg = f"Role description: {role_desc}\nAssess the resume and give:\n- score out of 100\n- top 5 strengths\n- top 5 improvements\n- top 5 weaknesses"
    resp = chat.predict(messages=[{"role": "user", "content": msg}])
    parts = resp.split("\n")
    score = float(parts[0].split(":")[1].strip())
    strengths = [s.strip() for s in parts[1].split(":")[1].split(",")]
    improvements = [s.strip() for s in parts[2].split(":")[1].split(",")]
    weaknesses = [s.strip() for s in parts[3].split(":")[1].split(",")]
    return ResumeAnalysisResult(score=score, strengths=strengths, improvements=improvements, weaknesses=weaknesses)

def generate_questions(role: str, difficulty: str, count: int, custom_qs: Optional[List[str]] = None) -> List[str]:
    chat = get_chat_model()
    msg = f"Generate {count} {difficulty} interview questions for a {role} candidate."
    if custom_qs:
        msg += " Also include custom questions: " + "; ".join(custom_qs)
    resp = chat.predict(messages=[{"role": "user", "content": msg}])
    return resp.split("\n")

def improve_resume_section(resume_text: str, section: str, role: Optional[str] = None) -> str:
    chat = get_chat_model()
    msg = f"Improve the '{section}' section of this resume"
    if role:
        msg += f" for a {role} role"
    msg += f". Original text:\n{resume_text}"
    resp = chat.predict(messages=[{"role": "user", "content": msg}])
    return resp
