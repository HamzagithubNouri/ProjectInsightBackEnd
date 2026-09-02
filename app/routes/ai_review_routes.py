from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.schemas.ai_review_schema import (
    CodeReviewRequest,
    CodeReviewResult,
    AutoFixRequest,
    AutoFixResult,
)
from app.services import ai_review_service
from app.auth.dependencies import get_current_user
from app.rag.rag_review_service import enrich_findings

router = APIRouter(
    prefix="/ai-review",
    tags=["AI Review"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/analyze", response_model=CodeReviewResult)
def analyze_pasted_code(data: CodeReviewRequest, current_user=Depends(get_current_user)):
    """Utilise par l'onglet 'Paste Code'."""
    return ai_review_service.review_code(data.code, data.filename, student_id=current_user.id)


@router.post("/analyze-file", response_model=CodeReviewResult)
async def analyze_uploaded_file(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """Utilise par l'onglet 'Upload File'."""
    raw_bytes = await file.read()
    try:
        code = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Fichier illisible (encodage non supporte). Utilise un fichier texte (.py, .js, .java, etc.)",
        )
    return ai_review_service.review_code(code, file.filename, student_id=current_user.id)


@router.post("/fix", response_model=AutoFixResult)
def generate_fix(data: AutoFixRequest):
    """Genere une version corrigee complete du fichier."""
    return ai_review_service.generate_fixed_code(data.code, data.filename)


@router.post("/analyze-with-rag")
def analyze_pasted_code_with_rag(data: CodeReviewRequest, current_user=Depends(get_current_user)):
    """Comme /analyze, mais enrichit les findings critical/high avec le RAG."""
    result = ai_review_service.review_code(data.code, data.filename, student_id=current_user.id)
    enriched = enrich_findings(result.findings)
    return {
        "review": result,
        "enriched_findings": enriched,
    }