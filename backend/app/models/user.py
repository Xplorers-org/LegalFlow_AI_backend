from enum import Enum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base_class import BaseModel


class UserRole(str, Enum):
    LANDLORD = "landlord"
    PROPERTY_MANAGER = "property_manager"
    TENANT = "tenant"
    ADMIN = "admin"


class User(BaseModel):
    """User entity representing commercial property landlords, managers, and tenants."""
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(50), default=UserRole.LANDLORD, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
