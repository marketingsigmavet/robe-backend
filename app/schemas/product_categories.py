import uuid
from pydantic import BaseModel
from typing import Optional

class ProductCategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    description: Optional[str] = None

class ProductCategoryResponse(ProductCategoryBase):
    product_category_id: uuid.UUID

    model_config = {"from_attributes": True}
