# 🤖 AI Resume Builder

> An AI-powered resume, portfolio, and cover letter generator built with **Streamlit** + **FastAPI**, backed by **OpenRouter LLMs**.

---

## ✨ Features

- **AI-Enhanced Resume** — Paste your details and a job description; the AI rewrites and tailors your resume to match the role
- **PDF & DOCX Export** — Download your resume as a professional PDF (Jake Ryan style) or a Word document
- **Portfolio Generator** — Instantly generates a downloadable personal portfolio website (HTML) from your resume data
- **Cover Letter Generator** — Creates a tailored, job-specific cover letter in seconds
- **Manual Input Forms** — Tab-by-tab structured input for Basic Info, Education, Experience, Projects, Skills, and Certifications
- **Live PDF Preview** — In-browser PDF preview before downloading
- **Unicode Sanitization** — Automatic cleanup of smart quotes, dashes, and special characters for clean PDF rendering

---

## 🖼️ App Overview

The app is organized into **4 main tabs**:

| Tab | Description |
|---|---|
| **Basic** | Enter all your information across sub-tabs (Info, Education, Experience, Projects, Skills, Certifications, Job Description) |
| **Resume** | Preview your AI-enhanced resume as PDF and download as PDF or Word |
| **Portfolio** | View and download an auto-generated personal portfolio website |
| **Cover Letter** | View and download an AI-written cover letter |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) |
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| AI / LLM | [OpenRouter API](https://openrouter.ai/) (`nvidia/nemotron-3-nano-30b-a3b:free`) |
| PDF Generation | [ReportLab](https://www.reportlab.com/) |
| DOCX Generation | [python-docx](https://python-docx.readthedocs.io/) |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) |
| HTTP Client | [httpx](https://www.python-httpx.org/) (async) |

---

## 📁 Project Structure

```
ai-resume-builder/
│
├── app.py                  # Streamlit frontend (UI, session state, tab logic)
├── main.py                 # FastAPI backend (API routes: /genai/enhance, /genai/cover-letter, /genai/portfolio)
├── ai_utils.py             # Async AI helper functions (OpenRouter calls)
├── pdf_generator.py        # ResumePDFGenerator and ResumeDOCXGenerator classes
├── portfolio.py            # generate_portfolio_html() — builds HTML portfolio page
├── schemas.py              # Pydantic models for all request/response data
├── requirements.txt        # Python dependencies
└── .gitignore
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-resume-builder.git
cd ai-resume-builder
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> Get a free API key at [openrouter.ai](https://openrouter.ai/)

### 5. Run the FastAPI backend

```bash
uvicorn main:app --reload --port 8000
```

### 6. Run the Streamlit frontend

In a separate terminal:

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

---

## 🔌 API Endpoints

The FastAPI backend exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/health` | Service status with timestamp |
| `GET` | `/version` | App version info |
| `POST` | `/resumes/test` | Test resume data submission |
| `POST` | `/genai/enhance` | AI-enhance resume against a job description |
| `POST` | `/genai/cover-letter` | Generate a tailored cover letter |
| `POST` | `/genai/portfolio` | Generate portfolio data from resume |

### Example request — `/genai/enhance`

```json
POST /genai/enhance
{
  "resume_text": "Your raw resume text here...",
  "job_description": "The job description to tailor towards..."
}
```

---

## ⚙️ How It Works

1. **User fills in** their details across the input tabs in Streamlit
2. **Resume text is assembled** from session state and sent to the AI
3. **OpenRouter LLM** rewrites and enhances the content to match the job description, returning structured JSON
4. **AI output is merged** with manual input (user's structure is preserved; AI enriches bullet points)
5. **PDF/DOCX** is generated using ReportLab and python-docx
6. **Portfolio HTML** is built from the same data and made available for download

---

## 📦 Requirements

```
fastapi
uvicorn[standard]
pydantic
python-dotenv
python-multipart
httpx
requests
aiohttp
pandas
numpy
reportlab
jinja2
python-docx
streamlit>=1.40.0
extra-streamlit-components
streamlit-pdf-viewer
altair<5
```

---

## 🙏 Acknowledgements

- Resume layout inspired by the popular [Jake Ryan LaTeX Resume Template](https://www.overleaf.com/latex/templates/jakes-resume/syzfjbzwjncs)
- LLM inference powered by [OpenRouter](https://openrouter.ai/)
