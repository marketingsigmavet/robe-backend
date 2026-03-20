from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.services.notifications.notification_service import notification_service

router = APIRouter()

@router.get("/")
async def list_notifications(
    db: AsyncSession = Depends(get_db)
):
    user_id = "stub-id"
    return await notification_service.get_user_notifications(db, user_id)

@router.patch("/{id}/read")
async def mark_notification_read(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    # Simplistic stub retrieval and update
    notifs = await notification_service.get_user_notifications(db, id)
    if notifs:
        return await notification_service.mark_as_read(db, db_obj=notifs[0])
    return {"status": "not_found"}
