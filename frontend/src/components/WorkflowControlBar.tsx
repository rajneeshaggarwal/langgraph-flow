import React, { useState, useMemo } from 'react';
import { useWorkflowStore } from '../store/workflowStore';
import { useWorkflow } from '../hooks/useWorkflow';
import { ExecutionDialog } from './ExecutionDialog';
import { PlaygroundDialog } from './PlaygroundDialog';

interface WorkflowControlBarProps {
  workflowId?: string;
}

export const WorkflowControlBar: React.FC<WorkflowControlBarProps> = ({ workflowId }) => {
  const [showExecutionDialog, setShowExecutionDialog] = useState(false);
  const [showPlaygroundDialog, setShowPlaygroundDialog] = useState(false);
  const [showPublishMenu, setShowPublishMenu] = useState(false);
  const [workflowName, setWorkflowName] = useState('Untitled Workflow');
  const { nodes } = useWorkflowStore();
  const { saveCurrentWorkflow, isUpdating, workflow } = useWorkflow(workflowId);

  // Check if workflow has chat input and output nodes
  const hasChatNodes = useMemo(() => {
    const hasChatInput = nodes.some(node => node.data.type === 'chatInput');
    const hasChatOutput = nodes.some(node => node.data.type === 'chatOutput');
    return hasChatInput && hasChatOutput;
  }, [nodes]);

  const handleSave = async () => {
    try {
      await saveCurrentWorkflow();
      console.log('Workflow saved successfully');
    } catch (error) {
      console.error('Failed to save workflow:', error);
    }
  };

  const handlePublish = (environment: string) => {
    console.log(`Publishing to ${environment}...`);
    // Implement publish logic here
    setShowPublishMenu(false);
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
          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={!workflowId || isUpdating}
            className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
              !workflowId || isUpdating
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
            </svg>
            <span>{isUpdating ? 'Saving...' : 'Save'}</span>
          </button>

          {/* Execute Button */}
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

          {/* Divider */}
          <div className="h-8 w-px bg-gray-300"></div>

          {/* Playground Button - Only visible when chat nodes are present */}
          {hasChatNodes && (
            <button
              onClick={() => setShowPlaygroundDialog(true)}
              disabled={!canExecute}
              className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
                !canExecute
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span>Playground</span>
            </button>
          )}

          {/* Publish Button with Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowPublishMenu(!showPublishMenu)}
              disabled={!workflowId}
              className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
                !workflowId
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-black text-white hover:bg-gray-800'
              }`}
            >
              <span>Publish</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Publish Dropdown Menu */}
            {showPublishMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50 border border-gray-200">
                <div className="py-1">
                  <button
                    onClick={() => handlePublish('production')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Deploy to Production
                    </div>
                  </button>
                  <button
                    onClick={() => handlePublish('staging')}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Deploy to Staging
                    </div>
                  </button>
                  <div className="border-t border-gray-200 my-1"></div>
                  <button
                    onClick={() => {
                      console.log('Export workflow...');
                      setShowPublishMenu(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                      </svg>
                      Export as JSON
                    </div>
                  </button>
                  <button
                    onClick={() => {
                      console.log('View API docs...');
                      setShowPublishMenu(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                      View API Documentation
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Click outside to close publish menu */}
      {showPublishMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowPublishMenu(false)}
        />
      )}

      {/* Dialogs */}
      {showExecutionDialog && workflowId && (
        <ExecutionDialog
          workflowId={workflowId}
          onClose={() => setShowExecutionDialog(false)}
        />
      )}

      {showPlaygroundDialog && workflowId && (
        <PlaygroundDialog
          workflowId={workflowId}
          onClose={() => setShowPlaygroundDialog(false)}
        />
      )}
    </>
  );
};