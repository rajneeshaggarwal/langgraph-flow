import React, { useEffect, useState } from 'react';
import { useWorkflowStore } from '../store/workflowStore';
import { wsService } from '../services/websocket';

interface ExecutionStatus {
  executionId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  currentAgent?: string;
  messages: Array<{
    agentId: string;
    message: string;
    timestamp: string;
  }>;
}

export const ExecutionMonitor: React.FC = () => {
  const [executions, setExecutions] = useState<Record<string, ExecutionStatus>>({});
  const [expandedExecution, setExpandedExecution] = useState<string | null>(null);
  const { highlightNode } = useWorkflowStore();

  useEffect(() => {
    // Subscribe to agent updates
    wsService.onAgentUpdate((data) => {
      const { execution_id, agent_id, status, data: updateData } = data;
      
      setExecutions(prev => ({
        ...prev,
        [execution_id]: {
          ...prev[execution_id],
          executionId: execution_id,
          status: status === 'completed' ? 'completed' : 
                  status === 'failed' ? 'failed' : 'running',
          currentAgent: agent_id,
          messages: [
            ...(prev[execution_id]?.messages || []),
            {
              agentId: agent_id,
              message: updateData?.message || JSON.stringify(updateData),
              timestamp: new Date().toISOString()
            }
          ]
        }
      }));

      // Highlight the current node
      if (agent_id !== 'system' && status === 'processing') {
        highlightNode(agent_id);
      }
    });
  }, [highlightNode]);

  return (
    <div className="fixed bottom-0 left-64 right-0 bg-white border-t border-gray-200 max-h-64 overflow-y-auto">
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2">Execution Monitor</h3>
        
        {Object.entries(executions).length === 0 ? (
          <p className="text-gray-500">No active executions</p>
        ) : (
          <div className="space-y-2">
            {Object.entries(executions).map(([id, execution]) => (
              <div
                key={id}
                className="border border-gray-200 rounded-lg p-3"
              >
                <div
                  className="flex justify-between items-center cursor-pointer"
                  onClick={() => setExpandedExecution(expandedExecution === id ? null : id)}
                >
                  <div className="flex items-center space-x-3">
                    <span className={`
                      inline-block w-3 h-3 rounded-full
                      ${execution.status === 'running' ? 'bg-yellow-500 animate-pulse' : ''}
                      ${execution.status === 'completed' ? 'bg-green-500' : ''}
                      ${execution.status === 'failed' ? 'bg-red-500' : ''}
                      ${execution.status === 'pending' ? 'bg-gray-400' : ''}
                    `} />
                    <span className="font-medium">Execution {id.slice(0, 8)}</span>
                    {execution.currentAgent && execution.status === 'running' && (
                      <span className="text-sm text-gray-500">
                        Current: {execution.currentAgent}
                      </span>
                    )}
                  </div>
                  <svg
                    className={`w-5 h-5 transform transition-transform ${
                      expandedExecution === id ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
                
                {expandedExecution === id && (
                  <div className="mt-3 space-y-1 max-h-32 overflow-y-auto">
                    {execution.messages.map((msg, idx) => (
                      <div key={idx} className="text-sm">
                        <span className="font-medium text-gray-600">
                          {msg.agentId}:
                        </span>{' '}
                        <span className="text-gray-800">{msg.message}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};