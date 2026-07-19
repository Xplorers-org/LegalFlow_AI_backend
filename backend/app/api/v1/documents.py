import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.api.v1.auth import get_current_user
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.schemas.document import DocumentResponse, DocumentApprovalRequest
from backend.app.schemas.user import UserResponse
from backend.app.models.document import ApprovalStatus

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    lease_id: uuid.UUID | None = None,
    case_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves generated legal documents."""
    repo = DocumentRepository(db)
    if case_id:
        docs = await repo.get_by_case(case_id)
    elif lease_id:
        docs = await repo.get_by_lease(lease_id)
    else:
        docs = await repo.get_all(skip=skip, limit=limit)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/{id}", response_model=DocumentResponse)
async def get_document(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves a specific generated legal document by UUID."""
    repo = DocumentRepository(db)
    doc = await repo.get(id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.post("/{id}/approve", response_model=DocumentResponse)
async def approve_or_reject_document(
    id: uuid.UUID,
    approval_in: DocumentApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Human-in-the-loop endpoint for landlord to approve or reject generated legal notices."""
    repo = DocumentRepository(db)
    doc = await repo.get(id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    new_status = ApprovalStatus.APPROVED if approval_in.approved else ApprovalStatus.REJECTED
    updated_fields = {
        "approval_status": new_status,
        "approved_at": datetime.now(timezone.utc) if approval_in.approved else None,
        "rejection_reason": approval_in.rejection_reason if not approval_in.approved else None,
    }
    
    updated_doc = await repo.update(id, updated_fields)
    return DocumentResponse.model_validate(updated_doc)
