// frontend/src/components/WorkflowCanvas.tsx
import React, { useCallback, useRef, useState } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  ReactFlowProvider,
  ReactFlowInstance,
  Node,
  Edge,
  Connection,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { useWorkflowStore } from '../store/workflowStore';
import { 
  AgentNode, 
  ToolNode, 
  ConditionalNode,
  ChatInputNode,
  TextInputNode,
  ChatOutputNode,
  TextOutputNode
} from './NodeTypes';
import { NodeConfigPanel } from './NodeConfigPanel';
import { ExecutionMonitor } from './ExecutionMonitor';
import { EdgeLabel } from './EdgeLabel';
import { useWebSocket } from '../hooks/useWebSocket';
import { useKeyPress } from '../hooks/useKeyPress';
import { updateEdge } from 'reactflow';

const nodeTypes = {
  agent: AgentNode,
  tool: ToolNode,
  conditional: ConditionalNode,
  chatInput: ChatInputNode,
  textInput: TextInputNode,
  chatOutput: ChatOutputNode,
  textOutput: TextOutputNode,
};

const edgeTypes = {
  labeled: EdgeLabel,
};

interface WorkflowCanvasProps {
  workflowId?: string;
}

export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({ workflowId }) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [copiedElements, setCopiedElements] = useState<{ nodes: Node[], edges: Edge[] } | null>(null);
  
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    deleteNode,
    pasteNodes,
  } = useWorkflowStore();
  
  const { sendUpdate } = useWebSocket(workflowId);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  
  // Copy handler
  const handleCopy = useCallback(() => {
    const selectedNodes = nodes.filter(node => node.selected);
    const selectedNodeIds = selectedNodes.map(node => node.id);
    const selectedEdges = edges.filter(
      edge => selectedNodeIds.includes(edge.source) && selectedNodeIds.includes(edge.target)
    );
    
    if (selectedNodes.length > 0) {
      setCopiedElements({ nodes: selectedNodes, edges: selectedEdges });
    }
  }, [nodes, edges]);
  
  // Paste handler
  const handlePaste = useCallback(() => {
    if (copiedElements && reactFlowInstance) {
      const viewportCenter = reactFlowInstance.project({
        x: window.innerWidth / 2,
        y: window.innerHeight / 2,
      });
      
      pasteNodes(copiedElements.nodes, copiedElements.edges, viewportCenter);
    }
  }, [copiedElements, reactFlowInstance, pasteNodes]);
  
  // Delete handler
  const handleDelete = useCallback(() => {
    const selectedNodes = nodes.filter(node => node.selected);
    selectedNodes.forEach(node => deleteNode(node.id));
  }, [nodes, deleteNode]);
  
  // Keyboard shortcuts
  useKeyPress('c', handleCopy, { ctrl: true, preventDefault: true });
  useKeyPress('c', handleCopy, { meta: true, preventDefault: true }); // For Mac
  useKeyPress('v', handlePaste, { ctrl: true, preventDefault: true });
  useKeyPress('v', handlePaste, { meta: true, preventDefault: true }); // For Mac
  useKeyPress('Delete', handleDelete);
  useKeyPress('Backspace', handleDelete); // Alternative delete key
  
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);
  
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      
      if (!reactFlowInstance || !reactFlowWrapper.current) return;
      
      const type = event.dataTransfer.getData('application/reactflow');
      if (!type) return;
      
      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });
      
      addNode(type, position);
    },
    [reactFlowInstance, addNode]
  );
  
  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);
  
  // Custom edge update handler
  const onEdgeUpdate = useCallback(
    (oldEdge: Edge, newConnection: Connection) => {
      // React Flow's updateEdge utility handles the connection validation
      const { edges: currentEdges, setEdges } = useWorkflowStore.getState();
      setEdges(updateEdge(oldEdge, newConnection, currentEdges));
    },[]);
  
  // Send updates via WebSocket when nodes or edges change
  React.useEffect(() => {
    if (workflowId) {
      sendUpdate({ nodes, edges });
    }
  }, [nodes, edges, workflowId, sendUpdate]);
  
  return (
    <div className="flex-1 flex flex-col" ref={reactFlowWrapper}>
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={handleNodeClick}
          onEdgeUpdate={onEdgeUpdate}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          snapToGrid
          snapGrid={[15, 15]}
          connectionLineStyle={{ stroke: '#b1b1b7' }}
          defaultEdgeOptions={{
            type: 'labeled',
            animated: true,
            style: { stroke: '#b1b1b7' },
          }}
        >
          <MiniMap
            nodeStrokeColor={(node) => {
              if (node.data?.highlighted) return '#ff0072';
              if (node.selected) return '#1a90ff';
              return '#b1b1b7';
            }}
            nodeColor={(node) => {
              if (node.data?.highlighted) return '#ff0072';
              return '#fff';
            }}
            nodeBorderRadius={2}
          />
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
        
        {/* Floating toolbar */}
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-2 flex space-x-2">
          <button
            onClick={handleCopy}
            className="p-2 hover:bg-gray-100 rounded"
            title="Copy (Ctrl+C)"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
          <button
            onClick={handlePaste}
            className="p-2 hover:bg-gray-100 rounded"
            title="Paste (Ctrl+V)"
            disabled={!copiedElements}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </button>
          <button
            onClick={handleDelete}
            className="p-2 hover:bg-gray-100 rounded"
            title="Delete (Delete)"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
      
      <ExecutionMonitor />
      
      {selectedNode && (
        <NodeConfigPanel
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
};

export const WorkflowCanvasWithProvider: React.FC<WorkflowCanvasProps> = (props) => (
  <ReactFlowProvider>
    <WorkflowCanvas {...props} />
  </ReactFlowProvider>
);