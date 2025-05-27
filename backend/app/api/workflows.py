from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
import json
import asyncio

from ..database import get_db
from ..models.workflow import Workflow, WorkflowExecution
from ..schemas.workflow import (
    WorkflowCreate, WorkflowResponse, 
    WorkflowExecutionCreate, WorkflowExecutionResponse
)
from ..core.workflow_executor import WorkflowExecutor

router = APIRouter(prefix="/api/workflows", tags=["workflows"])
executor = WorkflowExecutor()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow"""
    # Convert nodes and edges to JSON
    graph_data = {
        'nodes': [node.dict() for node in workflow.nodes],
        'edges': [edge.dict() for edge in workflow.edges]
    }
    
    # Create workflow record
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        graph_data=graph_data,
        langgraph_config={}  # Will be populated based on nodes
    )
    
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow)
    
    return db_workflow

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all workflows"""
    result = await db.execute(
        select(Workflow)
        .where(Workflow.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    workflows = result.scalars().all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow"""
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update a workflow"""
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    db_workflow = result.scalar_one_or_none()
    
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update fields
    db_workflow.name = workflow.name
    db_workflow.description = workflow.description
    db_workflow.graph_data = {
        'nodes': [node.dict() for node in workflow.nodes],
        'edges': [edge.dict() for edge in workflow.edges]
    }
    
    await db.commit()
    await db.refresh(db_workflow)
    
    return db_workflow

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: UUID,
    execution: WorkflowExecutionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Execute a workflow"""
    # Get workflow
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create execution record
    db_execution = WorkflowExecution(
        workflow_id=workflow_id,
        status='pending',
        input_data=execution.input_data
    )
    
    db.add(db_execution)
    await db.commit()
    await db.refresh(db_execution)
    
    # Start async execution
    asyncio.create_task(
        executor.execute_workflow(
            workflow_id=workflow_id,
            execution_id=db_execution.id,
            graph_data=workflow.graph_data,
            input_data=execution.input_data
        )
    )
    
    return db_execution

@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def get_workflow_executions(
    workflow_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all executions for a workflow"""
    result = await db.execute(
        select(WorkflowExecution)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .order_by(WorkflowExecution.started_at.desc())
        .offset(skip)
        .limit(limit)
    )
    executions = result.scalars().all()
    return executions