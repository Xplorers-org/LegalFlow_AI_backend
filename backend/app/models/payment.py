import uuid
from datetime import date
from enum import Enum
from sqlalchemy import String, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base_class import BaseModel


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    FAILED = "FAILED"


class Payment(BaseModel):
    """Payment record tracking monthly rent items and transaction status."""
    __tablename__ = "payments"

    lease_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leases.id", ondelete="CASCADE"), nullable=False
    )
    amount_due: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(String(50), default=PaymentStatus.PENDING, nullable=False, index=True)
    gateway: Mapped[str | None] = mapped_column(String(100), default="PayHere", nullable=True)
    gateway_reference: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    payment_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    lease = relationship("Lease", back_populates="payments")
