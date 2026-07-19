import uuid
from datetime import date
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.payment import Payment, PaymentStatus
from backend.app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Payment data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def get_by_lease(self, lease_id: uuid.UUID) -> Sequence[Payment]:
        """Retrieves payment schedule and transaction history for a lease."""
        result = await self.db.execute(
            select(Payment).filter(Payment.lease_id == lease_id).order_by(Payment.due_date.desc())
        )
        return result.scalars().all()

    async def get_overdue_payments_before(self, cutoff_date: date) -> Sequence[Payment]:
        """Finds all pending payments past their due date and grace period."""
        result = await self.db.execute(
            select(Payment).filter(
                Payment.due_date < cutoff_date,
                Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIALLY_PAID])
            )
        )
        return result.scalars().all()

    async def get_by_gateway_reference(self, gateway_reference: str) -> Payment | None:
        """Finds a payment record by gateway reference ID."""
        result = await self.db.execute(
            select(Payment).filter(Payment.gateway_reference == gateway_reference)
        )
        return result.scalars().first()
