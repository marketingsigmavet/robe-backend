from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import RoleChecker
from app.schemas.roles import RoleResponse, RoleCreate, RoleUpdate, UserRoleAssign, UserRoleResponse
from app.services.users.role_service import role_service
from app.models.users import User

router = APIRouter()

# --- Role Management ---
@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await role_service.get_all_roles(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=RoleResponse)
async def get_role(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await role_service.get_role(db, id)

@router.post("/", response_model=RoleResponse)
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await role_service.create_role(db, obj_in=payload)

@router.patch("/{id}", response_model=RoleResponse)
async def update_role(
    id: str,
    payload: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await role_service.update_role(db, id=id, obj_in=payload)

@router.delete("/{id}")
async def delete_role(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    await role_service.delete_role(db, id=id)
    return {"status": "deleted"}

# --- User Role Assignment ---
@router.post("/users/{user_id}/roles", response_model=UserRoleResponse)
async def assign_role_to_user(
    user_id: str,
    payload: UserRoleAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await role_service.assign_role_to_user(db, user_id=user_id, role_id=payload.role_id)

@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await role_service.remove_role_from_user(db, user_id=user_id, role_id=role_id)
