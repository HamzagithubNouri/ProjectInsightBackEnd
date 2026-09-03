from typing import Optional
from pydantic import BaseModel
from app.schemas.team_schema import TeamSummaryOut

class ClassCreate(BaseModel):
    name: str
    course_code: Optional[str] = None
    year: str
    max_students: Optional[int] = None


class ClassOut(BaseModel):
    id: int
    name: str
    course_code: Optional[str] = None
    year: str
    max_students: Optional[int] = None
    teacher_id: int

    class Config:
        from_attributes = True


class ClassSummaryOut(BaseModel):
    id: int
    name: str
    student_count: int
    team_count: int


class ClassDetailOut(BaseModel):
    id: int
    name: str
    student_count: int
    team_count: int
    teams: list[TeamSummaryOut]