from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user, RoleChecker
from app.schemas.breeds import BreedResponse, BreedCreate, BreedUpdate
from app.services.pets.breed_service import breed_service
from app.models.users import User

router = APIRouter()

@router.get("/", response_model=List[BreedResponse])
async def list_breeds(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))  # TODO: switch to admin role dependency
):
    return await breed_service.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=BreedResponse)
async def get_breed(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await breed_service.get(db, id)

@router.post("/", response_model=BreedResponse)
async def create_breed(
    payload: BreedCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await breed_service.create(db, obj_in=payload)

@router.patch("/{id}", response_model=BreedResponse)
async def update_breed(
    id: str,
    payload: BreedUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await breed_service.update(db, id=id, obj_in=payload)

@router.delete("/{id}")
async def delete_breed(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    await breed_service.delete(db, id=id)
    return {"status": "deleted"}
