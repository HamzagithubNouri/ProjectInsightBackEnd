from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
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


class PRFileReview(BaseModel):
    filename: str
    findings: list[Finding]


class DiffChunkFindings(BaseModel):
    """Sortie intermediaire du LLM pour un morceau de diff (pas exposee telle quelle a l'API)."""
    findings: list[Finding]


class PRSynthesisOutput(BaseModel):
    """Sortie intermediaire du LLM pour la synthese finale (pas exposee telle quelle a l'API)."""
    overall_quality_score: float = Field(description="Score global de qualite du PR entier, de 0 a 10")
    summary: str = Field(description="Resume executif en 3-5 phrases des problemes principaux du PR")
    recurring_issues: list[str] = Field(description="Problemes qui reviennent dans plusieurs fichiers")


class PRReviewResult(BaseModel):
    pr_number: int
    pr_title: str
    files: list[PRFileReview]
    overall_quality_score: float
    summary: str
    recurring_issues: list[str]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    
# Ce que le LLM doit produire (utilise par le parser LangChain, pas expose tel quel a l'API)
class EducationalEnrichment(BaseModel):
    educational_explanation: str
    related_concepts: list[str]


# Ce qui est renvoye a l'API : le finding original (inchange, controle par le code Python)
# + l'enrichissement genere par le LLM
class EnrichedFinding(BaseModel):
    finding: Finding
    educational_explanation: str
    related_concepts: list[str]


class PRSummaryOut(BaseModel):
    number: int
    title: str
    state: str
    already_reviewed: bool
    quality_score: Optional[float] = None
    reviewed_at: Optional[datetime] = None    