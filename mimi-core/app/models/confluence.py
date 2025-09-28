"""
Confluence-related models and DTOs.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class JobStatus(str, Enum):
    """Confluence sync job status."""
    QUEUED = "queued"
    DISCOVERING = "discovering"
    FETCHING = "fetching"
    NORMALIZING = "normalizing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    UPSERTING = "upserting"
    SNAPSHOT = "snapshot"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConfluenceFullSyncRequest(BaseModel):
    """Request model for Confluence full sync."""
    space_key: Optional[str] = None
    root_page_id: Optional[str] = None
    path_prefix: Optional[str] = None
    include_labels: List[str] = []
    exclude_labels: List[str] = []
    max_pages: int = 2000
    max_depth: int = 5
    dry_run: bool = False


class ConfluenceFullSyncResponse(BaseModel):
    """Response model for starting Confluence full sync."""
    job_id: str
    status: JobStatus


class ConfluenceProgress(BaseModel):
    """Progress tracking for Confluence sync job."""
    discovered_pages: int = 0
    fetched_pages: int = 0
    indexed_chunks: int = 0
    skipped_unchanged: int = 0
    failed_pages: int = 0


class ConfluenceJobStatus(BaseModel):
    """Status response for Confluence sync job."""
    job_id: str
    status: JobStatus
    progress: ConfluenceProgress
    current: Optional[Dict[str, Any]] = None
    logs_tail: List[str] = []
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ConfluenceCancelRequest(BaseModel):
    """Request model for cancelling Confluence sync job."""
    job_id: str


class ConfluenceReportRequest(BaseModel):
    """Request model for Confluence sync reports."""
    job_id: str
    type: str  # "failed", "indexed", "skipped"


class ConfluencePage(BaseModel):
    """Confluence page metadata."""
    page_id: str
    title: str
    version: int
    updated_at: datetime
    updated_by: str
    space_key: str
    labels: List[str] = []
    ancestors: List[str] = []
    content: Optional[str] = None
    url: Optional[str] = None


class ConfluenceChunkMetadata(BaseModel):
    """Enhanced chunk metadata for Confluence documents."""
    doc_id: str
    source: str = "confluence"
    path: str
    space_key: str
    page_id: str
    page_title: str
    version: int
    updated_by: str
    updated_at: datetime
    labels: List[str] = []
    ancestors: List[str] = []
    lang: Optional[str] = None
    hash: str
    section_title: Optional[str] = None
    ord: int


class ConfluenceSnapshot(BaseModel):
    """Snapshot record for Confluence sync job."""
    snapshot_id: str
    job_id: str
    scope: str  # space key or root page description
    totals: ConfluenceProgress
    checksum: str
    affected_docs: List[Dict[str, Any]] = []
    created_at: datetime