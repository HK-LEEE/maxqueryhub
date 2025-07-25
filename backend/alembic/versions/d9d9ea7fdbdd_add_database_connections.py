"""Add database connections

Revision ID: d9d9ea7fdbdd
Revises: 51a64177d7ec
Create Date: 2025-06-25 06:45:58.327570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9d9ea7fdbdd'
down_revision = '51a64177d7ec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('database_connections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('database_type', sa.Enum('MYSQL', 'POSTGRESQL', 'MSSQL', 'ORACLE', 'SQLITE', name='databasetype'), nullable=False),
    sa.Column('host', sa.String(length=255), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('database_name', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password_encrypted', sa.Text(), nullable=False),
    sa.Column('additional_params', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_database_connections_id'), 'database_connections', ['id'], unique=False)
    op.add_column('workspaces', sa.Column('database_connection_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'workspaces', 'database_connections', ['database_connection_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'workspaces', type_='foreignkey')
    op.drop_column('workspaces', 'database_connection_id')
    op.drop_index(op.f('ix_database_connections_id'), table_name='database_connections')
    op.drop_table('database_connections')
    # ### end Alembic commands ###