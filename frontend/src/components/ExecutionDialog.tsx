// frontend/src/components/ExecutionDialog.tsx
import React, { useState } from 'react';
import { useWorkflow } from '../hooks/useWorkflow';

interface ExecutionDialogProps {
  workflowId: string;
  onClose: () => void;
}

export const ExecutionDialog: React.FC<ExecutionDialogProps> = ({ workflowId, onClose }) => {
  const [inputData, setInputData] = useState<string>('{\n  "message": "Hello, AI agents!"\n}');
  const [isValid, setIsValid] = useState(true);
  const { executeWorkflow, isExecuting } = useWorkflow(workflowId);

  const handleInputChange = (value: string) => {
    setInputData(value);
    try {
      JSON.parse(value);
      setIsValid(true);
    } catch {
      setIsValid(false);
    }
  };

  const handleExecute = async () => {
    if (!isValid) return;

    try {
      const parsedData = JSON.parse(inputData);
      await executeWorkflow(parsedData);
      onClose();
    } catch (error) {
      console.error('Failed to execute workflow:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-bold mb-4">Execute Workflow</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Input Data (JSON)
          </label>
          <textarea
            value={inputData}
            onChange={(e) => handleInputChange(e.target.value)}
            className={`w-full h-40 px-3 py-2 border rounded-md font-mono text-sm ${
              isValid ? 'border-gray-300' : 'border-red-500'
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            placeholder='{"key": "value"}'
          />
          {!isValid && (
            <p className="mt-1 text-sm text-red-600">Invalid JSON format</p>
          )}
        </div>

        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Available Variables</h3>
          <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-600">
            <p>• <code>message</code>: Initial message for agents</p>
            <p>• <code>context</code>: Additional context object</p>
            <p>• <code>parameters</code>: Execution parameters</p>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={handleExecute}
            disabled={!isValid || isExecuting}
            className={`px-4 py-2 text-white rounded-md ${
              !isValid || isExecuting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isExecuting ? 'Executing...' : 'Execute'}
          </button>
        </div>
      </div>
    </div>
  );
};