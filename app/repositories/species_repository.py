from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pet_species import PetSpecies
from app.repositories.base import BaseRepository
from app.schemas.pet_species import PetSpeciesCreate, PetSpeciesUpdate

class PetSpeciesRepository(BaseRepository[PetSpecies, PetSpeciesCreate, PetSpeciesUpdate]):
    def __init__(self):
        super().__init__(PetSpecies)

    async def get_by_name(self, db: AsyncSession, name: str) -> PetSpecies | None:
        stmt = select(PetSpecies).where(PetSpecies.species_name == name, PetSpecies.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().first()

species_repository = PetSpeciesRepository()
