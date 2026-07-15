from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from app.services.gemini_service import ask_gemini
from app.services.analytics import increment_activity
from app.services.resume_db import get_resume_from_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/resume-improver")
async def resume_improver_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="resume_improver.html",
        context={
            "target_role": "",
            "improved_resume": "",
            "error": ""
        }
    )


@router.post("/resume-improver")
async def improve_resume(
    request: Request,
    target_role: str = Form(...)
):
    resume = get_resume_from_db()

    if not resume.strip():
        return templates.TemplateResponse(
            request=request,
            name="resume_improver.html",
            context={
                "target_role": target_role,
                "improved_resume": "",
                "error": "Please upload your resume before using the Resume Improver."
            }
        )

    prompt = f"""
You are CareerGPT, an expert resume writer and ATS specialist.

Improve the candidate's resume for this target role:

Target Role:
{target_role}

Original Resume:
--------------------------------
{resume}
--------------------------------

Create a polished improved resume draft.

Requirements:

1. Do not invent qualifications, companies, projects, achievements or experience.
2. Correct grammar and improve professional wording.
3. Use strong action verbs.
4. Make project and internship descriptions more impactful.
5. Improve ATS compatibility for the target role.
6. Add measurable wording only when supported by the original resume.
7. Keep the resume concise and suitable for a student or fresher.
8. Clearly organize the output using these headings:

PROFESSIONAL SUMMARY

EDUCATION

TECHNICAL SKILLS

INTERNSHIPS / EXPERIENCE

PROJECTS

CERTIFICATIONS

ACHIEVEMENTS

ATS KEYWORDS TO ADD

FINAL IMPROVEMENT TIPS

Write plain text only. Do not use Markdown tables.
"""

    improved_resume = ask_gemini(prompt)
    increment_activity("resume_improvements")

    return templates.TemplateResponse(
        request=request,
        name="resume_improver.html",
        context={
            "target_role": target_role,
            "improved_resume": improved_resume,
            "error": ""
        }
    )