import uuid
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field

class PetBase(BaseModel):
    pet_name: str
    gender: str | None = None
    date_of_birth: date | None = None
    age_in_months: int | None = None
    weight_kg: float | None = None
    color: str | None = None
    is_neutered: bool = False
    medical_notes: str | None = None
    allergies: dict[str, Any] | list[Any] | None = None
    dietary_preferences: dict[str, Any] | list[Any] | None = None
    activity_level: str | None = None
    profile_image_url: str | None = None
    is_active: bool = True

class PetCreate(PetBase):
    species_id: uuid.UUID
    breed_id: uuid.UUID | None = None

class PetUpdate(BaseModel):
    pet_name: str | None = None
    species_id: uuid.UUID | None = None
    breed_id: uuid.UUID | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    age_in_months: int | None = None
    weight_kg: float | None = None
    color: str | None = None
    is_neutered: bool | None = None
    medical_notes: str | None = None
    allergies: dict[str, Any] | list[Any] | None = None
    dietary_preferences: dict[str, Any] | list[Any] | None = None
    activity_level: str | None = None
    profile_image_url: str | None = None
    is_active: bool | None = None

class PetResponse(PetBase):
    pet_id: uuid.UUID
    user_id: uuid.UUID
    species_id: uuid.UUID
    breed_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
