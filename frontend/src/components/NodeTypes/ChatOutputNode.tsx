import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Tooltip } from 'react-tooltip';

export const ChatOutputNode = memo(({ data, selected, id }: NodeProps) => {
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
        selected ? 'border-purple-500' : 'border-gray-200'
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

      <Handle
        type="target"
        position={Position.Left}
        className="w-2.5 h-2.5 bg-purple-500"
        style={{ left: -5 }}
        data-tooltip-id="chat-output-tooltip"
        data-tooltip-content="Input: Message"
      />

      <div className="flex items-center space-x-2 pr-5">
        <div className="rounded-full w-7 h-7 flex items-center justify-center bg-purple-100 flex-shrink-0">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-4 h-4 text-purple-600"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
            />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold text-gray-900 truncate">
            {data.label}
          </div>
          <div className="text-[10px] text-gray-500">Chat Output</div>
        </div>
      </div>
      
      <Tooltip 
        id="chat-output-tooltip"
        place="left"
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
              <span style={{ fontSize: '11px' }}>Input:</span>
              <span style={{ 
                backgroundColor: '#9333EA', 
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
              <p style={{ fontSize: '11px', margin: 0 }}>Connect from outputs</p>
              <p style={{ fontSize: '11px', margin: 0 }}>Click to filter</p>
            </div>
          </div>
        )}
      />
    </div>
  );
});

ChatOutputNode.displayName = 'ChatOutputNode';