import re
import ast
from typing import Optional
from fastapi import HTTPException
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain.output_parsers import OutputFixingParser
from langchain_core.prompts import PromptTemplate

from app.config import settings
from app.schemas.ai_review_schema import (
    LLMReviewOutput,
    CodeReviewResult,
    AutoFixResult,
)

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


def review_code(code: str, filename: str | None = None) -> CodeReviewResult:
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
        # Erreurs de connexion / timeout Ollama (ConnectionError, ReadTimeout, etc.)
        raise HTTPException(
            status_code=503,
            detail=f"Impossible de contacter Ollama ou reponse invalide : {exc}",
        )

    findings = result.findings
    score = max(0.0, min(10.0, result.quality_score))  # on clamp entre 0 et 10 par securite

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