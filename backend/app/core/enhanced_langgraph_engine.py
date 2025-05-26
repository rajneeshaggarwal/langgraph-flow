from typing import Dict, Any, List, TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
import operator
from .agent_types import BaseAgent, LLMAgent, CoordinatorAgent, AgentRole
from .workflow_patterns import WorkflowOrchestrator, WorkflowPattern

class EnhancedAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_node: str
    context: Dict[str, Any]
    agents: Dict[str, BaseAgent]
    shared_state: Dict[str, Any]
    execution_pattern: WorkflowPattern

class EnhancedLangGraphEngine:
    def __init__(self):
        self.orchestrator = WorkflowOrchestrator()
    
    def build_graph_from_flow(self, nodes: List[Dict], edges: List[Dict]) -> StateGraph:
        """Convert React Flow structure to enhanced LangGraph"""
        workflow = StateGraph(EnhancedAgentState)
        
        # Initialize agents from nodes
        agents = self._initialize_agents(nodes)
        
        # Register agents with orchestrator
        for agent in agents.values():
            self.orchestrator.register_agent(agent)
        
        # Analyze workflow pattern
        pattern = self._detect_workflow_pattern(nodes, edges)
        
        # Build graph based on pattern
        if pattern == WorkflowPattern.HIERARCHICAL:
            return self._build_hierarchical_graph(workflow, nodes, edges, agents)
        elif pattern == WorkflowPattern.PARALLEL:
            return self._build_parallel_graph(workflow, nodes, edges, agents)
        else:
            return self._build_sequential_graph(workflow, nodes, edges, agents)
    
    def _initialize_agents(self, nodes: List[Dict]) -> Dict[str, BaseAgent]:
        """Initialize agents from node configurations"""
        agents = {}
        
        for node in nodes:
            node_id = node['id']
            node_type = node['data']['type']
            config = node['data'].get('config', {})
            
            if node_type == 'agent':
                role = AgentRole(config.get('role', 'executor'))
                
                if role == AgentRole.COORDINATOR:
                    agent = CoordinatorAgent(node_id, config)
                else:
                    agent = LLMAgent(node_id, role, config)
                
                agents[node_id] = agent
        
        return agents
    
    def _detect_workflow_pattern(self, nodes: List[Dict], edges: List[Dict]) -> WorkflowPattern:
        """Detect workflow pattern from graph structure"""
        # Check for coordinator node
        has_coordinator = any(
            node['data'].get('config', {}).get('role') == 'coordinator'
            for node in nodes
        )
        
        if has_coordinator:
            return WorkflowPattern.HIERARCHICAL
        
        # Check for parallel branches
        node_in_degree = {node['id']: 0 for node in nodes}
        node_out_degree = {node['id']: 0 for node in nodes}
        
        for edge in edges:
            node_out_degree[edge['source']] = node_out_degree.get(edge['source'], 0) + 1
            node_in_degree[edge['target']] = node_in_degree.get(edge['target'], 0) + 1
        
        # Multiple outputs from single node indicates parallel
        if any(degree > 1 for degree in node_out_degree.values()):
            return WorkflowPattern.PARALLEL
        
        return WorkflowPattern.SEQUENTIAL
    
    def _build_hierarchical_graph(
        self, 
        workflow: StateGraph, 
        nodes: List[Dict], 
        edges: List[Dict],
        agents: Dict[str, BaseAgent]
    ) -> StateGraph:
        """Build hierarchical workflow graph"""
        # Find coordinator
        coordinator_node = next(
            (node for node in nodes 
             if node['data'].get('config', {}).get('role') == 'coordinator'),
            None
        )
        
        if coordinator_node:
            coordinator_id = coordinator_node['id']
            coordinator = agents[coordinator_id]
            
            # Register sub-agents with coordinator
            for edge in edges:
                if edge['source'] == coordinator_id:
                    sub_agent = agents.get(edge['target'])
                    if sub_agent and isinstance(coordinator, CoordinatorAgent):
                        coordinator.register_agent(sub_agent)
            
            # Create coordinator node
            async def coordinator_node_func(state: EnhancedAgentState) -> Dict[str, Any]:
                result = await coordinator.coordinate_task(state['context'])
                return {
                    'messages': state['messages'] + [str(result)],
                    'current_node': coordinator_id,
                    'shared_state': result.get('state', {})
                }
            
            workflow.add_node(coordinator_id, coordinator_node_func)
            workflow.set_entry_point(coordinator_id)
            workflow.add_edge(coordinator_id, END)
        
        return workflow.compile()
    
    def _build_parallel_graph(
        self, 
        workflow: StateGraph, 
        nodes: List[Dict], 
        edges: List[Dict],
        agents: Dict[str, BaseAgent]
    ) -> StateGraph:
        """Build parallel workflow graph"""
        # Identify parallel branches
        branch_points = []
        merge_points = []
        
        for node_id, out_degree in self._calculate_out_degrees(edges).items():
            if out_degree > 1:
                branch_points.append(node_id)
        
        for node_id, in_degree in self._calculate_in_degrees(edges).items():
            if in_degree > 1:
                merge_points.append(node_id)
        
        # Build parallel execution nodes
        for node in nodes:
            node_id = node['id']
            
            async def create_parallel_node(state: EnhancedAgentState, nid=node_id) -> Dict[str, Any]:
                # Execute parallel pattern
                parallel_agents = self._get_parallel_agents(nid, edges)
                result = await self.orchestrator.execute_workflow(
                    WorkflowPattern.PARALLEL,
                    parallel_agents,
                    state['context']
                )
                
                return {
                    'messages': state['messages'] + [str(result)],
                    'current_node': nid,
                    'shared_state': result.get('aggregated', {})
                }
            
            if node_id in branch_points:
                workflow.add_node(node_id, create_parallel_node)
        
        return workflow.compile()
    
    def _build_sequential_graph(
        self, 
        workflow: StateGraph, 
        nodes: List[Dict], 
        edges: List[Dict],
        agents: Dict[str, BaseAgent]
    ) -> StateGraph:
        """Build sequential workflow graph"""
        # Standard sequential processing
        for node in nodes:
            node_id = node['id']
            agent = agents.get(node_id)
            
            if agent:
                async def create_agent_node(state: EnhancedAgentState, a=agent) -> Dict[str, Any]:
                    result = await a.process(state['context'])
                    return {
                        'messages': state['messages'] + [str(result)],
                        'current_node': a.agent_id,
                        'context': {**state['context'], 'last_result': result}
                    }
                
                workflow.add_node(node_id, create_agent_node)
        
        # Add edges
        for edge in edges:
            workflow.add_edge(edge['source'], edge['target'])
        
        # Set entry point
        entry_node = self._find_entry_node(nodes, edges)
        if entry_node:
            workflow.set_entry_point(entry_node['id'])
        
        return workflow.compile()
    
    def _calculate_out_degrees(self, edges: List[Dict]) -> Dict[str, int]:
        """Calculate out-degree for each node"""
        out_degrees = {}
        for edge in edges:
            out_degrees[edge['source']] = out_degrees.get(edge['source'], 0) + 1
        return out_degrees
    
    def _calculate_in_degrees(self, edges: List[Dict]) -> Dict[str, int]:
        """Calculate in-degree for each node"""
        in_degrees = {}
        for edge in edges:
            in_degrees[edge['target']] = in_degrees.get(edge['target'], 0) + 1
        return in_degrees
    
    def _get_parallel_agents(self, branch_node: str, edges: List[Dict]) -> List[str]:
        """Get agents that execute in parallel from branch node"""
        return [edge['target'] for edge in edges if edge['source'] == branch_node]
    
    def _find_entry_node(self, nodes: List[Dict], edges: List[Dict]) -> Optional[Dict]:
        """Find node with no incoming edges"""
        targets = {edge['target'] for edge in edges}
        for node in nodes:
            if node['id'] not in targets:
                return node
        return nodes[0] if nodes else None