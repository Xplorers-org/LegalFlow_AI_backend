import os
import httpx
from typing import Dict, Any
from ai_service.state.case_state import CaseState
from ai_service.utils.logging import get_logger

logger = get_logger("ai_service.legal_research_agent")


def legal_research_node(state: CaseState) -> Dict[str, Any]:
    """Legal Research Agent: Queries RAG service to pull relevant Sri Lankan statutory provisions."""
    logger.info("Legal Research Agent querying RAG microservice", case_id=state.get("case_id"))
    rag_url = os.getenv("RAG_SERVICE_URL", "http://rag-service:8002")

    facts = state.get("financial_facts", {})
    overdue_days = facts.get("max_overdue_days", 0)

    query_str = (
        f"Commercial lease rent arrears recovery, overdue {overdue_days} days, "
        f"Notice to Quit under Section 3 of Recovery of Possession of Premises Given on Lease Act No 1 of 2023"
    )

    context = "Section 3 & 4 of Recovery of Possession of Premises Given on Lease Act No. 1 of 2023 requires 30 days statutory notice to quit when rent is in arrears for more than 14 days."

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(f"{rag_url}/query", json={"query": query_str, "top_k": 3})
            if resp.status_code == 200:
                data = resp.json()
                context = data.get("formatted_context", context)
                logger.info("Successfully fetched live legal context from RAG service")
    except Exception as e:
        logger.warning("RAG HTTP call failed. Using embedded statutory context fallback.", error=str(e))

    messages = state.get("messages", [])
    messages.append("Legal Research Agent retrieved Sri Lankan statutory legal context.")

    return {
        "retrieved_legal_context": context,
        "messages": messages,
    }
