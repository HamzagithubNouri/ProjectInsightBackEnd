from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class SchoolClass(Base):
    """Une classe (ex: 'INF3135 - Construction de logiciels') supervisee par
    un seul enseignant. Nommee 'SchoolClass' et pas 'Class' car 'class' est
    un mot reserve en Python."""
    __tablename__ = "school_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course_code = Column(String, nullable=True)
    year = Column(String, nullable=False)  # ex: "H2025" (semestre)
    max_students = Column(Integer, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    teams = relationship("Team", back_populates="school_class")
