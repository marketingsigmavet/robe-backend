"""
User-facing product endpoints — read-only, active products only.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.products import ProductListResponse, ProductResponse
from app.services.products.product_service import product_service

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    brand_id: uuid.UUID | None = Query(None, description="Filter by brand"),
    category_id: uuid.UUID | None = Query(None, description="Filter by category"),
    species_id: uuid.UUID | None = Query(None, description="Filter by species"),
    search: str | None = Query(None, description="Search by product name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active products with optional filters."""
    products = await product_service.get_active_products(
        db,
        skip=skip,
        limit=limit,
        brand_id=brand_id,
        category_id=category_id,
        species_id=species_id,
        search=search,
    )
    total = await product_service.count_active_products(
        db,
        brand_id=brand_id,
        category_id=category_id,
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
    current_user: User = Depends(get_current_active_user),
):
    """Get a single active product by ID."""
    product = await product_service.get_product_for_user(db, product_id)
    return ProductResponse.model_validate(product)
