from app.database.database import SessionLocal
from app.models.resume import Resume


def save_resume_to_db(resume_text: str):

    db = SessionLocal()

    try:

        db.query(Resume).delete()

        new_resume = Resume(
            content=resume_text
        )

        db.add(new_resume)

        db.commit()

    finally:

        db.close()


def get_resume_from_db():

    db = SessionLocal()

    try:

        resume = db.query(Resume).first()

        if resume:

            return resume.content

        return ""

    finally:

        db.close()