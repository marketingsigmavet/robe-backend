"""
Notification schemas — request / response models.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Notification types
# ---------------------------------------------------------------------------

class NotificationType(StrEnum):
    """
    Categories of in-app notification.

    Extend as new features are added.
    """

    SYSTEM = "system"
    AUTH = "auth"
    PET = "pet"
    CHAT = "chat"
    RECOMMENDATION = "recommendation"
    PRODUCT = "product"
    SUBSCRIPTION = "subscription"
    PROMO = "promo"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class NotificationCreate(BaseModel):
    """Used internally by services to create a notification."""

    user_id: uuid.UUID
    title: str = Field(..., max_length=200)
    body: str
    notification_type: NotificationType = NotificationType.SYSTEM


# ---------------------------------------------------------------------------
# Query parameters
# ---------------------------------------------------------------------------

class NotificationListParams(BaseModel):
    """Query filters for listing notifications."""

    is_read: bool | None = None
    notification_type: NotificationType | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class NotificationResponse(BaseModel):
    notification_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    body: str
    notification_type: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Paginated list with unread count for badge display."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class MarkReadResponse(BaseModel):
    notification_id: uuid.UUID
    is_read: bool
    read_at: datetime | None = None


class BulkMarkReadResponse(BaseModel):
    marked_count: int
