"""
Flexible LLM factory supporting multiple providers (OpenAI, Ollama, etc.)
"""

import os
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings
import logging

logger = logging.getLogger(__name__)

class LLMFactory:
    """Factory class for creating LLM instances based on configuration"""
    
    @staticmethod
    def create_llm(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> BaseLanguageModel:
        """
        Create an LLM instance based on provider configuration
        
        Args:
            provider: LLM provider (openai, ollama, auto)
            model: Model name
            temperature: Temperature setting
            **kwargs: Additional provider-specific arguments
            
        Returns:
            LLM instance
        """
        # Get provider from environment if not specified
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "auto").lower()
        
        # Auto mode: try Ollama first, then OpenAI
        if provider == "auto":
            try:
                return LLMFactory._create_ollama_llm(model, temperature, **kwargs)
            except Exception as e:
                logger.info(f"Ollama not available ({e}), trying OpenAI...")
                return LLMFactory._create_openai_llm(model, temperature, **kwargs)
        
        elif provider == "ollama":
            return LLMFactory._create_ollama_llm(model, temperature, **kwargs)
        
        elif provider == "openai":
            return LLMFactory._create_openai_llm(model, temperature, **kwargs)
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    def _create_ollama_llm(
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> BaseLanguageModel:
        """Create Ollama LLM instance"""
        try:
            from langchain_ollama import ChatOllama
            import httpx
            
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            # Check if Ollama is running
            try:
                response = httpx.get(f"{base_url}/api/tags", timeout=2.0)
                if response.status_code != 200:
                    raise ConnectionError("Ollama server not responding")
            except Exception as e:
                raise ConnectionError(f"Cannot connect to Ollama at {base_url}: {e}")
            
            if model is None:
                model = os.getenv("OLLAMA_MODEL", "llama2")
            
            logger.info(f"Creating Ollama LLM with model: {model}")
            
            return ChatOllama(
                model=model,
                base_url=base_url,
                temperature=temperature,
                **kwargs
            )
            
        except ImportError:
            raise ImportError("langchain-ollama not installed. Run: pip install langchain-ollama")
    
    @staticmethod
    def _create_openai_llm(
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> BaseLanguageModel:
        """Create OpenAI LLM instance"""
        try:
            from langchain_openai import ChatOpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your_openai_api_key":
                raise ValueError("OpenAI API key not configured")
            
            if model is None:
                model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            logger.info(f"Creating OpenAI LLM with model: {model}")
            
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key,
                **kwargs
            )
            
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
    
    @staticmethod
    def create_embeddings(provider: Optional[str] = None) -> Embeddings:
        """Create embeddings instance based on provider"""
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "auto").lower()
        
        if provider == "auto":
            try:
                return LLMFactory._create_ollama_embeddings()
            except Exception as e:
                logger.info(f"Ollama embeddings not available ({e}), trying OpenAI...")
                return LLMFactory._create_openai_embeddings()
        
        elif provider == "ollama":
            return LLMFactory._create_ollama_embeddings()
        
        elif provider == "openai":
            return LLMFactory._create_openai_embeddings()
        
        else:
            raise ValueError(f"Unknown embeddings provider: {provider}")
    
    @staticmethod
    def _create_ollama_embeddings() -> Embeddings:
        """Create Ollama embeddings instance"""
        try:
            from langchain_ollama import OllamaEmbeddings
            
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
            
            return OllamaEmbeddings(
                model=model,
                base_url=base_url
            )
            
        except ImportError:
            raise ImportError("langchain-ollama not installed")
    
    @staticmethod
    def _create_openai_embeddings() -> Embeddings:
        """Create OpenAI embeddings instance"""
        try:
            from langchain_openai import OpenAIEmbeddings
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            return OpenAIEmbeddings(api_key=api_key)
            
        except ImportError:
            raise ImportError("langchain-openai not installed")
    
    @staticmethod
    def get_available_models(provider: Optional[str] = None) -> Dict[str, list]:
        """Get available models for each provider"""
        available = {}
        
        # Check Ollama
        try:
            import httpx
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            response = httpx.get(f"{base_url}/api/tags", timeout=2.0)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                available["ollama"] = [m["name"] for m in models]
        except Exception:
            available["ollama"] = []
        
        # OpenAI models (static list)
        if os.getenv("OPENAI_API_KEY"):
            available["openai"] = [
                "gpt-4",
                "gpt-4-turbo-preview", 
                "gpt-4-vision-preview",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ]
        else:
            available["openai"] = []
        
        return available