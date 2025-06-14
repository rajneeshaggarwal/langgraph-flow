from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from datetime import datetime

router = APIRouter(prefix="/workflows", tags=["workflows"])
security = HTTPBearer()

AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")

class WorkflowTriggerRequest(BaseModel):
    dag_id: str
    input_data: Dict[str, Any]
    execution_date: Optional[str] = None

class WorkflowResponse(BaseModel):
    dag_id: str
    dag_run_id: str
    execution_date: str
    state: str
    conf: Dict[str, Any]

async def trigger_workflow(request: WorkflowTriggerRequest, 
                         credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Trigger an Airflow DAG from FastAPI endpoint"""
    
    # Prepare the DAG run configuration
    dag_run_conf = {
        "input_data": request.input_data,
        "triggered_by": "visual-ai-api",
        "user_token": credentials.credentials,
        "trigger_time": datetime.utcnow().isoformat()
    }
    
    # Trigger DAG via Airflow REST API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AIRFLOW_URL}/api/v1/dags/{request.dag_id}/dagRuns",
            json={
                "conf": dag_run_conf,
                "logical_date": request.execution_date or datetime.utcnow().isoformat()
            },
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to trigger workflow: {response.text}"
            )
        
        return WorkflowResponse(**response.json())

@router.post("/trigger", response_model=WorkflowResponse)
async def trigger_visual_ai_workflow(
    request: WorkflowTriggerRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Trigger a Visual AI workflow"""
    return await trigger_workflow(request, credentials)

@router.get("/status/{dag_id}/{dag_run_id}")
async def get_workflow_status(dag_id: str, dag_run_id: str):
    """Get the status of a running workflow"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get workflow status: {response.text}"
            )
        
        return response.json()

@router.get("/tasks/{dag_id}/{dag_run_id}")
async def get_workflow_tasks(dag_id: str, dag_run_id: str):
    """Get task instances for a workflow run"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get task instances: {response.text}"
            )
        
        return response.json()

@router.post("/pause/{dag_id}")
async def pause_dag(dag_id: str):
    """Pause a DAG"""
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}",
            json={"is_paused": True},
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to pause DAG: {response.text}"
            )
        
        return {"message": f"DAG {dag_id} paused successfully"}

@router.post("/unpause/{dag_id}")
async def unpause_dag(dag_id: str):
    """Unpause a DAG"""
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}",
            json={"is_paused": False},
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to unpause DAG: {response.text}"
            )
        
        return {"message": f"DAG {dag_id} unpaused successfully"}