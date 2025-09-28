"""
Chunk-related models and DTOs.
"""
from typing import Dict, List, Any
from pydantic import BaseModel


class ChunkItem(BaseModel):
    """Individual chunk item with metadata."""
    id: str
    doc_id: str
    ord: int
    text: str
    metadata: Dict[str, Any]


class VectorUpsertBatch(BaseModel):
    """Batch of chunks for vector upsert operations."""
    doc_id: str
    items: List[ChunkItem]