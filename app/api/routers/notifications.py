"""
Notification router — authenticated endpoints for in-app notifications.

Endpoints
---------
GET    /notifications              – list current user's notifications (paginated, filterable)
GET    /notifications/unread-count – badge counter
PUT    /notifications/{id}/read    – mark one notification as read
PUT    /notifications/read-all     – mark all notifications as read
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.db import get_db
from app.models.users import User
from app.schemas.notifications import (
    BulkMarkReadResponse,
    MarkReadResponse,
    NotificationListResponse,
    NotificationResponse,
    NotificationType,
    UnreadCountResponse,
)
from app.services.notifications.notification_service import notification_service

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /notifications
# ---------------------------------------------------------------------------

@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    is_read: bool | None = Query(None, description="Filter by read status"),
    notification_type: NotificationType | None = Query(None, description="Filter by type"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Max items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List the current user's notifications, newest first.

    Supports filtering by ``is_read`` and ``notification_type``.
    Returns a paginated list with an ``unread_count`` for badge display.
    """
    user_id = current_user.user_id

    notifications = await notification_service.get_user_notifications(
        db,
        user_id,
        is_read=is_read,
        notification_type=notification_type.value if notification_type else None,
        skip=skip,
        limit=limit,
    )
    total = await notification_service.count_total(
        db,
        user_id,
        is_read=is_read,
        notification_type=notification_type.value if notification_type else None,
    )
    unread_count = await notification_service.get_unread_count(db, user_id)

    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


# ---------------------------------------------------------------------------
# GET /notifications/unread-count
# ---------------------------------------------------------------------------

@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the number of unread notifications (for badge display)."""
    count = await notification_service.get_unread_count(db, current_user.user_id)
    return UnreadCountResponse(unread_count=count)


# ---------------------------------------------------------------------------
# PUT /notifications/{notification_id}/read
# ---------------------------------------------------------------------------

@router.put("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark a single notification as read."""
    notif = await notification_service.mark_as_read(
        db, notification_id=notification_id, user_id=current_user.user_id
    )
    if notif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return MarkReadResponse(
        notification_id=notif.notification_id,
        is_read=notif.is_read,
        read_at=notif.read_at,
    )


# ---------------------------------------------------------------------------
# PUT /notifications/read-all
# ---------------------------------------------------------------------------

@router.put("/read-all", response_model=BulkMarkReadResponse)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark all of the current user's unread notifications as read."""
    count = await notification_service.mark_all_as_read(db, current_user.user_id)
    return BulkMarkReadResponse(marked_count=count)
