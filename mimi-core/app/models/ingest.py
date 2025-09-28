"""
Ingest-related models and DTOs.
"""
from typing import Optional
from pydantic import BaseModel


class IngestInput(BaseModel):
    """Input model for document ingestion."""
    doc_id: str
    source: str
    path: Optional[str] = None
    text: str
    lang: Optional[str] = None