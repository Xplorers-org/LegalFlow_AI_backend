from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base_class import BaseModel


class Tenant(BaseModel):
    """Tenant entity representing commercial tenant individuals or business entities."""
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    nic_passport: Mapped[str | None] = mapped_column(String(100), nullable=True)
    registration_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    leases = relationship("Lease", back_populates="tenant", cascade="all, delete-orphan")
