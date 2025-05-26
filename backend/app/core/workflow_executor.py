import asyncio
from typing import Dict, Any, Optional
from uuid import UUID
from ..models.workflow import WorkflowExecution
from ..models.agent import AgentExecution, AgentMessage
from ..database import AsyncSessionLocal
from .enhanced_langgraph_engine import EnhancedLangGraphEngine
from ..api.enhanced_websocket import manager
import json
from datetime import datetime
from sqlalchemy import update

class WorkflowExecutor:
    def __init__(self):
        self.engine = EnhancedLangGraphEngine()
        self.active_executions = {}
    
    async def execute_workflow(
        self, 
        workflow_id: UUID, 
        execution_id: UUID,
        graph_data: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None
    ):
        """Execute a workflow asynchronously with agent support"""
        try:
            # Send execution started update
            await manager.send_agent_update(
                execution_id,
                "system",
                "started",
                {"message": "Workflow execution started"}
            )
            
            # Build the graph with enhanced engine
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            graph = self.engine.build_graph_from_flow(nodes, edges)
            
            # Store active execution
            self.active_executions[execution_id] = {
                'graph': graph,
                'status': 'running',
                'agents': self.engine.orchestrator.agents
            }
            
            # Execute the graph
            initial_state = {
                'messages': [],
                'current_node': 'start',
                'context': input_data or {},
                'agents': self.engine.orchestrator.agents,
                'shared_state': {},
                'execution_pattern': self.engine._detect_workflow_pattern(nodes, edges)
            }
            
            # Run the graph with progress updates
            async for chunk in graph.astream(initial_state):
                # Send real-time updates
                current_node = chunk.get('current_node', '')
                if current_node and current_node != 'start':
                    await manager.send_agent_update(
                        execution_id,
                        current_node,
                        "processing",
                        chunk
                    )
                    
                    # Store agent execution in database
                    await self._store_agent_execution(
                        execution_id,
                        current_node,
                        chunk
                    )
            
            # Get final result
            result = await graph.ainvoke(initial_state)
            
            # Update execution status
            await self._update_execution(
                execution_id, 
                'completed', 
                output_data=result
            )
            
            # Send completion update
            await manager.send_agent_update(
                execution_id,
                "system",
                "completed",
                result
            )
            
        except Exception as e:
            # Update execution status with error
            await self._update_execution(
                execution_id, 
                'failed', 
                error_message=str(e)
            )
            
            # Send error update
            await manager.send_agent_update(
                execution_id,
                "system",
                "failed",
                {"error": str(e)}
            )
        finally:
            # Clean up
            self.active_executions.pop(execution_id, None)
    
    async def _store_agent_execution(
        self,
        execution_id: UUID,
        agent_id: str,
        data: Dict[str, Any]
    ):
        """Store agent execution details in database"""
        async with AsyncSessionLocal() as session:
            # Find the agent by node_id
            from sqlalchemy import select
            from ..models.agent import Agent
            
            result = await session.execute(
                select(Agent).where(Agent.node_id == agent_id)
            )
            agent = result.scalar_one_or_none()
            
            if agent:
                agent_execution = AgentExecution(
                    execution_id=execution_id,
                    agent_id=agent.id,
                    input_data=data.get('context', {}),
                    output_data=data.get('messages', [])[-1] if data.get('messages') else None,
                    state=data.get('shared_state', {})
                )
                session.add(agent_execution)
                await session.commit()
    
    async def _update_execution(
        self, 
        execution_id: UUID, 
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Update execution status in database"""
        async with AsyncSessionLocal() as session:
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == execution_id)
                .values(
                    status=status,
                    output_data=output_data,
                    error_message=error_message,
                    completed_at=datetime.utcnow() if status in ['completed', 'failed'] else None
                )
            )
            
            await session.execute(stmt)
            await session.commit()