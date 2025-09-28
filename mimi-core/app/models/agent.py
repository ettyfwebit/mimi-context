"""
Agent-related models and DTOs.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AgentQuery(BaseModel):
    """Query model for agent operations."""
    question: str
    top_k: int = 3
    session_id: Optional[str] = None  # For conversation memory


class CitationItem(BaseModel):
    """Citation metadata."""
    doc_id: str
    path: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent response with natural language answer and citations."""
    answer: str
    citations: List[CitationItem]
    raw_chunks: List[Dict[str, Any]]


class ConversationTurn(BaseModel):
    """A single conversation turn."""
    question: str
    answer: str
    timestamp: str


class ConversationMemory(BaseModel):
    """Conversation memory for a session."""
    session_id: str
    turns: List[ConversationTurn]