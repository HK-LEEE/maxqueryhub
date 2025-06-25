"""
Script to migrate all Integer IDs to UUID format in the database.
This script creates temporary UUID columns, migrates the data, 
and then replaces the original ID columns.
"""
import asyncio
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Convert to async URL if needed
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL


async def migrate_to_uuid():
    """Migrate all tables from Integer IDs to UUID IDs."""
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 1. Add temporary UUID columns to all tables
            print("Step 1: Adding temporary UUID columns...")
            
            await session.execute(text("ALTER TABLE database_connections ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid()"))
            await session.execute(text("ALTER TABLE workspaces ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid()"))
            await session.execute(text("ALTER TABLE workspaces ADD COLUMN uuid_database_connection_id UUID"))
            await session.execute(text("ALTER TABLE queries ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid()"))
            await session.execute(text("ALTER TABLE queries ADD COLUMN uuid_workspace_id UUID"))
            await session.execute(text("ALTER TABLE queries ADD COLUMN uuid_current_version_id UUID"))
            await session.execute(text("ALTER TABLE query_versions ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid()"))
            await session.execute(text("ALTER TABLE query_versions ADD COLUMN uuid_query_id UUID"))
            await session.execute(text("ALTER TABLE workspace_permissions ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid()"))
            await session.execute(text("ALTER TABLE workspace_permissions ADD COLUMN uuid_workspace_id UUID"))
            
            await session.commit()
            print("✓ Temporary UUID columns added")
            
            # 2. Update foreign key references with UUID values
            print("\nStep 2: Updating foreign key references...")
            
            # Update workspaces with database_connection UUID
            await session.execute(text("""
                UPDATE workspaces w
                SET uuid_database_connection_id = dc.uuid_id
                FROM database_connections dc
                WHERE w.database_connection_id = dc.id
            """))
            
            # Update queries with workspace UUID
            await session.execute(text("""
                UPDATE queries q
                SET uuid_workspace_id = w.uuid_id
                FROM workspaces w
                WHERE q.workspace_id = w.id
            """))
            
            # Update query_versions with query UUID
            await session.execute(text("""
                UPDATE query_versions qv
                SET uuid_query_id = q.uuid_id
                FROM queries q
                WHERE qv.query_id = q.id
            """))
            
            # Update queries with current_version UUID
            await session.execute(text("""
                UPDATE queries q
                SET uuid_current_version_id = qv.uuid_id
                FROM query_versions qv
                WHERE q.current_version_id = qv.id
            """))
            
            # Update workspace_permissions with workspace UUID
            await session.execute(text("""
                UPDATE workspace_permissions wp
                SET uuid_workspace_id = w.uuid_id
                FROM workspaces w
                WHERE wp.workspace_id = w.id
            """))
            
            await session.commit()
            print("✓ Foreign key references updated")
            
            # 3. Drop foreign key constraints
            print("\nStep 3: Dropping foreign key constraints...")
            
            # Get all foreign key constraints to drop
            constraints = await session.execute(text("""
                SELECT constraint_name, table_name
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_schema = 'public'
                AND table_name IN ('workspaces', 'queries', 'query_versions', 'workspace_permissions')
            """))
            
            for constraint in constraints:
                await session.execute(text(f"ALTER TABLE {constraint.table_name} DROP CONSTRAINT {constraint.constraint_name}"))
            
            await session.commit()
            print("✓ Foreign key constraints dropped")
            
            # 4. Drop old columns and rename new columns
            print("\nStep 4: Replacing ID columns...")
            
            # Database connections
            await session.execute(text("ALTER TABLE database_connections DROP COLUMN id"))
            await session.execute(text("ALTER TABLE database_connections RENAME COLUMN uuid_id TO id"))
            await session.execute(text("ALTER TABLE database_connections ADD PRIMARY KEY (id)"))
            
            # Workspaces
            await session.execute(text("ALTER TABLE workspaces DROP COLUMN id"))
            await session.execute(text("ALTER TABLE workspaces DROP COLUMN database_connection_id"))
            await session.execute(text("ALTER TABLE workspaces RENAME COLUMN uuid_id TO id"))
            await session.execute(text("ALTER TABLE workspaces RENAME COLUMN uuid_database_connection_id TO database_connection_id"))
            await session.execute(text("ALTER TABLE workspaces ADD PRIMARY KEY (id)"))
            
            # Queries
            await session.execute(text("ALTER TABLE queries DROP COLUMN id"))
            await session.execute(text("ALTER TABLE queries DROP COLUMN workspace_id"))
            await session.execute(text("ALTER TABLE queries DROP COLUMN current_version_id"))
            await session.execute(text("ALTER TABLE queries RENAME COLUMN uuid_id TO id"))
            await session.execute(text("ALTER TABLE queries RENAME COLUMN uuid_workspace_id TO workspace_id"))
            await session.execute(text("ALTER TABLE queries RENAME COLUMN uuid_current_version_id TO current_version_id"))
            await session.execute(text("ALTER TABLE queries ADD PRIMARY KEY (id)"))
            
            # Query versions
            await session.execute(text("ALTER TABLE query_versions DROP COLUMN id"))
            await session.execute(text("ALTER TABLE query_versions DROP COLUMN query_id"))
            await session.execute(text("ALTER TABLE query_versions RENAME COLUMN uuid_id TO id"))
            await session.execute(text("ALTER TABLE query_versions RENAME COLUMN uuid_query_id TO query_id"))
            await session.execute(text("ALTER TABLE query_versions ADD PRIMARY KEY (id)"))
            
            # Workspace permissions
            await session.execute(text("ALTER TABLE workspace_permissions DROP COLUMN id"))
            await session.execute(text("ALTER TABLE workspace_permissions DROP COLUMN workspace_id"))
            await session.execute(text("ALTER TABLE workspace_permissions RENAME COLUMN uuid_id TO id"))
            await session.execute(text("ALTER TABLE workspace_permissions RENAME COLUMN uuid_workspace_id TO workspace_id"))
            await session.execute(text("ALTER TABLE workspace_permissions ADD PRIMARY KEY (id)"))
            
            await session.commit()
            print("✓ ID columns replaced")
            
            # 5. Re-create foreign key constraints
            print("\nStep 5: Re-creating foreign key constraints...")
            
            await session.execute(text("ALTER TABLE workspaces ADD CONSTRAINT fk_workspaces_database_connection FOREIGN KEY (database_connection_id) REFERENCES database_connections(id)"))
            await session.execute(text("ALTER TABLE queries ADD CONSTRAINT fk_queries_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id)"))
            await session.execute(text("ALTER TABLE queries ADD CONSTRAINT fk_queries_current_version FOREIGN KEY (current_version_id) REFERENCES query_versions(id)"))
            await session.execute(text("ALTER TABLE query_versions ADD CONSTRAINT fk_query_versions_query FOREIGN KEY (query_id) REFERENCES queries(id)"))
            await session.execute(text("ALTER TABLE workspace_permissions ADD CONSTRAINT fk_workspace_permissions_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id)"))
            
            await session.commit()
            print("✓ Foreign key constraints re-created")
            
            # 6. Create indexes
            print("\nStep 6: Creating indexes...")
            
            await session.execute(text("CREATE INDEX idx_workspaces_owner_id ON workspaces(owner_id)"))
            await session.execute(text("CREATE INDEX idx_workspaces_database_connection_id ON workspaces(database_connection_id)"))
            await session.execute(text("CREATE INDEX idx_queries_workspace_id ON queries(workspace_id)"))
            await session.execute(text("CREATE INDEX idx_query_versions_query_id ON query_versions(query_id)"))
            await session.execute(text("CREATE INDEX idx_workspace_permissions_workspace_id ON workspace_permissions(workspace_id)"))
            
            await session.commit()
            print("✓ Indexes created")
            
            print("\n✨ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate_to_uuid())