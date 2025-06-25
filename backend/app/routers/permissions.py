from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_admin, get_current_user
from app.crud import workspace_crud, permission_crud
from app.schemas import PermissionCreate, PermissionResponse, PermissionBulkCreate
from app.services import ExternalAPIService
from app.models.permission import PrincipalType

router = APIRouter(prefix="/workspaces/{workspace_id}/permissions", tags=["permissions"])
external_api = ExternalAPIService()


@router.get("", response_model=List[PermissionResponse])
async def get_permissions(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
) -> List[PermissionResponse]:
    """Get all permissions for a workspace (admin only)."""
    workspace = await workspace_crud.get_by_uuid(db, uuid=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    permissions = await permission_crud.get_by_workspace(db, workspace_id=workspace.id)
    return [PermissionResponse.model_validate(p) for p in permissions]


@router.post("", response_model=List[PermissionResponse], status_code=status.HTTP_201_CREATED)
async def create_permissions(
    workspace_id: UUID,
    permissions_in: PermissionBulkCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
) -> List[PermissionResponse]:
    """Create or replace permissions for a workspace (admin only)."""
    workspace = await workspace_crud.get_by_uuid(db, uuid=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Get the token from request headers
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    
    # Validate principals exist in maxplatform
    for perm in permissions_in.permissions:
        if perm.principal_type == PrincipalType.USER:
            exists = await external_api.validate_user_exists(token, perm.principal_id)
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User '{perm.principal_id}' not found in maxplatform"
                )
        elif perm.principal_type == PrincipalType.GROUP:
            exists = await external_api.validate_group_exists(token, perm.principal_id)
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Group '{perm.principal_id}' not found in maxplatform"
                )
    
    # Replace all permissions
    permissions = await permission_crud.replace_permissions(
        db,
        workspace_id=workspace.id,
        permissions=permissions_in.permissions
    )
    
    return [PermissionResponse.model_validate(p) for p in permissions]