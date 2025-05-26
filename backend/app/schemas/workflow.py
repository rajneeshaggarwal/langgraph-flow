from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

class NodeData(BaseModel):
    label: str
    type: str
    config: Dict[str, Any] = {}

class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: NodeData

class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[Node]
    edges: List[Edge]

class WorkflowResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    graph_data: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class WorkflowExecutionCreate(BaseModel):
    workflow_id: UUID
    input_data: Optional[Dict[str, Any]] = None

class WorkflowExecutionResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True