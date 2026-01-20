import asyncio
from ai_utils import enhance_resume_ai, generate_cover_letter_ai
import requests
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import json
from src.services.portfolio import generate_portfolio_html
from pdf_generator import ResumePDFGenerator, ResumeDOCXGenerator
import streamlit as st
import requests
from streamlit_pdf_viewer import pdf_viewer


# other imports ...

# ---------- SESSION STATE INITIALIZATION ----------
if "basic_info" not in st.session_state:
    st.session_state.basic_info = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "summary": "",
    }

if "education" not in st.session_state:
    st.session_state.education = []

if "experience" not in st.session_state:
    st.session_state.experience = []

if "projects" not in st.session_state:
    st.session_state.projects = []

if "skills" not in st.session_state:
    st.session_state.skills = {"technical": [], "soft": []}

if "certifications" not in st.session_state:
    st.session_state.certifications = []

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "resume_data" not in st.session_state:
    st.session_state.resume_data = None

if "resume_data_formatted" not in st.session_state:
    st.session_state.resume_data_formatted = None



# Normalize experience 
def normalize_experience(manual_exp, ai_exp=None):
    """
    Ensures experience passed to PDF has a single, consistent schema.
    Manual input is the source of truth.
    AI is used only to enhance bullets (optional).
    """
    normalized = []

    # Map AI bullets by (company, title)
    ai_map = {}
    if ai_exp:
        for e in ai_exp:
            key = (e.get("company", "").strip(), e.get("title", "").strip())
            ai_map[key] = e.get("bullets", [])

    for exp in manual_exp:
        start = exp.get("start_date", "")
        end = exp.get("end_date", "")
        period = f"{start} – {end}" if start else ""

        bullets = exp.get("description", [])
        if isinstance(bullets, str):
            bullets = [b.strip() for b in bullets.split("\n") if b.strip()]

        # Try to enrich with AI bullets (only if company + role match)
        user_company = exp.get("company", "").strip()
        user_role = exp.get("role", "").strip()

        # Try to find AI bullets by ROLE ONLY (not company)
        ai_bullets = None
        if ai_exp:
            for e in ai_exp:
                if e.get("title", "").strip().lower() == user_role.lower():
                    ai_bullets = e.get("bullets")
                    break

        if ai_bullets:
            bullets = ai_bullets

        normalized.append({
            "company": exp.get("company", ""),
            "role": exp.get("role", ""),
            "location": "",
            "period": period,
            "description": bullets
        })

    return normalized


# Normalize projects
def normalize_projects(manual_projects, ai_projects=None):
    """
    Ensures projects passed to PDF have consistent structure.
    Title, duration, tech stack come from user.
    AI may enhance description bullets.
    """
    normalized = []

    ai_map = {}
    if ai_projects:
        for p in ai_projects:
            key = p.get("name", "").strip().lower()
            ai_map[key] = p.get("bullets", [])

    for proj in manual_projects:
        desc = proj.get("description", "")
        if isinstance(desc, str):
            bullets = [d.strip() for d in desc.split("\n") if d.strip()]
        else:
            bullets = desc or []

        title = proj.get("title", "").strip()

        # Optional AI bullet enrichment (title-based)
        ai_bullets = ai_map.get(title.lower())
        if ai_bullets:
            bullets = ai_bullets

        normalized.append({
            "title": title,
            "duration": proj.get("duration", ""),
            "github_link": proj.get("github_link", ""),
            "tech_stack": (
                [t.strip() for t in proj.get("tech_stack", "").split(",")]
                if isinstance(proj.get("tech_stack"), str)
                else proj.get("tech_stack", [])
            ),
            "description": bullets,   # ✅ LIST
        })

    return normalized


st.set_page_config(page_title="AI Resume, Portfolio & Cover Letter",layout = "wide")
st.markdown(
    """
    <style>
    /* Increase gap between inner tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 3rem;  /* increase this value for more space */
    }
    /* Make tab labels bold */
    .stTabs [data-baseweb="tab"] p {
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

API_BASE = "http://127.0.0.1:8000"

st.title("AI Resume Builder")

st.caption("Generate tailored resumes, portfolios, and cover letters from your profile and job descriptions.")
#-------------------------
#start

#===========================================================================================================
tab_basic, tab_resume, tab_portfolio, tab_cover = st.tabs(
    [" Basic", " Resume", " Portfolio", " Cover Letter"]
)

# ========== INPUT TAB ==========
with tab_basic:
    st.subheader("1. Provide your information")
    basic_tab,edu_tab,exp_tab,proj_tab,tech_tab,soft_tab,cert_tab,jd_tab= st.tabs(
        ["Basic Info","Education","Experience","Project","technical skill","soft skill","Certifications","Job Description",]
    )

    # ---------- BASIC INFO ----------
    with basic_tab:
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name", placeholder="e.g., Shyam Patil")
            email = st.text_input("Email", placeholder="abc@gmail.com")
            phone = st.text_input("Phone", placeholder="1234567890")

        with col2:
            linkedin = st.text_input("LinkedIn URL (optional)")
            github = st.text_input("GitHub URL (optional)")
            profile_image_url = st.text_input(
            "GitHub raw image URL (optional)",placeholder="https://raw.githubusercontent.com/username/repo/branch/image.png")
            resume_drive_link = st.text_input(
                "Resume Drive Link (optional)",
                placeholder="https://drive.google.com/..."
            )
            st.session_state.resume_drive_link = resume_drive_link


        summary = st.text_area(
            "Professional Summary",
            height=120,
            placeholder=(
                "2–3 sentences about your experience, strengths, and goals.\n"
                "Example: Backend Python developer specializing in FastAPI, PostgreSQL, and Docker..."
            ),
        )
        st.session_state.basic_info["name"] = name
        st.session_state.basic_info["email"] = email
        st.session_state.basic_info["phone"] = phone
        st.session_state.basic_info["linkedin"] = linkedin
        st.session_state.basic_info["github"] = github
        st.session_state.basic_info["summary"] = summary
        st.session_state.basic_info["profile_image_url"] = profile_image_url
        st.session_state.basic_info["resume_drive_link"] = resume_drive_link
    # ---------- EDUCATION ----------
    with edu_tab:
        st.markdown("#### Education")
        education = st.text_area(
            "Education",
            height=180,
            placeholder=(
                "- B.Tech in Computer Science, XYZ University (2019–2023)\n"
                "- 8.2 CGPA, relevant coursework: Data Structures, Algorithms, Databases..."
            ),
        )
    # ---------- EXPERIENCE ----------
    with exp_tab:
        st.markdown("### Work Experience")

        if "num_experiences" not in st.session_state:
            st.session_state.num_experiences = 1

        # Button to add another experience
        
        if st.button("➕ Add another experience"):
            st.session_state.num_experiences += 1

        experiences = []
        for i in range(st.session_state.num_experiences):
            st.markdown(f"#### Experience {i + 1}")
            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input(
                    f"Company name",
                    key=f"company_{i}",
                    placeholder="e.g., ABC Tech Pvt Ltd",
                )
                role = st.text_input(
                    f"Job title",
                    key=f"role_{i}",
                    placeholder="e.g., Backend Engineer",
                )

            with col2:
                start_date = st.date_input(
                    f"Start date",
                    key=f"start_date_{i}",
                )
                 # 2) End date (always shown)
                end_date = st.date_input(
                    f"End date",
                    key=f"end_date_{i}",
                )
                 # 3) Checkbox under end date
                still_working = st.checkbox(
                    f"Still working here",
                    key=f"still_working_{i}",
                    value=False,
                )
                # Optional: if checked, ignore end_date
                if still_working:
                    end_date = None
            desc = st.text_area(
                f"Key responsibilities / achievements",
                key=f"desc_{i}",
                height=120,
                placeholder="- Built REST APIs with FastAPI\n- Improved performance by 30%...",
            )

            experiences.append(
                {
                    "company": company,
                    "role": role,
                    "start_date": str(start_date),
                    "end_date": str(end_date) if end_date else "Present",
                    "still_working": still_working,
                    "description": desc,
                }
            )
        st.session_state.experience = experiences
            # Optionally store in session_state if needed later
        st.session_state.structured_experience = experiences


    # ---------- PROJECT ----------
    with proj_tab:
        st.markdown("### Projects")

        if "num_projects" not in st.session_state:
            st.session_state.num_projects = 1

        # Button to add another project
        if st.button("➕ Add another project"):
            st.session_state.num_projects += 1

        projects = []
        for i in range(st.session_state.num_projects):
            st.markdown(f"#### Project {i + 1}")
            col1, col2 = st.columns(2)

            with col1:
                title = st.text_input(
                    f"Project title",
                    key=f"proj_title_{i}",
                    placeholder="e.g., Task Management API",
                )
                github_link = st.text_input(
                    f"GitHub Repo Link",
                    key=f"proj_github_{i}",
                    placeholder="https://github.com/username/project"
                )


            with col2:
                duration = st.text_input(
                    f"Duration",
                    key=f"proj_duration_{i}",
                    placeholder="e.g., Jan 2023 – Jun 2023",
                )
                tech_stack = st.text_input(
                    f"Tech Stack",
                    key=f"tech_stack_{i}",
                    placeholder="e.g., Python, Streamlit, Pandas"
                )
                # ---------------------------

            description = st.text_area(
                f"Outcome / description",
                key=f"proj_desc_{i}",
                height=120,
                placeholder="- Built REST APIs with FastAPI\n- Improved performance by 30%...",
            )

            st.markdown("---")

            projects.append(
                {
                    "title": title,
                    "duration": duration,
                    "description": description,
                    "tech_stack": tech_stack,
                    "github_link": github_link,
                }
            )
        st.session_state.projects = projects
        st.session_state.structured_projects = projects
    
    # ---------- TECHNICAL SKILLS ----------
    with tech_tab:
        st.markdown("#### Technical Skills")
        technical_skills = st.text_area(
            "List your technical skills",
            height=150,
            placeholder=(
                "Example:\n"
                "- Programming: Python, Java, C++\n"
                "- Web: HTML, CSS, JavaScript, React\n"
                "- Databases: MySQL, PostgreSQL\n"
                "- Tools: Git, Docker, VS Code"
            ),
        )
        if technical_skills:
            # This logic handles both comma-separated values and newlines
            raw_skills = technical_skills.replace('\n', ',').split(',')
            cleaned_skills = [skill.strip() for skill in raw_skills if skill.strip()]
            
            # Update the session state
            st.session_state.skills["technical"] = cleaned_skills

    # ---------- SOFT SKILLS ----------
    with soft_tab:
        st.markdown("#### Soft Skills")
        soft_skills = st.text_area(
            "List your soft skills",
            height=150,
            placeholder=(
                "Example:\n"
                "- Communication\n"
                "- Teamwork\n"
                "- Problem-solving\n"
                "- Time management\n"
                "- Leadership"
            ),
        )
        # FIX: Save to session state so PDF generator can see it
        if soft_skills:
            # Handles comma-separated or newline-separated inputs
            raw_soft = soft_skills.replace('\n', ',').split(',')
            cleaned_soft = [s.strip() for s in raw_soft if s.strip()]
            
            st.session_state.skills["soft"] = cleaned_soft
    # ---------- CERTIFICATIONS ----------
    with cert_tab:
        st.markdown("#### Certifications")
        certifications = st.text_area(
            "Certifications",
            height=180,
            placeholder=(
                "- AWS Certified Cloud Practitioner\n"
                "- Microsoft Azure Fundamentals\n"
                "- Any other relevant certifications..."
            ),
        )
        # FIX: Save to session state so PDF generator can see it
        if certifications:
            # Handles newline-separated inputs (bullets are cleaned in PDF generator)
            raw_certs = certifications.split('\n')
            cleaned_certs = [c.strip() for c in raw_certs if c.strip()]
            
            st.session_state.certifications = cleaned_certs
    # ---------- JOB DESCRIPTION ----------
    with jd_tab:
        st.markdown("#### Target Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=220,
            placeholder=(
                "Paste the JD so the AI can tailor your resume, portfolio and cover letter to this role."
            ),
        )
        st.session_state.job_description = job_description

    st.markdown("---")

# ---------- STEP 3: PARSE JOB DESCRIPTION (MANDATORY) ----------


    # ACTION BUTTONS
    c1, c2, c3 = st.columns(3)
    with c1:
        gen_resume = st.button(" Generate Resume", use_container_width=True)
    with c2:
        gen_portfolio = st.button(" Generate Portfolio", use_container_width=True)
    with c3:
        gen_cover = st.button(" Generate Cover Letter", use_container_width=True)

    # Build resume_text when any action is requested
    if gen_resume or gen_portfolio or gen_cover:
        resume_text = f"""
{name}
{email} | {phone}
LinkedIn: {linkedin}
GitHub: {github}

Summary
{summary}

Education
{education}

Experience
{experiences}

Project 
{projects}

Technical Skill
{technical_skills if technical_skills else "Not provided"}

Soft skill
{soft_skills if soft_skills else "Not provided"}

Certifications
{certifications}
""".strip()
#=============================================================================
        # Basic validation
        if not name or not email or not job_description.strip():
            st.error("Please fill at least Name, Email, and Job Description.")
        else:
            # RESUME
            if gen_resume:
                with st.spinner("Generating enhanced resume..."):
                    # Call AI directly using asyncio
                    data = asyncio.run(enhance_resume_ai(resume_text, job_description))

                    if "error" in data:
                        st.error(data["error"])
                    else:
                        # Store all AI data in session state
                        st.session_state["resume_data"] = data
                        # We don't need to manually set individual keys like 'ai_contact' 
                        # because your PDF generator reads from 'resume_data' now.
                        st.success("Resume generated. Check the 📄 Resume tab.")

            # PORTFOLIO GENERATION
            if gen_portfolio:
                # Portfolio is derived from the resume data. 
                # If resume data doesn't exist yet, we generate it.
                if not st.session_state.get("resume_data"):
                     with st.spinner("Generating resume data for portfolio..."):
                        data = asyncio.run(enhance_resume_ai(resume_text, job_description))
                        if "error" in data:
                            st.error(data["error"])
                        else:
                            st.session_state["resume_data"] = data
                            st.success("Portfolio ready! Check the 🌐 Portfolio tab.")
                else:
                    st.success("Portfolio is ready! Check the 🌐 Portfolio tab.")

            # COVER LETTER GENERATION
            if gen_cover:
                with st.spinner("Generating cover letter..."):
                    letter = asyncio.run(generate_cover_letter_ai(resume_text, job_description))
                    
                    if "Error" in letter:
                        st.error(letter)
                    else:
                        st.session_state["cover_letter"] = letter
                        st.success("Cover letter generated. Check the ✉️ Cover Letter tab.")
# ========== RESUME TAB ============
with tab_resume:
    st.subheader("📄 AI-Enhanced Resume")

    # 1. Gather Data from Session State (Manual Inputs)
    basic = st.session_state.basic_info
    job_desc = st.session_state.job_description
    
    # 2. Check for minimum required info
    if not basic.get("name") or not basic.get("email"):
        st.warning("⚠️ Please go to the 'Basic' tab and fill in your Name and Email first.")
        st.stop()
        
    # 3. Build the Text Payload for the AI
    # We combine what you typed in the tabs to send to the AI
    resume_text_payload = f"""
    Name: {basic.get('name')}
    Email: {basic.get('email')}
    Phone: {basic.get('phone')}
    LinkedIn: {basic.get('linkedin')}
    
    Summary:
    {basic.get('summary')}
    
    Experience:
    {st.session_state.experience}
    
    Projects:
    {st.session_state.projects}
    
    Education:
    {st.session_state.education}
    
    Skills:
    {st.session_state.skills}
    """

    # 4. Generate AI Data (Only if not already done or forced)
    #if st.button("✨ Generate AI Resume"):
    #   if not job_desc:
    #        st.error("❌ Please provide a Job Description in the 'Basic' tab first.")
    #    else:
    #        with st.spinner("🤖 AI is enhancing your resume..."):
    #            try:
    #                response = requests.post(
    #                    f"{API_BASE}/genai/enhance",
    #                    json={"resume_text": resume_text_payload, "job_description": job_desc},
    #                    timeout=60
    #                )
    #                if response.status_code == 200:
    #                    st.session_state.resume_data = response.json()
    #                    st.success("✅ Enhancement Complete!")
    #                    st.rerun() # Refresh to show the preview
    #                else:
    #                    st.error(f"Server Error: {response.text}")
    #            except requests.exceptions.RequestException as e:
    #                # This catches connection errors, timeouts, etc.
    #                st.error(f"❌ Connection Failed: {e}")
    #            except Exception as e:
    #                # This catches any other generic errors
    #                st.error(f"❌ An error occurred: {e}")

    # 5. Prepare Data for PDF (Merge AI Output + Manual Input)
    # If AI data exists, we use it. Otherwise, we fall back to manual input.
    ai_data = st.session_state.resume_data or {}
    
    final_resume_data = {
        "name": basic.get("name"), # Always use the name you typed
        "email": basic.get("email"),
        "phone": basic.get("phone"),
        "linkedin": basic.get("linkedin"),
        "github": basic.get("github"),
        "profile_image_url": basic.get("profile_image_url"),
        "resume_drive_link": st.session_state.resume_drive_link,

        # Prefer AI summary, fallback to manual
        "professional_summary": ai_data.get("summary") or basic.get("summary", ""),
        
        # Prefer AI education/experience if available and valid, else manual
        "education": ai_data.get("education") if ai_data.get("education") else st.session_state.education,
        "experience": normalize_experience(
            st.session_state.experience,
            ai_data.get("experience")
        ),

        "projects": normalize_projects(
            st.session_state.projects,
            ai_data.get("projects")
        ),

        "skills": st.session_state.skills,
        "certifications": (
            st.session_state.certifications
            if st.session_state.certifications
            else ai_data.get("certifications", [])
        ),
    }

# ============================
# BUILD PORTFOLIO DATA (REQUIRED)
# ============================

    # 6. PDF Preview & Download
    # This section replaces the JSON view
    if final_resume_data["name"]:
        import base64
        from pdf_generator import ResumePDFGenerator, ResumeDOCXGenerator
        
        # Generate PDF Bytes
        pdf_gen = ResumePDFGenerator()
        pdf_buffer = pdf_gen.generate_pdf(final_resume_data)
        pdf_bytes = pdf_buffer.getvalue()
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # Display PDF
        # Display PDF using the secure viewer
        st.markdown("### Preview")
        pdf_viewer(input=pdf_bytes, width=700, height=800)
        
        # Download Buttons
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"{final_resume_data['name']}_Resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with c2:
            docx_gen = ResumeDOCXGenerator()
            docx_buffer = docx_gen.generate_docx(final_resume_data)
            st.download_button(
                label="⬇️ Download Word",
                data=docx_buffer.getvalue(),
                file_name=f"{final_resume_data['name']}_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

#=====build portfolio data function=====
def build_portfolio_data(resume_data):
    return {
        # HERO
        "hero_name": resume_data.get("name"),
        "hero_title": resume_data.get("headline")
            or resume_data.get("target_role")
            or resume_data.get("professional_summary"),
        "hero_summary": resume_data.get("professional_summary"),
        "about_me": resume_data.get("professional_summary"),

        # PROFILE IMAGE
        "profile_image": resume_data.get("profile_image_url"),

        # CONTENT
        "education": resume_data.get("education") or [],

        "experience": [
            {
                "title": e.get("role"),
                "company": e.get("company"),
                "period": e.get("period"),
                "bullets": e.get("description", []),
            }
            for e in resume_data.get("experience", [])
        ],

        "projects": [
            {
                "name": p.get("title"),
                "duration": p.get("duration"),
                "tech_stack": p.get("tech_stack", []),
                "highlights": p.get("description", []),
                "github_link": p.get("github_link", ""),
            }
            for p in resume_data.get("projects", [])
        ],

        "skills": (
            resume_data.get("skills", {}).get("technical", [])
            + resume_data.get("skills", {}).get("soft", [])
        ),

        "certifications": resume_data.get("certifications", []),

        # CONTACT
        "contact_email": resume_data.get("email"),
        "contact_linkedin": resume_data.get("linkedin"),
        "contact_github": resume_data.get("github"),
        "resume_link": resume_data.get("resume_drive_link"),
    }

st.session_state.portfolio_data = build_portfolio_data(final_resume_data)

# ========== PORTFOLIO TAB ==========
with tab_portfolio:
    st.subheader("3. Portfolio View")

    if "portfolio_data" not in st.session_state:
        st.info("Generate a portfolio from the ✏️ Basic tab to see it here.")
    else:
        p = st.session_state["portfolio_data"]
        
        # Generate and display HTML
        portfolio_html = generate_portfolio_html(p)
        st.download_button(
            label="⬇️ Download Portfolio Website",
            data=portfolio_html,
            file_name=f"{p.get('hero_name', 'My')}_Portfolio.html",
            mime="text/html",
            use_container_width=True
        )
        st.components.v1.html(portfolio_html, height=1200, scrolling=True)


# ========== COVER LETTER TAB ==========
with tab_cover:
    st.subheader("4. Cover Letter")

    if "cover_letter" not in st.session_state:
        st.info("Generate a cover letter from the ✏️ Input tab to see it here.")
    else:
        letter = st.session_state["cover_letter"]
        st.text_area("Generated Cover Letter", value=letter, height=350)

        st.download_button(
            label="⬇️ Download Cover Letter (.txt)",
            data=letter,
            file_name="Cover_Letter.txt",
            mime="text/plain",
            use_container_width=True
            )