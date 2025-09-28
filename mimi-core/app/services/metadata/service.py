"""
Metadata service for CRUD operations on documents, events, and chunks.
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.metadata.database import MetadataDatabase
from app.models import DocumentRecord, EventRecord, ChunkItem
from app.infra.logging import get_logger


class MetadataService:
    """Service for managing document and event metadata."""
    
    def __init__(self):
        """Initialize metadata service."""
        self.db = MetadataDatabase()
        self.logger = get_logger("metadata.service")
    
    async def initialize(self):
        """Initialize the service."""
        await self.db.initialize()
    
    # Document operations
    async def create_document(self, document: DocumentRecord) -> bool:
        """Create or update a document record."""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO documents 
                    (doc_id, source, path, hash, lang, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    document.doc_id,
                    document.source,
                    document.path,
                    document.hash,
                    document.lang,
                    document.updated_at.isoformat()
                ))
                await conn.commit()
            
            self.logger.info(f"Document created/updated: {document.doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create document: {e}")
            return False
    
    async def get_document(self, doc_id: str) -> Optional[DocumentRecord]:
        """Get a document by ID."""
        try:
            async with self.db.get_connection() as conn:
                cursor = await conn.execute(
                    "SELECT * FROM documents WHERE doc_id = ?",
                    (doc_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return DocumentRecord(
                        doc_id=row["doc_id"],
                        source=row["source"],
                        path=row["path"],
                        hash=row["hash"],
                        lang=row["lang"],
                        updated_at=datetime.fromisoformat(row["updated_at"])
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    async def list_documents(self, 
                           source: Optional[str] = None, 
                           limit: int = 100) -> List[DocumentRecord]:
        """List documents with optional filtering."""
        try:
            async with self.db.get_connection() as conn:
                if source:
                    cursor = await conn.execute("""
                        SELECT * FROM documents 
                        WHERE source = ? 
                        ORDER BY updated_at DESC 
                        LIMIT ?
                    """, (source, limit))
                else:
                    cursor = await conn.execute("""
                        SELECT * FROM documents 
                        ORDER BY updated_at DESC 
                        LIMIT ?
                    """, (limit,))
                
                rows = await cursor.fetchall()
                
                documents = []
                for row in rows:
                    document = DocumentRecord(
                        doc_id=row["doc_id"],
                        source=row["source"],
                        path=row["path"],
                        hash=row["hash"],
                        lang=row["lang"],
                        updated_at=datetime.fromisoformat(row["updated_at"])
                    )
                    documents.append(document)
                
                return documents
                
        except Exception as e:
            self.logger.error(f"Failed to list documents: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its chunks."""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
                await conn.commit()
            
            self.logger.info(f"Document deleted: {doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    # Event operations
    async def create_event(self, event: EventRecord) -> Optional[int]:
        """Create an event record."""
        try:
            async with self.db.get_connection() as conn:
                cursor = await conn.execute("""
                    INSERT INTO events (type, ref, status, details, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    event.type,
                    event.ref,
                    event.status,
                    json.dumps(event.details) if event.details else None,
                    event.created_at.isoformat()
                ))
                await conn.commit()
                
                event_id = cursor.lastrowid
                self.logger.info(f"Event created: {event_id}")
                return event_id
                
        except Exception as e:
            self.logger.error(f"Failed to create event: {e}")
            return None
    
    async def list_events(self, limit: int = 50) -> List[EventRecord]:
        """List recent events."""
        try:
            async with self.db.get_connection() as conn:
                cursor = await conn.execute("""
                    SELECT * FROM events 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                
                events = []
                for row in rows:
                    details = None
                    if row["details"]:
                        try:
                            details = json.loads(row["details"])
                        except json.JSONDecodeError:
                            pass
                    
                    event = EventRecord(
                        id=row["id"],
                        type=row["type"],
                        ref=row["ref"],
                        status=row["status"],
                        details=details,
                        created_at=datetime.fromisoformat(row["created_at"])
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to list events: {e}")
            return []
    
    # Chunk operations
    async def save_chunks(self, chunks: List[ChunkItem]) -> bool:
        """Save chunk metadata."""
        try:
            async with self.db.get_connection() as conn:
                for chunk in chunks:
                    text_preview = chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
                    
                    await conn.execute("""
                        INSERT OR REPLACE INTO chunks 
                        (chunk_id, doc_id, ord_idx, text_preview)
                        VALUES (?, ?, ?, ?)
                    """, (
                        chunk.id,
                        chunk.doc_id,
                        chunk.ord,
                        text_preview
                    ))
                
                await conn.commit()
            
            self.logger.info(f"Saved {len(chunks)} chunk records")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save chunks: {e}")
            return False
    
    async def delete_chunks_by_document(self, doc_id: str) -> bool:
        """Delete all chunks for a document."""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
                await conn.commit()
            
            self.logger.info(f"Deleted chunks for document: {doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete chunks for {doc_id}: {e}")
            return False