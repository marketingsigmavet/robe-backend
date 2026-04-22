"""Topic and TopicQuestion schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# Question — nested helpers
# ═══════════════════════════════════════════════════════════════════════════

class SpeciesTag(BaseModel):
    species_id: uuid.UUID
    species_name: str
    model_config = {"from_attributes": True}


class BreedTag(BaseModel):
    breed_id: uuid.UUID
    breed_name: str
    model_config = {"from_attributes": True}


class ProductTag(BaseModel):
    product_id: uuid.UUID
    product_name: str
    image_url: str | None = None
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# Question — request schemas
# ═══════════════════════════════════════════════════════════════════════════

class QuestionCreate(BaseModel):
    question_text: str = Field(..., max_length=500)
    description: str | None = None
    sort_order: int = 0
    is_active: bool = True
    species_ids: list[uuid.UUID] = []
    breed_ids: list[uuid.UUID] = []
    product_ids: list[uuid.UUID] = []


class QuestionUpdate(BaseModel):
    question_text: str | None = Field(None, max_length=500)
    description: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None
    species_ids: list[uuid.UUID] | None = None
    breed_ids: list[uuid.UUID] | None = None
    product_ids: list[uuid.UUID] | None = None


# ═══════════════════════════════════════════════════════════════════════════
# Question — response schemas
# ═══════════════════════════════════════════════════════════════════════════

class QuestionResponse(BaseModel):
    question_id: uuid.UUID
    topic_id: uuid.UUID
    question_text: str
    description: str | None = None
    sort_order: int
    is_active: bool
    species: list[SpeciesTag] = []
    breeds: list[BreedTag] = []
    products: list[ProductTag] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionSummary(BaseModel):
    """Lightweight question for user-facing topic detail."""
    question_id: uuid.UUID
    question_text: str
    description: str | None = None
    species: list[SpeciesTag] = []
    breeds: list[BreedTag] = []
    products: list[ProductTag] = []

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# Topic — request schemas
# ═══════════════════════════════════════════════════════════════════════════

class TopicCreate(BaseModel):
    topic_name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    description: str | None = None
    icon_url: str | None = Field(None, max_length=500)
    sort_order: int = 0
    is_active: bool = True


class TopicUpdate(BaseModel):
    topic_name: str | None = Field(None, max_length=200)
    slug: str | None = Field(None, max_length=200)
    description: str | None = None
    icon_url: str | None = Field(None, max_length=500)
    sort_order: int | None = None
    is_active: bool | None = None


# ═══════════════════════════════════════════════════════════════════════════
# Topic — response schemas
# ═══════════════════════════════════════════════════════════════════════════

class TopicResponse(BaseModel):
    """Admin response — includes all fields."""
    topic_id: uuid.UUID
    topic_name: str
    slug: str
    description: str | None = None
    icon_url: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    questions: list[QuestionResponse] = []

    model_config = {"from_attributes": True}


class TopicSummary(BaseModel):
    """User-facing topic listing — active questions only."""
    topic_id: uuid.UUID
    topic_name: str
    slug: str
    description: str | None = None
    icon_url: str | None = None
    sort_order: int
    questions: list[QuestionSummary] = []

    model_config = {"from_attributes": True}


class TopicDetailResponse(BaseModel):
    """User-facing single topic detail."""
    topic_id: uuid.UUID
    topic_name: str
    slug: str
    description: str | None = None
    icon_url: str | None = None
    sort_order: int
    questions: list[QuestionSummary] = []

    model_config = {"from_attributes": True}
