from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from app.services.gemini_service import ask_gemini
from app.services.analytics import increment_activity
from app.services.resume_db import get_resume_from_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "question": "",
            "answer": ""
        }
    )


@router.post("/chat")
async def ask_ai(
    request: Request,
    question: str = Form(...)
):

    resume = get_resume_from_db()

    prompt = f"""
You are CareerGPT.

You are an expert Career Mentor.

If resume information is available,
use it while answering.

Resume:

{resume}

Question:

{question}

Give detailed professional advice.
"""

    answer = ask_gemini(prompt)
    increment_activity("ai_chats")

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "question": question,
            "answer": answer
        }
    )