from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.query_version import QueryVersion
from app.models.query import Query
from app.schemas.query_version import QueryVersionCreate, QueryVersionResponse
import json


class CRUDQueryVersion(CRUDBase[QueryVersion, QueryVersionCreate, QueryVersionResponse]):
    async def create_version(
        self,
        db: AsyncSession,
        *,
        query_id: int,
        obj_in: QueryVersionCreate,
        created_by: str
    ) -> QueryVersion:
        """Create a new version for a query."""
        # Get the next version number
        query = select(func.max(QueryVersion.version_number)).where(
            QueryVersion.query_id == query_id
        )
        result = await db.execute(query)
        max_version = result.scalar() or 0
        
        # Create version data
        version_data = obj_in.model_dump()
        version_data.update({
            "query_id": query_id,
            "version_number": max_version + 1,
            "created_by": created_by,
            "is_active": False  # New versions are inactive by default
        })
        
        # Convert params_info to JSON string if provided
        if version_data.get("params_info"):
            version_data["params_info"] = json.dumps(version_data["params_info"])
        
        # Create the version
        db_obj = QueryVersion(**version_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def get_versions_by_query(
        self,
        db: AsyncSession,
        *,
        query_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[QueryVersion]:
        """Get all versions for a query."""
        query = (
            select(QueryVersion)
            .where(QueryVersion.query_id == query_id)
            .order_by(QueryVersion.version_number.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active_version(
        self,
        db: AsyncSession,
        *,
        query_id: int
    ) -> Optional[QueryVersion]:
        """Get the active version for a query."""
        query = select(QueryVersion).where(
            QueryVersion.query_id == query_id,
            QueryVersion.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def set_active_version(
        self,
        db: AsyncSession,
        *,
        query_id: int,
        version_id: int
    ) -> QueryVersion:
        """Set a version as active and deactivate others."""
        # Deactivate all versions for this query
        await db.execute(
            select(QueryVersion).where(
                QueryVersion.query_id == query_id
            ).update({"is_active": False})
        )
        
        # Activate the specified version
        version = await self.get(db, id=version_id)
        if version and version.query_id == query_id:
            version.is_active = True
            
            # Update the query's current_version_id
            query_obj = await db.get(Query, query_id)
            if query_obj:
                query_obj.current_version_id = version_id
                # Also update the query's SQL template and params to match the version
                query_obj.sql_template = version.sql_template
                query_obj.params_info = json.loads(version.params_info) if version.params_info else None
            
            db.add(version)
            db.add(query_obj)
            await db.commit()
            await db.refresh(version)
            
        return version
    
    async def get_version_count(
        self,
        db: AsyncSession,
        *,
        query_id: int
    ) -> int:
        """Get the total number of versions for a query."""
        query = select(func.count()).select_from(QueryVersion).where(
            QueryVersion.query_id == query_id
        )
        result = await db.execute(query)
        return result.scalar() or 0


query_version_crud = CRUDQueryVersion(QueryVersion)