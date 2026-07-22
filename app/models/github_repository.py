from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class GithubRepository(Base):
    """Le repo GitHub connecte par une equipe (via son team leader ou un membre).
    Un seul repo actif par equipe pour le MVP (team_id unique)."""
    __tablename__ = "github_repositories"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True, nullable=False)
    github_url = Column(String, nullable=False)
    branch = Column(String, nullable=False, default="main")
    github_username = Column(String, nullable=True)
    connected_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="connected")
    connected_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team")
