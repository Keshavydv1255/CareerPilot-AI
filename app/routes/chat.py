from collections.abc import Generator

from fastapi import APIRouter, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

from app.services.analytics import increment_activity
from app.services.gemini_service import stream_gemini
from app.services.resume_db import get_resume_from_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={},
    )


@router.post("/chat/stream")
async def stream_ai_answer(
    question: str = Form(...),
):
    clean_question = question.strip()

    if not clean_question:
        return StreamingResponse(
            iter(["Please enter a career-related question."]),
            media_type="text/plain; charset=utf-8",
        )

    resume = get_resume_from_db()

    prompt = f"""
You are CareerPilot AI, an expert career mentor.

Use the uploaded resume whenever resume information is available.

Resume information:

{resume or "No resume has been uploaded yet."}

User question:

{clean_question}

Instructions:

1. Give accurate, practical and professional career advice.
2. Use short headings and bullet points.
3. Refer to resume information only when it is relevant.
4. Do not invent qualifications, experience, projects or achievements.
5. Clearly separate urgent improvements from long-term recommendations.
6. Keep the answer detailed but easy to understand.
"""

    def generate_response() -> Generator[str, None, None]:
        completed = False

        try:
            for chunk in stream_gemini(prompt):
                yield chunk

            completed = True

        finally:
            if completed:
                increment_activity("ai_chats")

    return StreamingResponse(
        generate_response(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )