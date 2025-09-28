"""
Vector adapter interface definition.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models import VectorUpsertBatch, RagResultItem


class VectorAdapter(ABC):
    """Abstract interface for vector storage operations."""
    
    @abstractmethod
    async def upsert_batch(self, batch: VectorUpsertBatch) -> bool:
        """
        Upsert a batch of chunks into the vector store.
        
        Args:
            batch: Batch of chunks to upsert
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def search(self, 
                    query_text: str, 
                    top_k: int = 5, 
                    filters: Optional[Dict[str, Any]] = None) -> List[RagResultItem]:
        """
        Search for similar chunks.
        
        Args:
            query_text: Query text to search for
            top_k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of matching results
        """
        pass
    
    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete all chunks for a document.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if vector store is healthy.
        
        Returns:
            Health status
        """
        pass