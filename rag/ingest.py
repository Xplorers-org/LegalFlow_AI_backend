import os
import glob
from rag.chunking.legal_chunker import LegalSemanticChunker
from rag.serialization.semantic_serializer import SemanticSerializer
from rag.nodes.node_builder import NodeBuilder
from rag.embeddings.provider import EmbeddingProvider
from rag.vectorstore.chroma_store import ChromaVectorStore
from rag.utils.logging import setup_logging, get_logger

setup_logging("INFO")
logger = get_logger("rag.ingest")


def run_ingestion_pipeline(docs_dir: str = None) -> int:
    """Executes full unified RAG ingestion pipeline for Sri Lankan legal knowledge base."""
    if not docs_dir:
        docs_dir = os.path.join(os.path.dirname(__file__), "documents")

    logger.info("Starting Legal Knowledge Base Ingestion Pipeline", docs_dir=docs_dir)

    md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)
    if not md_files:
        logger.warning("No markdown legal files found in directory", docs_dir=docs_dir)
        return 0

    chunker = LegalSemanticChunker()
    serializer = SemanticSerializer()
    node_builder = NodeBuilder()
    embedder = EmbeddingProvider()
    vector_store = ChromaVectorStore()

    all_raw_chunks = []

    for file_path in md_files:
        doc_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = chunker.chunk_markdown(content, doc_name)
        for c in chunks:
            c["serialized_text"] = serializer.serialize(c)
            all_raw_chunks.append(c)

    logger.info("Document chunking and serialization completed", total_chunks=len(all_raw_chunks))

    # Build LlamaIndex TextNodes
    nodes = node_builder.build_nodes(all_raw_chunks)

    # Embeddings & Vector Indexing
    texts_to_embed = [node.text for node in nodes]
    logger.info("Generating HuggingFace embeddings...", model=embedder.model_name)
    embeddings = embedder.embed_documents(texts_to_embed)

    vector_store.add_nodes(nodes, embeddings)
    logger.info("Unified RAG Ingestion Pipeline completed successfully!", indexed_nodes=len(nodes))
    return len(nodes)


if __name__ == "__main__":
    run_ingestion_pipeline()
