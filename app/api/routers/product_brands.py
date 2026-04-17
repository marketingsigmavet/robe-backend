from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user
from app.models.users import User
from app.schemas.product_brands import ProductBrandResponse
from app.services.products.brand_service import brand_service

router = APIRouter()

@router.get("/", response_model=List[ProductBrandResponse])
async def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await brand_service.get_all_brands(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=ProductBrandResponse)
async def get_brand(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await brand_service.get_brand(db, id)
