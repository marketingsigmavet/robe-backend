import uuid
from typing import Any, Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pets import Pet
from app.repositories.pet_repository import pet_repository


class PetService:
    async def create_pet(self, db: AsyncSession, *, user_id: Any, pet_in: dict[str, Any]) -> Pet:
        pet_in["user_id"] = user_id
        return await pet_repository.create(db, obj_in=pet_in)

    async def get_pet(self, db: AsyncSession, user_id: Any, pet_id: Any) -> Pet:
        pet = await pet_repository.get_by_user_id_and_pet_id(db, user_id, pet_id)
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        return pet

    async def get_pets_for_user(self, db: AsyncSession, user_id: Any) -> Sequence[Pet]:
        return await pet_repository.get_by_user_id(db, user_id)

    async def update_pet(self, db: AsyncSession, *, user_id: Any, pet_id: Any, pet_in: dict[str, Any]) -> Pet:
        pet = await self.get_pet(db, user_id, pet_id)
        return await pet_repository.update(db, db_obj=pet, obj_in=pet_in)

    async def delete_pet(self, db: AsyncSession, *, user_id: Any, pet_id: Any) -> Pet:
        pet = await self.get_pet(db, user_id, pet_id)
        return await pet_repository.delete(db, id=pet.pet_id)


pet_service = PetService()
