from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import RoleChecker
from app.models.users import User
from app.schemas.products import ProductCreate, ProductUpdate, ProductResponse
from app.services.products.product_service import product_service

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await product_service.get_all_products(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=ProductResponse)
async def get_product(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await product_service.get_product(db, id)

@router.post("/", response_model=ProductResponse)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await product_service.create_product(db, obj_in=payload)

@router.patch("/{id}", response_model=ProductResponse)
async def update_product(
    id: str,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    return await product_service.update_product(db, product_id=id, obj_in=payload)

@router.delete("/{id}")
async def delete_product(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"]))
):
    await product_service.delete_product(db, product_id=id)
    return {"status": "deleted"}
