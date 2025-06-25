import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine
from app.core.rate_limit import rate_limit_middleware, execute_rate_limiter, api_rate_limiter
from app.services.scheduler import scheduler_service
from app.routers import (
    health_router,
    workspaces_router,
    queries_router,
    permissions_router,
    external_router,
    execute_router
)
from app.routers.auth_proxy import router as auth_router
from app.routers.database_connections import router as db_connections_router
from app.routers.query_versions import router as query_versions_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application."""
    # Startup
    print("Starting Query Hub API Gateway...")
    # Start scheduler
    scheduler_service.start()
    # Start rate limiter cleanup tasks
    async with execute_rate_limiter, api_rate_limiter:
        yield
    # Shutdown
    print("Shutting down Query Hub API Gateway...")
    scheduler_service.shutdown()
    await engine.dispose()


app = FastAPI(
    title="Query Hub API Gateway",
    description="API Gateway for managing and executing SQL queries",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting middleware first (it will be executed after CORS)
@app.middleware("http")
async def add_rate_limit(request, call_next):
    try:
        return await rate_limit_middleware(request, call_next)
    except Exception as e:
        # Let exceptions pass through so CORS headers can be added
        raise

# CORS middleware (added last, so it runs first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")  # Auth proxy router
app.include_router(workspaces_router, prefix="/api/v1")
app.include_router(queries_router, prefix="/api/v1")
app.include_router(permissions_router, prefix="/api/v1")
app.include_router(external_router, prefix="/api/v1")
app.include_router(execute_router, prefix="/api/v1")
app.include_router(db_connections_router, prefix="/api/v1")  # Database connections
app.include_router(query_versions_router, prefix="/api/v1")  # Query versions


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Query Hub API Gateway",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development"
    )