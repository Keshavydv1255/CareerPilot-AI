from sqlalchemy import Column, Integer, Text

from app.database.database import Base


class ReportSnapshot(Base):
    __tablename__ = "report_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False, default="resume.pdf")
    analysis_json = Column(Text, nullable=False)
    skill_gap_json = Column(Text, nullable=False)
    roadmap_json = Column(Text, nullable=False)
    questions_json = Column(Text, nullable=False)
