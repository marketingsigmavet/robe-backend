from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user, RoleChecker
from app.schemas.pet_species import PetSpeciesResponse, PetSpeciesCreate, PetSpeciesUpdate
from app.services.pets.species_service import species_service
from app.models.users import User

router = APIRouter()

@router.get("/", response_model=List[PetSpeciesResponse])
async def list_species(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))  # TODO: switch to admin role dependency
):
    return await species_service.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=PetSpeciesResponse)
async def get_species(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await species_service.get(db, id)

@router.post("/", response_model=PetSpeciesResponse)
async def create_species(
    payload: PetSpeciesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await species_service.create(db, obj_in=payload)

@router.patch("/{id}", response_model=PetSpeciesResponse)
async def update_species(
    id: str,
    payload: PetSpeciesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await species_service.update(db, id=id, obj_in=payload)

@router.delete("/{id}")
async def delete_species(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    await species_service.delete(db, id=id)
    return {"status": "deleted"}
