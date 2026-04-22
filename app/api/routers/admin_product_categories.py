"""
Admin product category endpoints — full CRUD (requires admin role).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import RoleChecker
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.product_categories import (
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCategoryUpdate,
)
from app.services.products.category_service import category_service

router = APIRouter()
admin_required = RoleChecker(["admin"])


@router.get("/", response_model=list[ProductCategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """List all categories (admin view — includes inactive)."""
    return await category_service.get_all_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=ProductCategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get a single category by ID."""
    return await category_service.get_category(db, category_id)


@router.post("/", response_model=ProductCategoryResponse, status_code=201)
async def create_category(
    payload: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Create a new product category."""
    return await category_service.create_category(db, obj_in=payload)


@router.patch("/{category_id}", response_model=ProductCategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    payload: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Update a product category."""
    return await category_service.update_category(
        db, category_id=category_id, obj_in=payload
    )


@router.delete("/{category_id}")
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Soft-delete a product category."""
    await category_service.delete_category(db, category_id=category_id)
    return {"status": "deleted"}
