from sqlalchemy import Column, String, JSON, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base
from ..core.agent_types import AgentRole

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"))
    node_id = Column(String(255), nullable=False)  # React Flow node ID
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(AgentRole), nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    input_data = Column(JSON)
    output_data = Column(JSON)
    state = Column(JSON)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

class AgentMessage(Base):
    __tablename__ = "agent_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id"))
    sender_id = Column(String(255), nullable=False)
    recipient_id = Column(String(255), nullable=False)
    message_type = Column(String(50), nullable=False)
    content = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())