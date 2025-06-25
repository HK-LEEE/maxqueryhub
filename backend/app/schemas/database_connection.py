from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.models.database_connection import DatabaseType


class DatabaseConnectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    database_type: DatabaseType
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., ge=0, le=65535)  # Changed gt=0 to ge=0 for SQLite
    database_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=0, max_length=100)  # Changed min_length=1 to min_length=0 for SQLite
    additional_params: Optional[Dict[str, Any]] = None
    is_active: bool = True


class DatabaseConnectionCreate(DatabaseConnectionBase):
    password: str = Field(..., min_length=0)  # 평문 비밀번호, 서버에서 암호화 (min_length=0 for SQLite)
    
    @field_validator('port')
    def validate_port(cls, v, values):
        # 데이터베이스 타입별 기본 포트 설정
        if v is None:
            db_type = values.get('database_type')
            default_ports = {
                DatabaseType.MYSQL: 3306,
                DatabaseType.POSTGRESQL: 5432,
                DatabaseType.MSSQL: 1433,
                DatabaseType.ORACLE: 1521,
                DatabaseType.SQLITE: None
            }
            return default_ports.get(db_type, 3306)
        return v


class DatabaseConnectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    database_type: Optional[DatabaseType] = None
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, ge=0, le=65535)  # Changed gt=0 to ge=0 for SQLite
    database_name: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, min_length=0, max_length=100)  # Changed min_length=1 to min_length=0 for SQLite
    password: Optional[str] = Field(None, min_length=0)  # 평문 비밀번호 (min_length=0 for SQLite)
    additional_params: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DatabaseConnectionResponse(DatabaseConnectionBase):
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class DatabaseConnectionListResponse(BaseModel):
    items: list[DatabaseConnectionResponse]
    total: int


class DatabaseConnectionTestRequest(BaseModel):
    database_type: DatabaseType
    host: str
    port: int = Field(..., ge=0, le=65535)  # Changed for SQLite compatibility
    database_name: str
    username: str
    password: str
    additional_params: Optional[Dict[str, Any]] = None


class DatabaseConnectionTestResponse(BaseModel):
    success: bool
    message: str
    version: Optional[str] = None