"""
Integration module for running LangGraph Flow agents within Apache Airflow
"""

from typing import Dict, Any, List, Optional
from langfuse.callback import CallbackHandler
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
import os
import logging

logger = logging.getLogger(__name__)

class AirflowLangGraphIntegration:
    """
    Integration class that bridges LangGraph Flow with Apache Airflow
    """
    
    def __init__(self, langfuse_config: Optional[Dict[str, str]] = None):
        """
        Initialize the integration with optional LangFuse configuration
        
        Args:
            langfuse_config: Optional configuration for LangFuse
        """
        self.langfuse_config = langfuse_config or {
            'secret_key': os.getenv("LANGFUSE_SECRET_KEY"),
            'public_key': os.getenv("LANGFUSE_PUBLIC_KEY"),
            'host': os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        }
        
        self.langfuse_handler = CallbackHandler(
            secret_key=self.langfuse_config['secret_key'],
            public_key=self.langfuse_config['public_key'],
            host=self.langfuse_config['host']
        )
    
    def create_visual_ai_agent(
        self,
        model: str = "gpt-4",
        tools: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None,
        airflow_context: Optional[Dict[str, Any]] = None
    ):
        """
        Create a Visual AI agent configured for Airflow execution
        
        Args:
            model: LLM model to use
            tools: List of tools for the agent
            system_prompt: System prompt for the agent
            airflow_context: Airflow execution context
            
        Returns:
            Configured agent ready for execution
        """
        from langgraph_flow.tools import (
            ImageAnalysisTool,
            DataProcessingTool,
            WebSearchTool,
            FileProcessingTool
        )
        
        # Default tools if none provided
        if tools is None:
            tools = [
                ImageAnalysisTool(),
                DataProcessingTool(),
                WebSearchTool(),
                FileProcessingTool()
            ]
        
        # Default system prompt
        if system_prompt is None:
            system_prompt = """You are a Visual AI assistant specialized in workflow orchestration.
            You help users analyze images, process data, and create comprehensive reports.
            Always provide detailed, actionable insights."""
        
        # Create agent with Airflow-specific configuration
        agent = create_react_agent(
            model=model,
            tools=tools,
            prompt=system_prompt
        )
        
        # Add Airflow context to agent metadata if provided
        if airflow_context:
            agent._metadata = {
                'dag_id': airflow_context.get('dag_id'),
                'dag_run_id': airflow_context.get('dag_run_id'),
                'task_id': airflow_context.get('task_id'),
                'execution_date': airflow_context.get('execution_date')
            }
        
        return agent
    
    def execute_agent_in_airflow(
        self,
        agent,
        input_data: Dict[str, Any],
        airflow_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a LangGraph agent within Airflow context
        
        Args:
            agent: The LangGraph agent to execute
            input_data: Input data for the agent
            airflow_context: Airflow execution context
            
        Returns:
            Agent execution results
        """
        # Prepare trace metadata
        trace_metadata = {
            'dag_id': airflow_context['dag'].dag_id,
            'dag_run_id': airflow_context['dag_run'].run_id,
            'task_id': airflow_context['task_instance'].task_id,
            'execution_date': airflow_context['execution_date'].isoformat(),
            'user_id': airflow_context['dag_run'].conf.get('user_id', 'system')
        }
        
        # Update LangFuse trace
        self.langfuse_handler.trace.update(
            name=f"airflow-{trace_metadata['dag_id']}-{trace_metadata['task_id']}",
            session_id=trace_metadata['dag_run_id'],
            user_id=trace_metadata['user_id'],
            metadata=trace_metadata
        )
        
        try:
            # Execute agent
            result = agent.invoke(
                input_data,
                config={
                    'callbacks': [self.langfuse_handler],
                    'metadata': trace_metadata,
                    'run_name': f"{trace_metadata['dag_id']}.{trace_metadata['task_id']}"
                }
            )
            
            # Log execution success
            logger.info(f"Agent execution successful for {trace_metadata['task_id']}")
            
            # Add execution metadata to result
            result['_execution_metadata'] = {
                'success': True,
                'dag_run_id': trace_metadata['dag_run_id'],
                'langfuse_trace_url': self.langfuse_handler.get_trace_url()
            }
            
            return result
            
        except Exception as e:
            # Log error with context
            logger.error(
                f"Agent execution failed for {trace_metadata['task_id']}: {str(e)}",
                exc_info=True
            )
            
            # Create error result
            error_result = {
                'error': str(e),
                'error_type': type(e).__name__,
                '_execution_metadata': {
                    'success': False,
                    'dag_run_id': trace_metadata['dag_run_id'],
                    'langfuse_trace_url': self.langfuse_handler.get_trace_url()
                }
            }
            
            # Score the error in LangFuse
            self.langfuse_handler.score(
                name="execution_error",
                value=1,
                comment=f"Error: {str(e)}"
            )
            
            raise

def create_airflow_compatible_graph(
    nodes: Dict[str, Any],
    edges: List[tuple],
    airflow_context: Optional[Dict[str, Any]] = None
) -> StateGraph:
    """
    Create a LangGraph StateGraph that's compatible with Airflow execution
    
    Args:
        nodes: Dictionary of node names to node functions
        edges: List of edges between nodes
        airflow_context: Optional Airflow context
        
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create state graph
    workflow = StateGraph(dict)
    
    # Add nodes with Airflow context injection
    for node_name, node_func in nodes.items():
        if airflow_context:
            # Wrap node function to include Airflow context
            def wrapped_node(state, func=node_func, ctx=airflow_context):
                state['_airflow_context'] = {
                    'dag_id': ctx.get('dag', {}).get('dag_id'),
                    'dag_run_id': ctx.get('dag_run', {}).get('run_id'),
                    'task_id': ctx.get('task_instance', {}).get('task_id')
                }
                return func(state)
            workflow.add_node(node_name, wrapped_node)
        else:
            workflow.add_node(node_name, node_func)
    
    # Add edges
    for source, target in edges:
        workflow.add_edge(source, target)
    
    # Set entry point (first node)
    if nodes:
        workflow.set_entry_point(list(nodes.keys())[0])
    
    return workflow.compile()

# Helper functions for common Airflow patterns

def get_upstream_results(context: Dict[str, Any], task_ids: List[str]) -> Dict[str, Any]:
    """
    Get results from upstream Airflow tasks
    
    Args:
        context: Airflow context
        task_ids: List of upstream task IDs
        
    Returns:
        Dictionary of task_id to result mapping
    """
    ti = context['task_instance']
    results = {}
    
    for task_id in task_ids:
        result = ti.xcom_pull(task_ids=task_id)
        if result:
            results[task_id] = result
    
    return results

def store_workflow_state(
    context: Dict[str, Any],
    state_key: str,
    state_value: Any
) -> None:
    """
    Store workflow state in Airflow XCom
    
    Args:
        context: Airflow context
        state_key: Key for the state
        state_value: Value to store
    """
    ti = context['task_instance']
    ti.xcom_push(key=state_key, value=state_value)

def create_agent_for_task_type(
    task_type: str,
    airflow_context: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Factory function to create appropriate agent based on task type
    
    Args:
        task_type: Type of task (vision, text, synthesis, etc.)
        airflow_context: Optional Airflow context
        
    Returns:
        Configured agent for the task type
    """
    integration = AirflowLangGraphIntegration()
    
    if task_type == 'vision':
        from langgraph_flow.agents.vision import VisionAgent
        from langgraph_flow.tools import ImageAnalysisTool, ObjectDetectionTool
        
        tools = [ImageAnalysisTool(), ObjectDetectionTool()]
        return integration.create_visual_ai_agent(
            model="gpt-4-vision-preview",
            tools=tools,
            system_prompt="You are specialized in analyzing visual content.",
            airflow_context=airflow_context
        )
    
    elif task_type == 'text':
        from langgraph_flow.agents.text import TextExtractionAgent
        from langgraph_flow.tools import TextExtractionTool, DocumentParsingTool
        
        tools = [TextExtractionTool(), DocumentParsingTool()]
        return integration.create_visual_ai_agent(
            model="gpt-4",
            tools=tools,
            system_prompt="You are specialized in extracting and analyzing text.",
            airflow_context=airflow_context
        )
    
    elif task_type == 'synthesis':
        from langgraph_flow.agents.synthesis import SynthesisAgent
        
        return integration.create_visual_ai_agent(
            model="gpt-4",
            tools=[],  # Synthesis typically doesn't need tools
            system_prompt="You are specialized in synthesizing information from multiple sources.",
            airflow_context=airflow_context
        )
    
    else:
        # Default generic agent
        return integration.create_visual_ai_agent(
            airflow_context=airflow_context
        )

# Example usage in an Airflow task
def example_airflow_task(**context):
    """
    Example of how to use the integration in an Airflow task
    """
    # Create integration
    integration = AirflowLangGraphIntegration()
    
    # Create agent
    agent = integration.create_visual_ai_agent(
        model="gpt-4",
        airflow_context=context
    )
    
    # Get input from DAG configuration
    input_data = context['dag_run'].conf.get('input_data', {})
    
    # Execute agent
    result = integration.execute_agent_in_airflow(
        agent=agent,
        input_data=input_data,
        airflow_context=context
    )
    
    # Store result for downstream tasks
    store_workflow_state(context, 'agent_result', result)
    
    return result