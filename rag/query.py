from typing import List, Dict, Any
from rag.embeddings.provider import EmbeddingProvider
from rag.vectorstore.chroma_store import ChromaVectorStore
from rag.utils.logging import get_logger

logger = get_logger("rag.query")


class LegalRetriever:
    """Metadata-aware legal vector retriever with similarity scoring and statutory citation building."""

    def __init__(self):
        self.embedder = EmbeddingProvider()
        self.vector_store = ChromaVectorStore()

    def retrieve(
        self, query: str, top_k: int = 5, doc_name_filter: str = None
    ) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant statutory clauses from ChromaDB."""
        logger.info("Executing legal retrieval query", query=query, top_k=top_k)
        query_vector = self.embedder.embed_text(query)

        where_filter = None
        if doc_name_filter:
            where_filter = {"doc_name": doc_name_filter}

        results = self.vector_store.query(
            query_embedding=query_vector,
            top_k=top_k,
            where_filter=where_filter,
        )
        return results

    def build_legal_context(self, retrieved_results: List[Dict[str, Any]]) -> str:
        """Formats retrieved legal clauses into structured text block with explicit statutory citations."""
        if not retrieved_results:
            return "No relevant statutory laws or templates retrieved from the legal knowledge base."

        formatted_excerpts = []
        for idx, item in enumerate(retrieved_results, start=1):
            meta = item.get("metadata", {})
            doc = meta.get("doc_name", "Sri Lankan Legal Code")
            section = meta.get("section", "General Provision")
            score = item.get("similarity_score", 0.0)

            excerpt = (
                f"[CITATION {idx}] Document: {doc} | Section: {section} | Confidence: {score}\n"
                f"{item['text']}\n"
            )
            formatted_excerpts.append(excerpt)

        return "\n----------------------------------------\n".join(formatted_excerpts)
