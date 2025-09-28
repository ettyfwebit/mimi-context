"""
LLM client for calling OpenAI or Ollama.
"""
import httpx
from abc import ABC, abstractmethod
from typing import Optional
from openai import AsyncOpenAI
from app.infra.logging import get_logger

logger = get_logger("services.agent_core.llm_client")


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI client implementation."""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4o-mini",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            if response.choices and len(response.choices) > 0:
                answer = response.choices[0].message.content or ""
                logger.info("Generated response using OpenAI")
                return answer
            else:
                logger.error("No response from OpenAI")
                return "I apologize, but I couldn't generate a response."
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to generate response: {e}")


class OllamaClient(LLMClient):
    """Ollama client implementation."""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434",
        model: str = "mistral",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Ollama API."""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens
                        }
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                answer = data.get("response", "")
                
                if answer:
                    logger.info("Generated response using Ollama")
                    return answer
                else:
                    logger.error("Empty response from Ollama")
                    return "I apologize, but I couldn't generate a response."
                
        except httpx.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise Exception(f"Failed to connect to Ollama: {e}")
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise Exception(f"Failed to generate response: {e}")


def create_llm_client(
    backend: str,
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-4o-mini",
    ollama_base_url: str = "http://localhost:11434",
    ollama_model: str = "mistral",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> LLMClient:
    """Factory function to create appropriate LLM client."""
    
    if backend.lower() == "openai":
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI backend")
        return OpenAIClient(
            api_key=openai_api_key,
            model=openai_model,
            max_tokens=max_tokens,
            temperature=temperature
        )
    elif backend.lower() == "ollama":
        return OllamaClient(
            base_url=ollama_base_url,
            model=ollama_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")