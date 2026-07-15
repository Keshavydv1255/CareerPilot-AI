from sqlalchemy import Column, Integer, String
from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    count = Column(Integer, nullable=False, default=0)
