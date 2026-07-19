import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.document import Document
from backend.app.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Document data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Document, db)

    async def get_by_lease(self, lease_id: uuid.UUID) -> Sequence[Document]:
        """Finds all legal documents generated for a lease."""
        result = await self.db.execute(
            select(Document).filter(Document.lease_id == lease_id).order_by(Document.generated_at.desc())
        )
        return result.scalars().all()

    async def get_by_case(self, case_id: uuid.UUID) -> Sequence[Document]:
        """Finds all legal documents generated for a compliance case."""
        result = await self.db.execute(
            select(Document).filter(Document.case_id == case_id).order_by(Document.generated_at.desc())
        )
        return result.scalars().all()
