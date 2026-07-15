from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text

from app.database.database import Base


class Resume(Base):

    __tablename__ = "resumes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    content = Column(
        Text,
        nullable=False
    )