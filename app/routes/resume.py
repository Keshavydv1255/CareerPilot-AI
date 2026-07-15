import os
import shutil

from fastapi import APIRouter, UploadFile, File, Request
from fastapi.templating import Jinja2Templates

from app.services.pdf_parser import extract_text_from_pdf
from app.services.resume_analyzer import ResumeAnalyzer
from app.services.skill_gap import SkillGapAnalyzer
from app.services.roadmap_generator import RoadmapGenerator
from app.services.resume_db import save_resume_to_db
from app.services.interview_generator import InterviewGenerator
from app.services.analytics import increment_activity
from app.services.report_snapshot import save_report_snapshot

router = APIRouter()

templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed."}

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text_from_pdf(file_path)
    save_resume_to_db(resume_text)

    analysis = ResumeAnalyzer.analyze(resume_text)

    skill_gap = SkillGapAnalyzer.analyze(
        analysis["skills"]
    )

    roadmap = RoadmapGenerator.generate(
        skill_gap
    )

    questions = InterviewGenerator.generate(
        resume_text
    )
    save_report_snapshot(file.filename, analysis, skill_gap, roadmap, questions)
    increment_activity("resume_analyses")

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "filename": file.filename,
            "resume_text": resume_text,
            "analysis": analysis,
            "skill_gap": skill_gap,
            "roadmap": roadmap,
            "questions": questions
        }
    )