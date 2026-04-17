from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import RoleChecker
from app.models.users import User
from app.schemas.product_brands import ProductBrandCreate, ProductBrandUpdate, ProductBrandResponse
from app.services.products.brand_service import brand_service

router = APIRouter()

@router.get("/", response_model=List[ProductBrandResponse])
async def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await brand_service.get_all_brands(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=ProductBrandResponse)
async def get_brand(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await brand_service.get_brand(db, id)

@router.post("/", response_model=ProductBrandResponse)
async def create_brand(
    payload: ProductBrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await brand_service.create_brand(db, obj_in=payload)

@router.patch("/{id}", response_model=ProductBrandResponse)
async def update_brand(
    id: str,
    payload: ProductBrandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await brand_service.update_brand(db, brand_id=id, obj_in=payload)

@router.delete("/{id}")
async def delete_brand(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    await brand_service.delete_brand(db, brand_id=id)
    return {"status": "deleted"}
