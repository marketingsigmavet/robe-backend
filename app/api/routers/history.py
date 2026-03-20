from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps.db import get_db
from app.services.chat.session_service import session_service

router = APIRouter()

@router.get("/sessions")
async def list_chat_history(
    db: AsyncSession = Depends(get_db)
):
    user_id = "stub-id"
    return await session_service.get_user_sessions(db, user_id)

@router.patch("/sessions/{id}/archive")
async def archive_session(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    session = await session_service.get_session(db, id)
    if session:
        return await session_service.archive_session(db, db_obj=session)
    return {"status": "not_found"}
