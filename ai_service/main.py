from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from ai_service.graph.compliance_graph import build_compliance_graph
from ai_service.utils.logging import setup_logging, get_logger

setup_logging("INFO")
logger = get_logger("ai_service.main")

app = FastAPI(
    title="LegalFlow AI - Independent AI Microservice",
    description="LangGraph Multi-Agent Legal Compliance Analysis and Document Generation Engine",
    version="1.0.0",
)

compiled_graph = build_compliance_graph()


class AnalysisRequest(BaseModel):
    case_id: str
    lease_id: str
    landlord_name: str = "Commercial Lessor"
    tenant_name: str = "Valued Tenant"
    tenant_company: Optional[str] = None
    property_address: str = "Colombo, Sri Lanka"
    lease_data: Dict[str, Any] = {}
    financial_facts: Dict[str, Any] = {}


class DocumentGenerationRequest(BaseModel):
    lease_id: str
    case_id: Optional[str] = None
    landlord_name: str = "Commercial Lessor"
    tenant_name: str = "Valued Tenant"
    tenant_company: Optional[str] = None
    property_address: str = "Colombo, Sri Lanka"
    financial_facts: Dict[str, Any] = {}


@app.post("/analyze", response_model=Dict[str, Any])
async def run_compliance_analysis(request: AnalysisRequest):
    """Triggers LangGraph multi-agent compliance analysis state machine."""
    logger.info("Executing LangGraph legal compliance workflow", case_id=request.case_id)
    
    initial_state = {
        "case_id": request.case_id,
        "lease_id": request.lease_id,
        "landlord_name": request.landlord_name,
        "tenant_name": request.tenant_name,
        "tenant_company": request.tenant_company,
        "property_address": request.property_address,
        "lease_data": request.lease_data,
        "payment_history": [],
        "financial_facts": request.financial_facts,
        "parsed_lease_terms": {},
        "retrieved_legal_context": "",
        "legal_analysis": {},
        "recommended_action": "NOTICE_TO_QUIT",
        "drafted_document": {},
        "messages": [],
    }

    try:
        final_state = compiled_graph.invoke(initial_state)
        return {
            "status": "success",
            "case_id": request.case_id,
            "financial_facts": final_state.get("financial_facts"),
            "parsed_lease_terms": final_state.get("parsed_lease_terms"),
            "legal_analysis": final_state.get("legal_analysis"),
            "recommended_action": final_state.get("recommended_action"),
            "drafted_document": final_state.get("drafted_document"),
            "workflow_log": final_state.get("messages"),
        }
    except Exception as e:
        logger.error("LangGraph execution error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LangGraph Multi-Agent execution failure: {str(e)}"
        )


@app.post("/generate/reminder", response_model=Dict[str, Any])
async def generate_reminder(request: DocumentGenerationRequest):
    """Directly triggers Drafting Agent for Payment Reminder."""
    initial_state = {
        "case_id": request.case_id or "direct_gen",
        "lease_id": request.lease_id,
        "landlord_name": request.landlord_name,
        "tenant_name": request.tenant_name,
        "tenant_company": request.tenant_company,
        "property_address": request.property_address,
        "lease_data": {},
        "payment_history": [],
        "financial_facts": request.financial_facts,
        "parsed_lease_terms": {},
        "retrieved_legal_context": "",
        "legal_analysis": {},
        "recommended_action": "REMINDER",
        "drafted_document": {},
        "messages": [],
    }
    final_state = compiled_graph.invoke(initial_state)
    return {"status": "success", "document": final_state.get("drafted_document")}


@app.post("/generate/notice", response_model=Dict[str, Any])
async def generate_notice(request: DocumentGenerationRequest):
    """Directly triggers Drafting Agent for Statutory Notice to Quit under Act No. 1 of 2023."""
    initial_state = {
        "case_id": request.case_id or "direct_gen",
        "lease_id": request.lease_id,
        "landlord_name": request.landlord_name,
        "tenant_name": request.tenant_name,
        "tenant_company": request.tenant_company,
        "property_address": request.property_address,
        "lease_data": {},
        "payment_history": [],
        "financial_facts": request.financial_facts,
        "parsed_lease_terms": {},
        "retrieved_legal_context": "",
        "legal_analysis": {},
        "recommended_action": "NOTICE_TO_QUIT",
        "drafted_document": {},
        "messages": [],
    }
    final_state = compiled_graph.invoke(initial_state)
    return {"status": "success", "document": final_state.get("drafted_document")}


@app.post("/generate/demand", response_model=Dict[str, Any])
async def generate_demand(request: DocumentGenerationRequest):
    """Directly triggers Drafting Agent for Letter of Demand."""
    initial_state = {
        "case_id": request.case_id or "direct_gen",
        "lease_id": request.lease_id,
        "landlord_name": request.landlord_name,
        "tenant_name": request.tenant_name,
        "tenant_company": request.tenant_company,
        "property_address": request.property_address,
        "lease_data": {},
        "payment_history": [],
        "financial_facts": request.financial_facts,
        "parsed_lease_terms": {},
        "retrieved_legal_context": "",
        "legal_analysis": {},
        "recommended_action": "LETTER_OF_DEMAND",
        "drafted_document": {},
        "messages": [],
    }
    final_state = compiled_graph.invoke(initial_state)
    return {"status": "success", "document": final_state.get("drafted_document")}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "legalflow-ai-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai_service.main:app", host="0.0.0.0", port=8001, reload=True)
