from langgraph.prebuilt import create_react_agent
from backend.app.core.llm_factory import LLMFactory

def create_synthesis_agent():
    """Create an agent that synthesizes results from multiple sources"""
    llm = LLMFactory.create_llm()
    
    # Add synthesis-specific tools here
    tools = []
    
    return create_react_agent(
        llm,
        tools=tools,
        system_message="You are a synthesis agent that combines and analyzes results from multiple sources."
    )
