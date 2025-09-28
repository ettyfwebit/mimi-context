"""
Test cases for the agent functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.agent_core.agent_core import AgentCore
from app.services.agent_core.rag_client import RagClient
from app.services.agent_core.llm_client import LLMClient
from app.models.agent import AgentResponse


@pytest.mark.asyncio
async def test_agent_core_process_query():
    """Test the main agent query processing flow."""
    
    # Mock RAG client
    mock_rag_client = AsyncMock(spec=RagClient)
    mock_rag_client.query.return_value = [
        {
            "chunk_id": "chunk1",
            "doc_id": "doc1",
            "source": "test",
            "path": "test.txt",
            "score": 0.95,
            "snippet": "This is a test document about booking tickets.",
            "full_text": "This is a test document about booking tickets. You can book by calling 123-456-7890."
        }
    ]
    
    # Mock LLM client
    mock_llm_client = AsyncMock(spec=LLMClient)
    mock_llm_client.generate_response.return_value = "To book a ticket, you can call 123-456-7890 as mentioned in the documentation. [doc1]"
    
    # Create agent core
    agent_core = AgentCore(
        rag_client=mock_rag_client,
        llm_client=mock_llm_client,
        enable_memory=False
    )
    
    # Test query processing
    response = await agent_core.process_query("How do I book a ticket?")
    
    # Verify response
    assert isinstance(response, AgentResponse)
    assert "book a ticket" in response.answer.lower()
    assert len(response.citations) == 1
    assert response.citations[0].doc_id == "doc1"
    assert len(response.raw_chunks) == 1
    
    # Verify calls
    mock_rag_client.query.assert_called_once_with("How do I book a ticket?", 3)
    mock_llm_client.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_agent_core_with_memory():
    """Test agent with conversation memory enabled."""
    
    # Mock clients
    mock_rag_client = AsyncMock(spec=RagClient)
    mock_rag_client.query.return_value = []
    
    mock_llm_client = AsyncMock(spec=LLMClient)
    mock_llm_client.generate_response.return_value = "I don't have enough information to answer that question."
    
    # Create agent with memory
    agent_core = AgentCore(
        rag_client=mock_rag_client,
        llm_client=mock_llm_client,
        enable_memory=True,
        memory_size=2
    )
    
    # First query
    response1 = await agent_core.process_query(
        "What is the weather like?", 
        session_id="test-session"
    )
    
    # Second query (should have context from first)
    response2 = await agent_core.process_query(
        "Can you elaborate?", 
        session_id="test-session"
    )
    
    # Verify memory is maintained
    assert "test-session" in agent_core.conversation_memory
    assert len(agent_core.conversation_memory["test-session"].turns) == 2


def test_build_prompt():
    """Test prompt building functionality."""
    
    mock_rag_client = MagicMock(spec=RagClient)
    mock_llm_client = MagicMock(spec=LLMClient)
    
    agent_core = AgentCore(
        rag_client=mock_rag_client,
        llm_client=mock_llm_client
    )
    
    chunks = [
        {
            "doc_id": "doc1",
            "full_text": "This is the full content of the document.",
            "snippet": "This is the full content..."
        }
    ]
    
    prompt = agent_core._build_prompt("Test question", chunks)
    
    assert "Test question" in prompt
    assert "This is the full content of the document." in prompt
    assert "## Context Information:" in prompt
    assert "## Instructions:" in prompt