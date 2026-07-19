from typing import Dict, Any
from ai-service.state.case_state import CaseState
from ai-service.utils.logging import get_logger

logger = get_logger("ai_service.lease_parser_agent")


def lease_parser_node(state: CaseState) -> Dict[str, Any]:
    """Lease Parser Agent: Extracts structural lease terms, grace periods, and notice clauses."""
    logger.info("Lease Parser Agent extracting terms", case_id=state.get("case_id"))
    lease_info = state.get("lease_data", {})

    parsed_terms = {
        "monthly_rent": lease_info.get("monthly_rent", 0.0),
        "deposit": lease_info.get("deposit", 0.0),
        "service_charge": lease_info.get("service_charge", 0.0),
        "payment_due_day": lease_info.get("payment_day", 1),
        "grace_period_days": lease_info.get("grace_period_days", 5),
        "annual_interest_rate": lease_info.get("interest_rate_pa", 12.0),
        "notice_period_days": 30,  # Statutory standard under Act No. 1 of 2023
    }

    messages = state.get("messages", [])
    messages.append("Lease Parser Agent extracted notice period 30 days and monthly rent terms.")

    return {
        "parsed_lease_terms": parsed_terms,
        "messages": messages,
    }
