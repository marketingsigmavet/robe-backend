import uuid
from pydantic import BaseModel
from datetime import datetime

class TopicBase(BaseModel):
    topic_name: str
    slug: str
    description: str | None = None
    icon_url: str | None = None
    sort_order: int = 0
    is_active: bool = True

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    topic_name: str | None = None
    slug: str | None = None
    description: str | None = None
    icon_url: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None

class TopicResponse(TopicBase):
    topic_id: uuid.UUID
    created_at: datetime
    is_deleted: bool
    deleted_at: datetime | None

    model_config = {"from_attributes": True}
