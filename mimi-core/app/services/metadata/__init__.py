"""
Metadata services for SQLite-based document and event management.
"""
from .database import MetadataDatabase
from .service import MetadataService

__all__ = ["MetadataDatabase", "MetadataService"]