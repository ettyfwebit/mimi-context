#!/usr/bin/env python3
"""
Database initialization script for Mimi Core.
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.metadata import MetadataService
from app.infra.logging import setup_logger, get_logger
from app.infra.config import get_settings


async def init_database():
    """Initialize the database schema."""
    
    # Setup logging
    settings = get_settings()
    setup_logger(settings.app_env)
    logger = get_logger("scripts.init_db")
    
    logger.info("Initializing Mimi Core database...")
    
    try:
        # Initialize metadata service (this creates the database schema)
        metadata_service = MetadataService()
        await metadata_service.initialize()
        
        logger.info("Database initialized successfully")
        
        # Test database connection
        documents = await metadata_service.list_documents(limit=1)
        logger.info(f"Database test query successful, found {len(documents)} documents")
        
        print("✓ Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_database())