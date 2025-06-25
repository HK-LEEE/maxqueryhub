from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.crud import query_crud, workspace_crud
from app.crud.query_version import query_version_crud
from app.schemas.query_version import (
    QueryVersionCreate,
    QueryVersionResponse,
    QueryVersionListResponse,
    QueryVersionActivate
)

router = APIRouter(tags=["query-versions"])


@router.get("/queries/{query_id}/versions", response_model=QueryVersionListResponse)
async def get_query_versions(
    query_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryVersionListResponse:
    """Get all versions for a query."""
    # Check if query exists and user has access
    query = await query_crud.get_by_uuid(db, uuid=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check workspace access
    has_access = await workspace_crud.has_access(
        db,
        workspace_id=query.workspace_id,
        user_id=current_user["user_id"],
        user_groups=current_user.get("groups", [])
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this query"
        )
    
    # Use integer ID for internal operations
    versions = await query_version_crud.get_versions_by_query(
        db, query_id=query.id, skip=skip, limit=limit
    )
    
    total = await query_version_crud.get_version_count(db, query_id=query.id)
    
    return QueryVersionListResponse(
        items=[QueryVersionResponse.model_validate(v) for v in versions],
        total=total
    )


@router.post("/queries/{query_id}/versions", response_model=QueryVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_query_version(
    query_id: UUID,
    version_in: QueryVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryVersionResponse:
    """Create a new version for a query."""
    # Check if query exists and user has access
    query = await query_crud.get_by_uuid(db, uuid=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check workspace access
    has_access = await workspace_crud.has_access(
        db,
        workspace_id=query.workspace_id,
        user_id=current_user["user_id"],
        user_groups=current_user.get("groups", [])
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this query"
        )
    
    # Use integer ID for internal operations
    version = await query_version_crud.create_version(
        db,
        query_id=query.id,
        obj_in=version_in,
        created_by=current_user["user_id"]
    )
    
    return QueryVersionResponse.model_validate(version)


@router.get("/queries/{query_id}/versions/{version_id}", response_model=QueryVersionResponse)
async def get_query_version(
    query_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryVersionResponse:
    """Get a specific version of a query."""
    # Check if query exists and user has access
    query = await query_crud.get_by_uuid(db, uuid=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check workspace access
    has_access = await workspace_crud.has_access(
        db,
        workspace_id=query.workspace_id,
        user_id=current_user["user_id"],
        user_groups=current_user.get("groups", [])
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this query"
        )
    
    # Get version by UUID and check it belongs to the query
    version = await query_version_crud.get_by_uuid(db, uuid=version_id)
    if not version or version.query_id != query.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return QueryVersionResponse.model_validate(version)


@router.put("/queries/{query_id}/versions/{version_id}/activate", response_model=QueryVersionResponse)
async def activate_query_version(
    query_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryVersionResponse:
    """Activate a specific version of a query."""
    # Check if query exists and user has access
    query = await query_crud.get_by_uuid(db, uuid=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check workspace access
    has_access = await workspace_crud.has_access(
        db,
        workspace_id=query.workspace_id,
        user_id=current_user["user_id"],
        user_groups=current_user.get("groups", [])
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this query"
        )
    
    # Get version by UUID to get its integer ID
    version = await query_version_crud.get_by_uuid(db, uuid=version_id)
    if not version or version.query_id != query.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # Use integer IDs for internal operations
    activated_version = await query_version_crud.set_active_version(
        db,
        query_id=query.id,
        version_id=version.id
    )
    
    if not activated_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return QueryVersionResponse.model_validate(activated_version)