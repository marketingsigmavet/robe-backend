import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class ChatSessionCreate(BaseModel):
    topic_id: uuid.UUID
    # pet_id optionally attached
    pet_id: Optional[uuid.UUID] = None

class ChatSessionResponse(BaseModel):
    chat_session_id: uuid.UUID
    user_id: uuid.UUID
    topic_id: Optional[uuid.UUID]
    pet_id: Optional[uuid.UUID]
    personality_id: Optional[uuid.UUID]
    session_title: str
    session_type: str
    session_summary: Optional[str]
    is_general_chat: bool
    is_archived: bool
    started_at: datetime
    last_message_at: Optional[datetime]
    ended_at: Optional[datetime]

    model_config = {"from_attributes": True}

class MessageCreate(BaseModel):
    message_text: str

class MessageResponse(BaseModel):
    message_id: uuid.UUID
    chat_session_id: uuid.UUID
    sender_user_id: Optional[uuid.UUID]
    sender_type: str
    message_text: str
    message_type: str
    message_metadata: Optional[Dict[str, Any]]
    sequence_number: int
    contains_recommendation: bool
    is_edited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
