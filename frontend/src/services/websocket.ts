// frontend/src/services/websocket.ts
class WebSocketService {
    private socket: WebSocket | null = null;
    private clientId: string;
    private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
    
    constructor() {
      this.clientId = this.generateClientId();
    }
    
    connect(): void {
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/${this.clientId}`;
      
      try {
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.startHeartbeat();
        };
        
        this.socket.onclose = () => {
          console.log('WebSocket disconnected');
          this.stopHeartbeat();
          this.attemptReconnect();
        };
        
        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        this.socket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
      } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        this.attemptReconnect();
      }
    }
    
    disconnect(): void {
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
      
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
      
      this.stopHeartbeat();
    }
    
    subscribeToWorkflow(workflowId: string): void {
      this.sendMessage({
        type: 'subscribe_workflow',
        workflow_id: workflowId,
      });
    }
    
    sendWorkflowUpdate(workflowId: string, data: any): void {
      this.sendMessage({
        type: 'workflow_update',
        workflow_id: workflowId,
        data,
      });
    }

    subscribeToExecution(executionId: string): void {
    this.sendMessage({
        type: 'subscribe_execution',
        execution_id: executionId,
      });
    }

    onExecutionUpdate(callback: (data: any) => void): void {
      this.messageHandlers.set('execution_update', callback);
    }
    
    onAgentUpdate(callback: (data: any) => void): void {
      this.messageHandlers.set('agent_update', callback);
    }
    
    onAgentMessage(callback: (data: any) => void): void {
      this.messageHandlers.set('agent_message', callback);
    }
    
    onWorkflowUpdate(callback: (data: any) => void): void {
      this.messageHandlers.set('workflow_update', callback);
    }
    
    private messageHandlers = new Map<string, (data: any) => void>();
    
    private handleMessage(message: any): void {
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(message);
      }
      
      // Handle specific message types
      if (message.type === 'heartbeat_ack') {
        // Heartbeat acknowledged
      } else if (message.type === 'subscription_confirmed') {
        console.log('Subscription confirmed for workflow:', message.workflow_id);
      }
    }
    
    private sendMessage(message: any): void {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify(message));
      } else {
        console.warn('WebSocket is not connected. Message not sent:', message);
      }
    }
    
    private startHeartbeat(): void {
      this.heartbeatInterval = setInterval(() => {
        this.sendMessage({ type: 'heartbeat' });
      }, 30000);
    }
    
    private stopHeartbeat(): void {
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = null;
      }
    }
    
    private attemptReconnect(): void {
      if (this.reconnectTimeout) return;
      
      this.reconnectTimeout = setTimeout(() => {
        console.log('Attempting to reconnect WebSocket...');
        this.reconnectTimeout = null;
        this.connect();
      }, 5000);
    }
    
    private generateClientId(): string {
      return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
  }
  
  export const wsService = new WebSocketService();