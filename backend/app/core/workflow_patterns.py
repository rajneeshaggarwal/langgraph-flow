from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
from .agent_types import BaseAgent, CoordinatorAgent

class WorkflowPattern(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    PIPELINE = "pipeline"

class WorkflowOrchestrator:
    """Orchestrates different workflow patterns"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.shared_state: Dict[str, Any] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent in the orchestrator"""
        self.agents[agent.agent_id] = agent
        
    async def execute_workflow(
        self, 
        pattern: WorkflowPattern, 
        agents: List[str], 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute workflow based on pattern"""
        
        if pattern == WorkflowPattern.SEQUENTIAL:
            return await self._execute_sequential(agents, input_data)
        elif pattern == WorkflowPattern.PARALLEL:
            return await self._execute_parallel(agents, input_data)
        elif pattern == WorkflowPattern.HIERARCHICAL:
            return await self._execute_hierarchical(agents, input_data)
        elif pattern == WorkflowPattern.CONSENSUS:
            return await self._execute_consensus(agents, input_data)
        elif pattern == WorkflowPattern.PIPELINE:
            return await self._execute_pipeline(agents, input_data)
        else:
            raise ValueError(f"Unknown workflow pattern: {pattern}")
    
    async def _execute_sequential(
        self, 
        agent_ids: List[str], 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents sequentially"""
        current_data = input_data
        results = []
        
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if not agent:
                continue
                
            result = await agent.process(current_data)
            results.append(result)
            
            # Pass output to next agent
            current_data = {
                "previous_result": result,
                "original_input": input_data,
                "shared_state": self.shared_state
            }
        
        return {
            "pattern": "sequential",
            "results": results,
            "final_output": results[-1] if results else None
        }
    
    async def _execute_parallel(
        self, 
        agent_ids: List[str], 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents in parallel"""
        tasks = []
        
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if agent:
                tasks.append(agent.process(input_data))
        
        results = await asyncio.gather(*tasks)
        
        return {
            "pattern": "parallel",
            "results": results,
            "aggregated": self._aggregate_parallel_results(results)
        }
    
    async def _execute_hierarchical(
        self, 
        agent_ids: List[str], 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents in hierarchical structure"""
        # First agent is coordinator
        coordinator_id = agent_ids[0]
        coordinator = self.agents.get(coordinator_id)
        
        if isinstance(coordinator, CoordinatorAgent):
            # Register sub-agents
            for agent_id in agent_ids[1:]:
                agent = self.agents.get(agent_id)
                if agent:
                    coordinator.register_agent(agent)
            
            # Execute coordination
            result = await coordinator.coordinate_task(input_data)
            return {
                "pattern": "hierarchical",
                "coordinator": coordinator_id,
                "result": result
            }
        else:
            # Fallback to sequential
            return await self._execute_sequential(agent_ids, input_data)
    
    async def _execute_consensus(
        self, 
        agent_ids: List[str], 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents and reach consensus"""
        # Get all agent responses
        results = await self._execute_parallel(agent_ids, input_data)
        
        # Implement voting or consensus mechanism
        consensus_data = {
            "all_results": results["results"],
            "votes": {},
            "consensus": None
        }
        
        # Simple majority voting (can be enhanced)
        for i, result in enumerate(results["results"]):
            vote = result.get("response", "")
            consensus_data["votes"][agent_ids[i]] = vote
        
        # Determine consensus (simplified)
        consensus_data["consensus"] = max(
            consensus_data["votes"].values(), 
            key=list(consensus_data["votes"].values()).count
        )
        
        return {
            "pattern": "consensus",
            "consensus_data": consensus_data
        }
    
    async def _execute_pipeline(
        self, 
        agent_ids: List[str], 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents in pipeline with transformations"""
        current_data = input_data
        pipeline_stages = []
        
        for i, agent_id in enumerate(agent_ids):
            agent = self.agents.get(agent_id)
            if not agent:
                continue
            
            # Process with transformation
            stage_input = self._transform_for_stage(current_data, i)
            result = await agent.process(stage_input)
            
            pipeline_stages.append({
                "stage": i,
                "agent": agent_id,
                "input": stage_input,
                "output": result
            })
            
            # Transform output for next stage
            current_data = self._transform_output(result, i)
        
        return {
            "pattern": "pipeline",
            "stages": pipeline_stages,
            "final_output": current_data
        }
    
    def _aggregate_parallel_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from parallel execution"""
        return {
            "count": len(results),
            "responses": [r.get("response", "") for r in results],
            "combined_state": self._merge_states([r.get("state", {}) for r in results])
        }
    
    def _merge_states(self, states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple agent states"""
        merged = {}
        for state in states:
            merged.update(state)
        return merged
    
    def _transform_for_stage(self, data: Dict[str, Any], stage: int) -> Dict[str, Any]:
        """Transform data for pipeline stage"""
        return {
            "stage_number": stage,
            "data": data,
            "shared_state": self.shared_state
        }
    
    def _transform_output(self, result: Dict[str, Any], stage: int) -> Dict[str, Any]:
        """Transform output for next pipeline stage"""
        return {
            "previous_stage": stage,
            "result": result.get("response", ""),
            "accumulated_state": result.get("state", {})
        }
    
    def update_shared_state(self, key: str, value: Any):
        """Update shared state accessible to all agents"""
        self.shared_state[key] = value
    
    def get_shared_state(self) -> Dict[str, Any]:
        """Get current shared state"""
        return self.shared_state.copy()