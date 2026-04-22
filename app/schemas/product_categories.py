"""Product Category schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class ProductCategoryCreate(BaseModel):
    category_name: str = Field(..., max_length=200)
    description: str | None = None
    image_url: str | None = Field(None, max_length=500)
    is_active: bool = True


class ProductCategoryUpdate(BaseModel):
    category_name: str | None = Field(None, max_length=200)
    description: str | None = None
    image_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class ProductCategoryResponse(BaseModel):
    product_category_id: uuid.UUID
    category_name: str
    description: str | None = None
    image_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductCategorySummary(BaseModel):
    """Lightweight category info embedded in product responses."""

    product_category_id: uuid.UUID
    category_name: str

    model_config = {"from_attributes": True}
