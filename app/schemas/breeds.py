import uuid
from pydantic import BaseModel

class BreedBase(BaseModel):
    species_id: uuid.UUID
    breed_name: str
    breed_notes: str | None = None

class BreedCreate(BreedBase):
    pass

class BreedUpdate(BaseModel):
    species_id: uuid.UUID | None = None
    breed_name: str | None = None
    breed_notes: str | None = None

class BreedResponse(BreedBase):
    breed_id: uuid.UUID

    model_config = {"from_attributes": True}
