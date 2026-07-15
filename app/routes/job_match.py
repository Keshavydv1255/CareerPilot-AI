import json

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from app.services.gemini_service import ask_gemini
from app.services.analytics import increment_activity
from app.services.resume_db import get_resume_from_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def safe_json_response(response: str) -> dict:
    try:
        start = response.find("{")
        end = response.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found.")

        return json.loads(response[start:end])

    except (json.JSONDecodeError, ValueError):
        return {
            "match_score": 0,
            "recommendation": "The AI response could not be processed.",
            "matching_skills": [],
            "missing_skills": [],
            "strengths": [],
            "risks": [],
            "preparation_plan": []
        }


@router.get("/job-match")
async def job_match_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="job_match.html",
        context={
            "job_description": "",
            "result": None,
            "error": ""
        }
    )


@router.post("/job-match")
async def analyze_job_match(
    request: Request,
    job_description: str = Form(...)
):
    resume = get_resume_from_db()

    if not resume.strip():
        return templates.TemplateResponse(
            request=request,
            name="job_match.html",
            context={
                "job_description": job_description,
                "result": None,
                "error": "Please upload your resume before using the Job Matcher."
            }
        )

    prompt = f"""
You are CareerGPT, an expert ATS recruiter and career advisor.

Compare the candidate's resume with the job description.

Return ONLY valid JSON using exactly this structure:

{{
    "match_score": 0,
    "recommendation": "",
    "matching_skills": [],
    "missing_skills": [],
    "strengths": [],
    "risks": [],
    "preparation_plan": []
}}

Rules:
- match_score must be an integer from 0 to 100.
- Do not invent skills or experience.
- matching_skills must contain skills present in both the resume and job description.
- missing_skills must contain important job requirements absent from the resume.
- recommendation must clearly say whether the candidate should apply.
- preparation_plan should contain practical preparation steps.
- Return JSON only. Do not use Markdown code fences.

Candidate Resume:
-------------------------
{resume}
-------------------------

Job Description:
-------------------------
{job_description}
-------------------------
"""

    response = ask_gemini(prompt)
    result = safe_json_response(response)
    increment_activity("job_matches")

    return templates.TemplateResponse(
        request=request,
        name="job_match.html",
        context={
            "job_description": job_description,
            "result": result,
            "error": ""
        }
    )