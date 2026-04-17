from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import RoleChecker
from app.models.users import User
from app.schemas.product_categories import ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse
from app.services.products.category_service import category_service

router = APIRouter()

@router.get("/", response_model=List[ProductCategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await category_service.get_all_categories(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=ProductCategoryResponse)
async def get_category(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await category_service.get_category(db, id)

@router.post("/", response_model=ProductCategoryResponse)
async def create_category(
    payload: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await category_service.create_category(db, obj_in=payload)

@router.patch("/{id}", response_model=ProductCategoryResponse)
async def update_category(
    id: str,
    payload: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await category_service.update_category(db, category_id=id, obj_in=payload)

@router.delete("/{id}")
async def delete_category(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    await category_service.delete_category(db, category_id=id)
    return {"status": "deleted"}
