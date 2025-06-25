from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud import query_crud
from app.schemas import QueryExecuteRequest, QueryExecuteResponse
from app.services import QueryExecutorService
from app.models.query import QueryStatus

router = APIRouter(tags=["execute"])
query_executor = QueryExecutorService()


@router.post("/execute/{query_id}", response_model=QueryExecuteResponse)
async def execute_query(
    query_id: UUID,
    request: QueryExecuteRequest,
    db: AsyncSession = Depends(get_db)
) -> QueryExecuteResponse:
    """
    Execute a published query (no authentication required).
    This is the public API endpoint for data consumption.
    """
    # Get query by UUID first
    query = await query_crud.get_by_uuid(db, uuid=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found or not available for public access"
        )
    
    # Get full query with workspace and database connection
    query = await query_crud.get_with_workspace(db, id=query.id)
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found or not available for public access"
        )
    
    if query.status != QueryStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Query is not available for public execution"
        )
    
    # Execute query
    result = await query_executor.execute_query(
        db,
        sql_template=query.sql_template,
        params=request.params,
        params_info=query.params_info,
        database_connection=query.workspace.database_connection
    )
    
    # Update last executed timestamp
    await query_crud.update_last_executed(db, query_id=query.id)
    
    return QueryExecuteResponse(
        query_id=query.id,
        query_uuid=query.uuid,
        query_name=query.name,
        **result
    )