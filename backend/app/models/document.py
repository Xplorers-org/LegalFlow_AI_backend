import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, ForeignKey, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base_class import BaseModel


class DocumentType(str, Enum):
    REMINDER = "REMINDER"
    NOTICE_TO_QUIT = "NOTICE_TO_QUIT"
    LETTER_OF_DEMAND = "LETTER_OF_DEMAND"


class ApprovalStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Document(BaseModel):
    """Document entity tracking AI-generated legal notices with landlord approval states."""
    __tablename__ = "documents"

    lease_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leases.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True
    )
    document_type: Mapped[DocumentType] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(100), default="AI_Legal_Agent", nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approval_status: Mapped[ApprovalStatus] = mapped_column(String(50), default=ApprovalStatus.DRAFT, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    lease = relationship("Lease", back_populates="documents")
    case = relationship("Case", back_populates="documents")
