from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class QueryVersion(Base):
    __tablename__ = "query_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sql_template = Column(Text, nullable=False)
    params_info = Column(Text, nullable=True)  # JSON stored as text
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    query = relationship("Query", foreign_keys=[query_id], back_populates="versions")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('query_id', 'version_number', name='uq_query_version'),
    )