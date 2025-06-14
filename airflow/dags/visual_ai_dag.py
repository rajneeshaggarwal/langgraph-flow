from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from langfuse.callback import CallbackHandler
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
import os
import json
from typing import Dict, Any

# Initialize LangFuse handler
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

default_args = {
    'owner': 'visual-ai-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def execute_langgraph_agent(**context):
    """Execute LangGraph agent within Airflow task with full observability"""
    
    # Create deterministic trace ID from Airflow context
    dag_run_id = context['dag_run'].run_id
    task_id = context['task_instance'].task_id
    
    # Get input from Airflow context
    input_data = context['dag_run'].conf.get('input_data', {})
    
    # Initialize LangGraph agent
    from langgraph_flow.agents import create_visual_ai_agent
    
    agent = create_visual_ai_agent(
        model="gpt-4",
        tools=get_visual_ai_tools(),
        prompt="You are a Visual AI assistant specialized in workflow orchestration"
    )
    
    # Execute agent with LangFuse tracing
    result = agent.invoke(
        {"messages": [{"role": "user", "content": input_data.get('query', '')}]},
        config={
            "callbacks": [langfuse_handler],
            "metadata": {
                "langfuse_session_id": f"dag-{dag_run_id}",
                "langfuse_user_id": "visual-ai-system",
                "dag_run_id": dag_run_id,
                "task_id": task_id
            }
        }
    )
    
    # Store results
    store_workflow_results(context, result)
    
    return result

def get_visual_ai_tools():
    """Get tools for Visual AI agent"""
    from langgraph_flow.tools import (
        ImageAnalysisTool,
        DataProcessingTool,
        WebSearchTool,
        FileProcessingTool
    )
    
    return [
        ImageAnalysisTool(),
        DataProcessingTool(),
        WebSearchTool(),
        FileProcessingTool()
    ]

def store_workflow_results(context: Dict[str, Any], result: Dict[str, Any]):
    """Store workflow execution results in database"""
    import psycopg2
    from psycopg2.extras import Json
    
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "airflow"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow")
    )
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO visual_ai.workflow_executions 
                (dag_id, dag_run_id, user_id, input_data, output_data, status, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                context['dag'].dag_id,
                context['dag_run'].run_id,
                context['dag_run'].conf.get('user_id', 'system'),
                Json(context['dag_run'].conf.get('input_data', {})),
                Json(result),
                'success',
                Json({
                    'task_id': context['task_instance'].task_id,
                    'execution_date': context['execution_date'].isoformat()
                })
            ))
            conn.commit()
    finally:
        conn.close()

def prepare_data(**context):
    """Prepare data for processing"""
    dag_run_conf = context['dag_run'].conf
    
    # Validate input data
    if not dag_run_conf.get('input_data'):
        raise ValueError("No input data provided")
    
    # Prepare data structure
    prepared_data = {
        'query': dag_run_conf['input_data'].get('query', ''),
        'files': dag_run_conf['input_data'].get('files', []),
        'parameters': dag_run_conf['input_data'].get('parameters', {}),
        'user_id': dag_run_conf.get('user_id', 'anonymous')
    }
    
    return prepared_data

def validate_results(**context):
    """Validate the results from LangGraph execution"""
    ti = context['task_instance']
    result = ti.xcom_pull(task_ids='execute_agent')
    
    if not result:
        raise ValueError("No results from agent execution")
    
    # Add validation logic here
    if 'error' in result:
        raise Exception(f"Agent execution failed: {result['error']}")
    
    return True

# Create the DAG
dag = DAG(
    'visual_ai_workflow',
    default_args=default_args,
    description='Visual AI workflow with LangGraph integration',
    schedule_interval=None,
    catchup=False,
    tags=['visual-ai', 'langgraph', 'production']
)

# Define tasks
prepare_task = PythonOperator(
    task_id='prepare_data',
    python_callable=prepare_data,
    dag=dag
)

execute_task = PythonOperator(
    task_id='execute_agent',
    python_callable=execute_langgraph_agent,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_results',
    python_callable=validate_results,
    dag=dag
)

# Set task dependencies
prepare_task >> execute_task >> validate_task