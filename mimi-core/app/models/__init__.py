"""
Models package containing all DTOs and type definitions for the Mimi Core application.
"""
from .ingest import IngestInput
from .chunk import ChunkItem, VectorUpsertBatch
from .rag import RagQuery, RagResultItem
from .metadata import EventRecord, DocumentRecord
from .agent import AgentQuery, AgentResponse, CitationItem, ConversationTurn, ConversationMemory
from .confluence import (
    ConfluenceFullSyncRequest, ConfluenceFullSyncResponse, ConfluenceProgress,
    ConfluenceJobStatus, ConfluenceCancelRequest, ConfluenceReportRequest,
    ConfluencePage, ConfluenceChunkMetadata, ConfluenceSnapshot, JobStatus
)

__all__ = [
    "IngestInput",
    "ChunkItem", 
    "VectorUpsertBatch",
    "RagQuery",
    "RagResultItem", 
    "EventRecord",
    "DocumentRecord",
    "AgentQuery",
    "AgentResponse",
    "CitationItem",
    "ConversationTurn",
    "ConversationMemory",
    "ConfluenceFullSyncRequest",
    "ConfluenceFullSyncResponse", 
    "ConfluenceProgress",
    "ConfluenceJobStatus",
    "ConfluenceCancelRequest",
    "ConfluenceReportRequest",
    "ConfluencePage",
    "ConfluenceChunkMetadata",
    "ConfluenceSnapshot",
    "JobStatus"
]