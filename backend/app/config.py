from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Visual AI Framework"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/visual_ai"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # WebSocket
    ws_heartbeat_interval: int = 30
    
    # LangGraph
    langgraph_checkpointer: str = "postgresql"
    
    class Config:
        env_file = ".env"

settings = Settings()