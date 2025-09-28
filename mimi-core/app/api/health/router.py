"""
Health check API router.
"""
from fastapi import APIRouter
from typing import Dict

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "ok"}