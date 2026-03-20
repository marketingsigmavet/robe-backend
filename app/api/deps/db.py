from collections.abc import AsyncGenerator
from typing import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session

# Simple alias for injecting database session instances to routers
async def get_db() -> AsyncIterable[AsyncSession]:
    async for session in get_db_session():
        yield session
