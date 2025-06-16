#!/usr/bin/env python3
"""
Test local LangFuse integration
"""

import os
import sys
from datetime import datetime
from langfuse import Langfuse
from langfuse.callback import CallbackHandler

def test_langfuse_connection():
    """Test connection to local LangFuse"""
    
    print("🧪 Testing Local LangFuse Connection")
    print("====================================")
    
    # Get configuration
    host = os.getenv("LANGFUSE_HOST", "http://localhost:3001")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    print(f"Host: {host}")
    print(f"Public Key: {public_key[:20]}..." if public_key else "❌ Not configured")
    print(f"Secret Key: {'✅ Configured' if secret_key else '❌ Not configured'}")
    print("")
    
    if not public_key or not secret_key:
        print("❌ LangFuse keys not configured in .env")
        print("Run: ./scripts/setup_langfuse.sh")
        return False
    
    try:
        # Create client
        langfuse = Langfuse(
            host=host,
            public_key=public_key,
            secret_key=secret_key,
            debug=True
        )
        
        # Create a test trace
        trace = langfuse.trace(
            name="test-trace",
            metadata={
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Create a test generation
        generation = trace.generation(
            name="test-generation",
            model="test-model",
            input="Hello, LangFuse!",
            output="Hello from local LangFuse!"
        )
        
        # Create a test score
        trace.score(
            name="test-score",
            value=0.95,
            comment="Test score from local setup"
        )
        
        # Flush immediately
        langfuse.flush()
        
        print("✅ Successfully sent test trace!")
        print(f"View at: {host}")
        print("")
        
        # Test callback handler
        print("Testing CallbackHandler...")
        handler = CallbackHandler(
            host=host,
            public_key=public_key,
            secret_key=secret_key
        )
        
        print("✅ CallbackHandler created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ollama_with_langfuse():
    """Test Ollama integration with LangFuse tracing"""
    
    print("\n🦙 Testing Ollama + LangFuse Integration")
    print("========================================")
    
    try:
        from langchain_ollama import ChatOllama
        from langfuse.callback import CallbackHandler
        
        # Create callback handler
        handler = CallbackHandler(
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3001"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            session_id="test-ollama-session",
            user_id="test-user"
        )
        
        # Create Ollama model
        llm = ChatOllama(
            model="llama2",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            callbacks=[handler]
        )
        
        # Test generation
        print("Sending test prompt to Ollama...")
        response = llm.invoke("Say 'Hello from Ollama with LangFuse tracing!'")
        
        print(f"Response: {response.content}")
        print("✅ Ollama + LangFuse integration working!")
        
        # Flush traces
        handler.langfuse.flush()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running and llama2 model is pulled")
        return False

def main():
    """Run all tests"""
    
    # Test basic connection
    if not test_langfuse_connection():
        sys.exit(1)
    
    # Test Ollama integration if available
    if os.getenv("LLM_PROVIDER", "").lower() in ["ollama", "auto"]:
        test_ollama_with_langfuse()
    
    print("\n✅ All tests completed!")
    print(f"View traces at: {os.getenv('LANGFUSE_HOST', 'http://localhost:3001')}")

if __name__ == "__main__":
    main()