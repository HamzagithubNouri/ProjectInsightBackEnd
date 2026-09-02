from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.ai_review_schema import Severity


class ActivityDayOut(BaseModel):
    day: str
    date: str
    commits: int


class RecentFindingOut(BaseModel):
    title: str
    severity: Severity
    filename: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True