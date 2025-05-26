# backend/scripts/run_workflow.py
import asyncio
import httpx
import json
import websockets
from uuid import uuid4

API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

async def execute_workflow_with_monitoring(workflow_id: str, input_data: dict):
    """Execute a workflow and monitor its progress via WebSocket"""
    
    client_id = f"monitor_{uuid4().hex[:8]}"
    
    # Connect to WebSocket first
    async with websockets.connect(f"{WS_BASE_URL}/ws/{client_id}") as websocket:
        print(f"Connected to WebSocket as {client_id}")
        
        # Execute the workflow
        async with httpx.AsyncClient() as http_client:
            print(f"\nExecuting workflow {workflow_id}...")
            response = await http_client.post(
                f"{API_BASE_URL}/api/workflows/{workflow_id}/execute",
                json={
                    "workflow_id": workflow_id,
                    "input_data": input_data
                }
            )
            
            if response.status_code == 200:
                execution = response.json()
                execution_id = execution['id']
                print(f"Started execution: {execution_id}")
                
                # Subscribe to execution updates
                await websocket.send(json.dumps({
                    "type": "subscribe_execution",
                    "execution_id": execution_id
                }))
                
                # Monitor execution
                print("\nMonitoring execution...")
                print("-" * 50)
                
                while True:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(), 
                            timeout=30.0
                        )
                        data = json.loads(message)
                        
                        if data.get('type') == 'agent_update':
                            agent_id = data.get('agent_id', 'Unknown')
                            status = data.get('status', 'Unknown')
                            update_data = data.get('data', {})
                            
                            print(f"\n[{status.upper()}] Agent: {agent_id}")
                            if isinstance(update_data, dict):
                                if 'message' in update_data:
                                    print(f"  Message: {update_data['message']}")
                                if 'response' in update_data:
                                    print(f"  Response: {update_data['response']}")
                            
                            if status in ['completed', 'failed']:
                                print("\n" + "=" * 50)
                                print(f"Execution {status}!")
                                break
                                
                    except asyncio.TimeoutError:
                        print("\nTimeout waiting for updates")
                        break
            else:
                print(f"Failed to execute workflow: {response.text}")

async def main():
    """Main function to demonstrate workflow execution"""
    
    # First, get list of workflows
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/workflows/")
        workflows = response.json()
        
        if not workflows:
            print("No workflows found. Please create a workflow first.")
            return
        
        print("Available workflows:")
        for i, workflow in enumerate(workflows):
            print(f"{i+1}. {workflow['name']} (ID: {workflow['id']})")
        
        # Select workflow
        selection = input("\nSelect workflow number (or press Enter for first): ").strip()
        workflow_idx = int(selection) - 1 if selection else 0
        selected_workflow = workflows[workflow_idx]
        
        print(f"\nSelected: {selected_workflow['name']}")
        
        # Get input data
        print("\nEnter input data (JSON format):")
        print("Default: {'message': 'Hello, AI agents!'}")
        input_str = input("Input data: ").strip()
        
        if not input_str:
            input_data = {"message": "Hello, AI agents!"}
        else:
            try:
                input_data = json.loads(input_str)
            except json.JSONDecodeError:
                print("Invalid JSON, using default")
                input_data = {"message": "Hello, AI agents!"}
        
        # Execute and monitor
        await execute_workflow_with_monitoring(
            selected_workflow['id'], 
            input_data
        )

if __name__ == "__main__":
    asyncio.run(main())