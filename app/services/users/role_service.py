from typing import Any, Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.roles import Role
from app.models.user_roles import UserRole
from app.repositories.role_repository import role_repository
from app.repositories.user_role_repository import user_role_repository
from app.services.users.user_service import user_service
from app.schemas.roles import RoleCreate, RoleUpdate

class RoleService:
    async def create_role(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        if await role_repository.get_by_name(db, obj_in.role_name):
            raise HTTPException(status_code=400, detail="Role already exists")
        return await role_repository.create(db, obj_in=obj_in)

    async def get_role(self, db: AsyncSession, id: Any) -> Role:
        obj = await role_repository.get(db, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Role not found")
        return obj

    async def get_all_roles(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Role]:
        return await role_repository.get_multi(db, skip=skip, limit=limit)

    async def update_role(self, db: AsyncSession, *, id: Any, obj_in: RoleUpdate) -> Role:
        obj = await self.get_role(db, id)
        return await role_repository.update(db, db_obj=obj, obj_in=obj_in)

    async def delete_role(self, db: AsyncSession, *, id: Any) -> Role:
        await self.get_role(db, id) # check if exists
        return await role_repository.delete(db, id=id)

    async def assign_role_to_user(self, db: AsyncSession, user_id: Any, role_id: Any) -> UserRole:
        user = await user_service.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        role = await self.get_role(db, role_id)
        
        existing = await user_role_repository.get_by_user_and_role(db, user_id, role_id)
        if existing:
            raise HTTPException(status_code=400, detail="Role already assigned to user")
            
        return await user_role_repository.create(db, obj_in={"user_id": user_id, "role_id": role_id})

    async def remove_role_from_user(self, db: AsyncSession, user_id: Any, role_id: Any) -> dict:
        existing = await user_role_repository.get_by_user_and_role(db, user_id, role_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Role assignment not found")
            
        await user_role_repository.delete(db, id=existing.user_role_id)
        return {"status": "success"}

role_service = RoleService()
