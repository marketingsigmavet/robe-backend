from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_active_user
from app.models.users import User
from app.schemas.product_categories import ProductCategoryResponse
from app.services.products.category_service import category_service

router = APIRouter()

@router.get("/", response_model=List[ProductCategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await category_service.get_all_categories(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=ProductCategoryResponse)
async def get_category(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await category_service.get_category(db, id)
