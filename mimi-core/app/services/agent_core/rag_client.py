"""
RAG client for calling Mimi's /rag/query endpoint.
"""
import httpx
from typing import List, Dict, Any
from app.infra.logging import get_logger

logger = get_logger("services.agent_core.rag_client")


class RagClient:
    """Client for interacting with Mimi's RAG service."""
    
    def __init__(self, rag_endpoint_url: str = "http://localhost:8080/rag/query"):
        self.rag_endpoint_url = rag_endpoint_url
    
    async def query(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Query the RAG endpoint and return the chunks.
        
        Args:
            question: The user's question
            top_k: Number of top results to return
            
        Returns:
            List of chunks from the RAG response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.rag_endpoint_url,
                    json={"question": question, "top_k": top_k},
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract chunks from the response
                # Based on the RAG router, response format is: {"answers": [{"chunks": [...]}]}
                if "answers" in data and len(data["answers"]) > 0:
                    chunks = data["answers"][0].get("chunks", [])
                    logger.info(f"Retrieved {len(chunks)} chunks from RAG service")
                    return chunks
                else:
                    logger.warning("No chunks found in RAG response")
                    return []
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling RAG service: {e}")
            raise Exception(f"Failed to query RAG service: {e}")
        except Exception as e:
            logger.error(f"Error calling RAG service: {e}")
            raise Exception(f"Failed to query RAG service: {e}")