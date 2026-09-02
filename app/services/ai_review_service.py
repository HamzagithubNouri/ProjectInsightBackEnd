import re
import ast
import json
from typing import Optional
from fastapi import HTTPException
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain.output_parsers import OutputFixingParser
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.database import SessionLocal
from app.models.review_history import ReviewHistoryEntry
from app.rag.vectorstore import get_review_history_store
from langchain_core.documents import Document as LangchainDocument

from app.config import settings
from app.schemas.ai_review_schema import (
    Finding,
    LLMReviewOutput,
    CodeReviewResult,
    AutoFixResult,
    PRFileReview,
    DiffChunkFindings,
    PRSynthesisOutput,
    PRReviewResult,
)
from app.models.pull_request_review import PullRequestReview
# --- LLM et parsers, instancies une seule fois au chargement du module ---

_llm = ChatOllama(
    base_url=settings.ollama_url,
    model=settings.ollama_model,
    temperature=0.2,  # faible temperature : analyse, pas creativite
)

_base_parser = PydanticOutputParser(pydantic_object=LLMReviewOutput)

# Si le JSON du LLM est malforme, on relance UN appel LLM supplementaire
# pour qu'il se corrige lui-meme selon le schema attendu (max 1 tentative
# pour eviter qu'un modele qui se trompe systematiquement ne boucle).
_fixing_parser = OutputFixingParser.from_llm(parser=_base_parser, llm=_llm, max_retries=1)

_review_prompt = PromptTemplate(
    template="""Tu es un reviewer de code senior. Analyse le code suivant, quel que soit
son langage, et identifie UNIQUEMENT les problemes reels et significatifs : bugs, failles
de securite, anti-patterns serieux. Ignore les micro-styles subjectifs (choix de print vs
autre fonction d'affichage, etc.) sauf s'ils causent un vrai probleme.

Ne cree jamais plusieurs findings differents pour le meme probleme sous des titres
differents : consolide-les en un seul finding.

Indique le numero de ligne EXACT ou chaque probleme se trouve, en te basant sur les
numeros de ligne reels du code fourni ci-dessous (compte les lignes toi-meme, en commencant
a 1 pour la premiere ligne).

Reponds TOUJOURS en francais, quelle que soit la langue des noms de variables/fonctions.

{format_instructions}

Code a analyser (fichier: {filename}) :
{code}
""",
    input_variables=["filename", "code"],
    partial_variables={"format_instructions": _base_parser.get_format_instructions()},
)

_review_chain = _review_prompt | _llm | _fixing_parser

def _persist_and_embed_findings(findings, filename: str | None, source_type: str = "paste", student_id: int | None = None):
    db = SessionLocal()
    docs_to_embed = []
    try:
        for f in findings:
            entry = ReviewHistoryEntry(
                student_id=student_id,
                source_type=source_type,
                filename=filename,
                finding_title=f.title,
                finding_severity=f.severity,
                finding_description=f.description,
            )
            db.add(entry)
            docs_to_embed.append(LangchainDocument(
                page_content=f"{f.title}\n{f.description}",
                metadata={"severity": f.severity, "filename": filename or ""},
            ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    if docs_to_embed:
        try:
            get_review_history_store().add_documents(docs_to_embed)
        except Exception:
            pass


def review_code(code: str, filename: str | None = None, student_id: int | None = None) -> CodeReviewResult:
    if not code.strip():
        raise HTTPException(status_code=400, detail="Le code fourni est vide")

    try:
        result: LLMReviewOutput = _review_chain.invoke(
            {"filename": filename or "sans nom", "code": code}
        )
    except OutputParserException:
        raise HTTPException(
            status_code=502,
            detail="Le modele a renvoye une reponse mal formee malgre la correction automatique. Reessaie.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Impossible de contacter Ollama ou reponse invalide : {exc}",
        )

    findings = result.findings
    score = max(0.0, min(10.0, result.quality_score))
    _persist_and_embed_findings(findings, filename, source_type="paste", student_id=student_id)

    return CodeReviewResult(
        filename=filename,
        quality_score=round(score, 1),
        findings=findings,
        critical_count=sum(1 for f in findings if f.severity == "critical"),
        high_count=sum(1 for f in findings if f.severity == "high"),
        medium_count=sum(1 for f in findings if f.severity == "medium"),
        low_count=sum(1 for f in findings if f.severity == "low"),
    )


# --- Auto-fix : appel separe, declenche a la demande depuis le frontend ---

_fix_prompt = PromptTemplate(
    template="""Tu es un expert en correction de code. Voici un fichier avec des problemes.
Reecris le fichier ENTIER en corrigeant tous les problemes que tu identifies,
sans changer le comportement voulu du programme. Garde le meme style et la meme structure
generale la ou c'est possible.

Reponds UNIQUEMENT avec le code corrige complet, sans explication, sans balises markdown.

Fichier (nom: {filename}) :
{code}
""",
    input_variables=["filename", "code"],
)

_fix_chain = _fix_prompt | _llm


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    return text.strip()


_PYTHON_EXTENSIONS = (".py",)


def _is_python_file(filename: str | None) -> bool:
    if not filename:
        return False
    return filename.lower().endswith(_PYTHON_EXTENSIONS)


def _check_python_syntax(code: str) -> tuple[bool, str | None]:
    """Retourne (valide, message_erreur). Applicable UNIQUEMENT au Python."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as exc:
        return False, f"Ligne {exc.lineno}: {exc.msg}"


_fix_retry_prompt = PromptTemplate(
    template="""Le code que tu as genere contient une erreur de syntaxe Python :
{syntax_error}

Corrige UNIQUEMENT cette erreur de syntaxe, en gardant le reste du code identique.
Reponds UNIQUEMENT avec le code corrige complet, sans explication, sans balises markdown.

Code a corriger (fichier: {filename}) :
{code}
""",
    input_variables=["filename", "code", "syntax_error"],
)

_fix_retry_chain = _fix_retry_prompt | _llm


def generate_fixed_code(code: str, filename: str | None = None) -> AutoFixResult:
    if not code.strip():
        raise HTTPException(status_code=400, detail="Le code fourni est vide")

    try:
        response = _fix_chain.invoke({"filename": filename or "sans nom", "code": code})
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Impossible de contacter Ollama : {exc}")

    corrected = _strip_markdown_fences(response.content)

    if not corrected.strip():
        raise HTTPException(
            status_code=502,
            detail="Le modele n'a pas pu generer de version corrigee. Reessaie.",
        )

    # --- Guardrail syntaxique : Python uniquement (contrainte connue du projet) ---
    syntax_valid: Optional[bool] = None
    syntax_note: Optional[str] = None

    if _is_python_file(filename):
        is_valid, error_msg = _check_python_syntax(corrected)

        if not is_valid:
            # Une seule tentative de correction automatique, pas de boucle
            try:
                retry_response = _fix_retry_chain.invoke(
                    {"filename": filename, "code": corrected, "syntax_error": error_msg}
                )
                retried_code = _strip_markdown_fences(retry_response.content)
                retried_valid, retried_error = _check_python_syntax(retried_code)

                if retried_valid:
                    corrected = retried_code
                    is_valid, error_msg = True, None
                else:
                    error_msg = retried_error  # on garde la derniere erreur connue
            except Exception:
                pass  # si le retry echoue reseau, on garde l'etat "invalide" tel quel

        syntax_valid = is_valid
        syntax_note = (
            None if is_valid
            else f"Attention : le code genere contient une erreur de syntaxe ({error_msg}). Verifie-le avant utilisation."
        )

    return AutoFixResult(
        filename=filename,
        corrected_code=corrected,
        summary_of_changes="Version corrigee generee automatiquement — a verifier avant utilisation.",
        syntax_valid=syntax_valid,
        syntax_note=syntax_note,
    )
    

# --- Analyse de PR : chunking + review par fichier + synthese finale ---

_DIFF_CHUNK_THRESHOLD = 3000  # caracteres, en dessous on ne splitte pas

_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=_DIFF_CHUNK_THRESHOLD,
    chunk_overlap=200,
)

_diff_chunk_parser = PydanticOutputParser(pydantic_object=DiffChunkFindings)
_diff_fixing_parser = OutputFixingParser.from_llm(parser=_diff_chunk_parser, llm=_llm, max_retries=1)

_diff_review_prompt = PromptTemplate(
    template="""Tu es un reviewer de code senior. Voici un extrait d'un diff Git (format patch unifie)
issu d'une Pull Request. Les lignes commencant par '+' sont ajoutees, celles par '-' sont supprimees.

Concentre-toi UNIQUEMENT sur les lignes AJOUTEES (+) : identifie les bugs, failles de securite
et anti-patterns serieux qu'elles introduisent. Ignore les lignes supprimees et le contexte
non modifie, sauf si necessaire pour comprendre un changement.

Ne cree jamais plusieurs findings pour le meme probleme. Reponds TOUJOURS en francais.

{format_instructions}

Fichier : {filename}
Extrait du diff :
{diff_chunk}
""",
    input_variables=["filename", "diff_chunk"],
    partial_variables={"format_instructions": _diff_chunk_parser.get_format_instructions()},
)

_diff_review_chain = _diff_review_prompt | _llm | _diff_fixing_parser


def _review_single_file_diff(filename: str, patch: str) -> PRFileReview:
    """Decoupe le patch si trop long, review chaque morceau, fusionne les findings.
    Un fichier binaire ou sans patch (ex: renommage pur) est ignore proprement."""
    if not patch or not patch.strip():
        return PRFileReview(filename=filename, findings=[])

    chunks = (
        _text_splitter.split_text(patch)
        if len(patch) > _DIFF_CHUNK_THRESHOLD
        else [patch]
    )

    all_findings: list[Finding] = []
    for chunk in chunks:
        try:
            result: DiffChunkFindings = _diff_review_chain.invoke(
                {"filename": filename, "diff_chunk": chunk}
            )
            all_findings.extend(result.findings)
        except Exception:
            continue  # un chunk illisible ne doit pas faire echouer toute la PR

    return PRFileReview(filename=filename, findings=all_findings)


_synthesis_parser = PydanticOutputParser(pydantic_object=PRSynthesisOutput)
_synthesis_fixing_parser = OutputFixingParser.from_llm(parser=_synthesis_parser, llm=_llm, max_retries=1)

_synthesis_prompt = PromptTemplate(
    template="""Voici la liste consolidee des problemes trouves dans une Pull Request,
fichier par fichier (format JSON). Fais une synthese executive : score global de qualite
du PR entier (0-10), resume en 3-5 phrases des problemes principaux.

Pour "recurring_issues" : un probleme n'est considere comme RECURRENT que s'il apparait
dans AU MOINS DEUX fichiers DIFFERENTS. Un probleme important mais isole dans un seul
fichier (meme s'il est critique) NE DOIT PAS figurer dans recurring_issues — il est deja
signale dans les findings de son fichier. Si aucun probleme n'apparait dans plusieurs
fichiers, renvoie une liste vide [].

Reponds TOUJOURS en francais.

{format_instructions}

Findings par fichier :
{findings_json}
""",
    input_variables=["findings_json"],
    partial_variables={"format_instructions": _synthesis_parser.get_format_instructions()},
)

_synthesis_chain = _synthesis_prompt | _llm | _synthesis_fixing_parser


def review_pr_diff(pr_number: int, pr_title: str, files: list[dict]) -> PRReviewResult:
    """files : liste de {'filename': str, 'patch': str}, venant de PyGithub (pr.get_files())."""
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier modifie dans cette PR")

    file_reviews = [_review_single_file_diff(f["filename"], f.get("patch", "")) for f in files]

    findings_summary = [
        {"filename": fr.filename, "findings": [f.model_dump() for f in fr.findings]}
        for fr in file_reviews
    ]

    try:
        synthesis: PRSynthesisOutput = _synthesis_chain.invoke(
            {"findings_json": json.dumps(findings_summary, ensure_ascii=False)}
        )
    except Exception:
        # Fallback : pas de synthese LLM disponible, on construit un resume minimal
        synthesis = PRSynthesisOutput(
            overall_quality_score=7.0,
            summary="Synthese automatique indisponible — consulte les findings par fichier ci-dessous.",
            recurring_issues=[],
        )

    all_findings = [f for fr in file_reviews for f in fr.findings]

    return PRReviewResult(
        pr_number=pr_number,
        pr_title=pr_title,
        files=file_reviews,
        overall_quality_score=round(max(0.0, min(10.0, synthesis.overall_quality_score)), 1),
        summary=synthesis.summary,
        recurring_issues=synthesis.recurring_issues,
        critical_count=sum(1 for f in all_findings if f.severity == "critical"),
        high_count=sum(1 for f in all_findings if f.severity == "high"),
        medium_count=sum(1 for f in all_findings if f.severity == "medium"),
        low_count=sum(1 for f in all_findings if f.severity == "low"),
    )

def save_pr_review(db, team_id: int, reviewed_by: int, result: PRReviewResult) -> None:
    """Upsert : une seule ligne par (team_id, pr_number), on ecrase l'ancienne."""
    existing = (
        db.query(PullRequestReview)
        .filter(PullRequestReview.team_id == team_id, PullRequestReview.pr_number == result.pr_number)
        .first()
    )
    payload = dict(
        pr_title=result.pr_title,
        files=[f.model_dump() for f in result.files],
        overall_quality_score=result.overall_quality_score,
        summary=result.summary,
        recurring_issues=result.recurring_issues,
        critical_count=result.critical_count,
        high_count=result.high_count,
        medium_count=result.medium_count,
        low_count=result.low_count,
        reviewed_by=reviewed_by,
    )
    if existing:
        for key, value in payload.items():
            setattr(existing, key, value)
    else:
        db.add(PullRequestReview(team_id=team_id, pr_number=result.pr_number, **payload))
    db.commit()    
    