// frontend/src/components/WorkflowSelector.tsx
import React, { useState } from 'react';
import { useWorkflowList } from '../hooks/useWorkflow';
import { workflowApi } from '../services/api';

interface WorkflowSelectorProps {
  currentWorkflowId: string | null;
  onSelectWorkflow: (workflowId: string | null) => void;
}

export const WorkflowSelector: React.FC<WorkflowSelectorProps> = ({
  currentWorkflowId,
  onSelectWorkflow,
}) => {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const { workflows, isLoading, refetch } = useWorkflowList();

  const handleCreateWorkflow = async () => {
    if (!newWorkflowName.trim()) return;

    try {
      const workflow = await workflowApi.createWorkflow({
        name: newWorkflowName,
        nodes: [],
        edges: [],
      });
      onSelectWorkflow(workflow.id);
      setNewWorkflowName('');
      setShowCreateDialog(false);
      refetch();
    } catch (error) {
      console.error('Failed to create workflow:', error);
    }
  };

  return (
    <div className="relative">
      <select
        value={currentWorkflowId || ''}
        onChange={(e) => onSelectWorkflow(e.target.value || null)}
        className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={isLoading}
      >
        <option value="">Select a workflow</option>
        {workflows.map((workflow) => (
          <option key={workflow.id} value={workflow.id}>
            {workflow.name}
          </option>
        ))}
      </select>

      <button
        onClick={() => setShowCreateDialog(true)}
        className="ml-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        New Workflow
      </button>

      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold mb-4">Create New Workflow</h2>
            
            <input
              type="text"
              value={newWorkflowName}
              onChange={(e) => setNewWorkflowName(e.target.value)}
              placeholder="Workflow name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && handleCreateWorkflow()}
            />

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowCreateDialog(false);
                  setNewWorkflowName('');
                }}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateWorkflow}
                disabled={!newWorkflowName.trim()}
                className={`px-4 py-2 text-white rounded-md ${
                  !newWorkflowName.trim()
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};