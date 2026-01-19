# src/backend/main.py
from fastapi import FastAPI, HTTPException
from datetime import datetime
import os
import httpx
import json

from src.services.portfolio import generate_portfolio_html
from pdf_generator import ResumePDFGenerator
import unicodedata

from .models.schemas import (
    ResumeCreate,
    GenAIEnhanceRequest,
    GenAIEnhanceResponse,
    ContactInfo,
    EducationItem,
    ExperienceItem,
    ProjectItem,
    CertificationItem,
    CoverLetterResponse,
    PortfolioResponse,
    PortfolioProject,
)
def sanitize_text_for_pdf(text: str) -> str:
    if not text:
        return ""
    # Replace smart quotes and dashes with standard ASCII versions
    replacements = {
        "\u2010": "-",  # HYPHEN (The likely culprit!)
        "\u2011": "-",  # NON-BREAKING HYPHEN
        "\u2012": "-",  # FIGURE DASH
        "\u2013": "-",  # EN DASH
        "\u2014": "-",  # EM DASH
        "\u2015": "-",  # HORIZONTAL BAR
        "\u2212": "-",  # MINUS SIGN
        "\u2018": "'",  # LEFT SINGLE QUOTATION MARK
        "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK
        "\u201C": '"',  # LEFT DOUBLE QUOTATION MARK
        "\u201D": '"',  # RIGHT DOUBLE QUOTATION MARK
        "\u00A0": " ",  # NO-BREAK SPACE
        "\u2022": "*",  # BULLET
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text
# -------------------------------------------------
# FastAPI app
# -------------------------------------------------

app = FastAPI(title="AI Resume Builder API")

# -------------------------------------------------
# Basic info / health endpoints
# -------------------------------------------------


@app.get("/")
def read_root():
    return {"message": "AI Resume Builder API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "ai-resume-builder-backend",
    }


@app.get("/version")
def get_version():
    return {
        "name": "AI Resume Portfolio Builder",
        "version": "0.1.0",
        "description": "Backend API for AI-powered resume and portfolio builder",
    }


# -------------------------------------------------
# Test endpoint for ResumeCreate model
# -------------------------------------------------


@app.post("/resumes/test")
def test_resume_input(resume: ResumeCreate):
    return {
        "message": "Resume received successfully",
        "user_id": resume.userid,
        "name": resume.ContactInfo.name,
        "skills_count": len(resume.skills),
        "data": resume,
    }


# -------------------------------------------------
# OpenRouter / GenAI configuration
# -------------------------------------------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set in environment variables.")

OPENROUTER_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"


# -------------------------------------------------
# Helper: call OpenRouter to enhance resume
# -------------------------------------------------


async def call_openrouter_for_resume(
    resume_text: str,
    job_description: str,
) -> GenAIEnhanceResponse:
    system_prompt = (
        "You are an expert resume writer having 20 years of experience in resume writing. "
        "Given a Jake Ryan style resume and a job description, you must return ONLY valid JSON "
        "in this exact format (no extra text):\n\n"
        "{\n"
        '  \"contact\": {\n'
        '    \"name\": \"string\",\n'
        '    \"phone\": \"string\",\n'
        '    \"email\": \"string\",\n'
        '    \"linkedin\": \"string or null\",\n'
        '    \"github\": \"string or null\"\n'
        "  },\n"
        '  \"summary\": \"string\",\n'
        '  \"education\": [\n'
        "    {\n"
        '      \"institution\": \"string\",\n'
        '      \"location\": \"string\",\n'
        '      \"degree\": \"string\",\n'
        '      \"period\": \"string\"\n'
        "    }\n"
        "  ],\n"
        '  \"experience\": [\n'
        "    {\n"
        '      \"company\": \"string\",\n'
        '      \"title\": \"string\",\n'
        '      \"location\": \"string\",\n'
        '      \"period\": \"string\",\n'
        '      \"bullets\": [\"string\", \"string\"]\n'
        "    }\n"
        "  ],\n"
        '  \"projects\": [\n'
        "    {\n"
        '      \"name\": \"string\",\n'
        '      \"tech_stack\": [\"string\", \"string\"],\n'
        '      \"period\": \"string\",\n'
        '      \"bullets\": [\"string\", \"string\"]\n'
        "    }\n"
        "  ],\n"
        '  \"skills\": [\"string\", \"string\"],\n'
        '  \"technical_skills\": [\"string\", \"string\"],\n'
        '  \"soft_skills\": [\"string\", \"string\"],\n'
        '  \"certifications\": [\n'
        "    {\n"
        '      \"name\": \"string\",\n'
        '      \"issuing_authority\": \"string\",\n'
        '      \"issue_date\": \"string\",\n'
        '      \"certificate_id\": \"string\"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Do not include any explanation, only the JSON."
    )

    # Stronger instructions so model fills all fields
    user_prompt = (
        f"RESUME:\n{resume_text}\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        "Rewrite and improve the resume so it strongly matches this job.\n"
        "You MUST:\n"
        "- Extract and improve: contact, summary, education, experience, projects, and skills.\n"
        "- technical_skills: 8–15 concrete technical skills drawn from the resume and job description.\n"
        "- soft_skills: 5–10 soft skills that are actually supported by the resume (e.g. communication, teamwork).\n"
        "- certifications: all real certifications explicitly mentioned in the resume; do NOT invent new ones.\n"
        "If a field truly has no data, return an empty list for that field. "
        "Return ONLY the JSON object in the exact schema described by the system message."
    )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Resume Builder",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)

    print("OpenRouter status:", response.status_code)
    print("OpenRouter response text:", response.text)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"OpenRouter error: {response.status_code} {response.text}",
        )

    data = response.json()
    raw_content = data["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model did not return valid JSON: {e}",
        )
    def clean_list(items, fields):
        cleaned = []
        for item in items:
            new_item = item.copy()
            for field in fields:
                if field in new_item and isinstance(new_item[field], str):
                    new_item[field] = sanitize_text_for_pdf(new_item[field])
                elif field in new_item and isinstance(new_item[field], list):
                    # Clean list of strings (e.g., bullets)
                    new_item[field] = [sanitize_text_for_pdf(s) for s in new_item[field]]
            cleaned.append(new_item)
        return cleaned
    contact = parsed.get("contact", {}) or {}

    clean_contact = {k: sanitize_text_for_pdf(v) if isinstance(v, str) else v for k, v in contact.items()}
    
    clean_summary = sanitize_text_for_pdf(parsed.get("summary", ""))
    
    clean_education = clean_list(parsed.get("education", []), ["institution", "location", "degree", "period"])
    clean_experience = clean_list(parsed.get("experience", []), ["company", "title", "location", "period", "bullets"])
    clean_projects = clean_list(parsed.get("projects", []), ["name", "tech_stack", "period", "bullets"])
    
    # Clean simple lists (Skills)
    clean_skills = [sanitize_text_for_pdf(s) for s in parsed.get("skills", [])]
    clean_tech_skills = [sanitize_text_for_pdf(s) for s in parsed.get("technical_skills", [])]
    clean_soft_skills = [sanitize_text_for_pdf(s) for s in parsed.get("soft_skills", [])]

    return GenAIEnhanceResponse(
        contact=ContactInfo(
            name=clean_contact.get("name", ""),
            email=clean_contact.get("email", ""),
            phone=clean_contact.get("phone"),
            location=clean_contact.get("location"),
            linkedin=clean_contact.get("linkedin"),
            github=clean_contact.get("github"),
        ),
        summary=clean_summary,
        education=clean_education,   # Uses cleaned data
        experience=clean_experience, # Uses cleaned data
        projects=clean_projects,     # Uses cleaned data
        skills=clean_skills,
        technical_skills=clean_tech_skills,
        soft_skills=clean_soft_skills,
        certifications=parsed.get("certifications", []), # Certs usually don't have long text, but you can clean if needed
    )


# -------------------------------------------------
# /genai/enhance endpoint
# -------------------------------------------------


@app.post("/genai/enhance", response_model=GenAIEnhanceResponse)
async def enhance_resume(payload: GenAIEnhanceRequest):
    enhanced = await call_openrouter_for_resume(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
    )
    return enhanced


# -------------------------------------------------
# Cover letter: helper and endpoint
# -------------------------------------------------


async def call_openrouter_for_cover_letter(
    resume_text: str, job_description: str
) -> str:
    system_prompt = (
        "You are an expert cover letter writer. "
        "Given a resume and a job description, write a professional, concise, 3–5 paragraph cover letter. "
        "Return ONLY the cover letter text, no JSON, no explanations."
    )

    user_prompt = (
        f"RESUME:\n{resume_text}\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        "Write a tailored cover letter for this role."
    )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Resume Builder",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"OpenRouter error: {response.status_code} {response.text}",
        )

    data = response.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected OpenRouter response format: {e}",
        )

    return text.strip()


@app.post("/genai/cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(payload: GenAIEnhanceRequest):
    letter = await call_openrouter_for_cover_letter(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
    )
    return CoverLetterResponse(cover_letter=letter)


# -------------------------------------------------
# Portfolio endpoint (uses enhanced resume)
# -------------------------------------------------


@app.post("/genai/portfolio", response_model=PortfolioResponse)
async def generate_portfolio(payload: GenAIEnhanceRequest):
    enhanced = await call_openrouter_for_resume(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
    )

    return PortfolioResponse(
        hero_name=enhanced.contact.name,
        hero_title="Backend Python Developer",  # later you can infer this via AI
        hero_summary=enhanced.summary,
        projects=[
            PortfolioProject(
                name=p.name,
                role=enhanced.experience[0].title if enhanced.experience else "Developer",
                tech_stack=p.tech_stack,
                description=(p.bullets[0] if p.bullets else ""),
                highlights=p.bullets,
                links={"github": enhanced.contact.github, "demo": None},
            )
            for p in enhanced.projects
        ],
        skills=enhanced.skills,
        contact_email=enhanced.contact.email,
        contact_linkedin=enhanced.contact.linkedin,
        contact_github=enhanced.contact.github,
    )