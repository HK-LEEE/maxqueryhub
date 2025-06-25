from app.routers.health import router as health_router
from app.routers.workspaces import router as workspaces_router
from app.routers.queries import router as queries_router
from app.routers.permissions import router as permissions_router
from app.routers.external import router as external_router
from app.routers.execute import router as execute_router

__all__ = [
    "health_router",
    "workspaces_router",
    "queries_router", 
    "permissions_router",
    "external_router",
    "execute_router"
]