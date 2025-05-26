// frontend/src/hooks/useWorkflow.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useWorkflowStore } from '../store/workflowStore';
import { workflowApi } from '../services/api';
import { Workflow, WorkflowNode, WorkflowEdge, WorkflowExecution } from '../types/workflow';
import { useCallback } from 'react';
import { Node, Edge } from 'reactflow';

// Helper function to convert React Flow nodes to our WorkflowNode type
const convertToWorkflowNode = (node: Node): WorkflowNode => ({
  id: node.id,
  type: node.type || 'default', // Provide default if type is undefined
  position: node.position,
  data: node.data as any, // We know our data structure matches
});

// Helper function to convert React Flow edges to our WorkflowEdge type
const convertToWorkflowEdge = (edge: Edge): WorkflowEdge => ({
  id: edge.id,
  source: edge.source,
  target: edge.target,
  sourceHandle: edge.sourceHandle ?? undefined,
  targetHandle: edge.targetHandle ?? undefined,
  data: edge.data,
});

export const useWorkflow = (workflowId?: string) => {
  const queryClient = useQueryClient();
  const { setNodes, setEdges, selectedWorkflowId } = useWorkflowStore();

  // Fetch all workflows
  const {
    data: workflows,
    isLoading: isLoadingWorkflows,
    error: workflowsError,
  } = useQuery({
    queryKey: ['workflows'],
    queryFn: workflowApi.getWorkflows,
  });

  // Fetch single workflow
  const {
    data: workflow,
    isLoading: isLoadingWorkflow,
    error: workflowError,
  } = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => workflowApi.getWorkflow(workflowId!),
    enabled: !!workflowId,
  });

  // Create workflow mutation
  const createWorkflowMutation = useMutation({
    mutationFn: workflowApi.createWorkflow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });

  // Update workflow mutation
  const updateWorkflowMutation = useMutation({
    mutationFn: ({ id, ...data }: { id: string; name: string; nodes: WorkflowNode[]; edges: WorkflowEdge[] }) =>
      workflowApi.updateWorkflow(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      if (workflowId) {
        queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] });
      }
    },
  });

  // Delete workflow mutation
  const deleteWorkflowMutation = useMutation({
    mutationFn: workflowApi.deleteWorkflow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });

  // Execute workflow mutation
  const executeWorkflowMutation = useMutation({
    mutationFn: ({ workflowId, inputData }: { workflowId: string; inputData?: Record<string, any> }) =>
      workflowApi.executeWorkflow(workflowId, inputData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['executions', variables.workflowId] });
    },
  });

  // Fetch workflow executions
  const {
    data: executions,
    isLoading: isLoadingExecutions,
    error: executionsError,
  } = useQuery({
    queryKey: ['executions', workflowId],
    queryFn: () => workflowApi.getExecutions(workflowId!),
    enabled: !!workflowId,
  });

  // Load workflow into the store
  const loadWorkflow = useCallback(
    (workflow: Workflow) => {
      if (workflow.graph_data) {
        setNodes(workflow.graph_data.nodes || []);
        setEdges(workflow.graph_data.edges || []);
      }
    },
    [setNodes, setEdges]
  );

  // Save current workflow from store
  const saveCurrentWorkflow = useCallback(async () => {
    const { nodes, edges } = useWorkflowStore.getState();
    
    if (!selectedWorkflowId && !workflowId) {
      console.error('No workflow ID available for saving');
      return;
    }

    const id = selectedWorkflowId || workflowId;
    
    try {
      // Convert React Flow types to our workflow types
      const workflowNodes = nodes.map(convertToWorkflowNode);
      const workflowEdges = edges.map(convertToWorkflowEdge);
      
      await updateWorkflowMutation.mutateAsync({
        id: id!,
        name: workflow?.name || 'Untitled Workflow',
        nodes: workflowNodes,
        edges: workflowEdges,
      });
    } catch (error) {
      console.error('Failed to save workflow:', error);
      throw error;
    }
  }, [selectedWorkflowId, workflowId, workflow, updateWorkflowMutation]);

  // Create new workflow from current state
  const createNewWorkflow = useCallback(
    async (name: string, description?: string) => {
      const { nodes, edges } = useWorkflowStore.getState();
      
      try {
        // Convert React Flow types to our workflow types
        const workflowNodes = nodes.map(convertToWorkflowNode);
        const workflowEdges = edges.map(convertToWorkflowEdge);
        
        const newWorkflow = await createWorkflowMutation.mutateAsync({
          name,
          description,
          nodes: workflowNodes,
          edges: workflowEdges,
        });
        return newWorkflow;
      } catch (error) {
        console.error('Failed to create workflow:', error);
        throw error;
      }
    },
    [createWorkflowMutation]
  );

  // Execute current workflow
  const executeCurrentWorkflow = useCallback(
    async (inputData?: Record<string, any>) => {
      const id = selectedWorkflowId || workflowId;
      
      if (!id) {
        console.error('No workflow ID available for execution');
        return;
      }

      try {
        const execution = await executeWorkflowMutation.mutateAsync({
          workflowId: id,
          inputData,
        });
        return execution;
      } catch (error) {
        console.error('Failed to execute workflow:', error);
        throw error;
      }
    },
    [selectedWorkflowId, workflowId, executeWorkflowMutation]
  );

  return {
    // Workflow data
    workflows,
    workflow,
    executions,
    
    // Loading states
    isLoadingWorkflows,
    isLoadingWorkflow,
    isLoadingExecutions,
    
    // Error states
    workflowsError,
    workflowError,
    executionsError,
    
    // Mutations
    createWorkflow: createNewWorkflow,
    updateWorkflow: updateWorkflowMutation.mutate,
    deleteWorkflow: deleteWorkflowMutation.mutate,
    executeWorkflow: executeCurrentWorkflow,
    
    // Mutation states
    isCreating: createWorkflowMutation.isPending,
    isUpdating: updateWorkflowMutation.isPending,
    isDeleting: deleteWorkflowMutation.isPending,
    isExecuting: executeWorkflowMutation.isPending,
    
    // Helper functions
    loadWorkflow,
    saveCurrentWorkflow,
    
    // Refresh functions
    refetchWorkflows: () => queryClient.invalidateQueries({ queryKey: ['workflows'] }),
    refetchWorkflow: () => queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] }),
    refetchExecutions: () => queryClient.invalidateQueries({ queryKey: ['executions', workflowId] }),
  };
};

// Hook for workflow list operations
export const useWorkflowList = () => {
  const { workflows, isLoadingWorkflows, workflowsError, refetchWorkflows } = useWorkflow();
  
  return {
    workflows: workflows || [],
    isLoading: isLoadingWorkflows,
    error: workflowsError,
    refetch: refetchWorkflows,
  };
};

// Hook for single workflow operations
export const useWorkflowDetails = (workflowId: string) => {
  const {
    workflow,
    isLoadingWorkflow,
    workflowError,
    loadWorkflow,
    saveCurrentWorkflow,
    executeWorkflow,
    executions,
    isUpdating,
    isExecuting,
  } = useWorkflow(workflowId);
  
  return {
    workflow,
    isLoading: isLoadingWorkflow,
    error: workflowError,
    loadWorkflow,
    save: saveCurrentWorkflow,
    execute: executeWorkflow,
    executions: executions || [],
    isSaving: isUpdating,
    isExecuting,
  };
};