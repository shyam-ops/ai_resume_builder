# src/backend/models/schemas.py

from pydantic import BaseModel
from typing import List, Dict, Optional

# -------------------------
# User
# -------------------------


class UserCreate(BaseModel):
    userid: str
    name: str
    email: str


# -------------------------
# Resume core structures (for manual resume creation)
# -------------------------


class ResumeContactInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class ResumeExperienceItem(BaseModel):
    role: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str


class ResumeProjectItem(BaseModel):
    title: str
    tech_stack: List[str] = []
    description: str


class ResumeEducationItem(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None


class ResumeCreate(BaseModel):
    userid: str
    ContactInfo: ResumeContactInfo
    summary: str
    experience: List[ResumeExperienceItem] = []
    projects: List[ResumeProjectItem] = []
    skills: List[str] = []
    education: List[ResumeEducationItem] = []
    targetrole: Optional[str] = None
    template: Optional[str] = "modern"


# -------------------------
# Gen AI base requests
# -------------------------


class EnhanceRequest(BaseModel):
    resumedata: Dict
    uselangchain: bool = False


class CoverLetterRequest(BaseModel):
    resumedata: Dict
    jobdescription: str
    companyname: str
    jobtitle: str


class ATSOptimizeRequest(BaseModel):
    resumetext: str
    jobdescription: str


# -------------------------
# Gen AI enhance (LLM) models
# -------------------------


class GenAIEnhanceRequest(BaseModel):
    resume_text: str
    job_description: str


class ContactInfo(BaseModel):
    name: str
    email: str
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


class CertificationItem(BaseModel):
    name: str
    issuing_authority: str
    issue_date: Optional[str] = None
    certificate_id: Optional[str] = None


class GenAIEnhanceResponse(BaseModel):
    contact: ContactInfo
    summary: str
    education: List[EducationItem]
    experience: List[ExperienceItem]
    projects: List[ProjectItem]
    skills: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    certifications: List[CertificationItem]


# -------------------------
# Cover letter
# -------------------------


class CoverLetterResponse(BaseModel):
    cover_letter: str


# -------------------------
# Portfolio
# -------------------------


class PortfolioProject(BaseModel):
    name: str
    role: str
    tech_stack: List[str]
    description: str
    highlights: List[str]
    links: Dict[str, Optional[str]]


class PortfolioResponse(BaseModel):
    hero_name: str
    hero_title: str
    hero_summary: str
    projects: List[PortfolioProject]
    skills: List[str]
    contact_email: str
    contact_linkedin: Optional[str]
    contact_github: Optional[str]

from typing import List, Dict, Optional
from pydantic import BaseModel


# =========================
# JOB DESCRIPTION SCHEMA
# =========================

class JDProfile(BaseModel):
    role: Optional[str] = None
    skills: List[str] = []
    tools: List[str] = []
    responsibilities: List[str] = []
    keywords: Dict[str, int] = {}


# =========================
# RESUME EXPERIENCE SCHEMA
# =========================

class ExperienceItem(BaseModel):
    title: str
    company: str
    period: str
    bullets: List[str]


# =========================
# RESUME PROJECT SCHEMA
# =========================

class ProjectItem(BaseModel):
    name: str
    duration: Optional[str] = ""
    tech_stack: List[str] = []
    highlights: List[str] = []
    github_link: Optional[str] = ""


# =========================
# FINAL RESUME SCHEMA
# =========================

class ResumeData(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

    professional_summary: str

    education: List[str]
    experience: List[ExperienceItem]
    projects: List[ProjectItem]

    skills: Dict[str, List[str]]   # {"technical": [...], "soft": [...]}
    certifications: List[str]
