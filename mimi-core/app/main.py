"""
Main FastAPI application for Mimi Core.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health_router, ingest_router, rag_router, admin_router, agent_router
from app.infra.config import get_settings
from app.infra.logging import setup_logger, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    
    # Setup logging
    setup_logger(settings.app_env)
    logger = get_logger("app.main")
    
    logger.info("Starting Mimi Core application")
    
    # Initialize services would go here
    # For now, services are initialized on-demand via dependencies
    
    yield
    
    logger.info("Shutting down Mimi Core application")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Mimi Core – My Information, My Intelligence",
        version="0.1.0",
        description="Single-service MNVP: upload documents → normalize → chunk → embed → index → RAG query with citations.",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(ingest_router)
    app.include_router(rag_router)
    app.include_router(admin_router)
    app.include_router(agent_router)
    
    return app


# Create the app instance
app = create_app()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mimi Core - My Information, My Intelligence",
        "version": "0.1.0",
        "docs": "/docs"
    }