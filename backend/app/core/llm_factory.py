import os
from typing import Optional, Any
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.schema.language_model import BaseLanguageModel

class LLMFactory:
    """Factory for creating LLM instances based on provider configuration"""
    
    @staticmethod
    def create_llm(
        provider: str = "auto",
        model: Optional[str] = None,
        **kwargs
    ) -> BaseLanguageModel:
        """
        Create an LLM instance based on the provider
        
        Args:
            provider: LLM provider (openai, ollama, auto)
            model: Model name (optional)
            **kwargs: Additional model parameters
            
        Returns:
            BaseLanguageModel instance
        """
        provider = provider.lower()
        
        if provider == "auto":
            # Try OpenAI first if API key exists
            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key":
                provider = "openai"
            else:
                provider = "ollama"
        
        if provider == "openai":
            return ChatOpenAI(
                model=model or os.getenv("OPENAI_MODEL", "gpt-4"),
                api_key=os.getenv("OPENAI_API_KEY"),
                **kwargs
            )
        elif provider == "ollama":
            return Ollama(
                model=model or "llama2",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                **kwargs
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
