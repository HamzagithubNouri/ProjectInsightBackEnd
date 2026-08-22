from typing import Optional, Literal
from pydantic import BaseModel, Field

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


# Ce que le LLM doit produire (utilise par le parser LangChain, pas expose tel quel a l'API)
class LLMReviewOutput(BaseModel):
    quality_score: float = Field(description="Score global de qualite du code, de 0 a 10")
    findings: list[Finding]


class CodeReviewResult(BaseModel):
    filename: Optional[str] = None
    quality_score: float
    findings: list[Finding]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


# --- Auto-fix (appel separe, declenche a la demande) ---

class AutoFixRequest(BaseModel):
    code: str
    filename: Optional[str] = None


class AutoFixResult(BaseModel):
    filename: Optional[str] = None
    corrected_code: str
    summary_of_changes: str
    syntax_valid: Optional[bool] = None  # None = langage non verifiable (pas Python)
    syntax_note: Optional[str] = None    # detail de l'erreur si syntax_valid=False