from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
from langfuse import observe, get_client
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List

default_args = {
    'owner': 'visual-ai-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

@observe()
def image_analysis_agent(**context):
    """Specialized agent for image analysis"""
    
    langfuse = get_client()
    langfuse.update_current_trace(
        name="image-analysis-agent",
        session_id=f"dag-{context['dag_run'].run_id}",
        tags=["visual-ai", "image-analysis"]
    )
    
    from langgraph_flow.agents.vision import create_vision_agent
    
    agent = create_vision_agent()
    
    input_data = context['task_instance'].xcom_pull(task_ids='prepare_data')
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": input_data.get('image_url', '')}]},
        config={"callbacks": [langfuse_handler]}
    )
    
    # Store results
    store_agent_results(context, result, "image_analysis")
    
    return result

@observe()
def text_extraction_agent(**context):
    """Agent for text extraction from documents"""
    
    langfuse = get_client()
    langfuse.update_current_trace(
        name="text-extraction-agent",
        session_id=f"dag-{context['dag_run'].run_id}",
        tags=["visual-ai", "text-extraction"]
    )
    
    from langgraph_flow.agents.text import create_text_extraction_agent
    
    agent = create_text_extraction_agent()
    
    input_data = context['task_instance'].xcom_pull(task_ids='prepare_data')
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"Extract text from: {input_data.get('document_url', '')}"}]},
        config={"callbacks": [langfuse_handler]}
    )
    
    store_agent_results(context, result, "text_extraction")
    
    return result

@observe()
def synthesis_agent(**context):
    """Agent that synthesizes results from multiple analysis agents"""
    
    # Pull results from all upstream agents
    image_results = context['task_instance'].xcom_pull(task_ids='agents.image_analysis')
    text_results = context['task_instance'].xcom_pull(task_ids='agents.text_extraction')
    
    from langgraph_flow.agents.synthesis import create_synthesis_agent
    
    synthesis_graph = create_synthesis_agent()
    
    result = synthesis_graph.invoke({
        "image_analysis": image_results,
        "text_extraction": text_results,
        "user_requirements": context['dag_run'].conf.get('requirements', {})
    })
    
    return result

def store_agent_results(context: Dict[str, Any], result: Dict[str, Any], agent_type: str):
    """Store individual agent results"""
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
            # Get workflow execution ID
            cur.execute("""
                SELECT id FROM visual_ai.workflow_executions 
                WHERE dag_run_id = %s
            """, (context['dag_run'].run_id,))
            
            workflow_execution_id = cur.fetchone()
            if workflow_execution_id:
                workflow_execution_id = workflow_execution_id[0]
            
            # Store agent trace
            cur.execute("""
                INSERT INTO visual_ai.agent_traces 
                (workflow_execution_id, agent_name, input_tokens, output_tokens, 
                 cost, duration_ms, success, langfuse_observation_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                workflow_execution_id,
                agent_type,
                result.get('usage', {}).get('input_tokens', 0),
                result.get('usage', {}).get('output_tokens', 0),
                result.get('usage', {}).get('total_cost', 0.0),
                result.get('duration_ms', 0),
                result.get('success', True),
                result.get('observation_id', '')
            ))
            conn.commit()
    finally:
        conn.close()

def prepare_multi_agent_data(**context):
    """Prepare data for multi-agent processing"""
    dag_run_conf = context['dag_run'].conf
    
    # Extract different data types for different agents
    prepared_data = {
        'image_url': dag_run_conf.get('input_data', {}).get('image_url', ''),
        'document_url': dag_run_conf.get('input_data', {}).get('document_url', ''),
        'requirements': dag_run_conf.get('requirements', {}),
        'user_id': dag_run_conf.get('user_id', 'anonymous')
    }
    
    return prepared_data

def store_final_results(**context):
    """Store the final synthesized results"""
    synthesis_results = context['task_instance'].xcom_pull(task_ids='synthesis')
    
    # Update workflow execution with final results
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
                UPDATE visual_ai.workflow_executions 
                SET output_data = %s, status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE dag_run_id = %s
            """, (
                Json(synthesis_results),
                'completed',
                context['dag_run'].run_id
            ))
            conn.commit()
    finally:
        conn.close()
    
    return synthesis_results

# Create the DAG
dag = DAG(
    'visual_ai_multi_agent_pipeline',
    default_args=default_args,
    description='Multi-agent Visual AI processing pipeline',
    schedule_interval=None,
    catchup=False,
    tags=['visual-ai', 'multi-agent', 'production']
)

# Prepare data task
prepare_data = PythonOperator(
    task_id='prepare_data',
    python_callable=prepare_multi_agent_data,
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
synthesis = PythonOperator(
    task_id='synthesis',
    python_callable=synthesis_agent,
    dag=dag
)

# Store results task
store_results = PythonOperator(
    task_id='store_results',
    python_callable=store_final_results,
    dag=dag
)

# Set dependencies
prepare_data >> agents >> synthesis >> store_results