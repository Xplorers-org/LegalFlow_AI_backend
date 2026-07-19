import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.case import Case, CaseStatus
from backend.app.repositories.base_repository import BaseRepository


class CaseRepository(BaseRepository[Case]):
    """Case data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Case, db)

    async def get_by_lease(self, lease_id: uuid.UUID) -> Sequence[Case]:
        """Finds active and past legal compliance cases for a lease."""
        result = await self.db.execute(
            select(Case).filter(Case.lease_id == lease_id).order_by(Case.created_at.desc())
        )
        return result.scalars().all()

    async def get_open_case_by_lease(self, lease_id: uuid.UUID) -> Case | None:
        """Finds current open case for a lease if any exists."""
        result = await self.db.execute(
            select(Case).filter(
                Case.lease_id == lease_id,
                Case.status.in_([CaseStatus.OPEN, CaseStatus.UNDER_REVIEW, CaseStatus.NOTICE_SENT, CaseStatus.DEMAND_SENT])
            )
        )
        return result.scalars().first()
