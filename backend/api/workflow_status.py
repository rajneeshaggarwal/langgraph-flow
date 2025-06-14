from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
import httpx
from typing import AsyncGenerator
from datetime import datetime
import os

router = APIRouter(prefix="/workflow-status", tags=["status"])

AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")

async def workflow_event_stream(
    dag_id: str, 
    dag_run_id: str, 
    request: Request
) -> AsyncGenerator:
    """Stream workflow status updates via SSE"""
    
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
                    auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
                )
                
                if dag_response.status_code == 200:
                    dag_run = dag_response.json()
                    
                    # Get task instances for this DAG run
                    tasks_response = await client.get(
                        f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
                        auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
                    )
                    
                    event_data = {
                        "dag_run_id": dag_run_id,
                        "state": dag_run["state"],
                        "start_date": dag_run["start_date"],
                        "end_date": dag_run.get("end_date"),
                        "tasks": tasks_response.json()["task_instances"] if tasks_response.status_code == 200 else [],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Send workflow update event
                    yield f"event: workflow_update\ndata: {json.dumps(event_data)}\n\n"
                    
                    # If workflow completed, send final event and close
                    if dag_run["state"] in ["success", "failed", "skipped"]:
                        yield f"event: workflow_complete\ndata: {json.dumps(event_data)}\n\n"
                        break
        
        except Exception as e:
            # Send error event
            error_data = {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
        
        # Poll every 2 seconds
        await asyncio.sleep(2)

@router.get("/stream/{dag_id}/{dag_run_id}")
async def stream_workflow_status(dag_id: str, dag_run_id: str, request: Request):
    """Stream real-time workflow status updates"""
    
    return StreamingResponse(
        workflow_event_stream(dag_id, dag_run_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable Nginx buffering
        }
    )

@router.get("/batch-status")
async def get_batch_workflow_status(dag_ids: str):
    """Get status for multiple workflows at once"""
    
    dag_id_list = dag_ids.split(",")
    results = {}
    
    async with httpx.AsyncClient() as client:
        for dag_id in dag_id_list:
            try:
                response = await client.get(
                    f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns",
                    params={"limit": 5, "order_by": "-execution_date"},
                    auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
                )
                
                if response.status_code == 200:
                    results[dag_id] = response.json()["dag_runs"]
                else:
                    results[dag_id] = {"error": f"Failed to fetch: {response.status_code}"}
            
            except Exception as e:
                results[dag_id] = {"error": str(e)}
    
    return results