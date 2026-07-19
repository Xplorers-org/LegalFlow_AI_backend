from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.tenant import Tenant
from backend.app.repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Tenant data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Tenant, db)
