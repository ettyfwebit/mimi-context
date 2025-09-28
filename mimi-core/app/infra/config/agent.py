"""
Agent service configuration.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """Agent service configuration."""
    
    # Backend selection
    agent_backend: str = "openai"  # openai|ollama
    
    # OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    
    # Ollama configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    ollama_temperature: float = 0.7
    ollama_max_tokens: int = 1000
    
    # Memory configuration
    conversation_memory_size: int = 3  # Number of turns to keep
    enable_memory: bool = False  # Set to True to enable conversation memory
    
    # Mimi Core RAG endpoint
    rag_endpoint_url: str = "http://localhost:8080/rag/query"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"