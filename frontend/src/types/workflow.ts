export interface NodeData {
  label: string;
  type:
    | "agent"
    | "tool"
    | "conditional"
    | "start"
    | "end"
    | "chatInput"
    | "textInput"
    | "chatOutput"
    | "textOutput";
  config: Record<string, any>;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: NodeData;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  data?: {
    condition?: string;
  };
}

// This matches what the backend returns
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  graph_data: {
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
  };
  langgraph_config?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// For creating/updating workflows
export interface WorkflowCreate {
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: "pending" | "running" | "completed" | "failed";
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}
