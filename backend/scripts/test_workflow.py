import asyncio
import httpx
import json
from uuid import uuid4

API_BASE_URL = "http://localhost:8000"

async def create_test_workflow():
    """Create a simple test workflow"""
    workflow_data = {
        "name": "Test Agent Workflow",
        "description": "A simple workflow to test the system",
        "nodes": [
            {
                "id": str(uuid4()),
                "type": "agent",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start Agent",
                    "type": "agent",
                    "config": {
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7
                    }
                }
            },
            {
                "id": str(uuid4()),
                "type": "tool",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Process Tool",
                    "type": "tool",
                    "config": {
                        "tool_name": "data_processor"
                    }
                }
            },
            {
                "id": str(uuid4()),
                "type": "agent",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "End Agent",
                    "type": "agent",
                    "config": {
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.5
                    }
                }
            }
        ],
        "edges": []
    }
    
    # Connect the nodes
    nodes = workflow_data["nodes"]
    workflow_data["edges"] = [
        {
            "id": str(uuid4()),
            "source": nodes[0]["id"],
            "target": nodes[1]["id"]
        },
        {
            "id": str(uuid4()),
            "source": nodes[1]["id"],
            "target": nodes[2]["id"]
        }
    ]
    
    async with httpx.AsyncClient() as client:
        # Create workflow
        response = await client.post(
            f"{API_BASE_URL}/api/workflows/",
            json=workflow_data
        )
        
        if response.status_code == 200:
            workflow = response.json()
            print(f"Created workflow: {workflow['id']}")
            return workflow['id']
        else:
            print(f"Failed to create workflow: {response.text}")
            return None

async def execute_workflow(workflow_id: str):
    """Execute a workflow"""
    async with httpx.AsyncClient() as client:
        # Execute workflow
        response = await client.post(
            f"{API_BASE_URL}/api/workflows/{workflow_id}/execute",
            json={
                "workflow_id": workflow_id,
                "input_data": {
                    "message": "Hello, this is a test message!",
                    "context": {"user": "test_user"}
                }
            }
        )
        
        if response.status_code == 200:
            execution = response.json()
            print(f"Started execution: {execution['id']}")
            print(f"Status: {execution['status']}")
            return execution['id']
        else:
            print(f"Failed to execute workflow: {response.text}")
            return None

async def check_execution_status(workflow_id: str, execution_id: str):
    """Check the status of a workflow execution"""
    async with httpx.AsyncClient() as client:
        # Note: This endpoint would need to be added to the API
        # For now, we'll just wait and assume it completes
        print("Waiting for execution to complete...")
        await asyncio.sleep(5)
        print("Execution should be complete. Check the database for results.")

async def main():
    """Main function"""
    print("Visual AI Framework - Workflow Test Script")
    print("=" * 50)
    
    # Create a test workflow
    workflow_id = await create_test_workflow()
    
    if workflow_id:
        # Execute the workflow
        execution_id = await execute_workflow(workflow_id)
        
        if execution_id:
            # Check execution status
            await check_execution_status(workflow_id, execution_id)
    
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(main())