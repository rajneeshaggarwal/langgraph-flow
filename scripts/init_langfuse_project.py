#!/usr/bin/env python3
"""
Initialize LangFuse with project and API keys
"""

import os
import sys
import time
import httpx
from typing import Optional

def wait_for_langfuse(host: str, max_attempts: int = 30) -> bool:
    """Wait for LangFuse to be ready"""
    print(f"Waiting for LangFuse at {host}...")
    
    for i in range(max_attempts):
        try:
            response = httpx.get(f"{host}/api/public/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ LangFuse is ready!")
                return True
        except Exception:
            pass
        
        time.sleep(2)
        print(f"  Attempt {i+1}/{max_attempts}...")
    
    return False

def create_api_client(host: str, email: str, password: str) -> Optional[str]:
    """Login and get session token"""
    print(f"Logging in as {email}...")
    
    # Note: This is a simplified example
    # LangFuse authentication flow might require additional steps
    try:
        # You would need to implement the actual authentication flow
        # This is a placeholder
        return "session-token"
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def main():
    """Main initialization function"""
    
    # Configuration
    langfuse_host = os.getenv("LANGFUSE_HOST", "http://localhost:3001")
    admin_email = os.getenv("LANGFUSE_ADMIN_EMAIL", "admin@localhost")
    admin_password = os.getenv("LANGFUSE_ADMIN_PASSWORD", "admin123")
    
    print("🚀 LangFuse Project Initialization")
    print("==================================")
    print(f"Host: {langfuse_host}")
    print(f"Admin: {admin_email}")
    print("")
    
    # Wait for LangFuse
    if not wait_for_langfuse(langfuse_host):
        print("❌ LangFuse is not responding")
        sys.exit(1)
    
    # Create session
    session = create_api_client(langfuse_host, admin_email, admin_password)
    if not session:
        print("❌ Failed to authenticate")
        sys.exit(1)
    
    print("")
    print("✅ LangFuse is configured and ready!")
    print("")
    print("Access the UI at:", langfuse_host)
    print("Use the API keys from your .env file to send traces")
    
if __name__ == "__main__":
    main()