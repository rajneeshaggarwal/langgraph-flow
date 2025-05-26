import { useEffect, useCallback } from 'react';
import { wsService } from '../services/websocket';

export const useWebSocket = (workflowId?: string) => {
  useEffect(() => {
    wsService.connect();
    
    return () => {
      wsService.disconnect();
    };
  }, []);
  
  useEffect(() => {
    if (workflowId) {
      wsService.subscribeToWorkflow(workflowId);
    }
  }, [workflowId]);
  
  const sendUpdate = useCallback((data: any) => {
    if (workflowId) {
      wsService.sendWorkflowUpdate(workflowId, data);
    }
  }, [workflowId]);
  
  return { sendUpdate };
};