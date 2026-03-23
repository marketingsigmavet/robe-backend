from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pets import Pet
from app.repositories.base import BaseRepository


class PetRepository(BaseRepository[Pet, Any, Any]):
    def __init__(self):
        super().__init__(Pet)

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Pet:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> Pet | None:
        return await super().get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[Pet]:
        return await super().get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: Pet, obj_in: dict[str, Any]) -> Pet:
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> Pet | None:
        return await super().delete(db, id=id)

    async def get_by_user_id(self, db: AsyncSession, user_id: Any) -> Sequence[Pet]:
        stmt = select(Pet).where(Pet.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id_and_pet_id(self, db: AsyncSession, user_id: Any, pet_id: Any) -> Pet | None:
        stmt = select(Pet).where(Pet.user_id == user_id, Pet.pet_id == pet_id)
        result = await db.execute(stmt)
        return result.scalars().first()


pet_repository = PetRepository()
