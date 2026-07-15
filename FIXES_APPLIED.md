# CareerPilot AI Stability Fix Pack

## Fixes included

- Gemini 429/503 retry handling with clean user-facing messages.
- Daily quota errors no longer expose raw API JSON in the interface.
- Local ATS fallback analysis when Gemini is temporarily unavailable.
- Resume analysis snapshot saved to SQLite after every upload.
- PDF report reuses the saved analysis instead of calling Gemini again.
- PDF includes ATS results, skills, strengths, weaknesses, roadmap, interview questions, and a complete extracted-resume appendix.
- Full-page loading overlay and disabled submit buttons while AI requests run.

## Important after upgrading

1. Copy your `.env` file into the project root.
2. Install requirements.
3. Start the server.
4. Upload the resume once again. This creates the new saved report snapshot.
5. Download the report from the result page.

The free Gemini daily request quota still belongs to Google and cannot be increased by application code. When the quota is exhausted, CareerPilot shows a clean message and resume analysis continues using the local fallback.
