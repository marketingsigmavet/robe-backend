from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from app.repositories.user_repository import user_repository


class UserService:
    async def create_user(self, db: AsyncSession, *, user_in: dict[str, Any]) -> User:
        return await user_repository.create(db, obj_in=user_in)

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        return await user_repository.get_by_email(db, email)
        
    async def get_user_by_mobile(self, db: AsyncSession, mobile_number: str) -> User | None:
        return await user_repository.get_by_mobile_number(db, mobile_number)

    async def get_user(self, db: AsyncSession, user_id: Any) -> User | None:
        return await user_repository.get(db, user_id)

    async def update_user(self, db: AsyncSession, *, db_obj: User, user_in: dict[str, Any]) -> User:
        return await user_repository.update(db, db_obj=db_obj, obj_in=user_in)

    async def deactivate_user(self, db: AsyncSession, *, db_obj: User) -> User:
        return await user_repository.deactivate_user(db, db_obj=db_obj)


user_service = UserService()
