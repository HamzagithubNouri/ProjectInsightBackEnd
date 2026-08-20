import json
import re

import requests
from fastapi import HTTPException

from app.config import settings
from app.schemas.ai_review_schema import Finding, CodeReviewResult


PROMPT_TEMPLATE = """Tu es un reviewer de code senior. Analyse le code suivant, quel que soit
son langage, et identifie les problemes reels : bugs, failles de securite,
anti-patterns, mauvaises pratiques.

Reponds UNIQUEMENT avec un tableau JSON valide, sans aucun texte avant ou apres,
sans balises markdown. Chaque element du tableau doit respecter exactement ce format :

[
  {{
    "severity": "critical" | "high" | "medium" | "low",
    "title": "titre court du probleme",
    "description": "explication precise du probleme et de son impact",
    "line_start": <numero de ligne ou commence le probleme>,
    "line_end": <numero de ligne ou il se termine>,
    "suggested_fix": "extrait de code corrige, ou null si pas applicable"
  }}
]

Si aucun probleme n'est trouve, reponds avec un tableau vide : []

Code a analyser (fichier: {filename}) :
{code}
"""


def _extract_json_array(raw_text: str) -> str:
    """Le modele peut parfois entourer le JSON de texte ou de balises markdown
    malgre la consigne ; on extrait le premier tableau [...] trouve."""
    match = re.search(r"\[.*\]", raw_text, re.DOTALL)
    if not match:
        raise ValueError("Aucun tableau JSON trouve dans la reponse du modele")
    return match.group(0)


def _call_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            f"{settings.ollama_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2},  # faible temperature : analyse, pas creativite
            },
            timeout=120,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Impossible de contacter Ollama. Verifie qu'il tourne en arriere-plan.",
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Le modele a mis trop de temps a repondre.")

    return response.json()["response"]


def review_code(code: str, filename: str | None = None) -> CodeReviewResult:
    if not code.strip():
        raise HTTPException(status_code=400, detail="Le code fourni est vide")

    prompt = PROMPT_TEMPLATE.format(filename=filename or "sans nom", code=code)
    raw_response = _call_ollama(prompt)

    try:
        json_text = _extract_json_array(raw_response)
        raw_findings = json.loads(json_text)
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(
            status_code=502,
            detail="Le modele a renvoye une reponse mal formee. Reessaie.",
        )

    findings: list[Finding] = []
    for item in raw_findings:
        try:
            findings.append(Finding(**item))
        except Exception:
            continue  # on ignore un finding individuel mal forme plutot que de tout faire echouer

    return CodeReviewResult(
        filename=filename,
        findings=findings,
        critical_count=sum(1 for f in findings if f.severity == "critical"),
        high_count=sum(1 for f in findings if f.severity == "high"),
        medium_count=sum(1 for f in findings if f.severity == "medium"),
        low_count=sum(1 for f in findings if f.severity == "low"),
    )
