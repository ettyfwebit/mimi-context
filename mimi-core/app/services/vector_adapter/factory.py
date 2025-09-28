"""
Factory for creating vector adapter instances.
"""
from app.services.vector_adapter.interface import VectorAdapter
from app.services.vector_adapter.qdrant_adapter import QdrantVectorAdapter
from app.services.vector_adapter.openai_adapter import OpenAIVectorAdapter
from app.infra.config import get_settings


def create_vector_adapter() -> VectorAdapter:
    """Create vector adapter based on configuration."""
    settings = get_settings()
    
    if settings.vector_backend == "qdrant":
        return QdrantVectorAdapter()
    elif settings.vector_backend == "openai":
        return OpenAIVectorAdapter()
    else:
        raise ValueError(f"Unsupported vector backend: {settings.vector_backend}")