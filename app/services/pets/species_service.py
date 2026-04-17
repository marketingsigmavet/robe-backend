from typing import Any, Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pet_species import PetSpecies
from app.models.pets import Pet
from app.repositories.species_repository import species_repository
from app.repositories.breed_repository import breed_repository
from app.schemas.pet_species import PetSpeciesCreate, PetSpeciesUpdate

class PetSpeciesService:
    async def create(self, db: AsyncSession, *, obj_in: PetSpeciesCreate) -> PetSpecies:
        if await species_repository.get_by_name(db, obj_in.species_name):
            raise HTTPException(status_code=400, detail="Species with this name already exists")
        return await species_repository.create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> PetSpecies:
        obj = await species_repository.get(db, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Species not found")
        return obj

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[PetSpecies]:
        return await species_repository.get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, id: Any, obj_in: PetSpeciesUpdate) -> PetSpecies:
        obj = await self.get(db, id)
        return await species_repository.update(db, db_obj=obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> PetSpecies:
        obj = await self.get(db, id)
        
        # Check constraints
        breeds = await breed_repository.get_by_species_id(db, id)
        if breeds:
            raise HTTPException(status_code=400, detail="Cannot delete species with assigned breeds.")
            
        stmt = select(Pet).where(Pet.species_id == id, Pet.is_deleted == False)
        result = await db.execute(stmt)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Cannot delete species with active pets.")
            
        return await species_repository.delete(db, id=id)

species_service = PetSpeciesService()
