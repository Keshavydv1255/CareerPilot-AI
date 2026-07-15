import json

from app.database.database import SessionLocal
from app.models.report_snapshot import ReportSnapshot


def save_report_snapshot(filename: str, analysis: dict, skill_gap: dict, roadmap: list, questions: dict) -> None:
    db = SessionLocal()
    try:
        db.query(ReportSnapshot).delete()
        db.add(
            ReportSnapshot(
                filename=filename or "resume.pdf",
                analysis_json=json.dumps(analysis, ensure_ascii=False),
                skill_gap_json=json.dumps(skill_gap, ensure_ascii=False),
                roadmap_json=json.dumps(roadmap, ensure_ascii=False),
                questions_json=json.dumps(questions, ensure_ascii=False),
            )
        )
        db.commit()
    finally:
        db.close()


def get_report_snapshot() -> dict | None:
    db = SessionLocal()
    try:
        row = db.query(ReportSnapshot).first()
        if row is None:
            return None
        return {
            "filename": row.filename,
            "analysis": json.loads(row.analysis_json),
            "skill_gap": json.loads(row.skill_gap_json),
            "roadmap": json.loads(row.roadmap_json),
            "questions": json.loads(row.questions_json),
        }
    finally:
        db.close()
