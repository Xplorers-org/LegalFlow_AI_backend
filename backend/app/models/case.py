import uuid
from enum import Enum
from sqlalchemy import String, Numeric, Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base_class import BaseModel


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    NOTICE_SENT = "NOTICE_SENT"
    DEMAND_SENT = "DEMAND_SENT"
    RESOLVED = "RESOLVED"
    LITIGATION = "LITIGATION"


class Case(BaseModel):
    """Case entity for tracking landlord legal compliance cases triggered by payment defaults."""
    __tablename__ = "cases"

    lease_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leases.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[CaseStatus] = mapped_column(String(50), default=CaseStatus.OPEN, nullable=False, index=True)
    total_arrears: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    overdue_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    risk_score: Mapped[str | None] = mapped_column(String(50), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    recommended_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    financial_facts_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    lease = relationship("Lease", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
