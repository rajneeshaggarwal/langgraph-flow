from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_node: str
    context: Dict[str, Any]

class LangGraphEngine:
    def __init__(self):
        self.graphs = {}
    
    def build_graph_from_flow(self, nodes: List[Dict], edges: List[Dict]) -> StateGraph:
        """Convert React Flow structure to LangGraph"""
        workflow = StateGraph(AgentState)
        
        # Build node map
        node_map = {node['id']: node for node in nodes}
        
        # Add nodes to graph
        for node in nodes:
            node_id = node['id']
            node_type = node['data']['type']
            
            if node_type == 'agent':
                workflow.add_node(node_id, self._create_agent_node(node['data']))
            elif node_type == 'tool':
                workflow.add_node(node_id, self._create_tool_node(node['data']))
            elif node_type == 'conditional':
                workflow.add_node(node_id, self._create_conditional_node(node['data']))
        
        # Add edges
        for edge in edges:
            if edge.get('data', {}).get('condition'):
                # Conditional edge
                workflow.add_conditional_edges(
                    edge['source'],
                    self._create_condition_function(edge['data']['condition']),
                    {
                        'true': edge['target'],
                        'false': END
                    }
                )
            else:
                # Regular edge
                workflow.add_edge(edge['source'], edge['target'])
        
        # Set entry point (find node with no incoming edges)
        entry_nodes = self._find_entry_nodes(nodes, edges)
        if entry_nodes:
            workflow.set_entry_point(entry_nodes[0]['id'])
        
        return workflow.compile()
    
    def _create_agent_node(self, node_data: Dict) -> callable:
        """Create an agent node function"""
        def agent_node(state: AgentState) -> Dict[str, Any]:
            # Placeholder for agent logic
            # In real implementation, this would initialize the appropriate LLM
            messages = state.get('messages', [])
            context = state.get('context', {})
            
            # Process with agent
            response = f"Agent {node_data.get('label', 'Unknown')} processed"
            
            return {
                'messages': messages + [response],
                'current_node': node_data.get('label', 'Unknown')
            }
        
        return agent_node
    
    def _create_tool_node(self, node_data: Dict) -> callable:
        """Create a tool node function"""
        def tool_node(state: AgentState) -> Dict[str, Any]:
            # Placeholder for tool execution
            tool_name = node_data.get('config', {}).get('tool_name', 'unknown')
            
            return {
                'messages': state['messages'] + [f"Tool {tool_name} executed"],
                'current_node': tool_name
            }
        
        return tool_node
    
    def _create_conditional_node(self, node_data: Dict) -> callable:
        """Create a conditional node function"""
        def conditional_node(state: AgentState) -> Dict[str, Any]:
            # Placeholder for conditional logic
            return state
        
        return conditional_node
    
    def _create_condition_function(self, condition: str) -> callable:
        """Create a condition checker function"""
        def check_condition(state: AgentState) -> str:
            # Placeholder - evaluate condition
            # In real implementation, this would parse and evaluate the condition
            return 'true'
        
        return check_condition
    
    def _find_entry_nodes(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Find nodes with no incoming edges"""
        targets = {edge['target'] for edge in edges}
        return [node for node in nodes if node['id'] not in targets]