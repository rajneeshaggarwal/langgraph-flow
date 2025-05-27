import React, { useEffect, useState } from 'react';
import { useWorkflowStore } from '../store/workflowStore';
import { wsService } from '../services/websocket';

interface OutputMessage {
  nodeId: string;
  nodeName: string;
  timestamp: string;
  content: any;
  status: 'success' | 'error' | 'processing';
}

interface ExecutionResult {
  executionId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: string;
  endTime?: string;
  outputs: OutputMessage[];
  error?: string;
}

export const OutputPanel: React.FC = () => {
  const [executions, setExecutions] = useState<Record<string, ExecutionResult>>({});
  const [selectedExecution, setSelectedExecution] = useState<string | null>(null);
  const [isMinimized, setIsMinimized] = useState(false);
  const { nodes } = useWorkflowStore();

  useEffect(() => {
    // Subscribe to agent updates
    wsService.onAgentUpdate((data) => {
      const { execution_id, agent_id, status, data: updateData } = data;
      
      setExecutions(prev => {
        const execution = prev[execution_id] || {
          executionId: execution_id,
          status: 'running',
          startTime: new Date().toISOString(),
          outputs: []
        };

        // Find node name
        const node = nodes.find(n => n.id === agent_id);
        const nodeName = node?.data.label || agent_id;

        if (status === 'processing' && updateData) {
          execution.outputs.push({
            nodeId: agent_id,
            nodeName,
            timestamp: new Date().toISOString(),
            content: updateData,
            status: 'success'
          });
        }

        if (status === 'completed') {
          execution.status = 'completed';
          execution.endTime = new Date().toISOString();
        } else if (status === 'failed') {
          execution.status = 'failed';
          execution.endTime = new Date().toISOString();
          execution.error = updateData?.error || 'Unknown error';
        }

        return {
          ...prev,
          [execution_id]: execution
        };
      });

      // Auto-select the latest execution
      if (!selectedExecution) {
        setSelectedExecution(execution_id);
      }
    });
  }, [nodes, selectedExecution]);

  const currentExecution = selectedExecution ? executions[selectedExecution] : null;

  if (Object.keys(executions).length === 0) {
    return null;
  }

  return (
    <div className={`fixed bottom-0 left-80 right-0 bg-white border-t border-gray-200 transition-all duration-300 ${
      isMinimized ? 'h-12' : 'h-80'
    }`}>
      {/* Header */}
      <div className="h-12 px-4 flex items-center justify-between bg-gray-50 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <h3 className="text-sm font-semibold text-gray-700">Output</h3>
          {currentExecution && (
            <div className="flex items-center space-x-2">
              <span className={`
                inline-block w-2 h-2 rounded-full
                ${currentExecution.status === 'running' ? 'bg-yellow-500 animate-pulse' : ''}
                ${currentExecution.status === 'completed' ? 'bg-green-500' : ''}
                ${currentExecution.status === 'failed' ? 'bg-red-500' : ''}
                ${currentExecution.status === 'pending' ? 'bg-gray-400' : ''}
              `} />
              <span className="text-xs text-gray-600">
                Execution {currentExecution.executionId.slice(0, 8)}
              </span>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Execution Selector */}
          {Object.keys(executions).length > 1 && (
            <select
              value={selectedExecution || ''}
              onChange={(e) => setSelectedExecution(e.target.value)}
              className="text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {Object.entries(executions).map(([id, exec]) => (
                <option key={id} value={id}>
                  {new Date(exec.startTime).toLocaleTimeString()} - {exec.status}
                </option>
              ))}
            </select>
          )}
          
          {/* Clear Button */}
          <button
            onClick={() => {
              setExecutions({});
              setSelectedExecution(null);
            }}
            className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
            title="Clear outputs"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          
          {/* Minimize/Maximize Button */}
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
          >
            <svg 
              className={`w-4 h-4 transform transition-transform ${isMinimized ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content */}
      {!isMinimized && currentExecution && (
        <div className="flex-1 overflow-y-auto p-4">
          {currentExecution.outputs.length === 0 && currentExecution.status === 'running' && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="mb-4">
                  <svg className="w-12 h-12 mx-auto text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <p className="text-gray-500">Executing workflow...</p>
              </div>
            </div>
          )}

          {currentExecution.error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-red-800">Execution Failed</h4>
                  <p className="text-sm text-red-700 mt-1">{currentExecution.error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            {currentExecution.outputs.map((output, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      output.status === 'success' ? 'bg-green-100' : 
                      output.status === 'error' ? 'bg-red-100' : 'bg-gray-100'
                    }`}>
                      {output.status === 'success' && (
                        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                      {output.status === 'error' && (
                        <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )}
                    </div>
                    <span className="text-sm font-medium text-gray-900">{output.nodeName}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(output.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="bg-gray-50 rounded p-3 font-mono text-sm">
                  {typeof output.content === 'object' ? (
                    <pre className="whitespace-pre-wrap text-gray-700">
                      {JSON.stringify(output.content, null, 2)}
                    </pre>
                  ) : (
                    <p className="text-gray-700">{output.content}</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {currentExecution.status === 'completed' && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="ml-2 text-sm font-medium text-green-800">
                  Execution completed successfully
                </span>
                {currentExecution.endTime && (
                  <span className="ml-auto text-xs text-green-600">
                    Duration: {
                      Math.round((new Date(currentExecution.endTime).getTime() - 
                                 new Date(currentExecution.startTime).getTime()) / 1000)
                    }s
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};