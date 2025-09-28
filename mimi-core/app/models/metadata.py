"""
Metadata-related models and DTOs.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class EventRecord(BaseModel):
    """Event record model for tracking operations."""
    id: Optional[int] = None
    type: str
    ref: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime


class DocumentRecord(BaseModel):
    """Document record model for metadata storage."""
    doc_id: str
    source: str
    path: Optional[str] = None
    hash: Optional[str] = None
    lang: Optional[str] = None
    updated_at: datetime