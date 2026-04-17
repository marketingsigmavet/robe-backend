import uuid
from pydantic import BaseModel

class PetSpeciesBase(BaseModel):
    species_name: str
    description: str | None = None

class PetSpeciesCreate(PetSpeciesBase):
    pass

class PetSpeciesUpdate(BaseModel):
    species_name: str | None = None
    description: str | None = None

class PetSpeciesResponse(PetSpeciesBase):
    species_id: uuid.UUID

    model_config = {"from_attributes": True}
