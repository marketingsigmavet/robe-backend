import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserSummary(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    mobile_number: str | None = None
    full_name: str | None = None
    profile_image_url: str | None = None
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}

class UserMeResponse(UserSummary):
    country: str | None = None
    city: str | None = None
    preferred_language: str | None = None
    created_at: datetime
    updated_at: datetime

class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    profile_image_url: str | None = None
    country: str | None = None
    city: str | None = None
    preferred_language: str | None = None
