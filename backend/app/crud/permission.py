from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.permission import WorkspacePermission, PrincipalType
from app.schemas.permission import PermissionCreate, PermissionResponse


class CRUDPermission(CRUDBase[WorkspacePermission, PermissionCreate, PermissionResponse]):
    async def get_by_workspace(
        self,
        db: AsyncSession,
        *,
        workspace_id: int
    ) -> List[WorkspacePermission]:
        """Get all permissions for a workspace."""
        query = select(WorkspacePermission).where(
            WorkspacePermission.workspace_id == workspace_id
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_bulk(
        self,
        db: AsyncSession,
        *,
        workspace_id: int,
        permissions: List[PermissionCreate]
    ) -> List[WorkspacePermission]:
        """Create multiple permissions at once."""
        db_objs = []
        for perm in permissions:
            db_obj = WorkspacePermission(
                workspace_id=workspace_id,
                principal_type=perm.principal_type,
                principal_id=perm.principal_id
            )
            db.add(db_obj)
            db_objs.append(db_obj)
        
        await db.commit()
        for obj in db_objs:
            await db.refresh(obj)
        
        return db_objs
    
    async def delete_by_workspace(
        self,
        db: AsyncSession,
        *,
        workspace_id: int
    ) -> None:
        """Delete all permissions for a workspace."""
        stmt = delete(WorkspacePermission).where(
            WorkspacePermission.workspace_id == workspace_id
        )
        await db.execute(stmt)
        await db.commit()
    
    async def replace_permissions(
        self,
        db: AsyncSession,
        *,
        workspace_id: int,
        permissions: List[PermissionCreate]
    ) -> List[WorkspacePermission]:
        """Replace all permissions for a workspace."""
        # Delete existing permissions
        await self.delete_by_workspace(db, workspace_id=workspace_id)
        
        # Create new permissions
        return await self.create_bulk(db, workspace_id=workspace_id, permissions=permissions)


permission_crud = CRUDPermission(WorkspacePermission)