"""
Modified LangGraph Flow application with Airflow support
This allows the application to run in both standalone and Airflow-orchestrated modes
"""

import os
import argparse
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Check if running within Airflow
IS_AIRFLOW_ENVIRONMENT = os.getenv("AIRFLOW_HOME") is not None

class WorkflowRequest(BaseModel):
    """Request model for workflow execution"""
    workflow_type: str
    input_data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

class LangGraphFlowApp:
    """
    Main application class that supports both standalone and Airflow execution
    """
    
    def __init__(self, mode: str = "standalone"):
        """
        Initialize the application
        
        Args:
            mode: Execution mode - "standalone" or "airflow"
        """
        self.mode = mode
        self.app = FastAPI(
            title="LangGraph Flow Visual AI",
            description="Visual AI Framework with optional Airflow orchestration",
            version="2.0.0"
        )
        
        # Setup routes
        self._setup_routes()
        
        # Initialize components based on mode
        if self.mode == "airflow":
            from langgraph_flow.agents.airflow_integration import AirflowLangGraphIntegration
            self.integration = AirflowLangGraphIntegration()
        else:
            self.integration = None
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "LangGraph Flow Visual AI Framework",
                "mode": self.mode,
                "airflow_enabled": self.mode == "airflow"
            }
        
        @self.app.post("/execute")
        async def execute_workflow(request: WorkflowRequest):
            """Execute a workflow based on the current mode"""
            
            if self.mode == "airflow":
                return await self._execute_airflow_workflow(request)
            else:
                return await self._execute_standalone_workflow(request)
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "mode": self.mode,
                "airflow_available": IS_AIRFLOW_ENVIRONMENT
            }
    
    async def _execute_standalone_workflow(self, request: WorkflowRequest) -> Dict[str, Any]:
        """Execute workflow in standalone mode"""
        
        from langgraph_flow.workflows import create_workflow
        from langfuse.callback import CallbackHandler
        
        # Create workflow based on type
        workflow = create_workflow(request.workflow_type)
        
        # Setup callbacks
        langfuse_handler = CallbackHandler(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY")
        )
        
        # Execute workflow
        try:
            result = workflow.invoke(
                request.input_data,
                config={
                    "callbacks": [langfuse_handler],
                    **request.config
                } if request.config else {"callbacks": [langfuse_handler]}
            )
            
            return {
                "status": "success",
                "result": result,
                "execution_mode": "standalone"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _execute_airflow_workflow(self, request: WorkflowRequest) -> Dict[str, Any]:
        """Execute workflow via Airflow"""
        
        import httpx
        
        # Trigger Airflow DAG via API
        airflow_url = os.getenv("AIRFLOW_URL", "http://localhost:8080")
        
        # Map workflow type to DAG ID
        dag_mapping = {
            "simple": "visual_ai_workflow",
            "multi_agent": "visual_ai_multi_agent_pipeline"
        }
        
        dag_id = dag_mapping.get(request.workflow_type, "visual_ai_workflow")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns",
                json={
                    "conf": {
                        "input_data": request.input_data,
                        "config": request.config,
                        "triggered_by": "langgraph_flow_app"
                    }
                },
                auth=(
                    os.getenv("AIRFLOW_USERNAME", "airflow"),
                    os.getenv("AIRFLOW_PASSWORD", "airflow")
                )
            )
            
            if response.status_code == 200:
                dag_run = response.json()
                return {
                    "status": "triggered",
                    "dag_run_id": dag_run["dag_run_id"],
                    "execution_mode": "airflow",
                    "monitor_url": f"/workflow-status/{dag_id}/{dag_run['dag_run_id']}"
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to trigger Airflow DAG: {response.text}"
                )
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the FastAPI application"""
        uvicorn.run(self.app, host=host, port=port)

def create_cli_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="LangGraph Flow Visual AI Framework"
    )
    
    parser.add_argument(
        "--mode",
        choices=["standalone", "airflow"],
        default="standalone",
        help="Execution mode"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to"
    )
    
    # Airflow-specific arguments
    parser.add_argument(
        "--airflow-url",
        default="http://localhost:8080",
        help="Airflow webserver URL"
    )
    
    parser.add_argument(
        "--airflow-username",
        default="airflow",
        help="Airflow username"
    )
    
    parser.add_argument(
        "--airflow-password",
        default="airflow",
        help="Airflow password"
    )
    
    return parser

def setup_environment(args):
    """Setup environment variables based on CLI arguments"""
    if args.mode == "airflow":
        os.environ["AIRFLOW_URL"] = args.airflow_url
        os.environ["AIRFLOW_USERNAME"] = args.airflow_username
        os.environ["AIRFLOW_PASSWORD"] = args.airflow_password

def main():
    """Main entry point"""
    # Parse arguments
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Setup environment
    setup_environment(args)
    
    # Create and run application
    app = LangGraphFlowApp(mode=args.mode)
    
    print(f"Starting LangGraph Flow in {args.mode} mode...")
    print(f"Server running at http://{args.host}:{args.port}")
    
    if args.mode == "airflow":
        print(f"Airflow integration enabled - URL: {args.airflow_url}")
    
    app.run(host=args.host, port=args.port)

# Support for running within Airflow DAGs
def create_airflow_compatible_app():
    """
    Factory function to create app instance for Airflow tasks
    """
    return LangGraphFlowApp(mode="airflow")

# Support for importing as a module
app = LangGraphFlowApp(mode="airflow" if IS_AIRFLOW_ENVIRONMENT else "standalone").app

if __name__ == "__main__":
    main()