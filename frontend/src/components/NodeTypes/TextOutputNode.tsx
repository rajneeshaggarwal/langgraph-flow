import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export const TextOutputNode = memo(({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-3 shadow-md rounded-lg bg-white border-2 min-w-[200px] ${
        selected ? 'border-indigo-500' : 'border-gray-200'
      }`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-indigo-500"
        style={{ left: -6 }}
      />

      <div className="flex items-center space-x-3">
        <div className="rounded-full w-10 h-10 flex items-center justify-center bg-indigo-100">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-5 h-5 text-indigo-600"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-gray-900 truncate">
            {data.label}
          </div>
          <div className="text-xs text-gray-500">Text Output</div>
          <div className="text-xs text-indigo-600 mt-1">
            Display text results
          </div>
        </div>
      </div>
    </div>
  );
});

TextOutputNode.displayName = 'TextOutputNode';