"""
Application settings and configuration.
"""
import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App configuration
    app_env: str = "development"
    port: int = 8080
    
    # Vector backend configuration
    vector_backend: str = "qdrant"  # qdrant|openai
    
    # Embedding configuration
    embedding_provider: str = "local"  # local|openai
    local_embedding_model: str = "all-MiniLM-L6-v2"
    
    # OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_vector_store_id: Optional[str] = None
    
    # Qdrant configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "mimi_chunks"
    
    # Upload configuration
    upload_max_size_mb: int = 10
    upload_allowed_extensions: str = ".txt,.md,.pdf"
    
    # Database configuration
    database_url: str = "sqlite:///./mimi_metadata.db"
    
    # Agent configuration
    agent_backend: str = "openai"  # openai|ollama
    agent_openai_model: str = "gpt-4o-mini"
    agent_ollama_model: str = "mistral"
    agent_enable_memory: bool = False
    
    # Confluence configuration
    confluence_base_url: Optional[str] = None
    confluence_auth_token: Optional[str] = None
    conf_space_key: Optional[str] = None
    conf_root_page_id: Optional[str] = None
    conf_include_labels: str = ""  # CSV
    conf_exclude_labels: str = ""  # CSV
    conf_path_prefix: Optional[str] = None
    conf_max_pages: int = 2000
    conf_max_depth: int = 5
    conf_concurrency: int = 4
    conf_dry_run_default: bool = False
    
    # RAG/ingest knobs
    chunk_target_size: int = 1000
    chunk_overlap: int = 140
    require_path: bool = True
    rag_min_score: float = 0.30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()