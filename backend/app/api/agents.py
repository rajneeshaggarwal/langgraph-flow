from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.agent import Agent, AgentExecution, AgentMessage
from ..schemas.agent import AgentCreate, AgentResponse, AgentExecutionResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent"""
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    await db.commit()
    await db.refresh(db_agent)
    return db_agent

@router.get("/workflow/{workflow_id}", response_model=List[AgentResponse])
async def get_workflow_agents(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all agents for a workflow"""
    result = await db.execute(
        select(Agent).where(Agent.workflow_id == workflow_id)
    )
    agents = result.scalars().all()
    return agents

@router.get("/executions/{execution_id}", response_model=List[AgentExecutionResponse])
async def get_agent_executions(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get agent execution details"""
    result = await db.execute(
        select(AgentExecution).where(AgentExecution.execution_id == execution_id)
    )
    executions = result.scalars().all()
    return executions

@router.get("/messages/{execution_id}")
async def get_agent_messages(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get messages between agents during execution"""
    result = await db.execute(
        select(AgentMessage)
        .where(AgentMessage.execution_id == execution_id)
        .order_by(AgentMessage.created_at)
    )
    messages = result.scalars().all()
    return messages