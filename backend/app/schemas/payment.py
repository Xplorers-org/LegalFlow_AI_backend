from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from backend.app.models.payment import PaymentStatus


class PaymentBase(BaseModel):
    lease_id: UUID
    amount_due: float
    amount_paid: float = 0.0
    due_date: date
    status: PaymentStatus = PaymentStatus.PENDING
    gateway: str | None = "PayHere"
    gateway_reference: str | None = None
    payment_link: str | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount_paid: float | None = None
    paid_date: date | None = None
    status: PaymentStatus | None = None
    gateway_reference: str | None = None


class PaymentResponse(PaymentBase):
    id: UUID
    paid_date: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentWebhookPayload(BaseModel):
    gateway_reference: str
    payment_id: UUID
    status: str  # PAID, FAILED, CANCELLED
    amount: float
    signature: str | None = None
