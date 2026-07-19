from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.user import User
from backend.app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """User data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Finds a user by email address."""
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
