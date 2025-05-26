from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from ..core.agent_types import AgentRole

class AgentCreate(BaseModel):
    workflow_id: UUID
    node_id: str
    name: str
    role: AgentRole
    config: Dict[str, Any]

class AgentResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    node_id: str
    name: str
    role: AgentRole
    config: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentExecutionResponse(BaseModel):
    id: UUID
    execution_id: UUID
    agent_id: UUID
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    state: Optional[Dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AgentMessageResponse(BaseModel):
    id: UUID
    execution_id: UUID
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True