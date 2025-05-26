// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WorkflowCanvasWithProvider } from './components/WorkflowCanvas';
import { NodePanel } from './components/NodePanel';
import { WorkflowControlBar } from './components/WorkflowControlBar';
import { WorkflowSelector } from './components/WorkflowSelector';
import { useWorkflowStore } from './store/workflowStore';

const queryClient = new QueryClient();

function WorkflowEditor() {
  const [currentWorkflowId, setCurrentWorkflowId] = useState<string | null>(null);
  const { clearWorkflow } = useWorkflowStore();

  const handleWorkflowSelect = (workflowId: string | null) => {
    if (!workflowId) {
      clearWorkflow();
    }
    setCurrentWorkflowId(workflowId);
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">
            Visual AI Framework
          </h1>
          <WorkflowSelector
            currentWorkflowId={currentWorkflowId}
            onSelectWorkflow={handleWorkflowSelect}
          />
        </div>
      </header>

      {currentWorkflowId && (
        <WorkflowControlBar workflowId={currentWorkflowId} />
      )}
      
      <div className="flex-1 flex">
        <NodePanel />
        <WorkflowCanvasWithProvider workflowId={currentWorkflowId} />
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WorkflowEditor />
    </QueryClientProvider>
  );
}

export default App;