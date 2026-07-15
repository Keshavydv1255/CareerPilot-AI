import os

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

from app.services.analytics import increment_activity
from app.services.interview_generator import InterviewGenerator
from app.services.report_generator import generate_report
from app.services.report_snapshot import get_report_snapshot
from app.services.resume_analyzer import ResumeAnalyzer
from app.services.resume_db import get_resume_from_db
from app.services.roadmap_generator import RoadmapGenerator
from app.services.skill_gap import SkillGapAnalyzer

router = APIRouter()
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@router.get("/report/download")
async def download_report():
    resume_text = get_resume_from_db()
    if not resume_text.strip():
        return RedirectResponse(url="/upload", status_code=303)

    snapshot = get_report_snapshot()

    if snapshot:
        filename = snapshot["filename"]
        analysis = snapshot["analysis"]
        skill_gap = snapshot["skill_gap"]
        roadmap = snapshot["roadmap"]
        questions = snapshot["questions"]
    else:
        # Backward-compatible fallback for a database created before snapshots existed.
        filename = "resume.pdf"
        analysis = ResumeAnalyzer.analyze(resume_text)
        skill_gap = SkillGapAnalyzer.analyze(analysis.get("skills", []))
        roadmap = RoadmapGenerator.generate(skill_gap)
        questions = InterviewGenerator.generate(resume_text)

    path = os.path.join(REPORT_DIR, "CareerPilot_AI_Resume_Report.pdf")
    generate_report(
        path,
        analysis,
        skill_gap,
        roadmap,
        questions,
        resume_text,
        original_filename=filename,
    )
    increment_activity("reports")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="CareerPilot_AI_Resume_Report.pdf",
    )
