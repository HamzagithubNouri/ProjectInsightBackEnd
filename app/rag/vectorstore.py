from pathlib import Path

from langchain_chroma import Chroma

from app.rag.embeddings import embeddings

# Stockage persistant sur disque, a la racine du projet backend
_CHROMA_DIR = Path(__file__).parent.parent.parent / "chroma_data"


def get_knowledge_base_store() -> Chroma:
    return Chroma(
        collection_name="knowledge_base",
        embedding_function=embeddings,
        persist_directory=str(_CHROMA_DIR / "knowledge_base"),
    )


def get_review_history_store() -> Chroma:
    return Chroma(
        collection_name="review_history",
        embedding_function=embeddings,
        persist_directory=str(_CHROMA_DIR / "review_history"),
    )