from app.database.database import SessionLocal
from app.models.activity import Activity

ACTIVITIES = (
    "resume_analyses",
    "ai_chats",
    "interviews",
    "cover_letters",
    "job_matches",
    "resume_improvements",
    "reports",
)


def increment_activity(name: str) -> None:
    if name not in ACTIVITIES:
        return
    db = SessionLocal()
    try:
        item = db.query(Activity).filter(Activity.name == name).first()
        if item is None:
            item = Activity(name=name, count=1)
            db.add(item)
        else:
            item.count += 1
        db.commit()
    finally:
        db.close()


def get_activity_counts() -> dict[str, int]:
    counts = {name: 0 for name in ACTIVITIES}
    db = SessionLocal()
    try:
        for item in db.query(Activity).all():
            if item.name in counts:
                counts[item.name] = item.count
    finally:
        db.close()
    return counts
