import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const ConditionalNode = memo(({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-2 shadow-md rounded-md bg-white border-2 ${
        selected ? 'border-orange-500' : 'border-gray-200'
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-orange-500"
      />
      
      <div className="flex items-center">
        <div className="rounded-full w-12 h-12 flex items-center justify-center bg-orange-100">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-6 h-6 text-orange-600"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5"
            />
          </svg>
        </div>
        <div className="ml-2">
          <div className="text-lg font-bold">{data.label}</div>
          <div className="text-gray-500 text-sm">Conditional</div>
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        id="true"
        className="w-3 h-3 bg-green-500"
        style={{ left: '25%' }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        className="w-3 h-3 bg-red-500"
        style={{ left: '75%' }}
      />
    </div>
  );
});

ConditionalNode.displayName = 'ConditionalNode';