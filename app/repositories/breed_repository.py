from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.breeds import Breed
from app.repositories.base import BaseRepository
from app.schemas.breeds import BreedCreate, BreedUpdate

class BreedRepository(BaseRepository[Breed, BreedCreate, BreedUpdate]):
    def __init__(self):
        super().__init__(Breed)

    async def get_by_species_id(self, db: AsyncSession, species_id: Any) -> Sequence[Breed]:
        stmt = select(Breed).where(Breed.species_id == species_id, Breed.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().all()

breed_repository = BreedRepository()
