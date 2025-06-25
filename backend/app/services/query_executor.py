import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
import re
from app.models.database_connection import DatabaseType, DatabaseConnection
from app.core.security import decrypt_password


class QueryExecutorService:
    """Service for executing SQL queries with parameter binding."""
    
    def __init__(self):
        self.engine_cache: Dict[int, Engine] = {}
    
    def _get_connection_string(self, db_conn: DatabaseConnection) -> str:
        """Generate database connection string based on database type."""
        password = decrypt_password(db_conn.password_encrypted)
        
        # Replace localhost with 127.0.0.1 to force IPv4
        host = db_conn.host
        if host.lower() == 'localhost':
            host = '127.0.0.1'
            
        if db_conn.database_type == DatabaseType.MYSQL:
            return f"mysql+pymysql://{db_conn.username}:{password}@{host}:{db_conn.port}/{db_conn.database_name}"
        elif db_conn.database_type == DatabaseType.POSTGRESQL:
            return f"postgresql://{db_conn.username}:{password}@{host}:{db_conn.port}/{db_conn.database_name}"
        elif db_conn.database_type == DatabaseType.MSSQL:
            return f"mssql+pyodbc://{db_conn.username}:{password}@{host}:{db_conn.port}/{db_conn.database_name}?driver=ODBC+Driver+17+for+SQL+Server"
        elif db_conn.database_type == DatabaseType.ORACLE:
            return f"oracle+cx_oracle://{db_conn.username}:{password}@{host}:{db_conn.port}/{db_conn.database_name}"
        elif db_conn.database_type == DatabaseType.SQLITE:
            return f"sqlite:///{db_conn.database_name}"
        else:
            raise ValueError(f"Unsupported database type: {db_conn.database_type}")
    
    def _get_engine(self, db_conn: DatabaseConnection) -> Engine:
        """Get or create database engine for connection."""
        conn_id = db_conn.id
        if conn_id not in self.engine_cache:
            conn_string = self._get_connection_string(db_conn)
            # Add connection pool settings
            if db_conn.database_type != DatabaseType.SQLITE:
                self.engine_cache[conn_id] = create_engine(
                    conn_string,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True
                )
            else:
                self.engine_cache[conn_id] = create_engine(conn_string)
        return self.engine_cache[conn_id]
    
    @staticmethod
    def validate_and_prepare_query(sql_template: str, params: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """
        Validate and prepare SQL query with parameters.
        Converts :param style to :param_name for SQLAlchemy.
        """
        # Find all parameters in the template
        param_pattern = r':(\w+)'
        template_params = set(re.findall(param_pattern, sql_template))
        
        # Check if all template parameters are provided
        missing_params = template_params - set(params.keys())
        if missing_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required parameters: {', '.join(missing_params)}"
            )
        
        # Filter params to only include those used in template
        filtered_params = {k: v for k, v in params.items() if k in template_params}
        
        return sql_template, filtered_params
    
    async def execute_query(
        self,
        db: AsyncSession,
        sql_template: str,
        params: Dict[str, Any],
        params_info: Optional[Dict[str, Any]] = None,
        database_connection: Optional[DatabaseConnection] = None
    ) -> Dict[str, Any]:
        """Execute a parameterized SQL query and return results."""
        import logging
        logger = logging.getLogger(__name__)
        
        start_time = time.time()
        
        # Check if we have a database connection
        if not database_connection:
            logger.error("No database connection provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No database connection configured for this workspace"
            )
        
        logger.info(f"Database connection: id={database_connection.id}, type={database_connection.database_type}, "
                   f"active={database_connection.is_active}")
        
        if not database_connection.is_active:
            logger.error(f"Database connection {database_connection.id} is not active")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database connection is not active"
            )
        
        try:
            logger.info(f"SQL template: {sql_template}")
            logger.info(f"Input params: {params}")
            logger.info(f"Params info: {params_info}")
            
            # Validate and prepare query
            prepared_sql, prepared_params = self.validate_and_prepare_query(sql_template, params)
            
            logger.info(f"Prepared params: {prepared_params}")
            
            # Convert parameter types based on params_info
            if params_info:
                print(f"Params info: {params_info}")  # Debug log
                print(f"Prepared params: {prepared_params}")  # Debug log
                for param_name, param_value in prepared_params.items():
                    if param_name in params_info and isinstance(params_info[param_name], dict):
                        param_type = params_info[param_name].get("type", "string")
                        
                        # Type conversion
                        if param_type == "date" and isinstance(param_value, str):
                            try:
                                prepared_params[param_name] = datetime.strptime(param_value, "%Y-%m-%d").date()
                            except ValueError:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Invalid date format for parameter '{param_name}'. Expected YYYY-MM-DD"
                                )
                        elif param_type == "integer":
                            try:
                                prepared_params[param_name] = int(param_value)
                            except ValueError:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Invalid integer value for parameter '{param_name}'"
                                )
                        elif param_type == "float":
                            try:
                                prepared_params[param_name] = float(param_value)
                            except ValueError:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Invalid float value for parameter '{param_name}'"
                                )
            
            # Execute query using the database connection
            logger.info(f"Getting engine for database connection {database_connection.id}")
            try:
                engine = self._get_engine(database_connection)
            except Exception as e:
                logger.error(f"Failed to create engine: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to connect to database: {str(e)}"
                )
            
            logger.info("Executing query...")
            with engine.connect() as conn:
                stmt = text(prepared_sql)
                result = conn.execute(stmt, prepared_params)
                
                # Fetch results
                columns = list(result.keys())
                rows = result.fetchall()
                
                # Convert to list of dicts
                data = [dict(zip(columns, row)) for row in rows]
                
            logger.info(f"Query executed successfully, fetched {len(data)} rows")
            
            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "executed_at": datetime.utcnow(),
                "row_count": len(data),
                "data": data,
                "execution_time_ms": execution_time
            }
            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Query execution error: {str(e)}"
            )
        except Exception as e:
            import traceback
            error_detail = f"Unexpected error: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(f"Query execution error: {error_detail}")  # Log to console
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )