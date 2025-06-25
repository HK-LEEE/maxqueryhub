from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query as QueryParam
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.crud import workspace_crud
from app.schemas import WorkspaceCreate, WorkspaceResponse, WorkspaceListResponse
from app.models.workspace import WorkspaceType

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=WorkspaceListResponse)
async def get_workspaces(
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> WorkspaceListResponse:
    """Get all workspaces accessible to the current user."""
    workspaces = await workspace_crud.get_by_user(
        db,
        user_id=current_user["user_id"],
        user_groups=current_user.get("groups", []),
        skip=skip,
        limit=limit
    )
    
    # Add query count to each workspace
    workspace_responses = []
    for ws in workspaces:
        ws_dict = {
            "id": ws.id,
            "name": ws.name,
            "type": ws.type,
            "owner_id": ws.owner_id,
            "auto_close_days": ws.auto_close_days,
            "database_connection_id": ws.database_connection_id,
            "database_connection_name": ws.database_connection.name if ws.database_connection else None,
            "created_at": ws.created_at,
            "query_count": len(ws.queries) if ws.queries else 0,
            "uuid": ws.uuid
        }
        workspace_responses.append(WorkspaceResponse(**ws_dict))
    
    total = len(workspace_responses)  # For simplicity, actual implementation should count from DB
    
    return WorkspaceListResponse(items=workspace_responses, total=total)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
) -> WorkspaceResponse:
    """Create a new workspace (admin only)."""
    workspace = await workspace_crud.create(
        db,
        obj_in=workspace_in,
        owner_id=current_user["user_id"]
    )
    
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        type=workspace.type,
        owner_id=workspace.owner_id,
        auto_close_days=workspace.auto_close_days,
        database_connection_id=workspace.database_connection_id,
        database_connection_name=workspace.database_connection.name if workspace.database_connection else None,
        created_at=workspace.created_at,
        query_count=0,
        uuid=workspace.uuid
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> WorkspaceResponse:
    """Get a specific workspace by UUID."""
    # Get workspace by UUID
    workspace = await workspace_crud.get_by_uuid(db, uuid=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check access
    has_access = await workspace_crud.has_access(
        db,
        workspace_id=workspace.id,
        user_id=current_user["user_id"],
        user_groups=current_user.get("groups", [])
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace"
        )
    
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        type=workspace.type,
        owner_id=workspace.owner_id,
        auto_close_days=workspace.auto_close_days,
        database_connection_id=workspace.database_connection_id,
        database_connection_name=workspace.database_connection.name if workspace.database_connection else None,
        created_at=workspace.created_at,
        query_count=len(workspace.queries) if workspace.queries else 0,
        uuid=workspace.uuid
    )