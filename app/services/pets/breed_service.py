from typing import Any, Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.breeds import Breed
from app.models.pets import Pet
from app.repositories.breed_repository import breed_repository
from app.schemas.breeds import BreedCreate, BreedUpdate

class BreedService:
    async def create(self, db: AsyncSession, *, obj_in: BreedCreate) -> Breed:
        return await breed_repository.create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> Breed:
        obj = await breed_repository.get(db, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Breed not found")
        return obj

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Breed]:
        return await breed_repository.get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, id: Any, obj_in: BreedUpdate) -> Breed:
        obj = await self.get(db, id)
        return await breed_repository.update(db, db_obj=obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> Breed:
        obj = await self.get(db, id)
        
        # Check constraints
        stmt = select(Pet).where(Pet.breed_id == id, Pet.is_deleted == False)
        result = await db.execute(stmt)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Cannot delete breed with active pets.")
            
        return await breed_repository.delete(db, id=id)

breed_service = BreedService()
