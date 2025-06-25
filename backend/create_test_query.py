#!/usr/bin/env python3
"""
Create a test query to debug the 500 error issue.
"""
import asyncio
import sys
from sqlalchemy import select

# Add the app directory to Python path
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.query import Query, QueryStatus
from app.models.workspace import Workspace
from app.models.database_connection import DatabaseConnection


async def create_test_query():
    """Create test query for debugging."""
    async with SessionLocal() as db:
        # First, let's check existing queries
        print("Existing queries:")
        stmt = select(Query).order_by(Query.id)
        result = await db.execute(stmt)
        queries = result.scalars().all()
        
        for query in queries:
            print(f"  Query {query.id}: {query.name} (workspace_id={query.workspace_id})")
        
        # Check workspaces with database connections
        print("\nWorkspaces with database connections:")
        stmt = select(Workspace).where(Workspace.database_connection_id.isnot(None))
        result = await db.execute(stmt)
        workspaces = result.scalars().all()
        
        if not workspaces:
            print("  No workspaces with database connections found!")
            return
        
        for ws in workspaces:
            print(f"  Workspace {ws.id}: {ws.name} (db_connection_id={ws.database_connection_id})")
        
        # Create a new test query
        workspace = workspaces[0]  # Use the first workspace with a DB connection
        
        test_query = Query(
            workspace_id=workspace.id,
            name="Test Query for Debugging",
            description="Simple test query to debug execution issues",
            sql_template="SELECT 'Hello' as greeting, :name as name, CURRENT_TIMESTAMP as timestamp",
            params_info={
                "name": {"type": "string", "label": "Your Name", "required": True}
            },
            status=QueryStatus.AVAILABLE,
            created_by="admin"
        )
        
        db.add(test_query)
        await db.commit()
        await db.refresh(test_query)
        
        print(f"\nCreated test query:")
        print(f"  ID: {test_query.id}")
        print(f"  Name: {test_query.name}")
        print(f"  Workspace: {workspace.name}")
        print(f"  SQL: {test_query.sql_template}")
        
        # Also create a test query with no parameters
        simple_query = Query(
            workspace_id=workspace.id,
            name="Simple Test Query (No Params)",
            description="Simple query without parameters",
            sql_template="SELECT 1 as id, 'Test' as message, CURRENT_TIMESTAMP as created_at",
            params_info={},
            status=QueryStatus.AVAILABLE,
            created_by="admin"
        )
        
        db.add(simple_query)
        await db.commit()
        await db.refresh(simple_query)
        
        print(f"\nCreated simple test query:")
        print(f"  ID: {simple_query.id}")
        print(f"  Name: {simple_query.name}")


if __name__ == "__main__":
    asyncio.run(create_test_query())