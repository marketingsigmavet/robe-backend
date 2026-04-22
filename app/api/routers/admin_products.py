"""
Admin product endpoints — full CRUD (requires admin role).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import RoleChecker
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.products import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.products.product_service import product_service

router = APIRouter()
admin_required = RoleChecker(["admin"])


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    brand_id: uuid.UUID | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    is_active: bool | None = Query(None, description="Filter by active status"),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """List all products (admin view — includes inactive)."""
    products = await product_service.get_all_products(
        db,
        skip=skip,
        limit=limit,
        brand_id=brand_id,
        category_id=category_id,
        is_active=is_active,
        search=search,
    )
    total = await product_service.count_all_products(
        db,
        brand_id=brand_id,
        category_id=category_id,
        is_active=is_active,
        search=search,
    )
    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Get a single product by ID (including inactive)."""
    product = await product_service.get_product(db, product_id)
    return ProductResponse.model_validate(product)


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Create a new product."""
    product = await product_service.create_product(db, obj_in=payload)
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Update a product."""
    product = await product_service.update_product(
        db, product_id=product_id, obj_in=payload
    )
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """Soft-delete a product."""
    await product_service.delete_product(db, product_id=product_id)
    return {"status": "deleted"}
