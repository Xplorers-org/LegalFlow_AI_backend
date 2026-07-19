from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from backend.app.models.document import DocumentType, ApprovalStatus


class DocumentBase(BaseModel):
    lease_id: UUID
    case_id: UUID | None = None
    document_type: DocumentType
    title: str
    content: str
    generated_by: str = "AI_Legal_Agent"


class DocumentCreate(DocumentBase):
    metadata_json: dict | None = None


class DocumentApprovalRequest(BaseModel):
    approved: bool
    rejection_reason: str | None = None


class DocumentResponse(DocumentBase):
    id: UUID
    generated_at: datetime
    storage_path: str | None = None
    approval_status: ApprovalStatus
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
