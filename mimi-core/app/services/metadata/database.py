"""
SQLite database setup and management.
"""
import sqlite3
from typing import Optional
from contextlib import asynccontextmanager
import aiosqlite
from app.infra.config import get_settings
from app.infra.logging import get_logger


class MetadataDatabase:
    """SQLite database manager for metadata storage."""
    
    def __init__(self):
        """Initialize database manager."""
        self.settings = get_settings()
        self.logger = get_logger("metadata.database")
        
        # Extract database path from URL
        db_url = self.settings.database_url
        if db_url.startswith("sqlite:///"):
            self.db_path = db_url[10:]  # Remove "sqlite:///"
        else:
            self.db_path = "mimi_metadata.db"
    
    async def initialize(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_tables(db)
            await db.commit()
        
        self.logger.info(f"Database initialized: {self.db_path}")
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create database tables."""
        
        # Documents table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                path TEXT,
                hash TEXT,
                lang TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Events table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                ref TEXT,
                status TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chunks table (for tracking chunk metadata)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                ord_idx INTEGER NOT NULL,
                text_preview TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES documents (doc_id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events (type)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_events_created_at ON events (created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_source ON documents (source)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents (updated_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks (doc_id)")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection context manager."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row  # Enable column access by name
            yield db