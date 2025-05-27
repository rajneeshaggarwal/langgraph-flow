// frontend/src/components/NodeTypes/PromptNode.tsx
import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const PromptNode = memo(({ data, selected }: NodeProps) => {
  return (
    <div
      className={`shadow-md rounded-lg bg-white border-2 min-w-[300px] ${
        selected ? 'border-blue-500' : 'border-gray-200'
      }`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-gray-400"
        style={{ left: -6 }}
      />
      
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-gray-100 rounded flex items-center justify-center">
            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-gray-900">Prompt</span>
          <button 
            className="ml-auto p-1 hover:bg-gray-100 rounded"
            onClick={(e) => {
              e.stopPropagation();
              // Toggle preview functionality would go here
            }}
          >
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Create a prompt template with dynamic variables.
        </p>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="mb-2">
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Template
          </label>
          <div className="relative">
            <div className="bg-gray-50 border border-gray-200 rounded-md p-3 min-h-[80px] text-sm text-gray-600">
              {data.promptTemplate || 'Type your prompt here...'}
            </div>
            <button className="absolute top-2 right-2 p-1 hover:bg-gray-200 rounded">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4" />
              </svg>
            </button>
          </div>
        </div>

        {/* Variables indicator */}
        {data.variables && data.variables.length > 0 && (
          <div className="mt-2">
            <p className="text-xs text-gray-500">
              Variables: {data.variables.map((v: string) => `{{${v}}}`).join(', ')}
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 rounded-b-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span className="text-xs text-gray-600">Prompt Message</span>
          </div>
          <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-blue-500"
        style={{ right: -6 }}
      />
    </div>
  );
});

PromptNode.displayName = 'PromptNode';