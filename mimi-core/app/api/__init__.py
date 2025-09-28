"""
API package containing all FastAPI routers.
"""
from .health import router as health_router
from .ingest import router as ingest_router
from .rag import router as rag_router
from .admin import router as admin_router
from .agent import router as agent_router

__all__ = ["health_router", "ingest_router", "rag_router", "admin_router", "agent_router"]