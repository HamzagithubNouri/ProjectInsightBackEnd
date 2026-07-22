from typing import Optional
from pydantic import BaseModel


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
