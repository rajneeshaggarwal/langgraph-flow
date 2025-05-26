import axios from 'axios';
import { Workflow, WorkflowCreate, WorkflowExecution } from '../types/workflow';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const workflowApi = {
  // Workflow CRUD operations
  async createWorkflow(workflow: WorkflowCreate): Promise<Workflow> {
    const response = await api.post('/api/workflows/', workflow);
    return response.data;
  },

  async getWorkflows(): Promise<Workflow[]> {
    const response = await api.get('/api/workflows/');
    return response.data;
  },

  async getWorkflow(id: string): Promise<Workflow> {
    const response = await api.get(`/api/workflows/${id}`);
    return response.data;
  },

  async updateWorkflow(id: string, workflow: Partial<WorkflowCreate>): Promise<Workflow> {
    const response = await api.put(`/api/workflows/${id}`, workflow);
    return response.data;
  },

  async deleteWorkflow(id: string): Promise<void> {
    await api.delete(`/api/workflows/${id}`);
  },

  // Execution operations
  async executeWorkflow(workflowId: string, inputData?: Record<string, any>): Promise<WorkflowExecution> {
    const response = await api.post(`/api/workflows/${workflowId}/execute`, {
      workflow_id: workflowId,
      input_data: inputData,
    });
    return response.data;
  },

  async getExecutions(workflowId: string): Promise<WorkflowExecution[]> {
    const response = await api.get(`/api/workflows/${workflowId}/executions`);
    return response.data;
  },
};