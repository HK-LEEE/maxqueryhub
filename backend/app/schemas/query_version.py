from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class QueryVersionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    sql_template: str = Field(..., min_length=1)
    params_info: Optional[Dict[str, Any]] = None


class QueryVersionCreate(QueryVersionBase):
    """Schema for creating a new query version"""
    pass


class QueryVersionResponse(QueryVersionBase):
    """Schema for query version response"""
    id: int
    uuid: UUID
    query_id: int
    version_number: int
    created_by: str
    created_at: datetime
    is_active: bool
    
    model_config = {
        "from_attributes": True
    }


class QueryVersionListResponse(BaseModel):
    """Schema for listing query versions"""
    items: List[QueryVersionResponse]
    total: int


class QueryVersionActivate(BaseModel):
    """Schema for activating a query version"""
    version_id: int