import asyncio
from typing import Dict, Any, Optional
import aiomysql
import asyncpg
from app.models.database_connection import DatabaseType
from app.schemas.database_connection import DatabaseConnectionTestRequest


class DatabaseTestService:
    """Service for testing database connections."""
    
    async def test_connection(self, conn_info: DatabaseConnectionTestRequest) -> Dict[str, Any]:
        """Test database connection based on type."""
        try:
            if conn_info.database_type == DatabaseType.MYSQL:
                return await self._test_mysql(conn_info)
            elif conn_info.database_type == DatabaseType.POSTGRESQL:
                return await self._test_postgresql(conn_info)
            elif conn_info.database_type == DatabaseType.MSSQL:
                return await self._test_mssql(conn_info)
            else:
                return {
                    "success": False,
                    "message": f"Database type {conn_info.database_type} is not supported yet"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    async def _test_mysql(self, conn_info: DatabaseConnectionTestRequest) -> Dict[str, Any]:
        """Test MySQL connection."""
        try:
            conn = await aiomysql.connect(
                host=conn_info.host,
                port=conn_info.port,
                user=conn_info.username,
                password=conn_info.password,
                db=conn_info.database_name,
                connect_timeout=5
            )
            
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT VERSION()")
                result = await cursor.fetchone()
                version = result[0] if result else "Unknown"
            
            conn.close()
            
            return {
                "success": True,
                "message": "Connection successful",
                "version": f"MySQL {version}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"MySQL connection failed: {str(e)}"
            }
    
    async def _test_postgresql(self, conn_info: DatabaseConnectionTestRequest) -> Dict[str, Any]:
        """Test PostgreSQL connection."""
        try:
            conn = await asyncpg.connect(
                host=conn_info.host,
                port=conn_info.port,
                user=conn_info.username,
                password=conn_info.password,
                database=conn_info.database_name,
                timeout=5
            )
            
            version = await conn.fetchval("SELECT version()")
            await conn.close()
            
            return {
                "success": True,
                "message": "Connection successful",
                "version": version.split(' ')[0] + ' ' + version.split(' ')[1] if version else "Unknown"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"PostgreSQL connection failed: {str(e)}"
            }
    
    async def _test_mssql(self, conn_info: DatabaseConnectionTestRequest) -> Dict[str, Any]:
        """Test MSSQL connection."""
        # TODO: Implement MSSQL connection test
        return {
            "success": False,
            "message": "MSSQL connection test not implemented yet"
        }
    
    def build_connection_string(self, db_connection) -> str:
        """Build connection string based on database type."""
        if db_connection.database_type == DatabaseType.MYSQL:
            return (f"mysql+aiomysql://{db_connection.username}:PASSWORD@"
                   f"{db_connection.host}:{db_connection.port}/{db_connection.database_name}")
        elif db_connection.database_type == DatabaseType.POSTGRESQL:
            return (f"postgresql+asyncpg://{db_connection.username}:PASSWORD@"
                   f"{db_connection.host}:{db_connection.port}/{db_connection.database_name}")
        else:
            raise ValueError(f"Unsupported database type: {db_connection.database_type}")


database_test_service = DatabaseTestService()