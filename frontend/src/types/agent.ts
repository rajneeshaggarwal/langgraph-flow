// frontend/src/types/agent.ts
export enum AgentRole {
    COORDINATOR = 'coordinator',
    RESEARCHER = 'researcher',
    ANALYZER = 'analyzer',
    WRITER = 'writer',
    REVIEWER = 'reviewer',
    EXECUTOR = 'executor',
  }
  
  export interface AgentConfig {
    role: AgentRole;
    model?: string;
    temperature?: number;
    systemPrompt?: string;
    tools?: string[];
  }
  
  export interface AgentExecution {
    id: string;
    executionId: string;
    agentId: string;
    inputData?: any;
    outputData?: any;
    state?: any;
    startedAt: string;
    completedAt?: string;
  }
  
  export interface AgentMessage {
    id: string;
    executionId: string;
    senderId: string;
    recipientId: string;
    messageType: string;
    content: any;
    createdAt: string;
  }