import os
from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingProvider:
    """Swappable HuggingFace Sentence Transformers embedding provider."""

    def __init__(self, model_name: str = None):
        if not model_name:
            model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a single text string."""
        return self.model.encode(text).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of text strings."""
        return self.model.encode(texts, show_progress_bar=False).tolist()
