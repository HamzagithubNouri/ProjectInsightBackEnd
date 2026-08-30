import re
from pathlib import Path

from langchain_core.documents import Document

from app.rag.vectorstore import get_knowledge_base_store

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge_base"


def _parse_metadata(text: str) -> dict:
    """Extrait Issue Type / Category / Severity du haut du fichier pour le metadata."""
    issue_type = re.search(r"Issue Type:\s*(.+)", text)
    category = re.search(r"Category:\s*(.+)", text)
    severity = re.search(r"Severity:\s*(.+)", text)
    return {
        "issue_type": issue_type.group(1).strip() if issue_type else "unknown",
        "category": category.group(1).strip() if category else "unknown",
        "severity": severity.group(1).strip() if severity else "unknown",
    }


def load_all():
    docs = []
    for md_file in KNOWLEDGE_DIR.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        metadata = _parse_metadata(text)
        metadata["source_file"] = md_file.name
        # Une fiche entiere = un seul chunk : on ne splitte JAMAIS un document
        # de connaissance, pour garder ensemble definition + bad/good example + fix.
        docs.append(Document(page_content=text, metadata=metadata))

    if not docs:
        print("Aucune fiche .md trouvee dans app/rag/knowledge_base/")
        return

    store = get_knowledge_base_store()
    store.add_documents(docs)
    print(f"{len(docs)} fiches chargees dans knowledge_base.")


if __name__ == "__main__":
    load_all()