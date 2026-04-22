"""
User-facing product brand endpoints — read-only, active brands only.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.product_brands import ProductBrandResponse
from app.services.products.brand_service import brand_service

router = APIRouter()


@router.get("/", response_model=list[ProductBrandResponse])
async def list_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, description="Search by brand name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active product brands."""
    return await brand_service.get_active_brands(db, skip=skip, limit=limit, search=search)


@router.get("/{brand_id}", response_model=ProductBrandResponse)
async def get_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a single active brand by ID."""
    return await brand_service.get_brand_for_user(db, brand_id)
