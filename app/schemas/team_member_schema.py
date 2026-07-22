from datetime import datetime
from pydantic import BaseModel


class TeamMemberOut(BaseModel):
    id: int
    team_id: int
    student_id: int
    joined_at: datetime

    class Config:
        from_attributes = True
