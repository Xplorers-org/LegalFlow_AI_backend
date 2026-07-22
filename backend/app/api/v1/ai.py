import uuid
import httpx
from datetime import datetime, timezone, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.api.v1.auth import get_current_user
from backend.app.repositories.case_repository import CaseRepository
from backend.app.repositories.lease_repository import LeaseRepository
from backend.app.repositories.tenant_repository import TenantRepository
from backend.app.repositories.payment_repository import PaymentRepository
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.services.financial_engine import FinancialEngine
from backend.app.schemas.user import UserResponse
from backend.app.models.document import DocumentType, ApprovalStatus
from backend.app.core.logging import get_logger

router = APIRouter(tags=["AI Compliance & Drafting"])
logger = get_logger("backend.api.ai")


@router.post("/analyze", response_model=dict)
async def analyze_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Triggers LangGraph multi-agent compliance analysis for an overdue lease case."""
    case_repo = CaseRepository(db)
    lease_repo = LeaseRepository(db)
    tenant_repo = TenantRepository(db)
    payment_repo = PaymentRepository(db)

    case = await case_repo.get(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    lease = await lease_repo.get(case.lease_id)
    tenant = await tenant_repo.get(lease.tenant_id)
    payments = await payment_repo.get_by_lease(lease.id)

    financial_facts = FinancialEngine.compile_financial_facts(lease, payments)

    ai_payload = {
        "case_id": str(case.id),
        "lease_id": str(lease.id),
        "landlord_name": current_user.name,
        "tenant_name": tenant.name,
        "tenant_company": tenant.company,
        "property_address": lease.property_address,
        "lease_data": {
            "monthly_rent": float(lease.monthly_rent),
            "deposit": float(lease.deposit),
            "service_charge": float(lease.service_charge),
            "payment_day": lease.payment_day,
            "grace_period_days": lease.grace_period_days,
            "interest_rate_pa": float(lease.interest_rate_pa),
        },
        "financial_facts": financial_facts,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{settings.AI_SERVICE_URL}/analyze", json=ai_payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="AI Service failed to execute compliance graph")
            ai_data = resp.json()
    except Exception as e:
        logger.error("Failed to communicate with AI microservice", error=str(e))
        # Fallback response if AI service is offline
        ai_data = {
            "recommended_action": "NOTICE_TO_QUIT",
            "legal_analysis": {
                "risk_score": "HIGH",
                "reasoning": f"Rent arrears of LKR {financial_facts['total_outstanding_arrears']} overdue. Notice to Quit recommended under Act No. 1 of 2023."
            },
            "drafted_document": {
                "document_type": "NOTICE_TO_QUIT",
                "title": f"Notice to Quit - {lease.property_address}",
                "content": f"STATUTORY NOTICE TO QUIT\n\nTo: {tenant.name}\nArrears: LKR {financial_facts['total_outstanding_arrears']:,.2f}",
            }
        }

    # Update case with AI assessment
    await case_repo.update(case.id, {
        "risk_score": ai_data.get("legal_analysis", {}).get("risk_score"),
        "recommended_action": ai_data.get("recommended_action"),
        "ai_reasoning": ai_data.get("legal_analysis", {}).get("reasoning"),
    })

    # Save drafted document to database in DRAFT status
    doc_draft = ai_data.get("drafted_document", {})
    if doc_draft:
        doc_repo = DocumentRepository(db)
        await doc_repo.create({
            "lease_id": lease.id,
            "case_id": case.id,
            "document_type": doc_draft.get("document_type", DocumentType.NOTICE_TO_QUIT),
            "title": doc_draft.get("title", "Generated Legal Notice"),
            "content": doc_draft.get("content", ""),
            "generated_by": "LangGraph_AI_Service",
            "generated_at": case.created_at,
            "approval_status": ApprovalStatus.DRAFT,
        })

    return ai_data


@router.post("/cases/{case_id}/generate", response_model=dict)
async def generate_case_document(
    case_id: uuid.UUID,
    document_type: DocumentType,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Explicitly triggers generation of a specific document type for a compliance case."""
    case_repo = CaseRepository(db)
    lease_repo = LeaseRepository(db)
    tenant_repo = TenantRepository(db)
    payment_repo = PaymentRepository(db)

    case = await case_repo.get(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    lease = await lease_repo.get(case.lease_id)
    tenant = await tenant_repo.get(lease.tenant_id)
    payments = await payment_repo.get_by_lease(lease.id)

    financial_facts = FinancialEngine.compile_financial_facts(lease, payments)

    ai_payload = {
        "case_id": str(case.id),
        "lease_id": str(lease.id),
        "landlord_name": current_user.name,
        "tenant_name": tenant.name,
        "tenant_company": tenant.company,
        "property_address": lease.property_address,
        "financial_facts": financial_facts,
    }

    # Determine endpoint based on document_type
    if document_type == DocumentType.REMINDER:
        ai_endpoint = "/generate/reminder"
    elif document_type == DocumentType.NOTICE_TO_QUIT:
        ai_endpoint = "/generate/notice"
    elif document_type == DocumentType.LETTER_OF_DEMAND:
        ai_endpoint = "/generate/demand"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported document type: {document_type}"
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{settings.AI_SERVICE_URL}{ai_endpoint}", json=ai_payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="AI Service failed to generate document")
            ai_data = resp.json()
    except Exception as e:
        logger.error(f"Failed to communicate with AI service at {ai_endpoint}", error=str(e))
        # Fallback response
        if document_type == DocumentType.LETTER_OF_DEMAND:
            content = f"FORMAL LETTER OF DEMAND\n\nDate: {date.today().strftime('%d %B %Y')}\nTo: {tenant.name}\nAddress: {lease.property_address}\n\nWe hereby demand payment of total arrears LKR {financial_facts['grand_total_payable']:,.2f} within seven (7) days, failing which legal proceedings under Act No. 1 of 2023 will be instituted in the District Court."
        elif document_type == DocumentType.REMINDER:
            content = f"COMMERCIAL RENT PAYMENT REMINDER\n\nDate: {date.today().strftime('%d %B %Y')}\nDear {tenant.name},\n\nThis is a friendly reminder that rent of LKR {lease.monthly_rent:,.2f} for {lease.property_address} is overdue. Total Arrears: LKR {financial_facts['total_outstanding_arrears']:,.2f}."
        else:
            content = f"STATUTORY NOTICE TO QUIT\n\nDate: {date.today().strftime('%d %B %Y')}\nTo: {tenant.name}\nAddress: {lease.property_address}\n\nNotice is hereby given under Section 3 of Act No. 1 of 2023 to vacate the premises within 30 days."

        ai_data = {
            "status": "success",
            "document": {
                "document_type": document_type.value,
                "title": f"{document_type.value.replace('_', ' ').title()} - {lease.property_address}",
                "content": content,
            }
        }

    # Save drafted document to database in DRAFT status
    doc_draft = ai_data.get("document", {})
    if doc_draft:
        doc_repo = DocumentRepository(db)
        created_doc = await doc_repo.create({
            "lease_id": lease.id,
            "case_id": case.id,
            "document_type": doc_draft.get("document_type", document_type.value),
            "title": doc_draft.get("title", "Generated Legal Notice"),
            "content": doc_draft.get("content", ""),
            "generated_by": "LangGraph_AI_Service",
            "generated_at": datetime.now(timezone.utc),
            "approval_status": ApprovalStatus.DRAFT,
        })
        
        # Also update case status based on document type
        new_case_status = case.status
        if document_type == DocumentType.NOTICE_TO_QUIT:
            new_case_status = "NOTICE_SENT"
        elif document_type == DocumentType.LETTER_OF_DEMAND:
            new_case_status = "DEMAND_SENT"
            
        await case_repo.update(case.id, {"status": new_case_status})
        
        return {
            "id": str(created_doc.id),
            "lease_id": str(created_doc.lease_id),
            "case_id": str(created_doc.case_id),
            "document_type": created_doc.document_type,
            "title": created_doc.title,
            "content": created_doc.content,
            "generated_by": created_doc.generated_by,
            "generated_at": created_doc.generated_at.isoformat(),
            "approval_status": created_doc.approval_status,
            "created_at": created_doc.created_at.isoformat(),
            "updated_at": created_doc.updated_at.isoformat(),
        }

    raise HTTPException(status_code=500, detail="Failed to parse drafted document from AI response")
