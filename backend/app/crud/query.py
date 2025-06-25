from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.query import Query, QueryStatus
from app.models.query_version import QueryVersion
from app.schemas.query import QueryCreate, QueryUpdate
import json


class CRUDQuery(CRUDBase[Query, QueryCreate, QueryUpdate]):
    async def get_by_workspace_and_uuid(
        self,
        db: AsyncSession,
        *,
        workspace_id: int,
        query_uuid: UUID
    ) -> Optional[Query]:
        """Get query by workspace ID and UUID."""
        query = (
            select(Query)
            .where(
                Query.workspace_id == workspace_id,
                Query.uuid == query_uuid
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    async def get_by_workspace(
        self,
        db: AsyncSession,
        *,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Query]:
        """Get queries by workspace."""
        query = (
            select(Query)
            .where(Query.workspace_id == workspace_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_status(
        self,
        db: AsyncSession,
        *,
        query_id: int,
        status: QueryStatus
    ) -> Optional[Query]:
        """Update query status."""
        query_obj = await self.get(db, id=query_id)
        if not query_obj:
            return None
            
        query_obj.status = status
        db.add(query_obj)
        await db.commit()
        await db.refresh(query_obj)
        return query_obj
    
    async def update_last_executed(
        self,
        db: AsyncSession,
        *,
        query_id: int
    ) -> None:
        """Update last executed timestamp."""
        stmt = (
            update(Query)
            .where(Query.id == query_id)
            .values(last_executed_at=datetime.utcnow())
        )
        await db.execute(stmt)
        await db.commit()
    
    async def get_inactive_queries(
        self,
        db: AsyncSession,
        *,
        days: int
    ) -> List[Query]:
        """Get queries that haven't been executed for specified days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(Query).where(
            Query.status == QueryStatus.AVAILABLE,
            (Query.last_executed_at.is_(None)) | (Query.last_executed_at < cutoff_date)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_workspace(
        self,
        db: AsyncSession,
        *,
        id: int
    ) -> Optional[Query]:
        """Get query with workspace and database connection loaded."""
        from app.models.workspace import Workspace
        query = (
            select(Query)
            .options(
                selectinload(Query.workspace)
                .selectinload(Workspace.database_connection)
            )
            .where(Query.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, *, obj_in: QueryCreate, **kwargs) -> Query:
        """Create a query with initial version."""
        # Create the query first
        query = await super().create(db, obj_in=obj_in, **kwargs)
        
        # Create initial version
        version_data = {
            "query_id": query.id,
            "version_number": 1,
            "name": "Initial version",
            "description": "Automatically created initial version",
            "sql_template": query.sql_template,
            "params_info": json.dumps(query.params_info) if query.params_info else None,
            "created_by": kwargs.get("created_by", "system"),
            "is_active": True
        }
        
        version = QueryVersion(**version_data)
        db.add(version)
        await db.commit()
        await db.refresh(version)
        
        # Update query with current_version_id
        query.current_version_id = version.id
        db.add(query)
        await db.commit()
        await db.refresh(query)
        
        return query


query_crud = CRUDQuery(Query)