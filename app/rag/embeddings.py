from langchain_ollama import OllamaEmbeddings

from app.config import settings

embeddings = OllamaEmbeddings(
    base_url=settings.ollama_url,
    model="nomic-embed-text",
)