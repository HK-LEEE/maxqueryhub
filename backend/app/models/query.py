from enum import Enum as PyEnum
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class QueryStatus(str, PyEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sql_template = Column(Text, nullable=False)
    params_info = Column(JSON, nullable=True)
    status = Column(Enum(QueryStatus), default=QueryStatus.UNAVAILABLE, nullable=False)
    created_by = Column(String(255), nullable=False)
    last_executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_version_id = Column(Integer, ForeignKey("query_versions.id"), nullable=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="queries")
    versions = relationship("QueryVersion", foreign_keys="QueryVersion.query_id", back_populates="query", cascade="all, delete-orphan")
    current_version = relationship("QueryVersion", foreign_keys=[current_version_id], post_update=True)