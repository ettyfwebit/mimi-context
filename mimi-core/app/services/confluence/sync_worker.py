"""
Confluence sync worker implementing the full sync pipeline.
"""
import asyncio
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from app.models.confluence import (
    ConfluenceFullSyncRequest, ConfluencePage, ConfluenceChunkMetadata, 
    JobStatus, ConfluenceSnapshot
)
from app.models import ChunkItem, VectorUpsertBatch, DocumentRecord, EventRecord
from app.services.confluence.client import ConfluenceClient
from app.services.confluence.normalizer import ConfluenceNormalizer
from app.services.confluence.job_manager import ConfluenceJobManager
from app.services.metadata import MetadataService
from app.services.pipeline_core import DocumentProcessor
from app.services.vector_adapter import create_vector_adapter
from app.infra.config import get_settings
from app.infra.logging import get_logger


class ConfluenceSyncWorker:
    """Worker for executing Confluence sync jobs."""
    
    def __init__(self):
        """Initialize sync worker."""
        self.logger = get_logger("services.confluence.sync_worker")
        self.settings = get_settings()
        self.normalizer = ConfluenceNormalizer()
        self.processor = DocumentProcessor()
        self._running_jobs: Dict[str, asyncio.Task] = {}
    
    async def execute_sync_job(self, job_manager: ConfluenceJobManager, job_id: str):
        """
        Execute a full sync job asynchronously.
        
        Args:
            job_manager: Job management instance
            job_id: Job identifier
        """
        # Create and track the task
        if job_id in self._running_jobs:
            self.logger.warning(f"Job {job_id} is already running")
            return
        
        task = asyncio.create_task(self._run_sync_pipeline(job_manager, job_id))
        self._running_jobs[job_id] = task
        
        try:
            await task
        finally:
            # Clean up task reference
            if job_id in self._running_jobs:
                del self._running_jobs[job_id]
    
    async def _run_sync_pipeline(self, job_manager: ConfluenceJobManager, job_id: str):
        """Run the complete sync pipeline for a job."""
        try:
            request = job_manager.get_job_request(job_id)
            if not request:
                job_manager.update_job_status(job_id, JobStatus.FAILED, "Job request not found")
                return
            
            self.logger.info(f"Starting sync job {job_id}")
            job_manager.add_log(job_id, "Starting Confluence sync pipeline")
            
            # Initialize services
            metadata_service = MetadataService()
            await metadata_service.initialize()
            
            vector_adapter = await create_vector_adapter()
            
            # Stage 1: Discovery
            pages = await self._discover_pages(job_manager, job_id, request)
            if job_manager.is_job_cancelled(job_id):
                return
            
            # Stage 2: Fetching and Processing
            processed_docs = await self._fetch_and_process_pages(
                job_manager, job_id, request, pages, metadata_service
            )
            if job_manager.is_job_cancelled(job_id):
                return
            
            # Stage 3: Embedding and Upserting
            await self._embed_and_upsert(
                job_manager, job_id, request, processed_docs, vector_adapter, metadata_service
            )
            if job_manager.is_job_cancelled(job_id):
                return
            
            # Stage 4: Create Snapshot
            await self._create_snapshot(job_manager, job_id, request, processed_docs)
            
            job_manager.update_job_status(job_id, JobStatus.COMPLETED)
            job_manager.add_log(job_id, "Sync completed successfully")
            
            self.logger.info(f"Completed sync job {job_id}")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Sync job {job_id} failed: {error_msg}")
            job_manager.update_job_status(job_id, JobStatus.FAILED, error_msg)
            job_manager.add_log(job_id, f"Sync failed: {error_msg}")
    
    async def _discover_pages(
        self, 
        job_manager: ConfluenceJobManager, 
        job_id: str, 
        request: ConfluenceFullSyncRequest
    ) -> List[ConfluencePage]:
        """Discover pages based on request parameters."""
        job_manager.update_job_status(job_id, JobStatus.DISCOVERING)
        job_manager.add_log(job_id, "Starting page discovery")
        
        async with ConfluenceClient() as client:
            pages = await client.discover_pages(
                space_key=request.space_key,
                root_page_id=request.root_page_id,
                include_labels=request.include_labels,
                exclude_labels=request.exclude_labels,
                path_prefix=request.path_prefix,
                max_pages=request.max_pages,
                max_depth=request.max_depth
            )
        
        job_manager.update_progress(job_id, discovered_pages=len(pages))
        job_manager.add_log(job_id, f"Discovered {len(pages)} pages")
        
        return pages
    
    async def _fetch_and_process_pages(
        self,
        job_manager: ConfluenceJobManager,
        job_id: str,
        request: ConfluenceFullSyncRequest,
        pages: List[ConfluencePage],
        metadata_service: MetadataService
    ) -> List[Tuple[ConfluencePage, List[ChunkItem], str]]:
        """Fetch content and process pages."""
        job_manager.update_job_status(job_id, JobStatus.FETCHING)
        job_manager.add_log(job_id, f"Fetching and processing {len(pages)} pages")
        
        processed_docs = []
        semaphore = asyncio.Semaphore(self.settings.conf_concurrency)
        
        async def process_single_page(page: ConfluencePage):
            async with semaphore:
                if job_manager.is_job_cancelled(job_id):
                    return None
                
                try:
                    return await self._process_single_page(
                        job_manager, job_id, request, page, metadata_service
                    )
                except Exception as e:
                    self.logger.error(f"Error processing page {page.page_id}: {e}")
                    job_manager.add_report_entry(job_id, 'failed', {
                        'page_id': page.page_id,
                        'title': page.title,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    job_manager.increment_progress(job_id, failed_pages=1)
                    return None
        
        # Process pages concurrently
        tasks = [process_single_page(page) for page in pages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        for result in results:
            if result and not isinstance(result, Exception):
                processed_docs.append(result)
        
        job_manager.add_log(job_id, f"Processed {len(processed_docs)} pages successfully")
        return processed_docs
    
    async def _process_single_page(
        self,
        job_manager: ConfluenceJobManager,
        job_id: str,
        request: ConfluenceFullSyncRequest,
        page: ConfluencePage,
        metadata_service: MetadataService
    ) -> Optional[Tuple[ConfluencePage, List[ChunkItem], str]]:
        """Process a single page: fetch content, normalize, and chunk."""
        
        # Update current activity
        job_manager.set_current_activity(job_id, {
            'page_id': page.page_id,
            'title': page.title
        })
        
        # Fetch full content
        async with ConfluenceClient() as client:
            full_page = await client.fetch_page_content(page.page_id)
        
        if not full_page or not full_page.content:
            self.logger.warning(f"No content for page {page.page_id}")
            job_manager.increment_progress(job_id, failed_pages=1)
            return None
        
        # Normalize content
        job_manager.update_job_status(job_id, JobStatus.NORMALIZING)
        normalized_text, detected_lang = self.normalizer.normalize_content(full_page.content)
        
        if not normalized_text.strip():
            self.logger.warning(f"Empty content after normalization for page {page.page_id}")
            job_manager.increment_progress(job_id, skipped_unchanged=1)
            return None
        
        # Compute content hash for deduplication
        content_hash = hashlib.sha256(normalized_text.encode()).hexdigest()
        
        # Check for existing document (incremental sync)
        doc_id = f"conf:{page.page_id}@{page.version}"
        existing_doc = await metadata_service.get_document(doc_id)
        
        if existing_doc and existing_doc.hash == content_hash:
            self.logger.info(f"Skipping unchanged page {page.page_id}")
            job_manager.increment_progress(job_id, skipped_unchanged=1)
            job_manager.add_report_entry(job_id, 'skipped', {
                'page_id': page.page_id,
                'title': page.title,
                'reason': 'unchanged_content',
                'timestamp': datetime.now().isoformat()
            })
            return None
        
        if request.dry_run:
            self.logger.info(f"Dry run: would process page {page.page_id}")
            job_manager.increment_progress(job_id, fetched_pages=1)
            return None
        
        # Create chunks with section awareness
        job_manager.update_job_status(job_id, JobStatus.CHUNKING)
        chunks = await self._create_confluence_chunks(
            full_page, normalized_text, content_hash, detected_lang
        )
        
        job_manager.increment_progress(job_id, fetched_pages=1, indexed_chunks=len(chunks))
        job_manager.add_log(job_id, f"Processed page {page.page_id}: {len(chunks)} chunks")
        
        return (full_page, chunks, content_hash)
    
    async def _create_confluence_chunks(
        self,
        page: ConfluencePage,
        normalized_text: str,
        content_hash: str,
        detected_lang: Optional[str]
    ) -> List[ChunkItem]:
        """Create chunks with Confluence-specific metadata."""
        
        # Extract sections for better chunking
        sections = self.normalizer.extract_sections(normalized_text)
        
        chunks = []
        chunk_ord = 0
        
        for section_title, section_text in sections:
            # Use configured chunk size
            target_size = self.settings.chunk_target_size
            overlap = self.settings.chunk_overlap
            
            # Simple text chunking within sections
            section_chunks = self._chunk_text_by_size(section_text, target_size, overlap)
            
            for chunk_text in section_chunks:
                if not chunk_text.strip():
                    continue
                
                # Generate chunk ID
                chunk_id = f"conf:{page.page_id}@{page.version}::c{chunk_ord}"
                
                # Create path - use URL if available, otherwise space/title format
                path = page.url or f"{page.space_key}/{page.title}"
                
                # Create enhanced metadata
                chunk_metadata = ConfluenceChunkMetadata(
                    doc_id=f"conf:{page.page_id}@{page.version}",
                    source="confluence",
                    path=path,
                    space_key=page.space_key,
                    page_id=page.page_id,
                    page_title=page.title,
                    version=page.version,
                    updated_by=page.updated_by,
                    updated_at=page.updated_at,
                    labels=page.labels,
                    ancestors=page.ancestors,
                    lang=detected_lang,
                    hash=content_hash,
                    section_title=section_title if section_title else None,
                    ord=chunk_ord
                )
                
                chunk_item = ChunkItem(
                    id=chunk_id,
                    doc_id=f"conf:{page.page_id}@{page.version}",
                    ord=chunk_ord,
                    text=chunk_text,
                    metadata=chunk_metadata.dict()
                )
                
                chunks.append(chunk_item)
                chunk_ord += 1
        
        return chunks
    
    def _chunk_text_by_size(self, text: str, target_size: int, overlap: int) -> List[str]:
        """Chunk text by target size with overlap."""
        if len(text) <= target_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + target_size
            
            if end >= len(text):
                # Last chunk
                chunks.append(text[start:])
                break
            
            # Try to break at word boundary
            chunk_text = text[start:end]
            last_space = chunk_text.rfind(' ')
            if last_space > target_size * 0.8:  # Only break if reasonably close to target
                end = start + last_space
            
            chunks.append(text[start:end])
            start = max(start + target_size - overlap, end - overlap)
        
        return chunks
    
    async def _embed_and_upsert(
        self,
        job_manager: ConfluenceJobManager,
        job_id: str,
        request: ConfluenceFullSyncRequest,
        processed_docs: List[Tuple[ConfluencePage, List[ChunkItem], str]],
        vector_adapter,
        metadata_service: MetadataService
    ):
        """Embed chunks and upsert to vector database."""
        if request.dry_run:
            job_manager.add_log(job_id, "Dry run: skipping embedding and upsert")
            return
        
        job_manager.update_job_status(job_id, JobStatus.EMBEDDING)
        job_manager.add_log(job_id, "Starting embedding and upsert")
        
        for page, chunks, content_hash in processed_docs:
            if job_manager.is_job_cancelled(job_id):
                return
            
            if not chunks:
                continue
            
            try:
                # Create document record
                doc_record = DocumentRecord(
                    doc_id=f"conf:{page.page_id}@{page.version}",
                    source="confluence",
                    path=page.url or f"{page.space_key}/{page.title}",
                    hash=content_hash,
                    lang=chunks[0].metadata.get('lang'),
                    updated_at=page.updated_at
                )
                
                # Save document metadata
                await metadata_service.create_document(doc_record)
                
                # Create upsert batch
                batch = VectorUpsertBatch(
                    doc_id=f"conf:{page.page_id}@{page.version}",
                    items=chunks
                )
                
                # Upsert to vector database
                job_manager.update_job_status(job_id, JobStatus.UPSERTING)
                await vector_adapter.upsert_batch(batch)
                
                # Log successful processing
                await metadata_service.create_event(EventRecord(
                    type="confluence_sync",
                    ref=f"conf:{page.page_id}@{page.version}",
                    status="success",
                    details={
                        "page_title": page.title,
                        "chunks": len(chunks),
                        "job_id": job_id
                    },
                    created_at=datetime.now()
                ))
                
                # Add to indexed report
                job_manager.add_report_entry(job_id, 'indexed', {
                    'page_id': page.page_id,
                    'title': page.title,
                    'doc_id': f"conf:{page.page_id}@{page.version}",
                    'chunks': len(chunks),
                    'timestamp': datetime.now().isoformat()
                })
                
                job_manager.add_log(job_id, f"Indexed page {page.page_id}: {len(chunks)} chunks")
                
            except Exception as e:
                error_msg = f"Error upserting page {page.page_id}: {e}"
                self.logger.error(error_msg)
                job_manager.add_log(job_id, error_msg)
                
                # Log failed event
                await metadata_service.create_event(EventRecord(
                    type="confluence_sync",
                    ref=f"conf:{page.page_id}@{page.version}",
                    status="error",
                    details={"error": str(e), "job_id": job_id},
                    created_at=datetime.now()
                ))
                
                job_manager.add_report_entry(job_id, 'failed', {
                    'page_id': page.page_id,
                    'title': page.title,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                job_manager.increment_progress(job_id, failed_pages=1)
    
    async def _create_snapshot(
        self,
        job_manager: ConfluenceJobManager,
        job_id: str,
        request: ConfluenceFullSyncRequest,
        processed_docs: List[Tuple[ConfluencePage, List[ChunkItem], str]]
    ):
        """Create completion snapshot."""
        job_manager.update_job_status(job_id, JobStatus.SNAPSHOT)
        job_manager.add_log(job_id, "Creating completion snapshot")
        
        # Determine scope description
        scope = request.space_key or request.root_page_id or "unknown"
        
        # Calculate checksum from all processed doc hashes
        all_hashes = [content_hash for _, _, content_hash in processed_docs]
        combined_hash = hashlib.sha256('|'.join(sorted(all_hashes)).encode()).hexdigest()
        
        # Prepare affected docs summary
        affected_docs = []
        for page, chunks, content_hash in processed_docs:
            affected_docs.append({
                'doc_id': f"conf:{page.page_id}@{page.version}",
                'page_title': page.title,
                'chunks': len(chunks)
            })
        
        # Create snapshot
        snapshot = job_manager.create_snapshot(job_id, scope, combined_hash, affected_docs)
        
        job_manager.add_log(job_id, f"Created snapshot: {snapshot.snapshot_id}")
        self.logger.info(f"Created snapshot {snapshot.snapshot_id} for job {job_id}")