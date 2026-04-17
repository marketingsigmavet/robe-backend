from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user
from app.models.users import User
from app.services.pets.pet_service import pet_service
from app.schemas.pets import PetResponse, PetCreate, PetUpdate

router = APIRouter()

@router.get("/", response_model=List[PetResponse])
async def list_pets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await pet_service.get_pets_for_user(db, current_user.user_id)


@router.post("/", response_model=PetResponse)
async def create_pet(
    payload: PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await pet_service.create_pet(db, user_id=current_user.user_id, pet_in=payload.model_dump(exclude_unset=True))


@router.get("/{id}", response_model=PetResponse)
async def get_pet(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await pet_service.get_pet(db, current_user.user_id, id)


@router.patch("/{id}", response_model=PetResponse)
async def update_pet(
    id: str,
    payload: PetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    update_data = payload.model_dump(exclude_unset=True)
    return await pet_service.update_pet(db, user_id=current_user.user_id, pet_id=id, pet_in=update_data)


@router.delete("/{id}")
async def delete_pet(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await pet_service.delete_pet(db, user_id=current_user.user_id, pet_id=id)
    return {"status": "deleted"}
