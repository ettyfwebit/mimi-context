"""
RAG-related models and DTOs.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class RagQuery(BaseModel):
    """Query model for RAG operations."""
    question: str
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None


class RagResultItem(BaseModel):
    """Individual result item from RAG query."""
    chunk_id: str
    doc_id: str
    source: str
    path: Optional[str] = None
    score: float
    snippet: str
    full_text: Optional[str] = None


class RagResponse(BaseModel):
    """RAG query response matching OpenAPI specification."""
    answers: List[Dict[str, Any]]