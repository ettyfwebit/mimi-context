"""
Embedding service that supports both OpenAI and local embedding models.
"""

import asyncio
import logging
from typing import List, Optional
from abc import ABC, abstractmethod

import openai
from sentence_transformers import SentenceTransformer

from ..infra.config.settings import Settings

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider using their API."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        # Dimensions for different OpenAI models
        self.dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension for the current model."""
        return self.dimensions.get(self.model, 1536)


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embedding provider using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with a sentence transformer model.
        
        Popular models:
        - all-MiniLM-L6-v2: Fast, 384 dimensions, good quality
        - all-mpnet-base-v2: Slower, 768 dimensions, better quality
        - paraphrase-multilingual-MiniLM-L12-v2: Multilingual support
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self._dimension: Optional[int] = None
        logger.info(f"Initializing local embedding model: {model_name}")
    
    def _load_model(self):
        """Lazy load the model when first needed."""
        if self.model is None:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            # Get dimension from a test embedding
            test_embedding = self.model.encode(["test"])
            self._dimension = len(test_embedding[0])
            logger.info(f"Model loaded. Embedding dimension: {self._dimension}")
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model."""
        self._load_model()
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, 
            self.model.encode, 
            texts
        )
        
        # Convert numpy arrays to lists
        return [embedding.tolist() for embedding in embeddings]
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            self._load_model()
        return self._dimension


class EmbeddingService:
    """Service that manages embedding generation with configurable providers."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider: Optional[EmbeddingProvider] = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the embedding provider based on settings."""
        embedding_provider = getattr(self.settings, 'EMBEDDING_PROVIDER', 'local')
        
        if embedding_provider == 'openai':
            if not self.settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key required for OpenAI embedding provider")
            
            self.provider = OpenAIEmbeddingProvider(
                api_key=self.settings.OPENAI_API_KEY,
                model=self.settings.OPENAI_EMBEDDING_MODEL
            )
            logger.info(f"Initialized OpenAI embedding provider with model: {self.settings.OPENAI_EMBEDDING_MODEL}")
        
        elif embedding_provider == 'local':
            model_name = getattr(self.settings, 'LOCAL_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
            self.provider = LocalEmbeddingProvider(model_name=model_name)
            logger.info(f"Initialized local embedding provider with model: {model_name}")
        
        else:
            raise ValueError(f"Unknown embedding provider: {embedding_provider}")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        embeddings = await self.provider.embed_texts(texts)
        logger.debug(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.provider.get_embedding_dimension()


# Global instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(settings: Settings) -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(settings)
    return _embedding_service