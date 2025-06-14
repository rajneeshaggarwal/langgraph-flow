from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from datetime import datetime
import json

router = APIRouter(prefix="/workflows", tags=["workflows"])
security = HTTPBearer()

AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")

class WorkflowTriggerRequest(BaseModel):
    dag_id: str
    input_data: Dict[str, Any]
    execution_date: Optional[str] = None
    user_id: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    dag_run_id: str
    dag_id: str
    status: str
    execution_date: str
    conf: Dict[str, Any]

async def trigger_workflow(
    request: WorkflowTriggerRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> WorkflowResponse:
    """Trigger an Airflow DAG from FastAPI endpoint"""
    
    # Prepare the DAG run configuration
    dag_run_conf = {
        "input_data": request.input_data,
        "triggered_by": "visual-ai-api",
        "user_token": credentials.credentials,
        "user_id": request.user_id or "anonymous",
        "requirements": request.requirements or {}
    }
    
    # Trigger DAG via Airflow REST API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AIRFLOW_URL}/api/v1/dags/{request.dag_id}/dagRuns",
                json={
                    "conf": dag_run_conf,
                    "logical_date": request.execution_date or datetime.utcnow().isoformat()
                },
                auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                dag_run = response.json()
                return WorkflowResponse(
                    dag_run_id=dag_run["dag_run_id"],
                    dag_id=dag_run["dag_id"],
                    status=dag_run["state"],
                    execution_date=dag_run["execution_date"],
                    conf=dag_run["conf"]
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to trigger workflow: {response.text}"
                )
                
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Timeout while triggering workflow"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error: {str(e)}"
            )

@router.post("/trigger", response_model=WorkflowResponse)
async def trigger_visual_ai_workflow(
    request: WorkflowTriggerRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Trigger a Visual AI workflow"""
    
    # Validate DAG ID
    valid_dags = ["visual_ai_workflow", "visual_ai_multi_agent_pipeline"]
    if request.dag_id not in valid_dags:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid DAG ID. Valid options: {valid_dags}"
        )
    
    # Trigger the workflow
    result = await trigger_workflow(request, credentials)
    
    # Add background task to track workflow progress
    background_tasks.add_task(
        track_workflow_progress,
        result.dag_id,
        result.dag_run_id,
        request.user_id
    )
    
    return result

@router.get("/list")
async def list_available_workflows(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> List[Dict[str, Any]]:
    """List all available Visual AI workflows"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AIRFLOW_URL}/api/v1/dags",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            params={"tags": "visual-ai"}
        )
        
        if response.status_code == 200:
            dags = response.json()["dags"]
            return [
                {
                    "dag_id": dag["dag_id"],
                    "description": dag["description"],
                    "is_paused": dag["is_paused"],
                    "tags": dag["tags"],
                    "last_run": dag.get("last_dag_run", {})
                }
                for dag in dags
            ]
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch workflows"
            )

@router.get("/{dag_id}/runs")
async def get_workflow_runs(
    dag_id: str,
    limit: int = 10,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> List[Dict[str, Any]]:
    """Get recent runs for a specific workflow"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            params={"limit": limit, "order_by": "-execution_date"}
        )
        
        if response.status_code == 200:
            return response.json()["dag_runs"]
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch workflow runs"
            )

@router.delete("/{dag_id}/runs/{dag_run_id}")
async def cancel_workflow_run(
    dag_id: str,
    dag_run_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cancel a running workflow"""
    
    async with httpx.AsyncClient() as client:
        # Update the state to 'failed' to cancel the run
        response = await client.patch(
            f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}",
            json={"state": "failed"},
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return {"message": "Workflow cancelled successfully"}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to cancel workflow"
            )

async def track_workflow_progress(dag_id: str, dag_run_id: str, user_id: Optional[str]):
    """Background task to track workflow progress"""
    # This could send notifications, update a cache, etc.
    # For now, just log the tracking
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Tracking workflow {dag_id}/{dag_run_id} for user {user_id}")