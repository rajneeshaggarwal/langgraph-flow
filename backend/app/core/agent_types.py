from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import asyncio
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYZER = "analyzer"
    WRITER = "writer"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"

@dataclass
class AgentMessage:
    sender: str
    recipient: str
    content: Any
    message_type: str = "task"
    metadata: Dict[str, Any] = None

class BaseAgent(ABC):
    def __init__(self, agent_id: str, role: AgentRole, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.role = role
        self.config = config
        self.memory = ConversationBufferMemory()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.state = {}
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass
    
    async def send_message(self, recipient: str, content: Any, message_type: str = "task"):
        """Send message to another agent"""
        message = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            content=content,
            message_type=message_type
        )
        # This will be handled by the coordinator
        return message
    
    async def receive_message(self, message: AgentMessage):
        """Receive message from another agent"""
        await self.message_queue.put(message)
    
    def update_state(self, key: str, value: Any):
        """Update agent's internal state"""
        self.state[key] = value
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent's current state"""
        return self.state.copy()

class LLMAgent(BaseAgent):
    """Agent powered by a language model"""
    
    def __init__(self, agent_id: str, role: AgentRole, config: Dict[str, Any]):
        super().__init__(agent_id, role, config)
        self.llm = ChatOpenAI(
            model=config.get("model", "gpt-3.5-turbo"),
            temperature=config.get("temperature", 0.7)
        )
        self.tools = self._setup_tools()
        
    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the agent"""
        # Add custom tools based on agent role
        tools = []
        if self.role == AgentRole.RESEARCHER:
            tools.append(
                Tool(
                    name="search",
                    func=self._search_tool,
                    description="Search for information"
                )
            )
        return tools
    
    async def _search_tool(self, query: str) -> str:
        """Mock search tool"""
        return f"Search results for: {query}"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input using LLM"""
        prompt = self._build_prompt(input_data)
        
        if self.tools:
            agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self.llm,
                tools=self.tools,
                memory=self.memory
            )
            response = await agent_executor.arun(prompt)
        else:
            response = await self.llm.apredict(prompt)
        
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "response": response,
            "state": self.get_state()
        }
    
    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build prompt based on role and input"""
        role_prompts = {
            AgentRole.COORDINATOR: "You are a coordinator agent. Manage and delegate tasks to other agents.",
            AgentRole.RESEARCHER: "You are a research agent. Find and analyze information.",
            AgentRole.ANALYZER: "You are an analysis agent. Analyze data and provide insights.",
            AgentRole.WRITER: "You are a writing agent. Create well-structured content.",
            AgentRole.REVIEWER: "You are a review agent. Review and improve content.",
        }
        
        base_prompt = role_prompts.get(self.role, "You are an AI agent.")
        task = input_data.get("task", "")
        context = input_data.get("context", "")
        
        return f"{base_prompt}\n\nTask: {task}\n\nContext: {context}"

class CoordinatorAgent(LLMAgent):
    """Special agent that coordinates other agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentRole.COORDINATOR, config)
        self.sub_agents: Dict[str, BaseAgent] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register a sub-agent"""
        self.sub_agents[agent.agent_id] = agent
        
    async def coordinate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate task execution among agents"""
        # Analyze task and determine which agents to involve
        task_analysis = await self._analyze_task(task)
        
        # Create execution plan
        execution_plan = self._create_execution_plan(task_analysis)
        
        # Execute plan
        results = await self._execute_plan(execution_plan)
        
        # Aggregate results
        final_result = await self._aggregate_results(results)
        
        return final_result
    
    async def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task to determine requirements"""
        prompt = f"""
        Analyze this task and determine which agents should be involved:
        Task: {task.get('description', '')}
        
        Available agents: {list(self.sub_agents.keys())}
        
        Return a structured plan.
        """
        
        response = await self.llm.apredict(prompt)
        
        # Parse response and return structured data
        return {
            "required_agents": ["researcher", "analyzer", "writer"],
            "workflow": "sequential",  # or "parallel"
            "dependencies": {}
        }
    
    def _create_execution_plan(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution plan based on task analysis"""
        plan = []
        
        for agent_id in task_analysis["required_agents"]:
            plan.append({
                "agent_id": agent_id,
                "action": "process",
                "dependencies": task_analysis["dependencies"].get(agent_id, [])
            })
        
        return plan
    
    async def _execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute plan with parallel/sequential support"""
        results = []
        completed = set()
        
        while len(completed) < len(plan):
            # Find tasks that can be executed (dependencies met)
            ready_tasks = [
                task for task in plan
                if task["agent_id"] not in completed
                and all(dep in completed for dep in task["dependencies"])
            ]
            
            # Execute ready tasks in parallel
            if ready_tasks:
                task_results = await asyncio.gather(*[
                    self._execute_agent_task(task) for task in ready_tasks
                ])
                
                results.extend(task_results)
                completed.update(task["agent_id"] for task in ready_tasks)
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        
        return results
    
    async def _execute_agent_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single agent task"""
        agent = self.sub_agents.get(task["agent_id"])
        if not agent:
            return {"error": f"Agent {task['agent_id']} not found"}
        
        result = await agent.process(task)
        return result
    
    async def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple agents"""
        prompt = f"""
        Aggregate and summarize these results from multiple agents:
        
        {results}
        
        Provide a coherent final output.
        """
        
        final_summary = await self.llm.apredict(prompt)
        
        return {
            "summary": final_summary,
            "detailed_results": results,
            "status": "completed"
        }