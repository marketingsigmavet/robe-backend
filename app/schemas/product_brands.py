"""Product Brand schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class ProductBrandCreate(BaseModel):
    brand_name: str = Field(..., max_length=200)
    description: str | None = None
    logo_url: str | None = Field(None, max_length=500)
    website_url: str | None = Field(None, max_length=500)
    is_active: bool = True


class ProductBrandUpdate(BaseModel):
    brand_name: str | None = Field(None, max_length=200)
    description: str | None = None
    logo_url: str | None = Field(None, max_length=500)
    website_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class ProductBrandResponse(BaseModel):
    brand_id: uuid.UUID
    brand_name: str
    description: str | None = None
    logo_url: str | None = None
    website_url: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductBrandSummary(BaseModel):
    """Lightweight brand info embedded in product responses."""

    brand_id: uuid.UUID
    brand_name: str
    logo_url: str | None = None

    model_config = {"from_attributes": True}
