import uuid
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    product_name: str
    sku: str
    brand_id: uuid.UUID
    product_category_id: uuid.UUID
    description: Optional[str] = None
    life_stage: Optional[str] = None
    usage_guidelines: Optional[str] = None
    ingredients: Optional[str] = None
    benefits: Optional[str] = None
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    species_ids: List[uuid.UUID] = []
    breed_ids: List[uuid.UUID] = []

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    sku: Optional[str] = None
    brand_id: Optional[uuid.UUID] = None
    product_category_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    life_stage: Optional[str] = None
    usage_guidelines: Optional[str] = None
    ingredients: Optional[str] = None
    benefits: Optional[str] = None
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    species_ids: Optional[List[uuid.UUID]] = None
    breed_ids: Optional[List[uuid.UUID]] = None

class ProductResponse(ProductBase):
    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
    # Ideally nested schemas used for fully resolved relations if frontend requires
