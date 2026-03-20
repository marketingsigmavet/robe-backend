from typing import Any
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.services.pets.pet_service import pet_service

router = APIRouter()

@router.get("/")
async def list_pets(
    db: AsyncSession = Depends(get_db)
):
    user_id = "stub-id"
    return await pet_service.get_pets_for_owner(db, user_id)

@router.post("/")
async def create_pet(
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    return await pet_service.create_pet(db, pet_in=payload)

@router.get("/{id}")
async def get_pet(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    return await pet_service.get_pet(db, id)

@router.patch("/{id}")
async def update_pet(
    id: str,
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    # Db fetch needed for update_pet
    return {"status": f"pet {id} updated"}

@router.delete("/{id}")
async def delete_pet(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    await pet_service.delete_pet(db, pet_id=id)
    return {"status": "deleted"}
