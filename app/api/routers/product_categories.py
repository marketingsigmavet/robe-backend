"""
User-facing product category endpoints — read-only, active categories only.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.product_categories import ProductCategoryResponse
from app.services.products.category_service import category_service

router = APIRouter()


@router.get("/", response_model=list[ProductCategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, description="Search by category name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active product categories."""
    return await category_service.get_active_categories(
        db, skip=skip, limit=limit, search=search
    )


@router.get("/{category_id}", response_model=ProductCategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a single active category by ID."""
    return await category_service.get_category_for_user(db, category_id)
