import uuid
from datetime import date
from enum import Enum
from sqlalchemy import String, Numeric, Integer, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base_class import BaseModel


class LeaseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    DEFAULTED = "DEFAULTED"


class Lease(BaseModel):
    """Lease entity representing commercial lease agreements and terms."""
    __tablename__ = "leases"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    property_name: Mapped[str] = mapped_column(String(255), nullable=False)
    property_address: Mapped[str] = mapped_column(Text, nullable=False)
    monthly_rent: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    deposit: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    service_charge: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    payment_day: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1st of month by default
    grace_period_days: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    interest_rate_pa: Mapped[float] = mapped_column(Numeric(5, 2), default=12.0, nullable=False)  # Statutory annual interest rate %
    lease_start: Mapped[date] = mapped_column(Date, nullable=False)
    lease_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[LeaseStatus] = mapped_column(String(50), default=LeaseStatus.ACTIVE, nullable=False)
    pdf_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="leases")
    payments = relationship("Payment", back_populates="lease", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="lease", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="lease", cascade="all, delete-orphan")
