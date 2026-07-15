# CareerPilot AI

CareerPilot AI is a full-stack, Gemini-powered career assistant built with FastAPI, Jinja2, SQLite and Bootstrap.

## Features
- AI resume analysis and ATS score
- Resume-aware career chat
- Interview simulator with answer evaluation
- Job description matcher
- Resume improver
- Cover letter generator
- Downloadable PDF report
- SQLite-backed resume persistence and live dashboard analytics
- Responsive SaaS-style interface with dark mode

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Gemini API key.
4. Start the app: `python -m uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000`

## Security
The `.env` file is ignored by Git. Never commit API keys.
