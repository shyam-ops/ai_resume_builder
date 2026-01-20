import os
import json
import httpx
import asyncio
from pydantic import BaseModel
from typing import List, Optional
import unicodedata

# --- 1. Define Data Models (Copied from your schemas) ---
class ContactInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

class EducationItem(BaseModel):
    institution: str
    location: str
    degree: str
    period: str

class ExperienceItem(BaseModel):
    company: str
    title: str
    location: str
    period: str
    bullets: List[str]

class ProjectItem(BaseModel):
    name: str
    tech_stack: List[str]
    period: str
    bullets: List[str]

class GenAIEnhanceResponse(BaseModel):
    contact: ContactInfo
    summary: str
    education: List[EducationItem]
    experience: List[ExperienceItem]
    projects: List[ProjectItem]
    skills: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    certifications: List[str] = []

# --- 2. Helper Functions ---

def sanitize_text_for_pdf(text: str) -> str:
    if not text:
        return ""
    # Standardize characters
    replacements = {
        "\u2013": "-", "\u2014": "-", "\u201c": '"', "\u201d": '"', 
        "\u2018": "'", "\u2019": "'", "\u2022": "*"
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    # Normalize to ASCII
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def clean_data_recursive(data):
    """Recursively cleans strings in the JSON data."""
    if isinstance(data, str):
        return sanitize_text_for_pdf(data)
    elif isinstance(data, list):
        return [clean_data_recursive(item) for item in data]
    elif isinstance(data, dict):
        return {k: clean_data_recursive(v) for k, v in data.items()}
    return data

# --- 3. Main AI Functions ---

async def enhance_resume_ai(resume_text: str, job_description: str):
    """
    Calls OpenRouter to enhance the resume. 
    Replaces the 'call_openrouter_for_resume' endpoint.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "Missing OPENROUTER_API_KEY in Secrets."}

    system_prompt = (
        "You are an expert resume writer. "
        "Return ONLY valid JSON in this exact structure:\n"
        "{\n"
        '  "contact": {"name": "", "email": "", "phone": "", "linkedin": "", "github": ""},\n'
        '  "summary": "",\n'
        '  "education": [{"institution": "", "location": "", "degree": "", "period": ""}],\n'
        '  "experience": [{"company": "", "title": "", "location": "", "period": "", "bullets": [""]}],\n'
        '  "projects": [{"name": "", "tech_stack": [""], "period": "", "bullets": [""]}],\n'
        '  "skills": ["string"],\n'
        '  "technical_skills": ["string"],\n'
        '  "soft_skills": ["string"],\n'
        '  "certifications": ["string"]\n'
        "}"
    )

    user_prompt = (
        f"RESUME:\n{resume_text}\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        "Improve the resume to match the job description. Return JSON only."
    )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io", 
        "X-Title": "AI Resume Builder",
    }
    payload = {
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                return {"error": f"API Error {response.status_code}: {response.text}"}
            
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]
            
            # Parse JSON
            parsed = json.loads(raw_content)
            
            # Clean text for PDF safety
            cleaned = clean_data_recursive(parsed)
            return cleaned

        except Exception as e:
            return {"error": f"Connection or Parsing Error: {str(e)}"}

async def generate_cover_letter_ai(resume_text: str, job_description: str):
    """
    Generates a cover letter.
    Replaces the 'call_openrouter_for_cover_letter' endpoint.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: Missing API Key"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "messages": [
            {"role": "system", "content": "You are an expert cover letter writer. Return ONLY the text."},
            {"role": "user", "content": f"RESUME:\n{resume_text}\n\nJOB:\n{job_description}\n\nWrite a cover letter."},
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"