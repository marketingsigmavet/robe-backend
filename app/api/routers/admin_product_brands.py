"""
Admin product brand endpoints — full CRUD (requires admin role).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import RoleChecker
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.product_brands import (
    ProductBrandCreate,
    ProductBrandResponse,
    ProductBrandUpdate,
)
from app.services.products.brand_service import brand_service

router = APIRouter()
admin_required = RoleChecker(["admin"])


@router.get("/", response_model=list[ProductBrandResponse])
async def list_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """List all brands (admin view — includes inactive)."""
    return await brand_service.get_all_brands(db, skip=skip, limit=limit)


@router.get("/{brand_id}", response_model=ProductBrandResponse)
async def get_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get a single brand by ID."""
    return await brand_service.get_brand(db, brand_id)


@router.post("/", response_model=ProductBrandResponse, status_code=201)
async def create_brand(
    payload: ProductBrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Create a new product brand."""
    return await brand_service.create_brand(db, obj_in=payload)


@router.patch("/{brand_id}", response_model=ProductBrandResponse)
async def update_brand(
    brand_id: uuid.UUID,
    payload: ProductBrandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Update a product brand."""
    return await brand_service.update_brand(db, brand_id=brand_id, obj_in=payload)


@router.delete("/{brand_id}")
async def delete_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Soft-delete a product brand."""
    await brand_service.delete_brand(db, brand_id=brand_id)
    return {"status": "deleted"}
