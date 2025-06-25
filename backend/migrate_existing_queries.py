import asyncio
import json
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine
from app.models.query import Query
from app.models.query_version import QueryVersion


async def migrate_existing_queries():
    """Migrate existing queries to have initial versions."""
    async with AsyncSessionLocal() as db:
        # Get all queries without versions
        query = select(Query).where(Query.current_version_id.is_(None))
        result = await db.execute(query)
        queries = result.scalars().all()
        
        if not queries:
            print("No queries to migrate")
            return
        
        print(f"Found {len(queries)} queries to migrate")
        
        for q in queries:
            # Create initial version
            version = QueryVersion(
                query_id=q.id,
                version_number=1,
                name="Initial version",
                description="Migrated from existing query",
                sql_template=q.sql_template,
                params_info=json.dumps(q.params_info) if q.params_info else None,
                created_by=q.created_by,
                is_active=True
            )
            db.add(version)
            await db.flush()  # Get the version ID
            
            # Update query with current_version_id
            q.current_version_id = version.id
            db.add(q)
            
            print(f"Migrated query '{q.name}' (ID: {q.id})")
        
        await db.commit()
        print("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate_existing_queries())