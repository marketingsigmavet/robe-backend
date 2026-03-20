import uuid
from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, Any, Any]):
    def __init__(self):
        super().__init__(User)

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> User:
        return await super().create(db, obj_in=obj_in)

    async def get(self, db: AsyncSession, id: Any) -> User | None:
        return await super().get(db, id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[User]:
        return await super().get_multi(db, skip=skip, limit=limit)

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: dict[str, Any]) -> User:
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> User | None:
        return await super().delete(db, id=id)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_mobile_number(self, db: AsyncSession, mobile_number: str) -> User | None:
        stmt = select(User).where(User.mobile_number == mobile_number)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def deactivate_user(self, db: AsyncSession, *, db_obj: User) -> User:
        return await self.update(db, db_obj=db_obj, obj_in={"is_active": False})


user_repository = UserRepository()
