from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

from rag.query import LegalRetriever
from rag.ingest import run_ingestion_pipeline
from rag.utils.logging import setup_logging, get_logger

setup_logging("INFO")
logger = get_logger("rag.main")

app = FastAPI(
    title="LegalFlow AI - RAG Microservice",
    description="Legal Knowledge Base vector search & retrieval engine for Sri Lankan Tenancy Law",
    version="1.0.0",
)

retriever = LegalRetriever()


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    doc_name_filter: str | None = None


class QueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    formatted_context: str


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Executes semantic search against ChromaDB legal vector store."""
    try:
        results = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            doc_name_filter=request.doc_name_filter
        )
        context = retriever.build_legal_context(results)
        return QueryResponse(
            query=request.query,
            results=results,
            formatted_context=context
        )
    except Exception as e:
        logger.error("RAG retrieval query failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query execution error: {str(e)}"
        )


@app.post("/index", response_model=dict)
async def trigger_ingestion():
    """Triggers unified document loading, chunking, embedding, and ChromaDB indexing."""
    try:
        count = run_ingestion_pipeline()
        return {"status": "success", "nodes_indexed": count}
    except Exception as e:
        logger.error("RAG ingestion pipeline failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion pipeline failure: {str(e)}"
        )


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "legalflow-rag-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag.main:app", host="0.0.0.0", port=8002, reload=True)
