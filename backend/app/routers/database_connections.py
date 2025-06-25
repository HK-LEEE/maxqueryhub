from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_admin
from app.crud.database_connection import database_connection_crud
from app.models.workspace import Workspace
from app.schemas.database_connection import (
    DatabaseConnectionCreate,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    DatabaseConnectionListResponse,
    DatabaseConnectionTestRequest,
    DatabaseConnectionTestResponse
)
from app.services.database_test import database_test_service

router = APIRouter(prefix="/database-connections", tags=["database-connections"])


@router.get("", response_model=DatabaseConnectionListResponse)
async def get_database_connections(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
) -> DatabaseConnectionListResponse:
    """Get all database connections (admin only)."""
    connections = await database_connection_crud.get_multi(db, skip=skip, limit=limit)
    total = await database_connection_crud.get_count(db)
    
    return DatabaseConnectionListResponse(
        items=[DatabaseConnectionResponse.model_validate(conn) for conn in connections],
        total=total
    )


@router.post("", response_model=DatabaseConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_database_connection(
    connection_in: DatabaseConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
) -> DatabaseConnectionResponse:
    """Create a new database connection (admin only)."""
    # Check if name already exists
    existing = await database_connection_crud.get_by_name(db, name=connection_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database connection with name '{connection_in.name}' already exists"
        )
    
    connection = await database_connection_crud.create(db, obj_in=connection_in)
    return DatabaseConnectionResponse.model_validate(connection)


@router.get("/{connection_id}", response_model=DatabaseConnectionResponse)
async def get_database_connection(
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
) -> DatabaseConnectionResponse:
    """Get a specific database connection (admin only)."""
    connection = await database_connection_crud.get_by_uuid(db, uuid=connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    
    return DatabaseConnectionResponse.model_validate(connection)


@router.patch("/{connection_id}", response_model=DatabaseConnectionResponse)
async def update_database_connection(
    connection_id: UUID,
    connection_in: DatabaseConnectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
) -> DatabaseConnectionResponse:
    """Update a database connection (admin only)."""
    connection = await database_connection_crud.get_by_uuid(db, uuid=connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    
    # Check if new name already exists (if name is being updated)
    if connection_in.name and connection_in.name != connection.name:
        existing = await database_connection_crud.get_by_name(db, name=connection_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database connection with name '{connection_in.name}' already exists"
            )
    
    updated_connection = await database_connection_crud.update(
        db, db_obj=connection, obj_in=connection_in
    )
    return DatabaseConnectionResponse.model_validate(updated_connection)


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database_connection(
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a database connection (admin only)."""
    connection = await database_connection_crud.get_by_uuid(db, uuid=connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    
    # Check if any workspaces are using this connection
    workspace_count_query = select(func.count()).select_from(Workspace).where(
        Workspace.database_connection_id == connection.id
    )
    result = await db.execute(workspace_count_query)
    workspace_count = result.scalar()
    
    if workspace_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete: {workspace_count} workspace(s) are using this connection"
        )
    
    await database_connection_crud.remove(db, id=connection.id)


@router.post("/test", response_model=DatabaseConnectionTestResponse)
async def test_database_connection(
    test_request: DatabaseConnectionTestRequest,
    current_user: dict = Depends(require_admin)
) -> DatabaseConnectionTestResponse:
    """Test a database connection without saving (admin only)."""
    result = await database_test_service.test_connection(test_request)
    return DatabaseConnectionTestResponse(**result)