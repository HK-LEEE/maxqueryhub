from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query as QueryParam
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.crud import workspace_crud, query_crud
from app.schemas import (
    QueryCreate, QueryResponse, QueryListResponse,
    QueryStatusUpdate, QueryExecuteRequest, QueryExecuteResponse
)
from app.services import QueryExecutorService
from app.models.query import QueryStatus

router = APIRouter(tags=["queries"])
query_executor = QueryExecutorService()


@router.get("/debug/query/{query_id}")
async def debug_query(
    query_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to check query details."""
    # Get query by UUID first
    query = await query_crud.get_by_uuid(db, uuid=query_id)
    if not query:
        return {"error": f"Query {query_id} not found"}
    
    # Get query with all relationships using the integer ID
    query = await query_crud.get_with_workspace(db, id=query.id)
    
    if not query:
        return {"error": f"Query {query_id} not found"}
    
    result = {
        "query_id": query.id,
        "query_uuid": query.uuid,
        "query_name": query.name,
        "workspace_id": query.workspace_id,
        "workspace_name": query.workspace.name if query.workspace else "NO WORKSPACE",
        "has_database_connection": bool(query.workspace and query.workspace.database_connection),
        "database_connection_details": None
    }
    
    if query.workspace and query.workspace.database_connection:
        db_conn = query.workspace.database_connection
        result["database_connection_details"] = {
            "id": db_conn.id,
            "name": db_conn.name,
            "type": db_conn.database_type,
            "host": db_conn.host,
            "port": db_conn.port,
            "database": db_conn.database_name,
            "is_active": db_conn.is_active
        }
    
    return result


@router.get("/workspaces/{workspace_id}/queries", response_model=QueryListResponse)
async def get_queries(
    workspace_id: UUID,
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryListResponse:
    """Get all queries in a workspace."""
    # Get workspace by UUID first
    workspace = await workspace_crud.get_by_uuid(db, uuid=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check access using integer ID
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
    
    queries = await query_crud.get_by_workspace(
        db,
        workspace_id=workspace.id,
        skip=skip,
        limit=limit
    )
    
    total = len(queries)  # Simplified, should count from DB
    
    # Add workspace UUID to each query response
    query_responses = []
    for q in queries:
        q_dict = QueryResponse.model_validate(q).model_dump()
        q_dict['workspace_uuid'] = workspace.uuid
        query_responses.append(QueryResponse(**q_dict))
    
    return QueryListResponse(
        items=query_responses,
        total=total
    )


@router.post("/workspaces/{workspace_id}/queries", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def create_query(
    workspace_id: UUID,
    query_in: QueryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryResponse:
    """Create a new query in a workspace."""
    # Get workspace by UUID first
    workspace = await workspace_crud.get_by_uuid(db, uuid=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check access using integer ID
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
    
    query = await query_crud.create(
        db,
        obj_in=query_in,
        workspace_id=workspace.id,
        created_by=current_user["user_id"]
    )
    
    # Add workspace UUID to response
    response = QueryResponse.model_validate(query)
    response_dict = response.model_dump()
    response_dict['workspace_uuid'] = workspace.uuid
    return QueryResponse(**response_dict)


@router.get("/queries/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryResponse:
    """Get a specific query by ID."""
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
    
    # Get workspace to include UUID
    workspace = await workspace_crud.get(db, id=query.workspace_id)
    
    # Add workspace UUID to response
    response = QueryResponse.model_validate(query)
    response_dict = response.model_dump()
    response_dict['workspace_uuid'] = workspace.uuid if workspace else None
    return QueryResponse(**response_dict)


@router.patch("/queries/{query_id}/status", response_model=QueryResponse)
async def update_query_status(
    query_id: UUID,
    status_update: QueryStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryResponse:
    """Update query status (publish/unpublish)."""
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
    
    updated_query = await query_crud.update_status(
        db,
        query_id=query.id,
        status=status_update.status
    )
    
    # Get workspace to include UUID
    workspace = await workspace_crud.get(db, id=updated_query.workspace_id)
    
    # Add workspace UUID to response
    response = QueryResponse.model_validate(updated_query)
    response_dict = response.model_dump()
    response_dict['workspace_uuid'] = workspace.uuid if workspace else None
    return QueryResponse(**response_dict)


@router.post("/internal/execute/{query_id}", response_model=QueryExecuteResponse)
async def execute_query_internal(
    query_id: UUID,
    request: QueryExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> QueryExecuteResponse:
    """Execute a query internally (for testing in UI)."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get query by UUID first
        logger.info(f"Fetching query with uuid={query_id}")
        query = await query_crud.get_by_uuid(db, uuid=query_id)
        if not query:
            logger.error(f"Query with uuid={query_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with uuid={query_id} not found"
            )
        
        # Get query with workspace and database connection using integer ID
        query = await query_crud.get_with_workspace(db, id=query.id)
        if not query:
            logger.error(f"Query with id={query.id} not found in get_with_workspace")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query not found"
            )
        
        logger.info(f"Query found: name={query.name}, workspace_id={query.workspace_id}")
        
        # Check if workspace exists
        if not query.workspace:
            logger.error(f"Query {query_id} has no associated workspace")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query {query_id} has no associated workspace"
            )
        
        # Check workspace access
        logger.info(f"Checking access for user={current_user['user_id']} to workspace={query.workspace_id}")
        has_access = await workspace_crud.has_access(
            db,
            workspace_id=query.workspace_id,
            user_id=current_user["user_id"],
            user_groups=current_user.get("groups", [])
        )
        
        if not has_access:
            logger.warning(f"Access denied for user={current_user['user_id']} to workspace={query.workspace_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this query"
            )
        
        # Check database connection
        if not query.workspace.database_connection:
            logger.error(f"No database connection configured for workspace {query.workspace_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No database connection configured for workspace '{query.workspace.name}'"
            )
        
        logger.info(f"Database connection found: type={query.workspace.database_connection.database_type}, "
                   f"host={query.workspace.database_connection.host}")
        
        # Log query execution details
        logger.info(f"Executing query with params={request.params}")
        
        # Execute query
        result = await query_executor.execute_query(
            db,
            sql_template=query.sql_template,
            params=request.params,
            params_info=query.params_info,
            database_connection=query.workspace.database_connection
        )
        
        logger.info(f"Query executed successfully, row_count={result.get('row_count', 0)}")
        
        # Update last executed timestamp using integer ID
        await query_crud.update_last_executed(db, query_id=query.id)
        
        return QueryExecuteResponse(
            query_id=query.id,
            query_uuid=query.uuid,
            query_name=query.name,
            **result
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Unexpected error executing query {query_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )