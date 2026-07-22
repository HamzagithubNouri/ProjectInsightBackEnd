from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "admin" | "teacher" | "student"

    # Rempli seulement pour role == "student" : la classe dans laquelle
    # le prof l'a inscrit (independant de son equipe, voir Team/TeamMember)
    school_class_id = Column(Integer, ForeignKey("school_classes.id"), nullable=True)
    school_class = relationship("SchoolClass", foreign_keys=[school_class_id])

    created_at = Column(DateTime(timezone=True), server_default=func.now())
