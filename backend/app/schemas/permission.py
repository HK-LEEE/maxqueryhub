from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.permission import PrincipalType


class PermissionBase(BaseModel):
    principal_type: PrincipalType
    principal_id: str = Field(..., min_length=1)


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    uuid: UUID
    workspace_id: int
    
    model_config = {
        "from_attributes": True
    }


class PermissionBulkCreate(BaseModel):
    permissions: List[PermissionCreate]