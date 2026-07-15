from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from app.services.gemini_service import ask_gemini
from app.services.resume_db import get_resume_from_db
from app.services.analytics import increment_activity

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/interview")
async def interview_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="interview.html",
        context={
            "question": "",
            "feedback": "",
            "interview_type": "Resume Based",
            "difficulty": "Medium"
        }
    )


@router.post("/interview/start")
async def start_interview(
    request: Request,
    interview_type: str = Form(...),
    difficulty: str = Form(...)
):
    resume = get_resume_from_db()

    if not resume.strip():
        return templates.TemplateResponse(
            request=request,
            name="interview.html",
            context={
                "question": "",
                "feedback": "Please upload your resume before starting a resume-based interview.",
                "interview_type": interview_type,
                "difficulty": difficulty
            }
        )

    prompt = f"""
You are CareerGPT, an expert technical interviewer.

Candidate resume:
-------------------------
{resume}
-------------------------

Interview type: {interview_type}
Difficulty: {difficulty}

Generate exactly ONE suitable interview question.

Requirements:
- Base the question on the selected interview type.
- Use the candidate's resume where relevant.
- Do not provide an answer.
- Do not add headings or explanations.
- Return only the interview question.
"""

    question = ask_gemini(prompt)

    return templates.TemplateResponse(
        request=request,
        name="interview.html",
        context={
            "question": question,
            "feedback": "",
            "interview_type": interview_type,
            "difficulty": difficulty
        }
    )


@router.post("/interview/evaluate")
async def evaluate_answer(
    request: Request,
    question: str = Form(...),
    candidate_answer: str = Form(...),
    interview_type: str = Form(...),
    difficulty: str = Form(...)
):
    resume = get_resume_from_db()

    prompt = f"""
You are CareerGPT, an expert interview evaluator.

Candidate resume:
-------------------------
{resume}
-------------------------

Interview type: {interview_type}
Difficulty: {difficulty}

Interview question:
{question}

Candidate answer:
{candidate_answer}

Evaluate the answer using this exact structure:

Score: X/10

What Was Good:
- point
- point

What Can Be Improved:
- point
- point

Better Sample Answer:
Write a concise but strong model answer.

Next Preparation Tip:
Give one practical preparation tip.

Be honest, constructive and professional.
"""

    feedback = ask_gemini(prompt)
    increment_activity("interviews")

    return templates.TemplateResponse(
        request=request,
        name="interview.html",
        context={
            "question": question,
            "feedback": feedback,
            "interview_type": interview_type,
            "difficulty": difficulty
        }
    )