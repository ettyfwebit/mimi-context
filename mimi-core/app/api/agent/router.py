"""
Agent API router.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.agent import AgentQuery, AgentResponse
from app.services.agent_core.agent_core import create_agent_core, AgentCore
from app.infra.config.settings import get_settings
from app.infra.logging import get_logger

router = APIRouter(prefix="/agent", tags=["agent"])
logger = get_logger("api.agent")


async def get_agent_core() -> AgentCore:
    """Dependency to get configured agent core."""
    settings = get_settings()
    
    try:
        agent_core = create_agent_core(
            rag_endpoint_url="http://localhost:8080/rag/query",
            backend=settings.agent_backend,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.agent_openai_model,
            ollama_model=settings.agent_ollama_model,
            enable_memory=settings.agent_enable_memory
        )
        return agent_core
    except Exception as e:
        logger.error(f"Failed to create agent core: {e}")
        raise HTTPException(status_code=500, detail="Agent service unavailable")


@router.post("/ask")
async def ask_agent(
    query: AgentQuery,
    agent_core: AgentCore = Depends(get_agent_core)
) -> AgentResponse:
    """
    Ask the conversational agent a question.
    
    The agent will:
    1. Query Mimi's RAG service for relevant document chunks
    2. Build a context-rich prompt with the user's question
    3. Generate a natural language answer using the configured LLM
    4. Return the answer with citations and raw chunk data
    
    Args:
        query: Agent query with question and parameters
        agent_core: Agent core dependency
        
    Returns:
        Natural language answer with citations and supporting chunks
    """
    try:
        logger.info(f"Agent query received: {query.question}")
        
        response = await agent_core.process_query(
            question=query.question,
            top_k=query.top_k,
            session_id=query.session_id
        )
        
        logger.info(f"Agent response generated with {len(response.citations)} citations")
        return response
        
    except Exception as e:
        logger.error(f"Agent query failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to process agent query"
        )