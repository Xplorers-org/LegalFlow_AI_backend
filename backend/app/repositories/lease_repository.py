import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.lease import Lease
from backend.app.repositories.base_repository import BaseRepository


class LeaseRepository(BaseRepository[Lease]):
    """Lease data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Lease, db)

    async def get_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[Lease]:
        """Finds all leases associated with a specific tenant."""
        result = await self.db.execute(select(Lease).filter(Lease.tenant_id == tenant_id))
        return result.scalars().all()
