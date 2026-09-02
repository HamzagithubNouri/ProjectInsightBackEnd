from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class ReviewHistoryEntry(Base):
    __tablename__ = "review_history_entries"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_type = Column(String, nullable=False)  # "paste" | "file" | "pr"
    filename = Column(String, nullable=True)
    finding_title = Column(String, nullable=False)
    finding_severity = Column(String, nullable=False)
    finding_description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())