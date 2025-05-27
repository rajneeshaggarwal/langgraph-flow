import { create } from 'zustand';
import {
  Node,
  Edge,
  OnNodesChange,
  OnEdgesChange,
  applyNodeChanges,
  applyEdgeChanges,
  Connection,
  addEdge,
} from 'reactflow';
import { v4 as uuidv4 } from 'uuid';

interface WorkflowState {
  nodes: Node[];
  edges: Edge[];
  selectedWorkflowId: string | null;
  
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: (connection: Connection) => void;
  
  addNode: (type: string, position: { x: number; y: number }) => void;
  deleteNode: (nodeId: string) => void;
  updateNodeData: (nodeId: string, data: any) => void;
  highlightNode: (nodeId: string) => void;
  
  pasteNodes: (nodes: Node[], edges: Edge[], offset: { x: number; y: number }) => void;
  groupNodes: (nodeIds: string[], groupName: string) => void;
  
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  
  clearWorkflow: () => void;
}

export const useWorkflowStore = create<WorkflowState>()((set, get) => ({
  nodes: [],
  edges: [],
  selectedWorkflowId: null,
  
  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  
  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  
  onConnect: (connection) => {
    const newEdge = {
      ...connection,
      id: uuidv4(),
      type: 'labeled',
      data: { label: connection.sourceHandle || 'default' },
    } as Edge;
    
    set({
      edges: addEdge(newEdge, get().edges),
    });
  },
  
  addNode: (type, position) => {
    // Generate appropriate label based on node type
    const getNodeLabel = (nodeType: string) => {
      switch (nodeType) {
        case 'chatInput':
          return 'Chat Input';
        case 'textInput':
          return 'Text Input';
        case 'chatOutput':
          return 'Chat Output';
        case 'textOutput':
          return 'Text Output';
        case 'prompt':
          return 'Prompt';
        default:
          return `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} Node`;
      }
    };

    // Generate default configuration based on node type
    const getDefaultConfig = (nodeType: string) => {
      switch (nodeType) {
        case 'chatInput':
          return {
            chatStyle: 'bubble',
            welcomeMessage: 'Hello! How can I help you today?',
            inputPlaceholder: 'Type your message...',
            enableFileUpload: false,
            historyLimit: 50,
          };
        case 'textInput':
          return {
            inputType: 'text',
            placeholder: 'Enter text...',
            defaultValue: '',
            required: false,
            pattern: '',
          };
        case 'chatOutput':
          return {
            displayMode: 'conversation',
            bubbleStyle: 'modern',
            showTimestamps: false,
            showAvatar: true,
            enableCopy: true,
            maxMessages: 100,
          };
        case 'textOutput':
          return {
            outputFormat: 'text',
            displayStyle: 'block',
            autoRefresh: false,
            refreshInterval: 30,
            maxLength: 1000,
          };
          case 'prompt':
            return {
              promptTemplate: '',
              variables: [],
              model: 'gpt-3.5-turbo',
              temperature: 0.7,
              systemMessage: '',
              outputFormat: 'text',
              enablePreview: false,
            };
        default:
          return {};
      }
    };

    const newNode: Node = {
      id: uuidv4(),
      type,
      position,
      data: {
        label: getNodeLabel(type),
        type,
        config: getDefaultConfig(type),
      },
    };
    
    set({
      nodes: [...get().nodes, newNode],
    });
  },
  
  deleteNode: (nodeId) => {
    set({
      nodes: get().nodes.filter((node) => node.id !== nodeId),
      edges: get().edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId
      ),
    });
  },
  
  updateNodeData: (nodeId, data) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
      ),
    });
  },
  
  highlightNode: (nodeId) => {
    set({
      nodes: get().nodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          highlighted: node.id === nodeId,
        },
      })),
    });
    
    // Remove highlight after 2 seconds
    setTimeout(() => {
      set({
        nodes: get().nodes.map((node) => ({
          ...node,
          data: {
            ...node.data,
            highlighted: false,
          },
        })),
      });
    }, 2000);
  },
  
  pasteNodes: (nodesToPaste, edgesToPaste, offset) => {
    const idMap = new Map<string, string>();
    
    // Create new nodes with new IDs
    const newNodes = nodesToPaste.map(node => {
      const newId = uuidv4();
      idMap.set(node.id, newId);
      
      return {
        ...node,
        id: newId,
        position: {
          x: node.position.x + offset.x,
          y: node.position.y + offset.y,
        },
        selected: false,
      };
    });
    
    // Create new edges with updated IDs
    const newEdges = edgesToPaste.map(edge => ({
      ...edge,
      id: uuidv4(),
      source: idMap.get(edge.source) || edge.source,
      target: idMap.get(edge.target) || edge.target,
    }));
    
    set({
      nodes: [...get().nodes, ...newNodes],
      edges: [...get().edges, ...newEdges],
    });
  },
  
  groupNodes: (nodeIds, groupName) => {
    const nodesToGroup = get().nodes.filter(node => nodeIds.includes(node.id));
    if (nodesToGroup.length === 0) return;
    
    // Calculate bounding box
    const bounds = nodesToGroup.reduce((acc, node) => ({
      minX: Math.min(acc.minX, node.position.x),
      minY: Math.min(acc.minY, node.position.y),
      maxX: Math.max(acc.maxX, node.position.x + (node.width || 150)),
      maxY: Math.max(acc.maxY, node.position.y + (node.height || 50)),
    }), {
      minX: Infinity,
      minY: Infinity,
      maxX: -Infinity,
      maxY: -Infinity,
    });
    
    const groupNode: Node = {
      id: uuidv4(),
      type: 'group',
      position: { x: bounds.minX - 20, y: bounds.minY - 40 },
      data: { label: groupName },
      style: {
        width: bounds.maxX - bounds.minX + 40,
        height: bounds.maxY - bounds.minY + 80,
        backgroundColor: 'rgba(240, 240, 240, 0.5)',
        border: '2px dashed #999',
      },
    };
    
    // Update nodes to be children of the group
    const updatedNodes = get().nodes.map(node => {
      if (nodeIds.includes(node.id)) {
        return {
          ...node,
          parentNode: groupNode.id,
          extent: 'parent' as const,
          position: {
            x: node.position.x - groupNode.position.x,
            y: node.position.y - groupNode.position.y,
          },
        };
      }
      return node;
    });
    
    set({
      nodes: [groupNode, ...updatedNodes],
    });
  },
  
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  
  clearWorkflow: () => set({ nodes: [], edges: [] }),
}));