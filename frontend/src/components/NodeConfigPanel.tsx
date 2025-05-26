import React, { useState, useEffect } from 'react';
import { Node } from 'reactflow';
import { useWorkflowStore } from '../store/workflowStore';

interface NodeConfigPanelProps {
  node: Node | null;
  onClose: () => void;
}

export const NodeConfigPanel: React.FC<NodeConfigPanelProps> = ({ node, onClose }) => {
  const updateNodeData = useWorkflowStore((state) => state.updateNodeData);
  const [config, setConfig] = useState<any>({});

  useEffect(() => {
    if (node) {
      setConfig(node.data.config || {});
    }
  }, [node]);

  if (!node) return null;

  const handleSave = () => {
    updateNodeData(node.id, { config });
    onClose();
  };

  const renderAgentConfig = () => (
    <>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Agent Role
        </label>
        <select
          value={config.role || 'executor'}
          onChange={(e) => setConfig({ ...config, role: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="coordinator">Coordinator</option>
          <option value="researcher">Researcher</option>
          <option value="analyzer">Analyzer</option>
          <option value="writer">Writer</option>
          <option value="reviewer">Reviewer</option>
          <option value="executor">Executor</option>
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Model
        </label>
        <select
          value={config.model || 'gpt-3.5-turbo'}
          onChange={(e) => setConfig({ ...config, model: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          <option value="gpt-4">GPT-4</option>
          <option value="claude-2">Claude 2</option>
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Temperature
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={config.temperature || 0.7}
          onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
          className="w-full"
        />
        <span className="text-sm text-gray-500">{config.temperature || 0.7}</span>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          System Prompt
        </label>
        <textarea
          value={config.systemPrompt || ''}
          onChange={(e) => setConfig({ ...config, systemPrompt: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={4}
          placeholder="Enter system prompt..."
        />
      </div>
    </>
  );

  const renderToolConfig = () => (
    <>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tool Name
        </label>
        <input
          type="text"
          value={config.toolName || ''}
          onChange={(e) => setConfig({ ...config, toolName: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter tool name..."
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tool Type
        </label>
        <select
          value={config.toolType || 'custom'}
          onChange={(e) => setConfig({ ...config, toolType: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="custom">Custom</option>
          <option value="search">Search</option>
          <option value="calculator">Calculator</option>
          <option value="file_reader">File Reader</option>
          <option value="api_call">API Call</option>
        </select>
      </div>
      
      {config.toolType === 'api_call' && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Endpoint
          </label>
          <input
            type="text"
            value={config.apiEndpoint || ''}
            onChange={(e) => setConfig({ ...config, apiEndpoint: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://api.example.com/endpoint"
          />
        </div>
      )}
    </>
  );

  const renderConditionalConfig = () => (
    <>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Condition Type
        </label>
        <select
          value={config.conditionType || 'expression'}
          onChange={(e) => setConfig({ ...config, conditionType: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="expression">Expression</option>
          <option value="contains">Contains Text</option>
          <option value="equals">Equals</option>
          <option value="greater_than">Greater Than</option>
          <option value="less_than">Less Than</option>
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Condition Value
        </label>
        <input
          type="text"
          value={config.conditionValue || ''}
          onChange={(e) => setConfig({ ...config, conditionValue: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter condition value..."
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Variable to Check
        </label>
        <input
          type="text"
          value={config.variableName || ''}
          onChange={(e) => setConfig({ ...config, variableName: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., response.status"
        />
      </div>
    </>
  );

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold">Configure {node.data.label}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Node Name
          </label>
          <input
            type="text"
            value={node.data.label}
            onChange={(e) => updateNodeData(node.id, { label: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {node.data.type === 'agent' && renderAgentConfig()}
        {node.data.type === 'tool' && renderToolConfig()}
        {node.data.type === 'conditional' && renderConditionalConfig()}

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};