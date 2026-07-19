import uuid
from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from backend.app.models.base_class import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Generic async repository providing CRUD operations for database entities."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: uuid.UUID) -> ModelType | None:
        """Retrieves a single model instance by UUID."""
        result = await self.db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Retrieves a paginated list of model instances."""
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, obj_in: dict) -> ModelType:
        """Creates a new model instance."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: uuid.UUID, obj_in: dict) -> ModelType | None:
        """Updates an existing model instance."""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**{k: v for k, v in obj_in.items() if v is not None})
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        return await self.get(id)

    async def delete(self, id: uuid.UUID) -> bool:
        """Deletes a model instance by UUID."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0
