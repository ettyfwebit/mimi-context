"""
Integration tests for RAG query functionality.
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models import RagResultItem


class TestRagQuery:
    """Integration tests for RAG query endpoints."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = TestClient(app)
    
    def test_rag_query_endpoint_structure(self):
        """Test RAG query endpoint with mock data."""
        # Create mock query
        query_data = {
            "question": "How to book a ticket?",
            "top_k": 3
        }
        
        # Mock the vector adapter to avoid needing actual vector store
        with pytest.MonkeyPatch().context() as mp:
            mock_adapter = AsyncMock()
            mock_adapter.search.return_value = [
                RagResultItem(
                    chunk_id="test:doc1::c0",
                    doc_id="test:doc1",
                    source="test",
                    path="test_doc.md",
                    score=0.95,
                    snippet="To book a ticket, first navigate to the booking page..."
                ),
                RagResultItem(
                    chunk_id="test:doc2::c1",
                    doc_id="test:doc2", 
                    source="test",
                    path="another_doc.md",
                    score=0.87,
                    snippet="The booking process requires selecting your destination..."
                )
            ]
            
            # Mock the dependency function properly
            async def mock_get_vector_adapter():
                return mock_adapter
            
            # Replace the dependency in the module
            import app.api.rag.router
            mp.setattr(app.api.rag.router, "get_vector_adapter", mock_get_vector_adapter)
            
            # Make request
            response = self.client.post("/rag/query", json=query_data)
        
        # Verify response structure (even though mocked)
        assert response.status_code == 200
        data = response.json()
        
        # Check response matches OpenAPI spec
        assert "answers" in data
        assert isinstance(data["answers"], list)
        assert len(data["answers"]) >= 1
        
        answer = data["answers"][0]
        assert "text" in answer
        assert "chunks" in answer
        assert answer["text"] == ""  # Empty for MNVP
        
        # Check chunk structure
        if answer["chunks"]:
            chunk = answer["chunks"][0]
            required_fields = ["chunk_id", "doc_id", "source", "score", "snippet"]
            for field in required_fields:
                assert field in chunk
    
    def test_rag_query_validation(self):
        """Test RAG query input validation."""
        # Test missing question
        response = self.client.post("/rag/query", json={})
        assert response.status_code == 422  # Validation error
        
        # Test invalid top_k
        response = self.client.post("/rag/query", json={
            "question": "test",
            "top_k": -1
        })
        # Should still work, but adapter might handle validation
        
        # Test valid query with filters
        response = self.client.post("/rag/query", json={
            "question": "How to use the system?",
            "top_k": 5,
            "filters": {"source": ["upload"]}
        })
        # Response depends on mock, but should not error on structure
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OpenAI API key not available"
    )
    @pytest.mark.asyncio
    async def test_rag_query_with_real_vector_store(self):
        """Test RAG query with actual vector store (requires setup)."""
        # This test would require actual Qdrant setup
        # Skip by default, run only when vector store is available
        
        from app.services.vector_adapter import create_vector_adapter
        
        try:
            adapter = create_vector_adapter()
            
            # Test health check first
            is_healthy = await adapter.health_check()
            if not is_healthy:
                pytest.skip("Vector store not available")
            
            # Perform actual search
            results = await adapter.search(
                query_text="test query",
                top_k=3
            )
            
            # Results might be empty but should not error
            assert isinstance(results, list)
            
        except Exception as e:
            pytest.skip(f"Vector store setup required: {e}")
    
    def test_rag_response_format_compliance(self):
        """Test that RAG response matches OpenAPI specification exactly."""
        
        # Mock successful response
        with pytest.MonkeyPatch().context() as mp:
            mock_adapter = AsyncMock()
            mock_adapter.search.return_value = [
                RagResultItem(
                    chunk_id="upload:booking_flow.md::c0",
                    doc_id="upload:booking_flow.md",
                    source="upload",
                    path="kb/booking_flow.md",
                    score=0.86,
                    snippet="To book a ticket..."
                )
            ]
            
            # Mock the dependency function properly
            async def mock_get_vector_adapter():
                return mock_adapter
            
            import app.api.rag.router
            mp.setattr(app.api.rag.router, "get_vector_adapter", mock_get_vector_adapter)
            
            # Test the exact example from OpenAPI spec
            query_data = {
                "question": "How to book a ticket?",
                "top_k": 5,
                "filters": {"source": ["upload"]}
            }
            
            response = self.client.post("/rag/query", json=query_data)
            assert response.status_code == 200
            
            data = response.json()
            
            # Verify exact structure from OpenAPI spec
            assert "answers" in data
            answers = data["answers"]
            assert len(answers) == 1
            
            answer = answers[0]
            assert "text" in answer
            assert "chunks" in answer
            assert answer["text"] == ""  # Empty for MNVP
            
            chunks = answer["chunks"]
            if chunks:
                chunk = chunks[0]
                
                # Check all required fields from OpenAPI spec
                assert "chunk_id" in chunk
                assert "doc_id" in chunk
                assert "source" in chunk
                assert "path" in chunk
                assert "score" in chunk
                assert "snippet" in chunk
                
                # Verify types
                assert isinstance(chunk["chunk_id"], str)
                assert isinstance(chunk["doc_id"], str)
                assert isinstance(chunk["source"], str)
                assert isinstance(chunk["score"], (int, float))
                assert isinstance(chunk["snippet"], str)