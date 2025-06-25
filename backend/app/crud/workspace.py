from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.workspace import Workspace, WorkspaceType
from app.models.permission import WorkspacePermission, PrincipalType
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class CRUDWorkspace(CRUDBase[Workspace, WorkspaceCreate, WorkspaceUpdate]):
    async def get_by_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: str,
        user_groups: List[str] = [],
        skip: int = 0,
        limit: int = 100
    ) -> List[Workspace]:
        """Get workspaces accessible by user (owned or with permissions)."""
        # Build conditions for workspace access
        conditions = [Workspace.owner_id == user_id]
        
        # Add personal workspace permissions
        personal_perm_query = select(WorkspacePermission.workspace_id).where(
            WorkspacePermission.principal_type == PrincipalType.USER,
            WorkspacePermission.principal_id == user_id
        )
        
        # Add group workspace permissions if user has groups
        if user_groups:
            group_perm_query = select(WorkspacePermission.workspace_id).where(
                WorkspacePermission.principal_type == PrincipalType.GROUP,
                WorkspacePermission.principal_id.in_(user_groups)
            )
            perm_subquery = personal_perm_query.union(group_perm_query)
        else:
            perm_subquery = personal_perm_query
            
        conditions.append(Workspace.id.in_(perm_subquery))
        
        # Execute query with query count
        query = (
            select(Workspace)
            .options(selectinload(Workspace.queries))
            .options(selectinload(Workspace.database_connection))
            .where(or_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def has_access(
        self,
        db: AsyncSession,
        *,
        workspace_id: int,
        user_id: str,
        user_groups: List[str] = []
    ) -> bool:
        """Check if user has access to workspace."""
        # Check if user is owner
        workspace = await self.get(db, id=workspace_id)
        if not workspace:
            return False
            
        if workspace.owner_id == user_id:
            return True
            
        # Check permissions
        conditions = [
            WorkspacePermission.workspace_id == workspace_id,
            WorkspacePermission.principal_type == PrincipalType.USER,
            WorkspacePermission.principal_id == user_id
        ]
        
        if user_groups:
            conditions.append(
                (WorkspacePermission.principal_type == PrincipalType.GROUP) &
                (WorkspacePermission.principal_id.in_(user_groups))
            )
            
        query = select(WorkspacePermission).where(or_(*conditions))
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def has_access_by_uuid(
        self,
        db: AsyncSession,
        *,
        workspace_uuid: UUID,
        user_id: str,
        user_groups: List[str] = []
    ) -> bool:
        """Check if user has access to workspace by UUID."""
        workspace = await self.get_by_uuid(db, uuid=workspace_uuid)
        if not workspace:
            return False
        return await self.has_access(
            db,
            workspace_id=workspace.id,
            user_id=user_id,
            user_groups=user_groups
        )


workspace_crud = CRUDWorkspace(Workspace)