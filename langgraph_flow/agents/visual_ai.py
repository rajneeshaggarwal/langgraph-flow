from langgraph.prebuilt import create_react_agent
from typing import List, Optional, Any
from backend.app.core.llm_factory import LLMFactory

def create_visual_ai_agent(
    provider: str = "auto",
    model: Optional[str] = None,
    tools: Optional[List[Any]] = None,
    prompt: Optional[str] = None
):
    """Create a Visual AI agent with specified LLM and tools"""
    llm = LLMFactory.create_llm(provider=provider, model=model)
    
    return create_react_agent(
        llm,
        tools=tools or [],
        system_message=prompt or "You are a Visual AI assistant specialized in workflow orchestration"
    )
