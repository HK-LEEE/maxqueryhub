from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.query import QueryStatus


class QueryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    sql_template: str = Field(..., min_length=1)
    params_info: Optional[Dict[str, Any]] = None


class QueryCreate(QueryBase):
    pass


class QueryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    sql_template: Optional[str] = Field(None, min_length=1)
    params_info: Optional[Dict[str, Any]] = None


class QueryStatusUpdate(BaseModel):
    status: QueryStatus


class QueryResponse(QueryBase):
    id: int
    uuid: UUID
    workspace_id: int
    workspace_uuid: Optional[UUID] = None
    status: QueryStatus
    created_by: str
    created_at: datetime
    last_executed_at: Optional[datetime] = None
    current_version_id: Optional[int] = None
    version_count: Optional[int] = 0
    
    model_config = {
        "from_attributes": True
    }


class QueryListResponse(BaseModel):
    items: List[QueryResponse]
    total: int


class QueryExecuteRequest(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)
    version_id: Optional[int] = None  # Optional version to execute


class QueryExecuteResponse(BaseModel):
    query_id: int
    query_uuid: UUID
    query_name: str
    executed_at: datetime
    row_count: int
    data: List[Dict[str, Any]]
    execution_time_ms: int