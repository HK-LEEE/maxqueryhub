#!/usr/bin/env python3
"""
Test script to debug query ID 7 execution issue.
"""
import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Add the app directory to Python path
sys.path.insert(0, '.')

from app.core.database import get_db, SessionLocal
from app.models.query import Query
from app.models.workspace import Workspace
from app.models.database_connection import DatabaseConnection


async def test_query_7():
    """Test query 7 and check its details."""
    async with SessionLocal() as db:
        # Get query with all relationships
        stmt = (
            select(Query)
            .options(
                selectinload(Query.workspace)
                .selectinload(Workspace.database_connection)
            )
            .where(Query.id == 7)
        )
        result = await db.execute(stmt)
        query = result.scalar_one_or_none()
        
        if not query:
            print("ERROR: Query with ID 7 not found!")
            return
        
        print(f"Query found:")
        print(f"  ID: {query.id}")
        print(f"  Name: {query.name}")
        print(f"  Workspace ID: {query.workspace_id}")
        print(f"  Status: {query.status}")
        print(f"  SQL Template: {query.sql_template}")
        print(f"  Params Info: {query.params_info}")
        
        if query.workspace:
            print(f"\nWorkspace:")
            print(f"  ID: {query.workspace.id}")
            print(f"  Name: {query.workspace.name}")
            print(f"  Database Connection ID: {query.workspace.database_connection_id}")
            
            if query.workspace.database_connection:
                db_conn = query.workspace.database_connection
                print(f"\nDatabase Connection:")
                print(f"  ID: {db_conn.id}")
                print(f"  Name: {db_conn.name}")
                print(f"  Type: {db_conn.database_type}")
                print(f"  Host: {db_conn.host}")
                print(f"  Port: {db_conn.port}")
                print(f"  Database: {db_conn.database_name}")
                print(f"  Is Active: {db_conn.is_active}")
            else:
                print("\n  WARNING: No database connection found!")
        else:
            print("\n  ERROR: No workspace found!")
        
        # Also check all queries in the database
        print("\n\nAll queries in database:")
        all_queries_stmt = select(Query)
        all_result = await db.execute(all_queries_stmt)
        all_queries = all_result.scalars().all()
        
        for q in all_queries:
            print(f"  Query {q.id}: {q.name} (workspace_id={q.workspace_id})")


if __name__ == "__main__":
    asyncio.run(test_query_7())