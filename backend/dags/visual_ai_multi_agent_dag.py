from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
from langfuse import observe, get_client
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List, TypedDict
import os
import json

class WorkflowState(TypedDict):
    """State for the multi-agent workflow"""
    messages: List[Dict[str, str]]
    image_analysis: Dict[str, Any]
    text_extraction: Dict[str, Any]
    synthesis: Dict[str, Any]
    final_output: str

def prepare_data(**context):
    """Prepare input data for multi-agent processing"""
    
    input_data = context['dag_run'].conf.get('input_data', {})
    
    # Validate and prepare data
    prepared_data = {
        "image_url": input_data.get("image_url"),
        "text_content": input_data.get("text_content"),
        "user_requirements": input_data.get("requirements", {}),
        "workflow_id": context['dag_run'].run_id
    }
    
    return prepared_data

@observe()
def image_analysis_agent(**context):
    """Specialized agent for image analysis"""
    
    langfuse = get_client()
    langfuse.update_current_trace(
        name="image-analysis-agent",
        session_id=f"dag-{context['dag_run'].run_id}",
        tags=["visual-ai", "image-analysis"]
    )
    
    # Initialize LLM with vision capabilities
    llm = ChatOpenAI(
        model="gpt-4-vision-preview",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    agent = create_react_agent(
        model=llm,
        tools=[],  # Add image analysis tools here
        prompt="You are an expert at analyzing visual content"
    )
    
    input_data = context['task_instance'].xcom_pull(task_ids='prepare_data')
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"Analyze this image: {input_data['image_url']}"}]},
        config={"callbacks": [langfuse_handler]}
    )
    
    return result

@observe()
def text_extraction_agent(**context):
    """Agent for text extraction and processing"""
    
    langfuse = get_client()
    langfuse.update_current_trace(
        name="text-extraction-agent",
        session_id=f"dag-{context['dag_run'].run_id}",
        tags=["visual-ai", "text-extraction"]
    )
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    agent = create_react_agent(
        model=llm,
        tools=[],  # Add text processing tools here
        prompt="You are an expert at extracting and analyzing text content"
    )
    
    input_data = context['task_instance'].xcom_pull(task_ids='prepare_data')
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"Extract text from: {input_data['text_content']}"}]},
        config={"callbacks": [langfuse_handler]}
    )
    
    return result

@observe()
def synthesis_agent(**context):
    """Agent that synthesizes results from multiple analysis agents"""
    
    # Pull results from all upstream agents
    image_results = context['task_instance'].xcom_pull(task_ids='agents.image_analysis')
    text_results = context['task_instance'].xcom_pull(task_ids='agents.text_extraction')
    
    # Create synthesis workflow using StateGraph
    synthesis_graph = StateGraph(WorkflowState)
    
    def aggregate_results(state: WorkflowState) -> WorkflowState:
        """Aggregate results from different agents"""
        state["synthesis"] = {
            "image_insights": state["image_analysis"],
            "text_insights": state["text_extraction"],
            "combined_analysis": "Aggregated insights here"
        }
        return state
    
    def generate_final_report(state: WorkflowState) -> WorkflowState:
        """Generate final report based on aggregated results"""
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        
        prompt = f"""
        Based on the following analysis results, create a comprehensive report:
        
        Image Analysis: {json.dumps(state["image_analysis"], indent=2)}
        Text Analysis: {json.dumps(state["text_extraction"], indent=2)}
        
        Create a synthesis that combines these insights.
        """
        
        response = llm.invoke(prompt)
        state["final_output"] = response.content
        return state
    
    # Define synthesis workflow
    synthesis_graph.add_node("aggregate", aggregate_results)
    synthesis_graph.add_node("generate_report", generate_final_report)
    synthesis_graph.add_edge("aggregate", "generate_report")
    synthesis_graph.add_edge("generate_report", END)
    
    workflow = synthesis_graph.compile()
    
    # Execute synthesis workflow
    result = workflow.invoke({
        "messages": [],
        "image_analysis": image_results,
        "text_extraction": text_results,
        "synthesis": {},
        "final_output": ""
    })
    
    return result

def store_results(**context):
    """Store final results in database"""
    
    synthesis_result = context['task_instance'].xcom_pull(task_ids='synthesis')
    
    # Store in your database
    # This is where you'd integrate with your existing storage solution
    print(f"Storing results: {json.dumps(synthesis_result, indent=2)}")
    
    return {"status": "stored", "workflow_id": context['dag_run'].run_id}

# Define default arguments
default_args = {
    'owner': 'visual-ai-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': handle_task_failure
}

# Define the DAG
dag = DAG(
    'visual_ai_multi_agent_pipeline',
    default_args=default_args,
    description='Multi-agent Visual AI processing pipeline',
    schedule_interval=None,
    catchup=False,
    tags=['visual-ai', 'multi-agent', 'production']
)

# Prepare data task
prepare_data_task = PythonOperator(
    task_id='prepare_data',
    python_callable=prepare_data,
    dag=dag
)

# Task groups for better organization
with TaskGroup("agents", tooltip="Parallel agent execution", dag=dag) as agents:
    image_task = PythonOperator(
        task_id='image_analysis',
        python_callable=image_analysis_agent
    )
    
    text_task = PythonOperator(
        task_id='text_extraction',
        python_callable=text_extraction_agent
    )

# Synthesis task
synthesis_task = PythonOperator(
    task_id='synthesis',
    python_callable=synthesis_agent,
    dag=dag
)

# Store results task
store_results_task = PythonOperator(
    task_id='store_results',
    python_callable=store_results,
    dag=dag
)

# Set task dependencies
prepare_data_task >> agents >> synthesis_task >> store_results_task