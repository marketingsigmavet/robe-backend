from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_roles import UserRole
from app.repositories.base import BaseRepository
from app.schemas.roles import UserRoleAssign

class UserRoleRepository(BaseRepository[UserRole, Any, Any]):
    def __init__(self):
        super().__init__(UserRole)

    async def get_by_user_and_role(self, db: AsyncSession, user_id: Any, role_id: Any) -> UserRole | None:
        stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id, UserRole.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().first()

user_role_repository = UserRoleRepository()
