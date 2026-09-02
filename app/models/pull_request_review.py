from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class PullRequestReview(Base):
    """Stocke le RESULTAT COMPLET de la derniere review d'une PR (pas d'historique
    multi-versions : une seule ligne par (team_id, pr_number), ecrasee a chaque
    nouvelle analyse via Review PR)."""
    __tablename__ = "pull_request_reviews"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String, nullable=False)
    files = Column(JSON, nullable=False)              # liste de PRFileReview serialisee
    overall_quality_score = Column(Float, nullable=False)
    summary = Column(String, nullable=False)
    recurring_issues = Column(JSON, nullable=False)
    critical_count = Column(Integer, nullable=False)
    high_count = Column(Integer, nullable=False)
    medium_count = Column(Integer, nullable=False)
    low_count = Column(Integer, nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("team_id", "pr_number", name="uq_team_pr_review"),)