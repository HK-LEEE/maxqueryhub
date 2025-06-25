#!/usr/bin/env python3
"""Update owner_id and created_by to your actual email"""
import asyncio
import sys
sys.path.append('.')

from app.core.database import AsyncSessionLocal
from sqlalchemy import update
from app.models import Workspace, Query


async def update_owner(email: str):
    """Update owner_id and created_by to specified email"""
    async with AsyncSessionLocal() as db:
        try:
            # Update workspaces
            stmt = update(Workspace).values(owner_id=email)
            result = await db.execute(stmt)
            workspace_count = result.rowcount
            
            # Update queries
            stmt = update(Query).values(created_by=email)
            result = await db.execute(stmt)
            query_count = result.rowcount
            
            await db.commit()
            
            print(f"✅ Updated successfully!")
            print(f"  - {workspace_count} workspaces updated")
            print(f"  - {query_count} queries updated")
            print(f"  - All items now owned by: {email}")
            
        except Exception as e:
            print(f"❌ Error updating owner: {e}")
            await db.rollback()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_owner.py <your-email>")
        print("Example: python update_owner.py admin@company.com")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(update_owner(email))