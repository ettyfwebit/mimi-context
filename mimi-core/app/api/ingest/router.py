"""
Ingest API router for document upload and processing.
"""
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, Dict, Any
from app.models import IngestInput, DocumentRecord, EventRecord, VectorUpsertBatch
from app.services.pipeline_core import DocumentProcessor
from app.services.vector_adapter import create_vector_adapter
from app.services.metadata import MetadataService
from app.infra.config import get_settings
from app.infra.logging import get_logger

router = APIRouter(prefix="/ingest", tags=["ingest"])
logger = get_logger("api.ingest")


async def get_processor():
    """Dependency to get document processor."""
    return DocumentProcessor()


async def get_vector_adapter():
    """Dependency to get vector adapter."""
    return create_vector_adapter()


async def get_metadata_service():
    """Dependency to get metadata service."""
    service = MetadataService()
    await service.initialize()
    return service


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    path: Optional[str] = Form(None),
    lang: Optional[str] = Form(None),
    processor: DocumentProcessor = Depends(get_processor),
    vector_adapter = Depends(get_vector_adapter),
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> Dict[str, Any]:
    """
    Upload a document for ingestion.
    
    Args:
        file: Document file to upload
        path: Optional file path for metadata
        lang: Optional language code
        processor: Document processor dependency
        vector_adapter: Vector adapter dependency
        metadata_service: Metadata service dependency
        
    Returns:
        Ingestion result
    """
    settings = get_settings()
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    allowed_extensions = settings.upload_allowed_extensions.split(",")
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed: {allowed_extensions}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > settings.upload_max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.upload_max_size_mb}MB"
        )
    
    # Create document ID
    doc_id = f"upload:{file.filename}"
    
    # Log start of ingestion
    start_time = datetime.utcnow()
    event = EventRecord(
        type="ingest",
        ref=doc_id,
        status="started",
        created_at=start_time
    )
    event_id = await metadata_service.create_event(event)
    
    try:
        # Decode file content
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")
        
        # Check for existing document and compute hash
        content_hash = processor.compute_document_hash(text_content)
        existing_doc = await metadata_service.get_document(doc_id)
        
        # Check for duplicate
        if existing_doc and processor.is_duplicate_document(content_hash, existing_doc.hash):
            logger.info(f"Skipping duplicate document: {doc_id}")
            
            # Log duplicate event
            await metadata_service.create_event(EventRecord(
                type="ingest",
                ref=doc_id,
                status="duplicate",
                details={"reason": "Content hash unchanged"},
                created_at=datetime.utcnow()
            ))
            
            return {
                "ok": True,
                "doc_id": doc_id,
                "chunks": 0,
                "message": "Document unchanged, skipped"
            }
        
        # Create ingest input
        ingest_input = IngestInput(
            doc_id=doc_id,
            source="upload",
            path=path or file.filename,
            text=text_content,
            lang=lang
        )
        
        # Process document
        chunks = processor.process_document(ingest_input)
        
        # Create vector batch
        batch = VectorUpsertBatch(
            doc_id=doc_id,
            items=chunks
        )
        
        # Upsert to vector store
        upsert_success = await vector_adapter.upsert_batch(batch)
        if not upsert_success:
            raise Exception("Failed to upsert chunks to vector store")
        
        # Save document metadata
        document_record = DocumentRecord(
            doc_id=doc_id,
            source="upload",
            path=path or file.filename,
            hash=content_hash,
            lang=lang or chunks[0].metadata.get("lang") if chunks else None,
            updated_at=datetime.utcnow()
        )
        
        await metadata_service.create_document(document_record)
        
        # Save chunk metadata
        await metadata_service.save_chunks(chunks)
        
        # Log success event
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        await metadata_service.create_event(EventRecord(
            type="ingest",
            ref=doc_id,
            status="success",
            details={
                "chunks_created": len(chunks),
                "duration_seconds": duration
            },
            created_at=end_time
        ))
        
        logger.info(
            "Document ingested successfully",
            extra={
                "doc_id": doc_id,
                "chunks": len(chunks),
                "duration": duration
            }
        )
        
        return {
            "ok": True,
            "doc_id": doc_id,
            "chunks": len(chunks)
        }
        
    except Exception as e:
        # Log error event
        await metadata_service.create_event(EventRecord(
            type="ingest",
            ref=doc_id,
            status="error",
            details={"error": str(e)},
            created_at=datetime.utcnow()
        ))
        
        logger.error(f"Failed to ingest document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document")