"""
Check UUID migration status
"""
import asyncio
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check if UUID columns exist
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'database_connections' 
        AND column_name IN ('id', 'uuid')
        ORDER BY column_name
    """))
    
    print("Database connections table columns:")
    for row in result:
        print(f"  {row.column_name}: {row.data_type}")
    
    # Check sample data
    result = conn.execute(text("""
        SELECT id, uuid, name 
        FROM database_connections 
        LIMIT 5
    """))
    
    print("\nSample data:")
    for row in result:
        print(f"  ID: {row.id}, UUID: {row.uuid}, Name: {row.name}")