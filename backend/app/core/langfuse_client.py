"""
LangFuse client configuration for local deployment
"""

import os
from typing import Optional
from langfuse import Langfuse
import logging

logger = logging.getLogger(__name__)

class LocalLangfuseClient:
    """Wrapper for LangFuse client with local configuration"""
    
    _instance: Optional[Langfuse] = None
    
    @classmethod
    def get_client(cls) -> Optional[Langfuse]:
        """Get or create LangFuse client instance"""
        
        if cls._instance is None:
            try:
                # Check if LangFuse is enabled
                if os.getenv("LANGFUSE_ENABLED", "true").lower() != "true":
                    logger.info("LangFuse is disabled")
                    return None
                
                # Get configuration
                host = os.getenv("LANGFUSE_HOST", "http://localhost:3001")
                public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
                secret_key = os.getenv("LANGFUSE_SECRET_KEY")
                
                if not public_key or not secret_key:
                    logger.warning("LangFuse keys not configured")
                    return None
                
                # Create client
                cls._instance = Langfuse(
                    host=host,
                    public_key=public_key,
                    secret_key=secret_key,
                    debug=os.getenv("DEBUG", "false").lower() == "true",
                    enabled=True,
                    # Local deployment specific settings
                    timeout=30,  # Longer timeout for local
                    max_retries=3,
                    flush_at=1,  # Flush immediately for local testing
                    flush_interval=1  # Flush every second
                )
                
                logger.info(f"LangFuse client initialized with host: {host}")
                
            except Exception as e:
                logger.error(f"Failed to initialize LangFuse client: {e}")
                return None
        
        return cls._instance
    
    @classmethod
    def flush(cls):
        """Flush any pending events"""
        if cls._instance:
            cls._instance.flush()
    
    @classmethod
    def shutdown(cls):
        """Shutdown the client"""
        if cls._instance:
            cls._instance.flush()
            cls._instance.shutdown()
            cls._instance = None

# Helper function for easy access
def get_langfuse() -> Optional[Langfuse]:
    """Get LangFuse client instance"""
    return LocalLangfuseClient.get_client()