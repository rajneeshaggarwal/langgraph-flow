import React, { memo } from "react";
import { Handle, Position, NodeProps } from "reactflow";

export const AgentNode = memo(({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-2 shadow-md rounded-md bg-white border-2 ${selected
        ? "border-blue-500"
        : "border-gray-200"}`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-blue-500"
      />

      <div className="flex items-center">
        <div className="rounded-full w-12 h-12 flex items-center justify-center bg-blue-100">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-6 h-6 text-blue-600"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
            />
          </svg>
        </div>
        <div className="ml-2">
          <div className="text-lg font-bold">
            {data.label}
          </div>
          <div className="text-gray-500 text-sm">Agent</div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 bg-blue-500"
      />
    </div>
  );
});

AgentNode.displayName = "AgentNode";
