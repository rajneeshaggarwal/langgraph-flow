import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Tooltip } from 'react-tooltip';

export const ChatInputNode = memo(({ data, selected, id }: NodeProps) => {
  const handleConfigClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    const event = new CustomEvent('nodeConfigClick', { 
      detail: { nodeId: id }
    });
    window.dispatchEvent(event);
  };

  return (
    <div
      className={`px-2 py-1.5 shadow-md rounded-md bg-white border-2 min-w-[140px] relative ${
        selected ? 'border-blue-500' : 'border-gray-200'
      }`}
    >
      {/* Configure Button - Smaller and positioned closer */}
      <button 
        onClick={handleConfigClick}
        className="absolute top-1 right-1 p-0.5 hover:bg-gray-100 rounded"
        title="Configure"
      >
        <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>

      <div className="flex items-center space-x-2 pr-5">
        <div className="rounded-full w-7 h-7 flex items-center justify-center bg-blue-100 flex-shrink-0">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-4 h-4 text-blue-600"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.020.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.740.194V21l4.155-4.155"
            />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold text-gray-900 truncate">
            {data.label}
          </div>
          <div className="text-[10px] text-gray-500">Chat Input</div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="w-2.5 h-2.5 bg-blue-500"
        style={{ right: -5 }}
        data-tooltip-id="chat-input-tooltip"
        data-tooltip-content="Output: Message"
      />
      
      <Tooltip 
        id="chat-input-tooltip"
        place="right"
        className="!bg-black !text-white !opacity-100 !p-0"
        style={{ 
          backgroundColor: 'black',
          padding: '12px',
          borderRadius: '6px',
          minWidth: '180px'
        }}
        render={() => (
          <div style={{ margin: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <span style={{ fontSize: '11px' }}>Output:</span>
              <span style={{ 
                backgroundColor: '#3B82F6', 
                color: 'white', 
                padding: '3px 8px', 
                borderRadius: '4px', 
                fontSize: '11px', 
                fontWeight: '500' 
              }}>
                Message
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <p style={{ fontSize: '11px', margin: 0 }}>Drag to connect</p>
              <p style={{ fontSize: '11px', margin: 0 }}>Click to filter</p>
            </div>
          </div>
        )}
      />
    </div>
  );
});

ChatInputNode.displayName = 'ChatInputNode';