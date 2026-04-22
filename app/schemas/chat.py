"""Chat session schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    """Used by users to start a new chat session."""
    topic_id: Optional[uuid.UUID] = None
    question_id: Optional[uuid.UUID] = None
    pet_id: Optional[uuid.UUID] = None
    personality_id: Optional[uuid.UUID] = None
    
    # If starting a general chat without a specific topic
    is_general_chat: bool = False
    initial_message: Optional[str] = None


class ChatSessionUpdate(BaseModel):
    session_title: Optional[str] = Field(None, max_length=200)
    is_archived: Optional[bool] = None


class ChatSessionResponse(BaseModel):
    chat_session_id: uuid.UUID
    user_id: uuid.UUID
    topic_id: Optional[uuid.UUID]
    question_id: Optional[uuid.UUID]
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


class ChatSessionSummary(BaseModel):
    """Lightweight session info for listing."""
    chat_session_id: uuid.UUID
    session_title: str
    session_type: str
    is_archived: bool
    started_at: datetime
    last_message_at: Optional[datetime]
    
    # ID links for frontend context
    topic_id: Optional[uuid.UUID]
    pet_id: Optional[uuid.UUID]

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    sessions: list[ChatSessionSummary]
    total: int


# ---------------------------------------------------------------------------
# Message schemas (for upcoming step, but defined here for reference)
# ---------------------------------------------------------------------------

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
