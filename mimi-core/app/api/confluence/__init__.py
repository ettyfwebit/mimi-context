"""
Confluence API router for full sync operations.
"""
import asyncio
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, List
from app.models.confluence import (
    ConfluenceFullSyncRequest, ConfluenceFullSyncResponse, ConfluenceJobStatus,
    ConfluenceCancelRequest
)
from app.services.confluence import ConfluenceJobManager, ConfluenceSyncWorker
from app.infra.config import get_settings
from app.infra.logging import get_logger

router = APIRouter(prefix="/admin/confluence", tags=["confluence"])
logger = get_logger("api.confluence")

# Global instances
job_manager = ConfluenceJobManager()
sync_worker = ConfluenceSyncWorker()


def get_confluence_settings():
    """Dependency to validate Confluence configuration."""
    settings = get_settings()
    if not settings.confluence_base_url or not settings.confluence_auth_token:
        raise HTTPException(
            status_code=503,
            detail="Confluence integration not configured. Please set CONFLUENCE_BASE_URL and CONFLUENCE_AUTH_TOKEN."
        )
    return settings


@router.post("/fullsync")
async def start_full_sync(
    request: ConfluenceFullSyncRequest,
    _settings = Depends(get_confluence_settings)
) -> ConfluenceFullSyncResponse:
    """
    Start a Confluence full sync job.
    
    Args:
        request: Sync configuration parameters
        
    Returns:
        Job ID and initial status
    """
    try:
        # Validate request
        if not request.space_key and not request.root_page_id:
            raise HTTPException(
                status_code=400,
                detail="Either space_key or root_page_id must be provided"
            )
        
        # Apply defaults from settings if not provided
        settings = get_settings()
        if request.max_pages <= 0:
            request.max_pages = settings.conf_max_pages
        if request.max_depth <= 0:
            request.max_depth = settings.conf_max_depth
        
        # Create job
        job_id = job_manager.create_job(request)
        
        # Start async execution
        asyncio.create_task(sync_worker.execute_sync_job(job_manager, job_id))
        
        logger.info(
            f"Started Confluence sync job: {job_id}",
            extra={
                "space_key": request.space_key,
                "root_page_id": request.root_page_id,
                "dry_run": request.dry_run
            }
        )
        
        return ConfluenceFullSyncResponse(
            job_id=job_id,
            status=job_manager.get_job_status(job_id).status
        )
        
    except Exception as e:
        logger.error(f"Failed to start sync job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start sync: {str(e)}")


@router.get("/sync-status")
async def get_sync_status(
    job_id: str = Query(..., description="Job ID to check status for")
) -> ConfluenceJobStatus:
    """
    Get the current status of a sync job.
    
    Args:
        job_id: Sync job identifier
        
    Returns:
        Current job status and progress
    """
    try:
        status = job_manager.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")


@router.post("/cancel")
async def cancel_sync_job(
    request: ConfluenceCancelRequest
) -> Dict[str, Any]:
    """
    Cancel a running sync job.
    
    Args:
        request: Job cancellation request
        
    Returns:
        Cancellation result
    """
    try:
        success = job_manager.cancel_job(request.job_id)
        
        if success:
            logger.info(f"Cancelled sync job: {request.job_id}")
            return {"ok": True, "message": f"Job {request.job_id} cancelled"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Job {request.job_id} not found or already completed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job: {e}")
        raise HTTPException(status_code=500, detail=f"Error cancelling job: {str(e)}")


@router.get("/sync-report")
async def get_sync_report(
    job_id: str = Query(..., description="Job ID to get report for"),
    type: str = Query(..., description="Report type: failed, indexed, or skipped")
) -> Dict[str, Any]:
    """
    Get detailed report for a sync job.
    
    Args:
        job_id: Sync job identifier
        type: Report type (failed/indexed/skipped)
        
    Returns:
        List of pages with details
    """
    try:
        if type not in ["failed", "indexed", "skipped"]:
            raise HTTPException(
                status_code=400,
                detail="Report type must be one of: failed, indexed, skipped"
            )
        
        # Check if job exists
        status = job_manager.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        # Get report data
        report_data = job_manager.get_job_report(job_id, type)
        
        return {
            "job_id": job_id,
            "report_type": type,
            "total_items": len(report_data),
            "items": report_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job report: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving report: {str(e)}")


@router.get("/jobs")
async def list_recent_jobs(
    limit: int = Query(10, description="Maximum number of jobs to return")
) -> Dict[str, Any]:
    """
    List recent Confluence sync jobs.
    
    Args:
        limit: Maximum number of jobs to return
        
    Returns:
        List of recent jobs with status
    """
    try:
        # This would need to be implemented in job_manager if needed
        # For now, return empty list as jobs are cleaned up automatically
        return {
            "jobs": [],
            "message": "Job history is not persisted beyond completion. Use specific job IDs to track active jobs."
        }
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing jobs: {str(e)}")