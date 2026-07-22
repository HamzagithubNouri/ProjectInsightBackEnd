from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("school_classes.id"), nullable=False)
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    school_class = relationship("SchoolClass", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")
