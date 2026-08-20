from typing import Optional, Literal
from pydantic import BaseModel

Severity = Literal["critical", "high", "medium", "low"]


class CodeReviewRequest(BaseModel):
    code: str
    filename: Optional[str] = None  # ex: "src/auth/login.py" - sert juste a l'affichage


class Finding(BaseModel):
    severity: Severity
    title: str
    description: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    suggested_fix: Optional[str] = None


class CodeReviewResult(BaseModel):
    filename: Optional[str] = None
    findings: list[Finding]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
