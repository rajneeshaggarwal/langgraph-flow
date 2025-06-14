from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from langfuse.callback import CallbackHandler
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import os
import json
from typing import Dict, Any

# Initialize LangFuse handler
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

def execute_langgraph_agent(**context):
    """Execute LangGraph agent within Airflow task with full observability"""
    
    # Create deterministic trace ID from Airflow context
    dag_run_id = context['dag_run'].run_id
    task_id = context['task_instance'].task_id
    
    # Initialize LLM
    llm = ChatOpenAI(
        temperature=0.7,
        model="gpt-4",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize LangGraph agent
    agent = create_react_agent(
        model=llm,
        tools=[],  # Add your tools here
        prompt="You are a Visual AI assistant"
    )
    
    # Get input from Airflow context
    input_data = context['dag_run'].conf.get('input_data', {})
    
    # Execute agent with LangFuse tracing
    result = agent.invoke(
        {"messages": [{"role": "user", "content": input_data.get('query', 'Hello')}]},
        config={
            "callbacks": [langfuse_handler],
            "metadata": {
                "langfuse_session_id": f"dag-{dag_run_id}",
                "langfuse_user_id": "visual-ai-system",
                "task_id": task_id
            }
        }
    )
    
    # Push result to XCom for downstream tasks
    context['task_instance'].xcom_push(key='agent_result', value=result)
    
    return result

def process_results(**context):
    """Process results from LangGraph agent"""
    
    # Pull results from upstream task
    agent_result = context['task_instance'].xcom_pull(
        task_ids='execute_agent',
        key='agent_result'
    )
    
    # Process the results (add your logic here)
    processed_data = {
        "status": "processed",
        "original_result": agent_result,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Store in database or send to external system
    print(f"Processed results: {json.dumps(processed_data, indent=2)}")
    
    return processed_data

def handle_task_failure(context):
    """Custom failure callback"""
    
    print(f"Task {context['task_instance'].task_id} failed!")
    # Add your error handling logic here (e.g., send alerts, log to monitoring system)

# Define default arguments
default_args = {
    'owner': 'visual-ai-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': handle_task_failure
}

# Define the DAG
dag = DAG(
    'visual_ai_workflow',
    default_args=default_args,
    description='Visual AI workflow with LangGraph integration',
    schedule_interval=None,  # Triggered manually or via API
    catchup=False,
    tags=['visual-ai', 'langgraph', 'production']
)

# Define tasks
execute_agent_task = PythonOperator(
    task_id='execute_agent',
    python_callable=execute_langgraph_agent,
    dag=dag
)

process_results_task = PythonOperator(
    task_id='process_results',
    python_callable=process_results,
    dag=dag
)

# Set task dependencies
execute_agent_task >> process_results_task