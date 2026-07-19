import uuid
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.api.v1.auth import get_current_user
from backend.app.repositories.payment_repository import PaymentRepository
from backend.app.repositories.lease_repository import LeaseRepository
from backend.app.schemas.payment import PaymentCreate, PaymentResponse, PaymentWebhookPayload
from backend.app.schemas.user import UserResponse
from backend.app.models.payment import PaymentStatus

router = APIRouter(prefix="/payment", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Creates a new payment schedule item for a lease."""
    lease_repo = LeaseRepository(db)
    lease = await lease_repo.get(payment_in.lease_id)
    if not lease:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lease does not exist")

    repo = PaymentRepository(db)
    payment = await repo.create(payment_in.model_dump())
    return PaymentResponse.model_validate(payment)


@router.get("", response_model=List[PaymentResponse])
async def list_payments(
    lease_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves payment records optionally filtered by lease ID."""
    repo = PaymentRepository(db)
    if lease_id:
        payments = await repo.get_by_lease(lease_id)
    else:
        payments = await repo.get_all(skip=skip, limit=limit)
    return [PaymentResponse.model_validate(p) for p in payments]


@router.post("/link", response_model=dict)
async def generate_payment_link(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Generates a secure checkout payment link for a pending rent item."""
    repo = PaymentRepository(db)
    payment = await repo.get(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    gateway_ref = f"PAYHERE-{uuid.uuid4().hex[:12].upper()}"
    link = f"https://sandbox.payhere.lk/pay/checkout?ref={gateway_ref}&amount={payment.amount_due}"
    
    await repo.update(payment_id, {
        "gateway": "PayHere",
        "gateway_reference": gateway_ref,
        "payment_link": link
    })

    return {
        "payment_id": str(payment_id),
        "gateway_reference": gateway_ref,
        "payment_link": link,
        "amount_due": float(payment.amount_due)
    }


@router.post("/webhook", response_model=dict)
async def payment_webhook(
    payload: PaymentWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """Webhook listener invoked by Payment Gateway to log completed payments."""
    repo = PaymentRepository(db)
    payment = await repo.get(payload.payment_id)
    if not payment:
        payment = await repo.get_by_gateway_reference(payload.gateway_reference)

    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

    if payload.status.upper() in ["PAID", "SUCCESS", "COMPLETED"]:
        await repo.update(payment.id, {
            "status": PaymentStatus.PAID,
            "amount_paid": payload.amount,
            "paid_date": date.today(),
            "gateway_reference": payload.gateway_reference
        })
        return {"status": "success", "message": "Payment verified and recorded as PAID"}
    else:
        await repo.update(payment.id, {"status": PaymentStatus.FAILED})
        return {"status": "failed", "message": "Payment recorded as FAILED"}
