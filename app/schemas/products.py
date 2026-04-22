"""Product schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.product_brands import ProductBrandSummary
from app.schemas.product_categories import ProductCategorySummary


# ---------------------------------------------------------------------------
# Nested helpers for species / breed display
# ---------------------------------------------------------------------------

class SpeciesSummary(BaseModel):
    species_id: uuid.UUID
    species_name: str

    model_config = {"from_attributes": True}


class BreedSummary(BaseModel):
    breed_id: uuid.UUID
    breed_name: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    product_name: str = Field(..., max_length=200)
    sku: str = Field(..., max_length=100)
    brand_id: uuid.UUID
    product_category_id: uuid.UUID
    description: str | None = None
    life_stage: str | None = Field(None, max_length=100)
    usage_guidelines: str | None = None
    ingredients: str | None = None
    benefits: str | None = None
    product_url: str | None = Field(None, max_length=500)
    image_url: str | None = Field(None, max_length=500)
    is_active: bool = True
    species_ids: list[uuid.UUID] = []
    breed_ids: list[uuid.UUID] = []


class ProductUpdate(BaseModel):
    product_name: str | None = Field(None, max_length=200)
    sku: str | None = Field(None, max_length=100)
    brand_id: uuid.UUID | None = None
    product_category_id: uuid.UUID | None = None
    description: str | None = None
    life_stage: str | None = Field(None, max_length=100)
    usage_guidelines: str | None = None
    ingredients: str | None = None
    benefits: str | None = None
    product_url: str | None = Field(None, max_length=500)
    image_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None
    species_ids: list[uuid.UUID] | None = None
    breed_ids: list[uuid.UUID] | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class ProductResponse(BaseModel):
    product_id: uuid.UUID
    product_name: str
    sku: str
    description: str | None = None
    life_stage: str | None = None
    usage_guidelines: str | None = None
    ingredients: str | None = None
    benefits: str | None = None
    product_url: str | None = None
    image_url: str | None = None
    is_active: bool

    # Foreign key IDs (always present)
    brand_id: uuid.UUID
    product_category_id: uuid.UUID

    # Resolved nested objects
    brand: ProductBrandSummary | None = None
    category: ProductCategorySummary | None = None
    species: list[SpeciesSummary] = []
    breeds: list[BreedSummary] = []

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Paginated product listing."""

    products: list[ProductResponse]
    total: int
