from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pets import Pet
from app.repositories.pet_repository import pet_repository


class PetService:
    async def create_pet(self, db: AsyncSession, *, pet_in: dict[str, Any]) -> Pet:
        return await pet_repository.create(db, obj_in=pet_in)

    async def get_pet(self, db: AsyncSession, pet_id: Any) -> Pet | None:
        return await pet_repository.get(db, pet_id)

    async def get_pets_for_owner(self, db: AsyncSession, owner_id: Any) -> Sequence[Pet]:
        return await pet_repository.get_by_owner_id(db, owner_id)

    async def update_pet(self, db: AsyncSession, *, db_obj: Pet, pet_in: dict[str, Any]) -> Pet:
        return await pet_repository.update(db, db_obj=db_obj, obj_in=pet_in)

    async def delete_pet(self, db: AsyncSession, *, pet_id: Any) -> Pet | None:
        return await pet_repository.delete(db, id=pet_id)


pet_service = PetService()
