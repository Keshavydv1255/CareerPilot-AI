from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from app.services.gemini_service import ask_gemini
from app.services.analytics import increment_activity
from app.services.resume_db import get_resume_from_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/cover-letter")
async def cover_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cover_letter.html",
        context={
            "cover_letter": ""
        }
    )


@router.post("/cover-letter")
async def generate_cover_letter(
    request: Request,
    company: str = Form(...),
    role: str = Form(...)
):

    resume = get_resume_from_db()
    prompt = f"""
You are an expert HR.

Using this resume:

{resume}

Generate a professional ATS-friendly cover letter.

Company:
{company}

Role:
{role}

The cover letter should be around 300 words.
"""

    answer = ask_gemini(prompt)
    increment_activity("cover_letters")

    return templates.TemplateResponse(
        request=request,
        name="cover_letter.html",
        context={
            "cover_letter": answer
        }
    )