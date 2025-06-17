from langgraph.prebuilt import create_react_agent
from backend.app.core.llm_factory import LLMFactory

def create_vision_agent():
    """Create an agent specialized in image analysis"""
    llm = LLMFactory.create_llm()
    
    # Add vision-specific tools here
    tools = []
    
    return create_react_agent(
        llm,
        tools=tools,
        system_message="You are a vision specialist agent focused on image analysis and visual data processing."
    )
