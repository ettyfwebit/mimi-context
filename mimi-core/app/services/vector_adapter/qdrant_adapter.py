"""
Qdrant vector adapter implementation.
"""
import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.services.vector_adapter.interface import VectorAdapter
from app.services.embeddings import get_embedding_service
from app.models import VectorUpsertBatch, RagResultItem
from app.infra.config import get_settings
from app.infra.logging import get_logger


class QdrantVectorAdapter(VectorAdapter):
    """Qdrant-based vector storage implementation."""
    
    def __init__(self):
        """Initialize Qdrant adapter."""
        self.settings = get_settings()
        self.logger = get_logger("vector.qdrant")
        
        # Initialize Qdrant client
        self.client = AsyncQdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key
        )
        
        # Initialize embedding service
        self.embedding_service = get_embedding_service(self.settings)
        self.collection_name = self.settings.qdrant_collection_name
        
        # Initialize collection on startup
        asyncio.create_task(self._ensure_collection())
    
    async def _ensure_collection(self):
        """Ensure collection exists with proper configuration."""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                embedding_dimension = self.embedding_service.get_embedding_dimension()
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                self.logger.info(f"Created collection: {self.collection_name} with dimension: {embedding_dimension}")
        except Exception as e:
            self.logger.error(f"Failed to ensure collection: {e}")
    
    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts."""
        try:
            return await self.embedding_service.embed_texts(texts)
        except Exception as e:
            self.logger.error(f"Failed to get embeddings: {e}")
            raise
    
    async def upsert_batch(self, batch: VectorUpsertBatch) -> bool:
        """Upsert a batch of chunks into Qdrant."""
        try:
            # Get embeddings for all chunk texts
            texts = [item.text for item in batch.items]
            embeddings = await self._get_embeddings(texts)
            
            # Create points for upsert
            points = []
            for item, embedding in zip(batch.items, embeddings):
                point = PointStruct(
                    id=item.id,
                    vector=embedding,
                    payload={
                        "doc_id": item.doc_id,
                        "source": item.metadata.get("source"),
                        "path": item.metadata.get("path"),
                        "lang": item.metadata.get("lang"),
                        "ord": item.ord,
                        "text": item.text,
                        "original_id": item.metadata.get("original_id")  # Include original chunk ID
                    }
                )
                points.append(point)
            
            # Upsert points
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            self.logger.info(
                "Batch upserted successfully",
                extra={
                    "doc_id": batch.doc_id,
                    "points_count": len(points)
                }
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upsert batch: {e}")
            return False
    
    async def search(self, 
                    query_text: str, 
                    top_k: int = 5, 
                    filters: Optional[Dict[str, Any]] = None) -> List[RagResultItem]:
        """Search for similar chunks in Qdrant."""
        try:
            # Get query embedding
            query_embeddings = await self._get_embeddings([query_text])
            query_vector = query_embeddings[0]
            
            # Build filter conditions
            filter_conditions = None
            if filters and any(v is not None and v != {} and v != [] and v != "" for v in filters.values()):
                conditions = []
                for key, value in filters.items():
                    if value is not None:  # Skip None values
                        if isinstance(value, list):
                            for v in value:
                                if v is not None:  # Skip None values in lists
                                    conditions.append(FieldCondition(key=key, match=MatchValue(value=v)))
                        else:
                            conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                
                if conditions:
                    filter_conditions = Filter(should=conditions)
            
            # Perform search
            search_results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_conditions,
                limit=top_k,
                with_payload=True
            )
            
            # Convert to result items
            results = []
            for result in search_results:
                payload = result.payload
                full_text = payload["text"]
                item = RagResultItem(
                    chunk_id=str(result.id),
                    doc_id=payload["doc_id"],
                    source=payload["source"],
                    path=payload.get("path"),
                    score=result.score,
                    snippet=full_text[:500] + "..." if len(full_text) > 500 else full_text,
                    full_text=full_text
                )
                results.append(item)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete all chunks for a document from Qdrant."""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[FieldCondition(key="doc_id", match={"value": doc_id})]
                )
            )
            
            self.logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check Qdrant health."""
        try:
            await self.client.get_collections()
            return True
        except Exception as e:
            self.logger.error(f"Qdrant health check failed: {e}")
            return False