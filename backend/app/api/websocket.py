from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from uuid import UUID

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.workflow_subscriptions: Dict[UUID, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections[client_id].discard(websocket)
        if not self.active_connections[client_id]:
            del self.active_connections[client_id]
        
        # Remove from workflow subscriptions
        for workflow_id, sockets in list(self.workflow_subscriptions.items()):
            sockets.discard(websocket)
            if not sockets:
                del self.workflow_subscriptions[workflow_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_workflow(self, workflow_id: UUID, message: dict):
        if workflow_id in self.workflow_subscriptions:
            disconnected = set()
            for websocket in self.workflow_subscriptions[workflow_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.workflow_subscriptions[workflow_id].discard(ws)

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message['type'] == 'subscribe_workflow':
                workflow_id = UUID(message['workflow_id'])
                if workflow_id not in manager.workflow_subscriptions:
                    manager.workflow_subscriptions[workflow_id] = set()
                manager.workflow_subscriptions[workflow_id].add(websocket)
                
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'subscription_confirmed',
                        'workflow_id': str(workflow_id)
                    }),
                    websocket
                )
            
            elif message['type'] == 'workflow_update':
                # Broadcast workflow updates to all subscribers
                workflow_id = UUID(message['workflow_id'])
                await manager.broadcast_to_workflow(
                    workflow_id,
                    {
                        'type': 'workflow_update',
                        'workflow_id': str(workflow_id),
                        'data': message['data']
                    }
                )
            
            elif message['type'] == 'heartbeat':
                await manager.send_personal_message(
                    json.dumps({'type': 'heartbeat_ack'}),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        await manager.broadcast_to_workflow(
            workflow_id,
            {
                'type': 'user_disconnected',
                'client_id': client_id
            }
        )