from enum import Enum as PyEnum
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class WorkspaceType(str, PyEnum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"


class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(WorkspaceType), nullable=False)
    owner_id = Column(String(255), nullable=False, index=True)
    database_connection_id = Column(Integer, ForeignKey("database_connections.id"), nullable=True)
    auto_close_days = Column(Integer, nullable=True, default=90)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    queries = relationship("Query", back_populates="workspace", cascade="all, delete-orphan")
    permissions = relationship("WorkspacePermission", back_populates="workspace", cascade="all, delete-orphan")
    database_connection = relationship("DatabaseConnection", back_populates="workspaces")