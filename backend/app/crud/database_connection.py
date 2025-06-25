from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.database_connection import DatabaseConnection
from app.schemas.database_connection import DatabaseConnectionCreate, DatabaseConnectionUpdate
from app.core.security import encrypt_password
import json


class CRUDDatabaseConnection(CRUDBase[DatabaseConnection, DatabaseConnectionCreate, DatabaseConnectionUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: DatabaseConnectionCreate) -> DatabaseConnection:
        """Create a new database connection with encrypted password."""
        obj_data = obj_in.model_dump(exclude={'password'})
        
        # Encrypt password
        obj_data['password_encrypted'] = encrypt_password(obj_in.password)
        
        # Convert additional_params to JSON string if provided
        if obj_data.get('additional_params'):
            obj_data['additional_params'] = json.dumps(obj_data['additional_params'])
        
        db_obj = DatabaseConnection(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: DatabaseConnection, 
        obj_in: DatabaseConnectionUpdate
    ) -> DatabaseConnection:
        """Update database connection."""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Handle password update
        if 'password' in update_data:
            update_data['password_encrypted'] = encrypt_password(update_data.pop('password'))
        
        # Convert additional_params to JSON string if provided
        if 'additional_params' in update_data and update_data['additional_params'] is not None:
            update_data['additional_params'] = json.dumps(update_data['additional_params'])
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[DatabaseConnection]:
        """Get database connection by name."""
        query = select(DatabaseConnection).where(DatabaseConnection.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_connections(self, db: AsyncSession) -> list[DatabaseConnection]:
        """Get all active database connections."""
        query = select(DatabaseConnection).where(DatabaseConnection.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_count(self, db: AsyncSession) -> int:
        """Get total count of database connections."""
        from sqlalchemy import func
        query = select(func.count()).select_from(DatabaseConnection)
        result = await db.execute(query)
        return result.scalar() or 0


database_connection_crud = CRUDDatabaseConnection(DatabaseConnection)