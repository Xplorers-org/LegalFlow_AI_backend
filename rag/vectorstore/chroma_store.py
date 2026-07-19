import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from rag.utils.logging import get_logger

logger = get_logger("rag.vectorstore")


class ChromaVectorStore:
    """Persistent ChromaDB vector database interface."""

    def __init__(
        self,
        collection_name: str = "sri_lankan_legal_kb",
        host: str = None,
        port: int = None,
        persist_dir: str = None,
    ):
        self.collection_name = collection_name
        host = host or os.getenv("CHROMA_HOST", "localhost")
        port = int(port or os.getenv("CHROMA_PORT", 8000))
        persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")

        # Fallback to local persistent client if HTTP server is not active
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            self.client.heartbeat()
            logger.info("Connected to ChromaDB HTTP Server", host=host, port=port)
        except Exception:
            os.makedirs(persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_dir)
            logger.info("Using ChromaDB PersistentClient", path=persist_dir)

        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_nodes(self, nodes: List[Any], embeddings: List[List[float]]) -> None:
        """Adds embedded nodes into ChromaDB collection."""
        ids = [node.id_ for node in nodes]
        documents = [node.text for node in nodes]
        metadatas = [node.metadata for node in nodes]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info("Successfully added nodes to ChromaDB", count=len(nodes), collection=self.collection_name)

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where_filter: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Performs vector similarity search against ChromaDB."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity_score": round(1.0 - float(dist), 4),
                })

        return formatted_results
