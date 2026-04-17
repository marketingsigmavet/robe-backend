import uuid
from pydantic import BaseModel
from typing import Optional

class ProductBrandBase(BaseModel):
    brand_name: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    is_active: bool = True

class ProductBrandCreate(ProductBrandBase):
    pass

class ProductBrandUpdate(BaseModel):
    brand_name: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductBrandResponse(ProductBrandBase):
    brand_id: uuid.UUID

    model_config = {"from_attributes": True}
