from langgraph.prebuilt import create_react_agent
from backend.app.core.llm_factory import LLMFactory

def create_text_extraction_agent():
    """Create an agent specialized in text extraction"""
    llm = LLMFactory.create_llm()
    
    # Add text-specific tools here
    tools = []
    
    return create_react_agent(
        llm,
        tools=tools,
        system_message="You are a text extraction specialist focused on document processing and text analysis."
    )
