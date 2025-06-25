from enum import Enum as PyEnum
import uuid
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class PrincipalType(str, PyEnum):
    USER = "USER"
    GROUP = "GROUP"


class WorkspacePermission(Base):
    __tablename__ = "workspace_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    principal_type = Column(Enum(PrincipalType), nullable=False)
    principal_id = Column(String(255), nullable=False)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="permissions")