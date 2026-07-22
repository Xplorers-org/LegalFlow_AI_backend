from typing import TypedDict, List, Dict, Any, Optional


class CaseState(TypedDict):
    """Typed State for LangGraph Multi-Agent Legal Compliance Workflow."""
    case_id: str
    lease_id: str
    landlord_name: str
    tenant_name: str
    tenant_company: Optional[str]
    property_address: str
    lease_data: Dict[str, Any]
    payment_history: List[Dict[str, Any]]
    
    # Node outputs
    financial_facts: Dict[str, Any]
    parsed_lease_terms: Dict[str, Any]
    retrieved_legal_context: str
    legal_analysis: Dict[str, Any]
    recommended_action: str
    drafted_document: Dict[str, Any]
    messages: List[str]
