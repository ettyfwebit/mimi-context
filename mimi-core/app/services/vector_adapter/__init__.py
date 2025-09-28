"""
Vector adapter services for embedding and search operations.
"""
from .interface import VectorAdapter
from .qdrant_adapter import QdrantVectorAdapter
from .openai_adapter import OpenAIVectorAdapter
from .factory import create_vector_adapter

__all__ = ["VectorAdapter", "QdrantVectorAdapter", "OpenAIVectorAdapter", "create_vector_adapter"]