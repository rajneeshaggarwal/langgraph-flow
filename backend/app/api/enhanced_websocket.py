from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any
import json
import asyncio
from uuid import UUID
from datetime import datetime

router = APIRouter()

class EnhancedConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.workflow_subscriptions: Dict[UUID, Set[WebSocket]] = {}
        self.execution_subscriptions: Dict[UUID, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections[client_id].discard(websocket)
        if not self.active_connections[client_id]:
            del self.active_connections[client_id]
        
        # Remove from subscriptions
        for workflow_id, sockets in list(self.workflow_subscriptions.items()):
            sockets.discard(websocket)
            if not sockets:
                del self.workflow_subscriptions[workflow_id]
        
        for execution_id, sockets in list(self.execution_subscriptions.items()):
            sockets.discard(websocket)
            if not sockets:
                del self.execution_subscriptions[execution_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_workflow(self, workflow_id: UUID, message: dict):
        if workflow_id in self.workflow_subscriptions:
            await self._broadcast_to_sockets(
                self.workflow_subscriptions[workflow_id], 
                message
            )
    
    async def broadcast_to_execution(self, execution_id: UUID, message: dict):
        if execution_id in self.execution_subscriptions:
            await self._broadcast_to_sockets(
                self.execution_subscriptions[execution_id], 
                message
            )
    
    async def _broadcast_to_sockets(self, sockets: Set[WebSocket], message: dict):
        disconnected = set()
        for websocket in sockets:
            try:
                await websocket.send_json(message)
            except:
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for ws in disconnected:
            sockets.discard(ws)
    
    async def send_agent_update(self, execution_id: UUID, agent_id: str, status: str, data: Any = None):
        """Send real-time agent execution updates"""
        message = {
            'type': 'agent_update',
            'execution_id': str(execution_id),
            'agent_id': agent_id,
            'status': status,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_execution(execution_id, message)
    
    async def send_agent_message(self, execution_id: UUID, sender: str, recipient: str, content: Any):
        """Send inter-agent communication updates"""
        message = {
            'type': 'agent_message',
            'execution_id': str(execution_id),
            'sender': sender,
            'recipient': recipient,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_execution(execution_id, message)

manager = EnhancedConnectionManager()

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
            
            elif message['type'] == 'subscribe_execution':
                execution_id = UUID(message['execution_id'])
                if execution_id not in manager.execution_subscriptions:
                    manager.execution_subscriptions[execution_id] = set()
                manager.execution_subscriptions[execution_id].add(websocket)
                
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'execution_subscription_confirmed',
                        'execution_id': str(execution_id)
                    }),
                    websocket
                )
            
            elif message['type'] == 'workflow_update':
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