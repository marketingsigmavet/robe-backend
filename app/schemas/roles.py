import uuid
from datetime import datetime
from pydantic import BaseModel

class RoleBase(BaseModel):
    role_name: str
    description: str | None = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    role_name: str | None = None
    description: str | None = None

class RoleResponse(RoleBase):
    role_id: uuid.UUID
    is_deleted: bool
    deleted_at: datetime | None

    model_config = {"from_attributes": True}

class UserRoleAssign(BaseModel):
    role_id: uuid.UUID

class UserRoleResponse(BaseModel):
    user_role_id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    assigned_at: datetime
    role: RoleResponse

    model_config = {"from_attributes": True}
