import asyncio
from datetime import datetime
from sqlalchemy import select
from app.core.database import AsyncSessionLocal as SessionLocal, Base, engine
from app.core.security import encrypt_password
from app.models.workspace import Workspace, WorkspaceType
from app.models.query import Query, QueryStatus
from app.models.permission import WorkspacePermission, PrincipalType
from app.models.database_connection import DatabaseConnection, DatabaseType
import json


async def create_sample_data():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as db:
        # Check if sample data already exists
        result = await db.execute(select(DatabaseConnection).limit(1))
        if result.scalar():
            print("Sample data already exists")
            return
        
        # Create sample database connections
        db_connections = []
        
        # Local MySQL connection
        mysql_conn = DatabaseConnection(
            name="Local MySQL",
            database_type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            database_name="test_db",
            username="root",
            password_encrypted=encrypt_password("password123"),
            is_active=True
        )
        db.add(mysql_conn)
        db_connections.append(mysql_conn)
        
        # Local PostgreSQL connection
        pg_conn = DatabaseConnection(
            name="Local PostgreSQL",
            database_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database_name="max_queryhub",
            username="postgres",
            password_encrypted=encrypt_password("postgres"),
            is_active=True
        )
        db.add(pg_conn)
        db_connections.append(pg_conn)
        
        # Sample SQLite connection
        sqlite_conn = DatabaseConnection(
            name="Sample SQLite",
            database_type=DatabaseType.SQLITE,
            host="localhost",
            port=0,
            database_name="/tmp/sample.db",
            username="",
            password_encrypted=encrypt_password(""),
            is_active=True
        )
        db.add(sqlite_conn)
        db_connections.append(sqlite_conn)
        
        await db.commit()
        
        # Create sample workspaces with database connections
        ws1 = Workspace(
            name="Sales Analytics",
            type=WorkspaceType.GROUP,
            owner_id="admin",
            auto_close_days=90,
            database_connection_id=mysql_conn.id
        )
        db.add(ws1)
        
        ws2 = Workspace(
            name="HR Reports",
            type=WorkspaceType.GROUP,
            owner_id="admin",
            auto_close_days=60,
            database_connection_id=pg_conn.id
        )
        db.add(ws2)
        
        ws3 = Workspace(
            name="My Personal Queries",
            type=WorkspaceType.PERSONAL,
            owner_id="user1",
            auto_close_days=30,
            database_connection_id=sqlite_conn.id
        )
        db.add(ws3)
        
        await db.commit()
        
        # Create sample queries
        q1 = Query(
            workspace_id=ws1.id,
            name="Daily Sales Report",
            description="Get daily sales data for specified date range",
            sql_template="SELECT date, product_id, SUM(amount) as total_sales FROM sales WHERE date BETWEEN :start_date AND :end_date GROUP BY date, product_id",
            params_info={
                "start_date": {"type": "date", "label": "Start Date", "required": True},
                "end_date": {"type": "date", "label": "End Date", "required": True}
            },
            status=QueryStatus.AVAILABLE,
            created_by="admin"
        )
        db.add(q1)
        
        q2 = Query(
            workspace_id=ws1.id,
            name="Product Performance",
            description="Analyze product performance by category",
            sql_template="SELECT category, COUNT(*) as product_count, AVG(price) as avg_price FROM products WHERE category = :category GROUP BY category",
            params_info={
                "category": {"type": "string", "label": "Product Category", "required": True}
            },
            status=QueryStatus.UNAVAILABLE,
            created_by="admin"
        )
        db.add(q2)
        
        q3 = Query(
            workspace_id=ws2.id,
            name="Employee List",
            description="Get employee list by department",
            sql_template="SELECT employee_id, name, position, hire_date FROM employees WHERE department = :dept_name ORDER BY hire_date",
            params_info={
                "dept_name": {"type": "string", "label": "Department Name", "required": True}
            },
            status=QueryStatus.AVAILABLE,
            created_by="admin"
        )
        db.add(q3)
        
        await db.commit()
        
        # Create sample permissions
        # Give user1 access to Sales Analytics workspace
        perm1 = WorkspacePermission(
            workspace_id=ws1.id,
            principal_type=PrincipalType.USER,
            principal_id="user1"
        )
        db.add(perm1)
        
        # Give sales group access to Sales Analytics workspace
        perm2 = WorkspacePermission(
            workspace_id=ws1.id,
            principal_type=PrincipalType.GROUP,
            principal_id="sales"
        )
        db.add(perm2)
        
        # Give hr group access to HR Reports workspace
        perm3 = WorkspacePermission(
            workspace_id=ws2.id,
            principal_type=PrincipalType.GROUP,
            principal_id="hr"
        )
        db.add(perm3)
        
        await db.commit()
        
        print("Sample data created successfully!")
        print("\nDatabase Connections:")
        for conn in db_connections:
            print(f"  - {conn.name} ({conn.database_type})")
        print(f"\nWorkspaces: {3}")
        print(f"Queries: {3}")
        print(f"Permissions: {3}")


if __name__ == "__main__":
    asyncio.run(create_sample_data())