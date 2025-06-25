from datetime import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.crud import query_crud, workspace_crud
from app.models.query import QueryStatus
import logging

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing background scheduled tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    async def cleanup_inactive_queries(self):
        """Clean up inactive queries based on workspace settings."""
        logger.info("Starting inactive query cleanup task")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get all workspaces with auto_close_days set
                workspaces = await workspace_crud.get_multi(db, limit=1000)
                
                for workspace in workspaces:
                    if workspace.auto_close_days:
                        # Get inactive queries for this workspace
                        inactive_queries = await query_crud.get_inactive_queries(
                            db,
                            days=workspace.auto_close_days
                        )
                        
                        # Filter queries belonging to this workspace
                        workspace_queries = [
                            q for q in inactive_queries 
                            if q.workspace_id == workspace.id
                        ]
                        
                        # Update status to UNAVAILABLE
                        for query in workspace_queries:
                            await query_crud.update_status(
                                db,
                                query_id=query.id,
                                status=QueryStatus.UNAVAILABLE
                            )
                            logger.info(
                                f"Set query {query.id} to UNAVAILABLE due to inactivity"
                            )
                
                logger.info("Completed inactive query cleanup task")
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
    
    def start(self):
        """Start the scheduler."""
        # Schedule cleanup task to run daily at midnight
        self.scheduler.add_job(
            self.cleanup_inactive_queries,
            CronTrigger(hour=0, minute=0),  # Midnight every day
            id="cleanup_inactive_queries",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")


# Global scheduler instance
scheduler_service = SchedulerService()