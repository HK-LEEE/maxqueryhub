"""add_uuid_columns

Revision ID: add_uuid_columns
Revises: 0b342fc69676
Create Date: 2025-06-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_uuid_columns'
down_revision = '0b342fc69676'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add UUID extension if using PostgreSQL
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Add UUID columns to all tables (keeping integer IDs)
    op.add_column('database_connections', sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False))
    op.add_column('workspaces', sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False))
    op.add_column('queries', sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False))
    op.add_column('query_versions', sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False))
    op.add_column('workspace_permissions', sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False))
    
    # Create unique indexes on UUID columns
    op.create_index('ix_database_connections_uuid', 'database_connections', ['uuid'], unique=True)
    op.create_index('ix_workspaces_uuid', 'workspaces', ['uuid'], unique=True)
    op.create_index('ix_queries_uuid', 'queries', ['uuid'], unique=True)
    op.create_index('ix_query_versions_uuid', 'query_versions', ['uuid'], unique=True)
    op.create_index('ix_workspace_permissions_uuid', 'workspace_permissions', ['uuid'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_workspace_permissions_uuid', 'workspace_permissions')
    op.drop_index('ix_query_versions_uuid', 'query_versions')
    op.drop_index('ix_queries_uuid', 'queries')
    op.drop_index('ix_workspaces_uuid', 'workspaces')
    op.drop_index('ix_database_connections_uuid', 'database_connections')
    
    # Drop UUID columns
    op.drop_column('workspace_permissions', 'uuid')
    op.drop_column('query_versions', 'uuid')
    op.drop_column('queries', 'uuid')
    op.drop_column('workspaces', 'uuid')
    op.drop_column('database_connections', 'uuid')