from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.roles import Role
from app.repositories.base import BaseRepository
from app.schemas.roles import RoleCreate, RoleUpdate

class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(Role)

    async def get_by_name(self, db: AsyncSession, role_name: str) -> Role | None:
        stmt = select(Role).where(Role.role_name == role_name, Role.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalars().first()

role_repository = RoleRepository()
