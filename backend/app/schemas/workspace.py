from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.workspace import WorkspaceType


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: WorkspaceType
    auto_close_days: Optional[int] = Field(90, ge=1, le=365)
    database_connection_id: Optional[int] = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    auto_close_days: Optional[int] = Field(None, ge=1, le=365)
    database_connection_id: Optional[int] = None


class WorkspaceResponse(WorkspaceBase):
    id: int
    uuid: UUID
    owner_id: str
    created_at: datetime
    query_count: int = 0
    database_connection_name: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }


class WorkspaceListResponse(BaseModel):
    items: List[WorkspaceResponse]
    total: int