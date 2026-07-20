from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class TenantBase(BaseModel):
    name: str
    company: str | None = None
    email: EmailStr
    phone: str
    nic_passport: str | None = None
    registration_no: str | None = None
    address: str | None = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: str | None = None
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    nic_passport: str | None = None
    registration_no: str | None = None
    address: str | None = None


class TenantResponse(TenantBase):
    id: UUID
    temp_password: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
