// frontend/src/components/WorkflowControlBar.tsx
import React, { useState } from 'react';
import { useWorkflowStore } from '../store/workflowStore';
import { useWorkflow } from '../hooks/useWorkflow';
import { ExecutionDialog } from './ExecutionDialog';

interface WorkflowControlBarProps {
  workflowId?: string;
}

export const WorkflowControlBar: React.FC<WorkflowControlBarProps> = ({ workflowId }) => {
  const [showExecutionDialog, setShowExecutionDialog] = useState(false);
  const [workflowName, setWorkflowName] = useState('Untitled Workflow');
  const { nodes } = useWorkflowStore();
  const { saveCurrentWorkflow, isSaving, workflow } = useWorkflow(workflowId);

  const handleSave = async () => {
    try {
      await saveCurrentWorkflow();
      console.log('Workflow saved successfully');
    } catch (error) {
      console.error('Failed to save workflow:', error);
    }
  };

  const canExecute = nodes.length > 0 && workflowId;

  return (
    <>
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <input
            type="text"
            value={workflow?.name || workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="text-lg font-semibold bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1"
          />
          {workflowId && (
            <span className="text-sm text-gray-500">
              ID: {workflowId.slice(0, 8)}...
            </span>
          )}
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleSave}
            disabled={!workflowId || isSaving}
            className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
              !workflowId || isSaving
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
            </svg>
            <span>{isSaving ? 'Saving...' : 'Save'}</span>
          </button>

          <button
            onClick={() => setShowExecutionDialog(true)}
            disabled={!canExecute}
            className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
              !canExecute
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Execute</span>
          </button>
        </div>
      </div>

      {showExecutionDialog && workflowId && (
        <ExecutionDialog
          workflowId={workflowId}
          onClose={() => setShowExecutionDialog(false)}
        />
      )}
    </>
  );
};