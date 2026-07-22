from datetime import date, timedelta
from typing import Dict, Any
from ai_service.state.case_state import CaseState
from ai_service.utils.prompt_manager import PromptManager
from ai_service.utils.logging import get_logger
from ai_service.tools.llm_service import LLMService

logger = get_logger("ai_service.drafting_agent")


def drafting_agent_node(state: CaseState) -> Dict[str, Any]:
    """Drafting Agent: Formulates statutory legal document text citing Sri Lankan Law."""
    action = state.get("recommended_action", "REMINDER")
    logger.info("Drafting Agent generating statutory document", action=action, case_id=state.get("case_id"))

    facts = state.get("financial_facts", {})
    landlord_name = state.get("landlord_name", "Commercial Property Lessor")
    tenant_name = state.get("tenant_name", "Valued Tenant")
    tenant_company = state.get("tenant_company", "")
    property_address = state.get("property_address", "Commercial Premises, Colombo, Sri Lanka")

    today = date.today()
    expiry_30_days = (today + timedelta(days=30)).strftime("%d %B %Y")
    today_str = today.strftime("%d %B %Y")

    monthly_rent = facts.get("monthly_rent", state.get("lease_data", {}).get("monthly_rent", 0.0))
    arrears = facts.get("total_outstanding_arrears", 0.0)
    interest = facts.get("total_statutory_interest_accrued", 0.0)
    total_payable = facts.get("grand_total_payable", arrears + interest)

    prompt_mgr = PromptManager()
    llm_svc = LLMService()

    content = ""

    if action == "NOTICE_TO_QUIT":
        doc_type = "NOTICE_TO_QUIT"
        title = f"Statutory Notice to Quit - {property_address}"
        try:
            prompt_text = prompt_mgr.load_prompt(
                "drafting_notice_prompt.txt",
                current_date=today_str,
                landlord_name=landlord_name,
                tenant_name=tenant_name,
                tenant_company=tenant_company,
                property_address=property_address,
                monthly_rent=f"{monthly_rent:,.2f}",
                outstanding_arrears=f"{arrears:,.2f}",
                statutory_interest=f"{interest:,.2f}",
                total_payable=f"{total_payable:,.2f}",
                expiry_date=expiry_30_days,
                statutory_citations="Section 3 & 4 of Recovery of Possession of Premises Given on Lease Act No. 1 of 2023",
            )
            content = llm_svc.invoke(prompt_text)
        except Exception as e:
            logger.warning("LLM Notice generation failed, using fallback", error=str(e))
            content = f"STATUTORY NOTICE TO QUIT UNDER SECTION 3 OF ACT NO. 1 OF 2023\n\nDate: {today_str}\nTo: {tenant_name}\nAddress: {property_address}\n\nTake notice that in terms of Section 3 of Act No. 1 of 2023, you are required to quit and vacate the premises on or before {expiry_30_days}. Total Arrears Due: LKR {arrears:,.2f} + Interest LKR {interest:,.2f}."
            
    elif action == "LETTER_OF_DEMAND":
        doc_type = "LETTER_OF_DEMAND"
        title = f"Attorney Letter of Demand - {property_address}"
        try:
            prompt_text = prompt_mgr.load_prompt(
                "drafting_demand_prompt.txt",
                current_date=today_str,
                landlord_name=landlord_name,
                tenant_name=tenant_name,
                tenant_company=tenant_company,
                property_address=property_address,
                monthly_rent=f"{monthly_rent:,.2f}",
                outstanding_arrears=f"{arrears:,.2f}",
                statutory_interest=f"{interest:,.2f}",
                total_payable=f"{total_payable:,.2f}",
                demand_due_days="7",
                statutory_citations="Section 3 & 4 of Recovery of Possession of Premises Given on Lease Act No. 1 of 2023",
            )
            content = llm_svc.invoke(prompt_text)
        except Exception as e:
            logger.warning("LLM Demand generation failed, using fallback", error=str(e))
            content = f"FORMAL LETTER OF DEMAND\n\nDate: {today_str}\nTo: {tenant_name}\nAddress: {property_address}\n\nWe hereby demand payment of total arrears LKR {total_payable:,.2f} within seven (7) days, failing which legal proceedings under Act No. 1 of 2023 will be instituted in the District Court."
            
    else:
        doc_type = "REMINDER"
        title = f"Friendly Payment Reminder - {property_address}"
        try:
            prompt_text = prompt_mgr.load_prompt(
                "drafting_reminder_prompt.txt",
                current_date=today_str,
                landlord_name=landlord_name,
                tenant_name=tenant_name,
                tenant_company=tenant_company,
                property_address=property_address,
                monthly_rent=f"{monthly_rent:,.2f}",
                outstanding_arrears=f"{arrears:,.2f}",
                total_payable=f"{total_payable:,.2f}",
            )
            content = llm_svc.invoke(prompt_text)
        except Exception as e:
            logger.warning("LLM Reminder generation failed, using fallback", error=str(e))
            content = f"COMMERCIAL RENT PAYMENT REMINDER\n\nDate: {today_str}\nDear {tenant_name},\n\nThis is a friendly reminder that rent of LKR {monthly_rent:,.2f} for {property_address} is overdue. Total Arrears: LKR {arrears:,.2f}. Please make payment promptly."

    drafted_doc = {
        "document_type": doc_type,
        "title": title,
        "content": content,
        "generated_by": "LangGraph_Drafting_Agent",
        "generated_at": today_str,
        "approval_status": "DRAFT",
    }

    messages = state.get("messages", [])
    messages.append(f"Drafting Agent created statutory document draft: {title}")

    return {
        "drafted_document": drafted_doc,
        "messages": messages,
    }
