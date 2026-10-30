# CareerPath AI

AI-Enhanced Career Guidance System for Personalized Career Pathways.

The app scores a resume against a job description, then uses Google Gemini to recommend career pathways, a skills-gap learning plan, interview practice, and advisor chat. Built with FastAPI + Streamlit, spaCy, and Sentence Transformers.

## What it does

1. Upload a resume (PDF / DOC / DOCX) and optionally paste a job description.
2. The backend parses the resume with Gemini, extracts skills and experience, and compares them to the JD using semantic similarity.
3. You get an ATS score and a breakdown by category (formatting, keywords, content, skill validation, ATS compatibility).
4. Gemini then builds personalized career pathways, a 30/60/90-day learning roadmap, interview questions grounded in your resume, and a career advisor chat.
5. Past analyses can be saved to your account if Supabase is configured.

## Tech stack

- **Frontend:** Streamlit
- **Backend:** FastAPI (Python)
- **NLP:** spaCy (`en_core_web_md`), Sentence Transformers (`all-MiniLM-L6-v2`)
- **LLM:** Google Gemini API
- **Auth + Database:** Supabase (email/password and Google OAuth)
- **PDF report export:** WeasyPrint + Jinja2

## Project structure

```
ai-resume-ats-main/
├── backend/              FastAPI app, NLP services, Gemini career guidance
├── frontend/             Streamlit app, views, components
├── jupyter notebooks/    Research and dataset prep (not used at runtime)
├── ml model/             Exported ML artifacts
├── requirements.txt      Combined backend + frontend dependencies
└── .env.example          Template for environment variables
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd ai-resume-ats-main
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

WeasyPrint needs system libraries on Linux:

```bash
# Fedora
sudo dnf install -y cairo pango gdk-pixbuf2 libffi

# Debian / Ubuntu
sudo apt install -y libcairo2 libpango-1.0-0 libpangoft2-1.0-0 libffi-dev
```

### 3. Configure environment variables

Copy the template and fill in your keys:

```bash
cp .env.example .env
```

You need:

- A **Gemini** API key from [Google AI Studio](https://aistudio.google.com/apikey).
- (Optional) A **Supabase** project — `SUPABASE_URL`, `SUPABASE_KEY` (service role), and `SUPABASE_ANON_KEY` from Project Settings → API.
- (Optional) Google OAuth in the Supabase dashboard if you want Google sign-in.

The Streamlit frontend also reads Supabase config from `frontend/.streamlit/secrets.toml` when that file exists.

### 4. Run the backend

From the project root:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now at `http://localhost:8000`.

### 5. Run the frontend

In a new terminal (with the venv activated):

```bash
streamlit run frontend/streamlit_app.py
```

The app opens at `http://localhost:8501`.

## Notes

- **Never commit `.env` or `secrets.toml`** — they hold API keys.
- The first run downloads the Sentence Transformer model (~80 MB). It's cached afterwards.
- Resume scoring needs `GEMINI_API_KEY` because Gemini parses the resume and job description. Career Pathways, Learning Roadmap, Interview Coach, and Career Advisor also call Gemini.
- `jupyter notebooks/` and `ml model/` are for experimentation and aren't required to run the app.
