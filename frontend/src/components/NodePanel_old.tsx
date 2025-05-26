import React from 'react';
import { useWorkflowStore } from '../store/workflowStore';

const nodeTypes = [
  { type: 'agent', label: 'Agent', icon: '🤖' },
  { type: 'tool', label: 'Tool', icon: '🔧' },
  { type: 'conditional', label: 'Conditional', icon: '🔀' },
];

export const NodePanel: React.FC = () => {
  const addNode = useWorkflowStore((state) => state.addNode);
  
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };
  
  return (
    <aside className="w-64 bg-gray-100 p-4 border-r border-gray-200">
      <h3 className="text-lg font-semibold mb-4">Components</h3>
      
      <div className="space-y-2">
        {nodeTypes.map((node) => (
          <div
            key={node.type}
            className="flex items-center p-3 bg-white rounded-lg shadow cursor-move hover:shadow-md transition-shadow"
            onDragStart={(e) => onDragStart(e, node.type)}
            draggable
          >
            <span className="text-2xl mr-3">{node.icon}</span>
            <span className="font-medium">{node.label}</span>
          </div>
        ))}
      </div>
      
      <div className="mt-8">
        <h4 className="text-sm font-semibold text-gray-600 mb-2">Quick Add</h4>
        <div className="space-y-1">
          {nodeTypes.map((node) => (
            <button
              key={node.type}
              onClick={() => addNode(node.type, { x: 250, y: 250 })}
              className="w-full text-left p-2 text-sm bg-gray-50 hover:bg-gray-200 rounded transition-colors"
            >
              Add {node.label}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};