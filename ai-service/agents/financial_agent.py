from ai-service.state.case_state import CaseState
from ai-service.utils.logging import get_logger

logger = get_logger("ai_service.financial_agent")


def financial_agent_node(state: CaseState) -> Dict[str, Any]:
    """Financial Agent: Ingests immutable financial facts computed by Backend.
    
    CRITICAL RULE: This agent NEVER performs arithmetic calculations. It verifies
    the presence of facts and formats them for downstream legal research.
    """
    logger.info("Financial Agent processing case facts", case_id=state.get("case_id"))
    facts = state.get("financial_facts", {})

    if not facts:
        # Fallback if facts were passed in lease_data
        facts = {
            "total_outstanding_arrears": state.get("lease_data", {}).get("total_arrears", 0.0),
            "max_overdue_days": state.get("lease_data", {}).get("overdue_days", 0),
            "monthly_rent": state.get("lease_data", {}).get("monthly_rent", 0.0),
        }

    messages = state.get("messages", [])
    messages.append(f"Financial Agent ingested arrears LKR {facts.get('total_outstanding_arrears')}")

    return {
        "financial_facts": facts,
        "messages": messages,
    }
