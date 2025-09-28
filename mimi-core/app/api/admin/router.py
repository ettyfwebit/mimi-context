"""
Admin API router for system management and monitoring.
"""
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List, Optional
from app.services.metadata import MetadataService
from app.infra.logging import get_logger

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger("api.admin")


async def get_metadata_service():
    """Dependency to get metadata service."""
    service = MetadataService()
    await service.initialize()
    return service


@router.get("/updates")
async def list_updates(
    limit: int = Query(50, description="Maximum number of events to return"),
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> Dict[str, Any]:
    """
    List recent ingestion events.
    
    Args:
        limit: Maximum number of events to return
        metadata_service: Metadata service dependency
        
    Returns:
        List of recent events
    """
    try:
        events = await metadata_service.list_events(limit=limit)
        
        # Convert to response format
        event_list = []
        for event in events:
            event_dict = {
                "id": event.id,
                "type": event.type,
                "ref": event.ref,
                "status": event.status,
                "created_at": event.created_at.isoformat() + "Z"
            }
            event_list.append(event_dict)
        
        logger.info(f"Listed {len(event_list)} events")
        
        return {"events": event_list}
        
    except Exception as e:
        logger.error(f"Failed to list events: {e}")
        return {"events": []}


@router.get("/docs")
async def list_documents(
    source: Optional[str] = Query(None, description="Filter by document source"),
    limit: int = Query(100, description="Maximum number of documents to return"),
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> Dict[str, Any]:
    """
    List recent documents.
    
    Args:
        source: Optional source filter
        limit: Maximum number of documents to return
        metadata_service: Metadata service dependency
        
    Returns:
        List of recent documents
    """
    try:
        documents = await metadata_service.list_documents(source=source, limit=limit)
        
        # Convert to response format
        doc_list = []
        for doc in documents:
            doc_dict = {
                "doc_id": doc.doc_id,
                "source": doc.source,
                "path": doc.path,
                "hash": doc.hash,
                "lang": doc.lang,
                "updated_at": doc.updated_at.isoformat() + "Z"
            }
            doc_list.append(doc_dict)
        
        logger.info(f"Listed {len(doc_list)} documents")
        
        return {"documents": doc_list}
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        return {"documents": []}