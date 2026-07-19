from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from backend.app.models.lease import LeaseStatus


class LeaseBase(BaseModel):
    tenant_id: UUID
    property_name: str
    property_address: str
    monthly_rent: float
    deposit: float = 0.0
    service_charge: float = 0.0
    payment_day: int = 1
    grace_period_days: int = 5
    interest_rate_pa: float = 12.0
    lease_start: date
    lease_end: date
    status: LeaseStatus = LeaseStatus.ACTIVE


class LeaseCreate(LeaseBase):
    pass


class LeaseUpdate(BaseModel):
    property_name: str | None = None
    property_address: str | None = None
    monthly_rent: float | None = None
    deposit: float | None = None
    service_charge: float | None = None
    payment_day: int | None = None
    grace_period_days: int | None = None
    interest_rate_pa: float | None = None
    lease_start: date | None = None
    lease_end: date | None = None
    status: LeaseStatus | None = None


class LeaseResponse(LeaseBase):
    id: UUID
    pdf_storage_path: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
