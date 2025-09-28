"""
Confluence sync job management and state tracking.
"""
import asyncio
import uuid
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from collections import defaultdict
from app.models.confluence import (
    ConfluenceFullSyncRequest, ConfluenceJobStatus, ConfluenceProgress,
    ConfluenceSnapshot, JobStatus
)
from app.infra.logging import get_logger


class ConfluenceJobManager:
    """Manager for Confluence sync jobs with in-memory state tracking."""
    
    def __init__(self):
        """Initialize job manager."""
        self.logger = get_logger("services.confluence.job_manager")
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.job_logs: Dict[str, List[str]] = defaultdict(list)
        self.max_logs_per_job = 200
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _start_cleanup_task(self):
        """Start background task to cleanup old jobs."""
        if not self._cleanup_task or self._cleanup_task.done():
            try:
                self._cleanup_task = asyncio.create_task(self._cleanup_old_jobs())
            except RuntimeError:
                # No event loop running - will start task later when needed
                self.logger.info("No event loop available - cleanup task will start when needed")
    
    async def _cleanup_old_jobs(self):
        """Cleanup jobs older than 24 hours."""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)
                jobs_to_remove = []
                
                for job_id, job_data in self.jobs.items():
                    created_at = job_data.get('created_at', datetime.now())
                    if created_at < cutoff_time and job_data.get('status') in [
                        JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED
                    ]:
                        jobs_to_remove.append(job_id)
                
                for job_id in jobs_to_remove:
                    self._remove_job(job_id)
                    self.logger.info(f"Cleaned up old job: {job_id}")
                
                # Sleep for 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def create_job(self, request: ConfluenceFullSyncRequest) -> str:
        """
        Create a new sync job.
        
        Args:
            request: Sync request parameters
            
        Returns:
            Generated job ID
        """
        # Start cleanup task if not already running
        self._start_cleanup_task()
        
        job_id = f"conf-sync-{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}-{uuid.uuid4().hex[:8]}"
        
        job_data = {
            'job_id': job_id,
            'status': JobStatus.QUEUED,
            'request': request,
            'progress': ConfluenceProgress(),
            'current': None,
            'error_message': None,
            'created_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'cancelled': False,
            'reports': {
                'failed': [],
                'indexed': [],
                'skipped': []
            }
        }
        
        self.jobs[job_id] = job_data
        self.job_logs[job_id] = []
        
        self.add_log(job_id, f"Job created: {job_id}")
        self.logger.info(f"Created sync job: {job_id}")
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[ConfluenceJobStatus]:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status or None if not found
        """
        job_data = self.jobs.get(job_id)
        if not job_data:
            return None
        
        return ConfluenceJobStatus(
            job_id=job_id,
            status=job_data['status'],
            progress=job_data['progress'],
            current=job_data.get('current'),
            logs_tail=self.job_logs[job_id][-20:],  # Last 20 log entries
            error_message=job_data.get('error_message'),
            started_at=job_data.get('started_at'),
            completed_at=job_data.get('completed_at')
        )
    
    def update_job_status(self, job_id: str, status: JobStatus, error_message: str = None):
        """Update job status."""
        if job_id not in self.jobs:
            return
        
        job_data = self.jobs[job_id]
        old_status = job_data['status']
        job_data['status'] = status
        
        if error_message:
            job_data['error_message'] = error_message
        
        # Update timestamps
        if status == JobStatus.DISCOVERING and old_status == JobStatus.QUEUED:
            job_data['started_at'] = datetime.now()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            job_data['completed_at'] = datetime.now()
        
        self.add_log(job_id, f"Status changed: {old_status} → {status}")
        if error_message:
            self.add_log(job_id, f"Error: {error_message}")
    
    def update_progress(self, job_id: str, **kwargs):
        """Update job progress counters."""
        if job_id not in self.jobs:
            return
        
        progress = self.jobs[job_id]['progress']
        
        # Update progress fields
        for key, value in kwargs.items():
            if hasattr(progress, key):
                setattr(progress, key, value)
    
    def increment_progress(self, job_id: str, **kwargs):
        """Increment job progress counters."""
        if job_id not in self.jobs:
            return
        
        progress = self.jobs[job_id]['progress']
        
        # Increment progress fields
        for key, increment in kwargs.items():
            if hasattr(progress, key):
                current_value = getattr(progress, key)
                setattr(progress, key, current_value + increment)
    
    def set_current_activity(self, job_id: str, activity: Dict[str, Any]):
        """Set current activity for a job."""
        if job_id not in self.jobs:
            return
        
        self.jobs[job_id]['current'] = activity
    
    def add_log(self, job_id: str, message: str):
        """Add a log entry for a job."""
        if job_id not in self.job_logs:
            self.job_logs[job_id] = []
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.job_logs[job_id].append(log_entry)
        
        # Keep only recent logs
        if len(self.job_logs[job_id]) > self.max_logs_per_job:
            self.job_logs[job_id] = self.job_logs[job_id][-self.max_logs_per_job:]
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was cancelled, False if not found or already finished
        """
        job_data = self.jobs.get(job_id)
        if not job_data:
            return False
        
        current_status = job_data['status']
        if current_status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False
        
        job_data['cancelled'] = True
        self.update_job_status(job_id, JobStatus.CANCELLED)
        
        self.logger.info(f"Cancelled job: {job_id}")
        return True
    
    def is_job_cancelled(self, job_id: str) -> bool:
        """Check if job is cancelled."""
        job_data = self.jobs.get(job_id)
        if not job_data:
            return True  # Treat missing jobs as cancelled
        
        return job_data.get('cancelled', False)
    
    def add_report_entry(self, job_id: str, report_type: str, entry: Dict[str, Any]):
        """Add an entry to job reports."""
        job_data = self.jobs.get(job_id)
        if not job_data:
            return
        
        if report_type in job_data['reports']:
            job_data['reports'][report_type].append(entry)
    
    def get_job_report(self, job_id: str, report_type: str) -> List[Dict[str, Any]]:
        """Get job report by type."""
        job_data = self.jobs.get(job_id)
        if not job_data:
            return []
        
        return job_data['reports'].get(report_type, [])
    
    def get_job_request(self, job_id: str) -> Optional[ConfluenceFullSyncRequest]:
        """Get original job request."""
        job_data = self.jobs.get(job_id)
        if not job_data:
            return None
        
        return job_data['request']
    
    def _remove_job(self, job_id: str):
        """Remove job from memory."""
        if job_id in self.jobs:
            del self.jobs[job_id]
        if job_id in self.job_logs:
            del self.job_logs[job_id]
    
    def create_snapshot(self, job_id: str, scope: str, checksum: str, affected_docs: List[Dict[str, Any]]) -> ConfluenceSnapshot:
        """Create a snapshot record for completed job."""
        job_data = self.jobs.get(job_id)
        if not job_data:
            raise ValueError(f"Job not found: {job_id}")
        
        snapshot_id = f"conf:{scope}:{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        snapshot = ConfluenceSnapshot(
            snapshot_id=snapshot_id,
            job_id=job_id,
            scope=scope,
            totals=job_data['progress'],
            checksum=checksum,
            affected_docs=affected_docs,
            created_at=datetime.now()
        )
        
        return snapshot