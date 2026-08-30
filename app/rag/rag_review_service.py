from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_core.prompts import PromptTemplate

from app.config import settings
from app.schemas.ai_review_schema import Finding, EducationalEnrichment, EnrichedFinding
from app.rag.vectorstore import get_knowledge_base_store

# Modele plus puissant, reserve a cette tache ou la precision compte plus que la vitesse
_deepseek_llm = ChatOllama(
    base_url=settings.ollama_url,
    model="deepseek-coder-v2:16b",
    temperature=0.2,
)

# Le LLM ne produit QUE l'enrichissement pedagogique — jamais le finding lui-meme,
# qui reste controle par le code Python (evite que le LLM "reinvente" title/severity/
# suggested_fix a partir du contexte RAG, cause du bug observe precedemment).
_enrich_parser = PydanticOutputParser(pydantic_object=EducationalEnrichment)
_enrich_fixing_parser = OutputFixingParser.from_llm(parser=_enrich_parser, llm=_deepseek_llm, max_retries=1)

_enrich_prompt = PromptTemplate(
    template="""Tu es un formateur en genie logiciel. Un etudiant a un probleme de code
detecte automatiquement. Utilise le contexte pedagogique fourni pour ecrire une explication
personnalisee, adaptee a un etudiant, en francais.

IMPORTANT : le contexte pedagogique ci-dessous peut contenir plusieurs fiches sur des sujets
differents. Base ton explication UNIQUEMENT sur la fiche qui correspond exactement au
probleme detecte ({title}). Ignore les fiches non pertinentes, meme si elles apparaissent
dans le contexte.

Probleme detecte :
Titre : {title}
Description : {description}

Contexte pedagogique (peut contenir plusieurs fiches) :
{context}

Produis UNIQUEMENT l'explication pedagogique et les concepts lies au probleme detecte
ci-dessus — ne reproduis pas le contenu d'une fiche non liee a ce probleme precis.

{format_instructions}
""",
    input_variables=["title", "description", "context"],
    partial_variables={"format_instructions": _enrich_parser.get_format_instructions()},
)

_enrich_chain = _enrich_prompt | _deepseek_llm | _enrich_fixing_parser

# Seuls les findings a partir de ce niveau de severite sont enrichis (cout/perf)
_ENRICH_SEVERITIES = {"critical", "high"}


def enrich_finding(finding: Finding) -> EnrichedFinding:
    store = get_knowledge_base_store()
    results = store.similarity_search(f"{finding.title} {finding.description}", k=2)
    context = "\n\n---\n\n".join(doc.page_content for doc in results) or "Aucun contexte trouve."

    try:
        enrichment: EducationalEnrichment = _enrich_chain.invoke({
            "title": finding.title,
            "description": finding.description,
            "context": context,
        })
        return EnrichedFinding(
            finding=finding,  # toujours le finding original, jamais regenere par le LLM
            educational_explanation=enrichment.educational_explanation,
            related_concepts=enrichment.related_concepts,
        )
    except Exception:
        return EnrichedFinding(
            finding=finding,
            educational_explanation="Explication enrichie indisponible pour ce probleme.",
            related_concepts=[],
        )


def enrich_findings(findings: list[Finding]) -> list[EnrichedFinding]:
    return [enrich_finding(f) for f in findings if f.severity in _ENRICH_SEVERITIES]