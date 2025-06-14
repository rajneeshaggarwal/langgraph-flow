from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List
from datetime import datetime
import httpx
import os

router = APIRouter(prefix="/workflow-status", tags=["status"])

AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")

class WorkflowStatusUpdate:
    def __init__(self, dag_id: str, dag_run_id: str, state: str, tasks: List[Dict]):
        self.dag_id = dag_id
        self.dag_run_id = dag_run_id
        self.state = state
        self.tasks = tasks
        self.timestamp = datetime.utcnow().isoformat()

async def workflow_event_stream(
    dag_id: str, 
    dag_run_id: str, 
    request: Request
) -> AsyncGenerator[str, None]:
    """Stream workflow status updates via SSE"""
    
    previous_state = None
    previous_task_states = {}
    
    while True:
        # Check if client disconnected
        if await request.is_disconnected():
            break
        
        try:
            # Query Airflow for current status
            async with httpx.AsyncClient() as client:
                # Get DAG run status
                dag_response = await client.get(
                    f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}",
                    auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
                    timeout=10.0
                )
                
                if dag_response.status_code == 200:
                    dag_run = dag_response.json()
                    
                    # Get task instances for this DAG run
                    tasks_response = await client.get(
                        f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
                        auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
                        timeout=10.0
                    )
                    
                    tasks = []
                    if tasks_response.status_code == 200:
                        task_instances = tasks_response.json()["task_instances"]
                        
                        for task in task_instances:
                            task_data = {
                                "task_id": task["task_id"],
                                "state": task["state"],
                                "start_date": task["start_date"],
                                "end_date": task.get("end_date"),
                                "duration": task.get("duration"),
                                "try_number": task.get("try_number", 1)
                            }
                            tasks.append(task_data)
                            
                            # Check if task state changed
                            task_key = task["task_id"]
                            if (task_key not in previous_task_states or 
                                previous_task_states[task_key] != task["state"]):
                                
                                # Send task update event
                                task_event = {
                                    "event": "task_update",
                                    "data": {
                                        "dag_run_id": dag_run_id,
                                        "task": task_data
                                    }
                                }
                                yield f"event: task_update\ndata: {json.dumps(task_event['data'])}\n\n"
                                previous_task_states[task_key] = task["state"]
                    
                    # Create status update
                    status_update = {
                        "dag_run_id": dag_run_id,
                        "state": dag_run["state"],
                        "start_date": dag_run["start_date"],
                        "end_date": dag_run.get("end_date"),
                        "execution_date": dag_run["execution_date"],
                        "tasks": tasks,
                        "progress": calculate_progress(tasks)
                    }
                    
                    # Send update if state changed
                    if previous_state != dag_run["state"]:
                        yield f"event: workflow_update\ndata: {json.dumps(status_update)}\n\n"
                        previous_state = dag_run["state"]
                    
                    # If workflow completed, send final event and close
                    if dag_run["state"] in ["success", "failed", "skipped"]:
                        final_event = {
                            **status_update,
                            "final": True,
                            "duration": calculate_duration(
                                dag_run["start_date"], 
                                dag_run.get("end_date")
                            )
                        }
                        yield f"event: workflow_complete\ndata: {json.dumps(final_event)}\n\n"
                        break
                
                else:
                    # Send error event
                    error_event = {
                        "error": f"Failed to fetch workflow status: {dag_response.status_code}"
                    }
                    yield f"event: error\ndata: {json.dumps(error_event)}\n\n"
                    break
                    
        except Exception as e:
            # Send error event
            error_event = {"error": str(e)}
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"
            break
        
        # Poll every 2 seconds
        await asyncio.sleep(2)
    
    # Send close event
    yield f"event: close\ndata: {json.dumps({'message': 'Stream closed'})}\n\n"

def calculate_progress(tasks: List[Dict[str, Any]]) -> float:
    """Calculate workflow progress percentage"""
    if not tasks:
        return 0.0
    
    completed_states = ["success", "failed", "skipped", "upstream_failed"]
    completed_tasks = sum(1 for task in tasks if task["state"] in completed_states)
    
    return round((completed_tasks / len(tasks)) * 100, 2)

def calculate_duration(start_date: str, end_date: str) -> float:
    """Calculate duration in seconds"""
    if not start_date or not end_date:
        return 0.0
    
    start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    return (end - start).total_seconds()

@router.get("/stream/{dag_id}/{dag_run_id}")
async def stream_workflow_status(dag_id: str, dag_run_id: str, request: Request):
    """Stream real-time workflow status updates via Server-Sent Events"""
    
    return StreamingResponse(
        workflow_event_stream(dag_id, dag_run_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable Nginx buffering
        }
    )

@router.get("/{dag_id}/{dag_run_id}")
async def get_workflow_status(dag_id: str, dag_run_id: str) -> Dict[str, Any]:
    """Get current workflow status (non-streaming)"""
    
    async with httpx.AsyncClient() as client:
        # Get DAG run status
        dag_response = await client.get(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        
        if dag_response.status_code != 200:
            raise HTTPException(
                status_code=dag_response.status_code,
                detail="Failed to fetch workflow status"
            )
        
        dag_run = dag_response.json()
        
        # Get task instances
        tasks_response = await client.get(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        
        tasks = []
        if tasks_response.status_code == 200:
            tasks = tasks_response.json()["task_instances"]
        
        # Get logs for failed tasks
        failed_tasks = [t for t in tasks if t["state"] == "failed"]
        for task in failed_tasks:
            log_response = await client.get(
                f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task['task_id']}/logs/1",
                auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
            )
            if log_response.status_code == 200:
                task["logs"] = log_response.text
        
        return {
            "dag_id": dag_id,
            "dag_run_id": dag_run_id,
            "state": dag_run["state"],
            "start_date": dag_run["start_date"],
            "end_date": dag_run.get("end_date"),
            "execution_date": dag_run["execution_date"],
            "conf": dag_run.get("conf", {}),
            "tasks": tasks,
            "progress": calculate_progress(tasks),
            "duration": calculate_duration(
                dag_run["start_date"], 
                dag_run.get("end_date")
            )
        }

@router.get("/{dag_id}/{dag_run_id}/logs/{task_id}")
async def get_task_logs(dag_id: str, dag_run_id: str, task_id: str, try_number: int = 1):
    """Get logs for a specific task"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_number}",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        
        if response.status_code == 200:
            return {"logs": response.text}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch task logs"
            )