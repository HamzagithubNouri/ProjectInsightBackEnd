from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.schemas.ai_review_schema import (
    CodeReviewRequest,
    CodeReviewResult,
    AutoFixRequest,
    AutoFixResult,
)
from app.services import ai_review_service
from app.auth.dependencies import get_current_user

# Accessible a tout utilisateur authentifie (student ET teacher), pas de role impose
router = APIRouter(
    prefix="/ai-review",
    tags=["AI Review"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/analyze", response_model=CodeReviewResult)
def analyze_pasted_code(data: CodeReviewRequest):
    """Utilise par l'onglet 'Paste Code'."""
    return ai_review_service.review_code(data.code, data.filename)


@router.post("/analyze-file", response_model=CodeReviewResult)
async def analyze_uploaded_file(file: UploadFile = File(...)):
    """Utilise par l'onglet 'Upload File'. Accepte n'importe quel langage
    (le fichier est juste lu comme texte, le LLM detecte le langage lui-meme)."""
    raw_bytes = await file.read()
    try:
        code = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Fichier illisible (encodage non supporte). Utilise un fichier texte (.py, .js, .java, etc.)",
        )
    return ai_review_service.review_code(code, file.filename)


@router.post("/fix", response_model=AutoFixResult)
def generate_fix(data: AutoFixRequest):
    """Genere une version corrigee complete du fichier — appel plus lourd,
    a declencher explicitement depuis le frontend (bouton separe de la review)."""
    return ai_review_service.generate_fixed_code(data.code, data.filename)
