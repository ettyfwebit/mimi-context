"""
RAG query API router.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from app.models import RagQuery, RagResultItem
from app.services.vector_adapter import create_vector_adapter
from app.infra.logging import get_logger

router = APIRouter(prefix="/rag", tags=["rag"])
logger = get_logger("api.rag")


async def get_vector_adapter():
    """Dependency to get vector adapter."""
    return create_vector_adapter()


@router.post("/query")
async def query_documents(
    query: RagQuery,
    vector_adapter = Depends(get_vector_adapter)
) -> Dict[str, Any]:
    """
    Query documents using RAG (Retrieval Augmented Generation).
    
    Args:
        query: RAG query parameters
        vector_adapter: Vector adapter dependency
        
    Returns:
        Query results with chunks and citations
    """
    try:
        # Perform vector search
        results = await vector_adapter.search(
            query_text=query.question,
            top_k=query.top_k,
            filters=query.filters
        )
        
        # Convert to response format matching OpenAPI spec
        chunks = []
        for result in results:
            chunk = {
                "chunk_id": result.chunk_id,
                "doc_id": result.doc_id,
                "source": result.source,
                "path": result.path,
                "score": result.score,
                "snippet": result.snippet,
                "full_text": result.full_text
            }
            chunks.append(chunk)
        
        # For MNVP, text is empty (consumer composes the answer)
        response = {
            "answers": [
                {
                    "text": "",  # Empty for MNVP
                    "chunks": chunks
                }
            ]
        }
        
        logger.info(
            "RAG query completed",
            extra={
                "question": query.question,
                "results_count": len(results),
                "top_k": query.top_k
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail="Query processing failed")